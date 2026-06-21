"""Продуктовая аналитика — сводка и воронка (P3.4).

В проде эндпоинты стоит закрыть админ-доступом: данные агрегированные (без PII), но это
метрики по всей базе пользователей.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.analytics import analytics_overview, funnel

router = APIRouter(prefix="/analytics", tags=["Аналитика"])

# Воронка онбординга по умолчанию (по реально логируемым событиям).
_DEFAULT_FUNNEL = ["login_success", "obligation_created", "goal_created"]


@router.get("/overview", summary="Сводка продуктовых метрик за период")
def overview(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)) -> dict:
    return analytics_overview(db, days=days)


@router.get("/funnel", summary="Воронка завершения шагов онбординга")
def funnel_endpoint(
    steps: str | None = Query(None, description="Список event_type через запятую"),
    db: Session = Depends(get_db),
) -> dict:
    step_list = [s.strip() for s in steps.split(",") if s.strip()] if steps else _DEFAULT_FUNNEL
    return {"steps": funnel(db, step_list)}
