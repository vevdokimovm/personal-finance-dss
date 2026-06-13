from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    amount: float
    type: Literal["income", "expense"]
    date: datetime
    category: Optional[str] = None
    description: Optional[str] = None
    mcc: Optional[str] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    category: str
    category_id: Optional[int] = None
    type: Literal["income", "expense"]
    date: datetime
    description: Optional[str] = None
    external_id: Optional[str] = None
    mcc: Optional[str] = None
    is_recurring: bool = False
    is_synced: bool = False
    created_at: Optional[datetime] = None
