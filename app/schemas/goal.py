from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GoalCategory(str, Enum):
    income_growth = "income_growth"
    safety = "safety"
    material = "material"
    emotional = "emotional"


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: datetime
    category: GoalCategory = GoalCategory.material
    comment: Optional[str] = None
    priority: int = 0


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
    is_active: bool = True
    achieved_at: Optional[datetime] = None
