"""B2B-маршрут `/v1/analyze` (FR-23, INFRA-15).

Партнёр присылает данные в канонической модели FinancialSnapshot и получает
Recommendation. Движок — реальный CoreFinanceEngine под Protocol FinanceEngine.
Контракт provider-agnostic: партнёру не нужно знать о внутренней схеме БД.

Авторизация — статический API-ключ (заголовок X-API-Key) из настроек. Пустой
список ключей (по умолчанию) отключает эндпоинт — портал включается осознанно.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db import SessionLocal
from app.ingestion.engine import CoreFinanceEngine
from app.ingestion.models import (
    Account,
    Debt,
    FinancialSnapshot,
    Goal,
    RiskProfile,
    Transaction,
    TransactionType,
)
from app.services.currency import CurrencyConverter
from app.services.event_logger import log_event

router = APIRouter(prefix="/v1", tags=["B2B"])


# ── Контрактные DTO партнёра ─────────────────────────────────────────────
class AccountDTO(BaseModel):
    account_id: str
    name: str
    balance: float
    currency: str = "RUB"
    is_liquid: bool = False
    interest_rate: float = 0.0


class TransactionDTO(BaseModel):
    transaction_id: str
    amount: float
    type: int = Field(description="1=income, 2=expense")
    date: datetime
    currency: str = "RUB"
    description: Optional[str] = None
    mcc: Optional[str] = None


class DebtDTO(BaseModel):
    debt_id: str
    name: str
    balance: float
    monthly_payment: float
    interest_rate: float
    term_months: int = 0
    currency: str = "RUB"


class GoalDTO(BaseModel):
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: datetime
    category: str = "material"
    currency: str = "RUB"


class SnapshotDTO(BaseModel):
    base_currency: str = "RUB"
    risk_profile: int = Field(default=3, ge=1, le=5)
    accounts: list[AccountDTO] = Field(default_factory=list)
    transactions: list[TransactionDTO] = Field(default_factory=list)
    debts: list[DebtDTO] = Field(default_factory=list)
    goals: list[GoalDTO] = Field(default_factory=list)
    l_min: float = 0.0
    r_bench: float = 0.14
    horizon_months: int = 12


class AllocationDTO(BaseModel):
    to_debt: float
    to_reserve: float
    to_goals: float


class RecommendationDTO(BaseModel):
    allocation: AllocationDTO
    rt: float
    lt: float
    dt: float
    blr: float
    u_score: float
    currency: str
    reasoning: str
    alternatives_total: int
    alternatives_accepted: int


def _require_api_key(x_api_key: Optional[str]) -> None:
    keys = settings.b2b_api_keys_list
    if not keys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="B2B-эндпоинт не активирован.",
        )
    if not x_api_key or x_api_key not in keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный API-ключ.",
        )


def _to_snapshot(dto: SnapshotDTO) -> FinancialSnapshot:
    return FinancialSnapshot(
        base_currency=dto.base_currency,
        risk_profile=RiskProfile(dto.risk_profile),
        l_min=Decimal(str(dto.l_min)),
        r_bench=Decimal(str(dto.r_bench)),
        horizon_months=dto.horizon_months,
        accounts=[
            Account(
                account_id=a.account_id, name=a.name, balance=Decimal(str(a.balance)),
                currency=a.currency, is_liquid=a.is_liquid,
                interest_rate=Decimal(str(a.interest_rate)),
            )
            for a in dto.accounts
        ],
        transactions=[
            Transaction(
                transaction_id=t.transaction_id, amount=Decimal(str(t.amount)),
                type=TransactionType(t.type), date=t.date, currency=t.currency,
                description=t.description, mcc=t.mcc,
            )
            for t in dto.transactions
        ],
        debts=[
            Debt(
                debt_id=d.debt_id, name=d.name, balance=Decimal(str(d.balance)),
                monthly_payment=Decimal(str(d.monthly_payment)),
                interest_rate=Decimal(str(d.interest_rate)),
                term_months=d.term_months, currency=d.currency,
            )
            for d in dto.debts
        ],
        goals=[
            Goal(
                goal_id=g.goal_id, name=g.name, target_amount=Decimal(str(g.target_amount)),
                current_amount=Decimal(str(g.current_amount)), deadline=g.deadline,
                category=g.category, currency=g.currency,
            )
            for g in dto.goals
        ],
    )


@router.post(
    "/analyze",
    response_model=RecommendationDTO,
    summary="B2B: анализ канонического снимка финансов партнёра",
)
def analyze(
    payload: SnapshotDTO,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> RecommendationDTO:
    _require_api_key(x_api_key)

    snapshot = _to_snapshot(payload)
    # Конвертер из БД — мультивалютные снимки приводятся к base_currency.
    db: Session = SessionLocal()
    try:
        converter = CurrencyConverter.from_db(db)
    finally:
        db.close()

    engine = CoreFinanceEngine(converter=converter)
    rec = engine.analyze(snapshot, snapshot.risk_profile)

    log_event(
        "b2b_analyze",
        {
            "base_currency": snapshot.base_currency,
            "debts": len(snapshot.debts),
            "goals": len(snapshot.goals),
            "alternatives_total": rec.alternatives_total,
        },
    )

    return RecommendationDTO(
        allocation=AllocationDTO(
            to_debt=float(rec.allocation.to_debt),
            to_reserve=float(rec.allocation.to_reserve),
            to_goals=float(rec.allocation.to_goals),
        ),
        rt=float(rec.rt), lt=float(rec.lt), dt=float(rec.dt), blr=float(rec.blr),
        u_score=float(rec.u_score), currency=rec.currency, reasoning=rec.reasoning,
        alternatives_total=rec.alternatives_total,
        alternatives_accepted=rec.alternatives_accepted,
    )
