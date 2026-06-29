"""Продуктовая аналитика на событийном логе (P3.4).

Агрегации поверх таблицы events (LOG-01): счётчики событий, число активных пользователей,
completion-воронка. Не пишет данные — только читает существующий лог.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Event, Experiment, ExperimentAssignment
from app.utils.time import utcnow


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
    since = utcnow() - timedelta(days=days)
    counts = event_counts(db, since=since)
    return {
        "period_days": days,
        "total_events": sum(counts.values()),
        "active_users": active_users(db, since=since),
        "event_counts": counts,
    }


def experiment_results(db: Session, key: str) -> dict | None:
    """Результаты A/B-эксперимента (P3.5): по каждому варианту assigned/converted/rate.

    Точность обеспечена фиксацией назначений: знаем поимённо, кто в каком варианте. Конверсия —
    subject (user_id или session_id) с событием `conversion_event`. None — если эксперимента нет.
    """
    experiment = db.query(Experiment).filter(Experiment.key == key).first()
    if experiment is None:
        return None

    subjects_by_variant: dict[str, set[str]] = {}
    rows = (
        db.query(ExperimentAssignment.variant, ExperimentAssignment.subject_id)
        .filter(ExperimentAssignment.experiment_id == experiment.id)
        .all()
    )
    for variant, subject in rows:
        subjects_by_variant.setdefault(variant, set()).add(subject)

    converted_subjects: set[str] = set()
    if experiment.conversion_event:
        for user_id, session_id in (
            db.query(Event.user_id, Event.session_id)
            .filter(Event.event_type == experiment.conversion_event)
            .all()
        ):
            if user_id:
                converted_subjects.add(user_id)
            if session_id:
                converted_subjects.add(session_id)

    variants_out = []
    for variant in experiment.variants:
        name = variant["name"]
        assigned = subjects_by_variant.get(name, set())
        converted = len(assigned & converted_subjects)
        total = len(assigned)
        variants_out.append({
            "variant": name,
            "assigned": total,
            "converted": converted,
            "conversion_rate": round(converted / total, 4) if total else 0.0,
        })

    return {
        "key": experiment.key,
        "status": experiment.status,
        "conversion_event": experiment.conversion_event,
        "variants": variants_out,
    }
