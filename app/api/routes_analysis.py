from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.crud import get_goals, get_obligations, get_transactions
from app.dependencies import get_db
from app.schemas.recommendation import IndicatorsResponse
from app.services.pipeline import run_pipeline


router = APIRouter(tags=["Аналитика"])


@router.get(
    "/analysis",
    summary="Получить финансовые показатели",
    response_model=IndicatorsResponse,
)
def get_analysis(db: Session = Depends(get_db)) -> IndicatorsResponse:
    result = run_pipeline(
        transactions=get_transactions(db),
        obligations=get_obligations(db),
        goals=get_goals(db),
    )
    return IndicatorsResponse(**result["indicators"])
