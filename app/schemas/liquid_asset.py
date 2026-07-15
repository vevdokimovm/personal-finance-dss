from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LiquidAssetCreate(BaseModel):
    name: str = "Депозит"
    amount: float = Field(default=0.0, ge=0)
    interest_rate: float = Field(default=0.0, ge=0)
    type: str = "deposit"  # deposit | savings_account | cash
    comment: Optional[str] = None
    currency: str = "RUB"
    household_id: Optional[int] = None


class LiquidAssetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    interest_rate: Optional[float] = Field(default=None, ge=0)
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
