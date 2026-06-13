from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.goal import GoalCreate
from app.schemas.obligation import ObligationCreate
from app.schemas.transaction import TransactionCreate


class BLRStatus(BaseModel):
    level: str
    label: str


class IndicatorsResponse(BaseModel):
    It: Optional[float] = None
    Et: Optional[float] = None
    SigmaP: Optional[float] = None
    CFt: Optional[float] = None
    Rt: float
    Lt: float
    Dt: float
    Bt: Optional[float] = None
    Bliq: Optional[float] = None
    BLR: Optional[float] = None
    BLR_status: Optional[BLRStatus] = None


class RecommendationCreate(BaseModel):
    transactions: List[TransactionCreate] = Field(default_factory=list)
    obligations: List[ObligationCreate] = Field(default_factory=list)
    goals: List[GoalCreate] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    indicators: IndicatorsResponse
    recommendation: str
    input_summary: Dict[str, Any]
