"""Ручной провайдер данных + персистентность (KEEP-06, INFRA-18).

Для рынков без open banking (РФ) ручной ввод — основной путь. Снимок хранится
в БД (`manual_snapshots`) как JSON и переживает рестарт — это отличие от
референсного InMemory-репозитория.

Сериализация Decimal→str сохраняет точность при round-trip через JSON.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.models import ManualSnapshot
from app.ingestion.models import (
    Account,
    Debt,
    FinancialSnapshot,
    Goal,
    RiskProfile,
    Transaction,
    TransactionType,
)


class ManualSnapshotRepository:
    """Персистентное хранилище FinancialSnapshot ручного ввода (INFRA-18)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, user_ref: str, snapshot: FinancialSnapshot) -> None:
        payload = _serialize(snapshot)
        row = (
            self._db.query(ManualSnapshot)
            .filter(ManualSnapshot.user_ref == user_ref)
            .first()
        )
        if row is None:
            row = ManualSnapshot(user_ref=user_ref, payload=payload)
            self._db.add(row)
        else:
            row.payload = payload
        self._db.commit()

    def load(self, user_ref: str) -> FinancialSnapshot | None:
        row = (
            self._db.query(ManualSnapshot)
            .filter(ManualSnapshot.user_ref == user_ref)
            .first()
        )
        return _deserialize(row.payload) if row else None


class ManualProvider:
    """FinancialDataProvider поверх персистентного репозитория."""

    name = "manual"

    def __init__(self, repository: ManualSnapshotRepository) -> None:
        self._repository = repository

    def fetch_snapshot(self, user_ref: str) -> FinancialSnapshot:
        snapshot = self._repository.load(user_ref)
        if snapshot is None:
            return FinancialSnapshot()
        return snapshot


def _serialize(snapshot: FinancialSnapshot) -> dict:
    return {
        "base_currency": snapshot.base_currency,
        "risk_profile": int(snapshot.risk_profile),
        "l_min": str(snapshot.l_min),
        "r_bench": str(snapshot.r_bench),
        "horizon_months": snapshot.horizon_months,
        "accounts": [
            {
                "account_id": a.account_id,
                "name": a.name,
                "balance": str(a.balance),
                "currency": a.currency,
                "is_liquid": a.is_liquid,
                "interest_rate": str(a.interest_rate),
            }
            for a in snapshot.accounts
        ],
        "transactions": [
            {
                "transaction_id": t.transaction_id,
                "amount": str(t.amount),
                "type": int(t.type),
                "date": t.date.isoformat(),
                "currency": t.currency,
                "description": t.description,
                "mcc": t.mcc,
                "category": t.category,
            }
            for t in snapshot.transactions
        ],
        "debts": [
            {
                "debt_id": d.debt_id,
                "name": d.name,
                "balance": str(d.balance),
                "monthly_payment": str(d.monthly_payment),
                "interest_rate": str(d.interest_rate),
                "term_months": d.term_months,
                "currency": d.currency,
            }
            for d in snapshot.debts
        ],
        "goals": [
            {
                "goal_id": g.goal_id,
                "name": g.name,
                "target_amount": str(g.target_amount),
                "current_amount": str(g.current_amount),
                "deadline": g.deadline.isoformat(),
                "category": g.category,
                "currency": g.currency,
            }
            for g in snapshot.goals
        ],
    }


def _deserialize(payload: dict) -> FinancialSnapshot:
    return FinancialSnapshot(
        base_currency=payload.get("base_currency", "RUB"),
        risk_profile=RiskProfile(payload.get("risk_profile", 3)),
        l_min=Decimal(payload.get("l_min", "0.0")),
        r_bench=Decimal(payload.get("r_bench", "0.14")),
        horizon_months=payload.get("horizon_months", 12),
        accounts=[
            Account(
                account_id=a["account_id"],
                name=a["name"],
                balance=Decimal(a["balance"]),
                currency=a.get("currency", "RUB"),
                is_liquid=a.get("is_liquid", False),
                interest_rate=Decimal(a.get("interest_rate", "0")),
            )
            for a in payload.get("accounts", [])
        ],
        transactions=[
            Transaction(
                transaction_id=t["transaction_id"],
                amount=Decimal(t["amount"]),
                type=TransactionType(t["type"]),
                date=datetime.fromisoformat(t["date"]),
                currency=t.get("currency", "RUB"),
                description=t.get("description"),
                mcc=t.get("mcc"),
                category=t.get("category"),
            )
            for t in payload.get("transactions", [])
        ],
        debts=[
            Debt(
                debt_id=d["debt_id"],
                name=d["name"],
                balance=Decimal(d["balance"]),
                monthly_payment=Decimal(d["monthly_payment"]),
                interest_rate=Decimal(d["interest_rate"]),
                term_months=d.get("term_months", 0),
                currency=d.get("currency", "RUB"),
            )
            for d in payload.get("debts", [])
        ],
        goals=[
            Goal(
                goal_id=g["goal_id"],
                name=g["name"],
                target_amount=Decimal(g["target_amount"]),
                current_amount=Decimal(g["current_amount"]),
                deadline=datetime.fromisoformat(g["deadline"]),
                category=g.get("category", "material"),
                currency=g.get("currency", "RUB"),
            )
            for g in payload.get("goals", [])
        ],
    )
