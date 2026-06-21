"""Email-уведомления (P2.5): дедлайны целей и превышение бюджета.

Чистые функции определения условий + дедупликация через NotificationLog (одно
уведомление на событие в календарный месяц). Оркестратор run_all_notifications
дёргается по расписанию (cron) через POST /notifications/run.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.database.crud import get_budget_status, get_goals
from app.database.models import Goal, NotificationLog, User
from app.services.email_service import email_service


def goals_near_deadline(
    db: Session, user_id: str | None, within_days: int = 7
) -> list[tuple[Goal, int]]:
    """Активные недостигнутые цели с дедлайном в пределах within_days дней."""
    now = datetime.utcnow()
    result: list[tuple[Goal, int]] = []
    for goal in get_goals(db, active_only=True, user_id=user_id):
        if goal.deadline is None:
            continue
        days_left = (goal.deadline - now).days
        if 0 <= days_left <= within_days:
            result.append((goal, days_left))
    return result


def budgets_over(db: Session, user_id: str | None) -> list[dict]:
    """Бюджеты, по которым расходы превысили лимит."""
    return [b for b in get_budget_status(db, user_id=user_id) if b.get("over")]


def was_notified(db: Session, user_id: str, dedup_key: str) -> bool:
    """Уже слали это уведомление (по dedup_key)?"""
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id, NotificationLog.dedup_key == dedup_key)
        .first()
        is not None
    )


def record_notification(db: Session, user_id: str, notification_type: str, dedup_key: str) -> None:
    db.add(
        NotificationLog(
            user_id=user_id,
            notification_type=notification_type,
            dedup_key=dedup_key,
            sent_at=datetime.utcnow(),
        )
    )
    db.commit()


def run_user_notifications(db: Session, user: User) -> dict[str, int]:
    """Проверяет условия для пользователя, шлёт недостающие уведомления, дедупит.

    Возвращает счётчики реально отправленного (без дублей).
    """
    month = datetime.utcnow().strftime("%Y-%m")
    sent = {"goal_deadline": 0, "budget_overrun": 0}

    for goal, days_left in goals_near_deadline(db, user.id):
        key = f"goal_deadline:{goal.id}:{month}"
        if was_notified(db, user.id, key):
            continue
        email_service.send_goal_deadline_reminder(
            user.email, goal.name, days_left,
            float(goal.current_amount), float(goal.target_amount), user.display_name,
        )
        record_notification(db, user.id, "goal_deadline", key)
        sent["goal_deadline"] += 1

    for budget in budgets_over(db, user.id):
        key = f"budget_overrun:{budget['category']}:{month}"
        if was_notified(db, user.id, key):
            continue
        email_service.send_budget_overrun_alert(
            user.email, budget["category"],
            float(budget["spent"]), float(budget["limit_amount"]), user.display_name,
        )
        record_notification(db, user.id, "budget_overrun", key)
        sent["budget_overrun"] += 1

    return sent


def run_all_notifications(db: Session) -> dict[str, int]:
    """Оркестратор для cron: проходит по всем пользователям с email."""
    totals = {"goal_deadline": 0, "budget_overrun": 0, "users": 0}
    for user in db.query(User).filter(User.email.isnot(None)).all():
        res = run_user_notifications(db, user)
        totals["goal_deadline"] += res["goal_deadline"]
        totals["budget_overrun"] += res["budget_overrun"]
        totals["users"] += 1
    return totals
