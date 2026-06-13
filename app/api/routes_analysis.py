from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.crud import (
    get_goals,
    get_liquid_assets,
    get_obligations,
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

    result = run_pipeline(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=liquid_assets,
    )
    return result
