from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ADR-017: только тип А получает численный расчёт вычета — см.
# app/core/investment.py::estimate_iis_deduction.
IISType = Literal["none", "A", "B", "three"]


class UserPrefsUpdate(BaseModel):
    l_min: Optional[float] = Field(None, ge=0.0, le=10.0)
    risk_tolerance: Optional[int] = Field(None, ge=1, le=5)
    horizon: Optional[int] = Field(None, ge=1, le=24)
    r_bench: Optional[float] = Field(None, ge=0.0, le=1.0)
    base_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    iis_type: Optional[IISType] = None
    iis_contributed_this_year: Optional[float] = Field(None, ge=0.0)


class UserPrefsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    l_min: float
    risk_tolerance: int
    horizon: int
    r_bench: float
    base_currency: str = "RUB"
    iis_type: IISType = "none"
    iis_contributed_this_year: float = 0.0
