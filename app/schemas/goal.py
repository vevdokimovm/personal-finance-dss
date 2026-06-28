from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GoalCategory(str, Enum):
    income_growth = "income_growth"
    safety = "safety"
    material = "material"
    emotional = "emotional"


class GoalCreate(BaseModel):
    name: str
    target_amount: float = Field(ge=0)
    current_amount: float = Field(default=0.0, ge=0)
    deadline: datetime
    category: GoalCategory = GoalCategory.material
    comment: Optional[str] = None
    priority: int = 0
    savings_rate: float = Field(default=0.0, ge=0)
    linked_asset_id: Optional[int] = None
    currency: str = "RUB"
    # P3.7: положить цель в общий бюджет household. None = личная (дефолт).
    household_id: Optional[int] = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: datetime
    category: str
    comment: Optional[str] = None
    priority: int = 0
    savings_rate: float = 0.0
    linked_asset_id: Optional[int] = None
    is_active: bool = True
    achieved_at: Optional[datetime] = None
