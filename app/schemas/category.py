from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    type: Literal["income", "expense"] = "expense"


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    is_system: bool = False
