from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=64)
    limit_amount: float = Field(..., gt=0)
    household_id: Optional[int] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    limit_amount: float
    created_at: Optional[datetime] = None


class BudgetStatus(BaseModel):
    category: str
    limit_amount: float
    spent: float
    pct: float
    over: bool
