"""Продуктовая аналитика на событийном логе (P3.4).

Агрегации поверх таблицы events (LOG-01): счётчики событий, число активных пользователей,
completion-воронка. Не пишет данные — только читает существующий лог.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Event


def event_counts(db: Session, since: datetime | None = None) -> dict[str, int]:
    """Число событий по типам."""
    query = db.query(Event.event_type, func.count(Event.id))
    if since is not None:
        query = query.filter(Event.created_at >= since)
    return {etype: count for etype, count in query.group_by(Event.event_type).all()}


def active_users(db: Session, since: datetime | None = None) -> int:
    """Число уникальных авторизованных пользователей (гости с NULL не считаются)."""
    query = db.query(Event.user_id).filter(Event.user_id.isnot(None))
    if since is not None:
        query = query.filter(Event.created_at >= since)
    return query.distinct().count()


def funnel(db: Session, steps: list[str], since: datetime | None = None) -> list[dict]:
    """Completion-воронка: на каждом шаге — пользователи, прошедшие все шаги до текущего
    включительно (пересечение множеств). Конверсия считается от первого шага.

    Это воронка завершения шагов, а не строгая временная последовательность.
    """
    result: list[dict] = []
    eligible: set | None = None
    base: int | None = None
    for step in steps:
        query = db.query(Event.user_id).filter(
            Event.event_type == step, Event.user_id.isnot(None)
        )
        if since is not None:
            query = query.filter(Event.created_at >= since)
        step_users = {uid for (uid,) in query.distinct().all()}
        passed = step_users if eligible is None else (eligible & step_users)
        count = len(passed)
        if base is None:
            base = count
        conversion = (count / base * 100) if base else 0.0
        result.append({"step": step, "users": count, "conversion_pct": round(conversion, 1)})
        eligible = passed
    return result


def analytics_overview(db: Session, days: int = 30) -> dict:
    """Сводка за период: всего событий, активные пользователи, разбивка по типам."""
    since = datetime.utcnow() - timedelta(days=days)
    counts = event_counts(db, since=since)
    return {
        "period_days": days,
        "total_events": sum(counts.values()),
        "active_users": active_users(db, since=since),
        "event_counts": counts,
    }
