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
from app.dependencies import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.pipeline import run_pipeline


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
) -> RecommendationResponse:
    if payload and (payload.transactions or payload.obligations or payload.goals or payload.liquid_assets):
        transactions = payload.transactions
        obligations = payload.obligations
        goals = payload.goals
        liquid_assets = payload.liquid_assets
    else:
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
    return RecommendationResponse(**result)
