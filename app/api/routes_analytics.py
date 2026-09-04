"""Продуктовая аналитика — сводка и воронка (P3.4).

В проде эндпоинты стоит закрыть админ-доступом: данные агрегированные (без PII), но это
метрики по всей базе пользователей.
"""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.utils.time import utcnow
from app.dependencies import get_db, require_admin
from app.services.analytics import analytics_overview, funnel

router = APIRouter(prefix="/analytics", tags=["Аналитика"], dependencies=[Depends(require_admin)])

# Воронка онбординга по умолчанию (по реально логируемым событиям).
_DEFAULT_FUNNEL = ["login_success", "obligation_created", "goal_created"]


class AnalyticsOverview(BaseModel):
    """Сводка продуктовых метрик за период.

    🔴 `event_counts` — свободное отображение «тип события → сколько раз», и это
    намеренно: ключи появляются вместе с новым логируемым действием в коде. Перечислить
    их полями значило бы править контракт при каждом таком действии и всё равно
    отставать — событие уже пишется, а схема о нём не знает.
    """

    period_days: int
    total_events: int
    active_users: int
    event_counts: dict[str, int] = Field(description="Тип события → число за период.")


class FunnelStep(BaseModel):
    """Шаг воронки: сколько людей до него дошло."""

    step: str = Field(description="Тип события (`login_success`, `goal_created`, …).")
    users: int
    conversion_pct: float = Field(description="Доля от первого шага, проценты.")


class FunnelResponse(BaseModel):
    """Воронка завершения шагов онбординга.

    🔴 `period_days` в ответе, а не только в запросе: экран обязан подписать, за какое
    окно посчитано. До v8.48.0 воронка молча считалась за всю историю, а подпись
    над ней говорила «за 30 дней».

    Это **воронка завершения**, а не временная последовательность: на каждом шаге —
    люди, прошедшие все предыдущие шаги, независимо от порядка во времени
    (`app/services/analytics.py::funnel`).
    """

    period_days: int
    steps: list[FunnelStep]


@router.get("/overview", summary="Сводка продуктовых метрик за период")
def overview(
    days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
) -> AnalyticsOverview:
    return AnalyticsOverview(**analytics_overview(db, days=days))


@router.get("/funnel", summary="Воронка завершения шагов онбординга")
def funnel_endpoint(
    steps: str | None = Query(None, description="Список event_type через запятую"),
    days: int = Query(30, ge=1, le=365, description="Окно, дней — как у /overview."),
    db: Session = Depends(get_db),
) -> FunnelResponse:
    """🔴 `days` появился в v8.48.0. До этого воронка считалась ЗА ВСЮ ИСТОРИЮ, а сводка
    рядом — за 30 дней, и экран печатал над обеими «за последние 30 дней». Владелец
    сравнил бы «37 активных за месяц» со «100 человек на первом шаге» и решил, что данные
    битые или конверсия рухнула. Сервис `since` поддерживал всегда — его просто
    не передавали (design-critic).
    """
    step_list = [s.strip() for s in steps.split(",") if s.strip()] if steps else _DEFAULT_FUNNEL
    since = utcnow() - timedelta(days=days)
    return FunnelResponse(
        period_days=days,
        steps=[FunnelStep(**s) for s in funnel(db, step_list, since=since)],
    )
