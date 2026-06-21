from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api._guards import ensure_calculable
from app.database.crud import (
    get_goals,
    get_liquid_assets,
    get_obligations,
    get_transactions,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas.recommendation import RecommendationResponse
from app.database.crud import get_user_prefs
from app.services.currency import to_base_currency
from app.services.pipeline import run_pipeline

import hashlib

from app.services.cache import TTLCache

# Кэш результатов рекомендации. Ключ включает отпечаток входных данных, поэтому любое
# изменение операций/обязательств/целей даёт новый ключ и автоматический пересчёт.
_recommendation_cache = TTLCache(ttl_seconds=180, max_size=512)


def _data_fingerprint(transactions, obligations, goals, liquid_assets, base_currency: str) -> str:
    def num(obj, attr: str) -> float:
        return round(float(getattr(obj, attr, 0) or 0), 2)

    parts = (
        base_currency,
        tuple(sorted(
            (str(getattr(t, "type", "")), num(t, "amount"), str(getattr(t, "date", ""))[:10])
            for t in transactions
        )),
        tuple(sorted(
            (num(o, "amount"), round(float(getattr(o, "interest_rate", 0) or 0), 4),
             num(o, "monthly_payment"))
            for o in obligations
        )),
        tuple(sorted(
            (num(g, "current_amount"), num(g, "target_amount"), str(getattr(g, "deadline", ""))[:10])
            for g in goals
        )),
        tuple(sorted(num(a, "amount") for a in liquid_assets)),
    )
    return hashlib.sha256(repr(parts).encode("utf-8")).hexdigest()


class RecommendationRequest(BaseModel):
    transactions: list[dict[str, Any]] = Field(default_factory=list)
    obligations: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    liquid_assets: list[dict[str, Any]] = Field(default_factory=list)


router = APIRouter(tags=["Рекомендации"])


@router.post(
    "/recommendation",
    summary="Быстрая текстовая рекомендация по показателям финансового состояния",
    response_model=RecommendationResponse,
)
def create_recommendation(
    payload: Optional[RecommendationRequest] = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> RecommendationResponse:
    if payload and (payload.transactions or payload.obligations or payload.goals or payload.liquid_assets):
        transactions = payload.transactions
        obligations = payload.obligations
        goals = payload.goals
        liquid_assets = payload.liquid_assets
    else:
        transactions = get_transactions(db, user_id=user_id)
        obligations = get_obligations(db, user_id=user_id)
        goals = get_goals(db, user_id=user_id)
        liquid_assets = get_liquid_assets(db, user_id=user_id)

    base_currency = (get_user_prefs(db, user_id=user_id).base_currency or "RUB").upper()
    transactions = to_base_currency(db, transactions, base_currency)
    obligations = to_base_currency(db, obligations, base_currency)
    goals = to_base_currency(db, goals, base_currency)
    liquid_assets = to_base_currency(db, liquid_assets, base_currency)

    ensure_calculable(transactions, obligations)

    # Кэшируем только расчёт по данным пользователя из БД (не явный payload — он разовый).
    use_cache = not (payload and (
        payload.transactions or payload.obligations or payload.goals or payload.liquid_assets
    ))
    cache_key = None
    if use_cache:
        fingerprint = _data_fingerprint(transactions, obligations, goals, liquid_assets, base_currency)
        cache_key = f"rec:{user_id or 'guest'}:{fingerprint}"
        cached = _recommendation_cache.get(cache_key)
        if cached is not None:
            return RecommendationResponse(**cached)

    result = run_pipeline(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=liquid_assets,
    )
    if cache_key is not None:
        _recommendation_cache.set(cache_key, result)
    return RecommendationResponse(**result)
