from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    amount: float
    category: str
    type: Literal["income", "expense"]
    date: datetime


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    category: str
    type: Literal["income", "expense"]
    date: datetime
