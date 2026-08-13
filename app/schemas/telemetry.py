from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AdviceEventCreate(BaseModel):
    """Событие показа плана (волна 0, п. 0.6, `docs/model/telemetry_spec.md`)."""

    model_version: str = Field(min_length=1)
    app_version: str = Field(min_length=1)
    input_snapshot_hash: str = Field(min_length=1, max_length=64)
    advice: dict[str, Any]


class AdviceDecision(BaseModel):
    """Решение пользователя по ранее показанному плану."""

    outcome: Literal["accepted", "modified", "ignored"]
    modified_to: Optional[dict[str, Any]] = None


class AdviceEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: str
    model_version: str
    app_version: str
    input_snapshot_hash: str
    advice: dict[str, Any]
    outcome: Optional[str] = None
    modified_to: Optional[dict[str, Any]] = None
    shown_at: datetime
    decided_at: Optional[datetime] = None
