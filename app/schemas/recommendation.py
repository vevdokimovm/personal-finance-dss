from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.goal import GoalCreate
from app.schemas.obligation import ObligationCreate
from app.schemas.transaction import TransactionCreate


class IndicatorsResponse(BaseModel):
    Rt: float
    Lt: float
    Dt: float


class RecommendationCreate(BaseModel):
    transactions: list[TransactionCreate] = Field(default_factory=list)
    obligations: list[ObligationCreate] = Field(default_factory=list)
    goals: list[GoalCreate] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    indicators: IndicatorsResponse
    recommendation: str
    explanation: str
    input_summary: dict[str, int]
