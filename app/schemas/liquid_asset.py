from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class LiquidAssetCreate(BaseModel):
    name: str = "Депозит"
    amount: float = 0.0
    interest_rate: float = 0.0
    type: str = "deposit"  # deposit | savings_account | cash
    comment: Optional[str] = None


class LiquidAssetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    interest_rate: Optional[float] = None
    type: Optional[str] = None
    comment: Optional[str] = None


class LiquidAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    amount: float
    interest_rate: float
    type: str
    comment: Optional[str] = None
