from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict


class ObligationCreate(BaseModel):
    name: str
    amount: float
    interest_rate: float = 0.0
    term: int = 0
    monthly_payment: float
    payment_day: int = 1
    comment: Optional[str] = None


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    amount: float
    interest_rate: float
    term: int
    monthly_payment: float
    payment_day: int
    comment: Optional[str] = None
