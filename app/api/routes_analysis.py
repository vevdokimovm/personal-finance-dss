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
from app.dependencies import get_db
from app.services.pipeline import run_pipeline

router = APIRouter(tags=["Анализ"])


@router.get("/analysis", summary="Финансовые показатели текущего состояния")
def get_analysis(db: Session = Depends(get_db)) -> dict[str, Any]:
    transactions = get_transactions(db)
    obligations = get_obligations(db)
    goals = get_goals(db)
    liquid_assets = get_liquid_assets(db)

    ensure_calculable(transactions, obligations)

    result = run_pipeline(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=liquid_assets,
    )
    return result


@router.get("/analysis/spending", summary="Разрез расходов по категориям и топ-мерчанты (FR-14)")
def get_spending(days: int = 30, db: Session = Depends(get_db)) -> dict[str, Any]:
    return get_spending_by_category(db, days=days)
