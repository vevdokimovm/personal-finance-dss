from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.crud import get_goals, get_obligations, get_transactions
from app.dependencies import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.pipeline import run_pipeline


class RecommendationRequest(BaseModel):
    transactions: list[dict[str, Any]] = Field(default_factory=list)
    obligations: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)


router = APIRouter(tags=["Рекомендации"])


@router.post(
    "/recommendation",
    summary="Получить финансовую рекомендацию",
    response_model=RecommendationResponse,
)
def create_recommendation(
    payload: Optional[RecommendationRequest] = None,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    if payload and (payload.transactions or payload.obligations or payload.goals):
        transactions = payload.transactions
        obligations = payload.obligations
        goals = payload.goals
    else:
        transactions = get_transactions(db)
        obligations = get_obligations(db)
        goals = get_goals(db)

    result = run_pipeline(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
    )
    return RecommendationResponse(**result)
