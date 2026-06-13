from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserPrefsUpdate(BaseModel):
    l_min: Optional[float] = Field(None, ge=0.0, le=10.0)
    risk_tolerance: Optional[int] = Field(None, ge=1, le=5)
    horizon: Optional[int] = Field(None, ge=1, le=24)
    r_bench: Optional[float] = Field(None, ge=0.0, le=1.0)


class UserPrefsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    l_min: float
    risk_tolerance: int
    horizon: int
    r_bench: float
