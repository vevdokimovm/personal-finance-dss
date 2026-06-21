"""Маршрут запуска email-уведомлений по расписанию (P2.5)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies import require_admin

router = APIRouter(prefix="/notifications", tags=["Уведомления"])


@router.post("/run", summary="Запустить рассылку уведомлений (для cron)", dependencies=[Depends(require_admin)])
def run_notifications(db: Session = Depends(get_db)) -> dict:
    """Проверяет дедлайны целей и превышения бюджета по всем пользователям и шлёт
    недостающие уведомления. Идемпотентно (дедуп по месяцу) — безопасно дёргать по cron."""
    from app.services.notifications import run_all_notifications

    return run_all_notifications(db)
