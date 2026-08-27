from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api._guards import ensure_calculable
from app.database.crud import (
    get_goals,
    get_liquid_assets,
    get_obligations,
    get_spending_by_category,
    get_transactions,
)
from app.dependencies import get_current_user_id, get_db
from app.database.crud import get_user_prefs
from app.services.currency import to_base_currency
from app.services.pipeline import run_pipeline

router = APIRouter(tags=["Анализ"])


@router.get("/analysis", summary="Финансовые показатели текущего состояния")
def get_analysis(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    base_currency = (get_user_prefs(db, user_id=user_id).base_currency or "RUB").upper()
    transactions = to_base_currency(db, get_transactions(db, user_id=user_id), base_currency)
    obligations = to_base_currency(db, get_obligations(db, user_id=user_id), base_currency)
    goals = to_base_currency(db, get_goals(db, user_id=user_id), base_currency)
    liquid_assets = to_base_currency(db, get_liquid_assets(db, user_id=user_id), base_currency)

    ensure_calculable(transactions, obligations)

    result = run_pipeline(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=liquid_assets,
    )
    return result


@router.get("/analysis/spending", summary="Разрез расходов по категориям и топ-мерчанты (FR-14)")
def get_spending(
    days: int = 30,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    return get_spending_by_category(db, days=days, user_id=user_id)
