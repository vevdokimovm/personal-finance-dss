from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: datetime
    comment: str | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: datetime
    comment: str | None = None
