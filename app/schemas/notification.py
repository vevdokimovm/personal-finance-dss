"""Схемы in-app уведомлений (P2.3)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    """Уведомление в ленте колокольчика."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    body: str
    link: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationFeed(BaseModel):
    """Ответ ленты: уведомления + счётчик непрочитанных (для бейджа)."""

    items: list[NotificationOut]
    unread_count: int
