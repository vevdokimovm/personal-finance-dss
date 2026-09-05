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
    # None = бессрочная цель: копим фоном, срочность нейтральная (канон §6.3).
    deadline: Optional[datetime] = None
    category: GoalCategory = GoalCategory.material
    comment: Optional[str] = None
    priority: int = 0
    savings_rate: float = Field(default=0.0, ge=0)
    linked_asset_id: Optional[int] = None
    currency: str = "RUB"
    # P3.7: положить цель в общий бюджет household. None = личная (дефолт).
    household_id: Optional[int] = None


class GoalUpdate(BaseModel):
    """Правка цели. `current_amount` сознательно отсутствует (владелец: не общий edit
    для прогресса — только через `POST /goals/{id}/contributions`); лишние поля в теле
    запроса Pydantic молча игнорирует, не 422."""

    name: Optional[str] = None
    target_amount: Optional[float] = Field(default=None, ge=0)
    deadline: Optional[datetime] = None
    category: Optional[GoalCategory] = None
    comment: Optional[str] = None
    priority: Optional[int] = None
    savings_rate: Optional[float] = Field(default=None, ge=0)
    linked_asset_id: Optional[int] = None


class GoalContributionCreate(BaseModel):
    amount: float = Field(gt=0)


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime] = None
    category: str
    comment: Optional[str] = None
    priority: int = 0
    savings_rate: float = 0.0
    linked_asset_id: Optional[int] = None
    is_active: bool = True
    achieved_at: Optional[datetime] = None
    # 🔴 Общий доступ виден в ответе (v8.55.0). Без этого поля продукт принимал
    # `household_id` и отдавал ответ, по которому нельзя понять, стала ли запись
    # общей: человек думает «поделился», а проверить это нечем.
    household_id: Optional[int] = None
