from __future__ import annotations

from datetime import datetime
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
    bank: Optional[str] = None
    type: str = "other"
    start_date: Optional[datetime] = None


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
    bank: Optional[str] = None
    type: str = "other"
    start_date: Optional[datetime] = None
    is_active: bool = True
    closed_at: Optional[datetime] = None
