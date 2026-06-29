"""Email-уведомления (P2.5): дедлайны целей и превышение бюджета.

Чистые функции определения условий + дедупликация через NotificationLog (одно
уведомление на событие в календарный месяц). Оркестратор run_all_notifications
дёргается по расписанию (cron) через POST /notifications/run.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database.crud import create_notification, get_budget_status, get_goals, get_transactions
from app.database.models import Goal, NotificationLog, User
from app.services.email_service import email_service
from app.services.telegram import telegram_service
from app.utils.time import utcnow


def notify_telegram_if_linked(user: User, text: str) -> None:
    """Отправить текст в Telegram, если у пользователя привязан чат. Без токена бота —
    no-op (telegram_service сам тихо пропустит). Ошибки доставки не валят рассылку."""
    if getattr(user, "telegram_chat_id", None):
        telegram_service.send_message(user.telegram_chat_id, text)


def goals_near_deadline(
    db: Session, user_id: str | None, within_days: int = 7
) -> list[tuple[Goal, int]]:
    """Активные недостигнутые цели с дедлайном в пределах within_days дней."""
    now = utcnow()
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


def _previous_month(today: datetime | None = None) -> str:
    """YYYY-MM предыдущего календарного месяца."""
    today = today or utcnow()
    last_prev = today.replace(day=1) - timedelta(days=1)
    return last_prev.strftime("%Y-%m")


def build_monthly_digest(db: Session, user_id: str | None, year_month: str) -> dict:
    """Сводка за месяц: доходы, расходы, чистый поток, топ-категория трат, число целей."""
    income = expense = 0.0
    count = 0
    by_category: dict[str, float] = defaultdict(float)
    for txn in get_transactions(db, user_id=user_id):
        if txn.date.strftime("%Y-%m") != year_month:
            continue
        amount = float(txn.amount)
        count += 1
        if txn.type == "income":
            income += amount
        else:
            expense += amount
            by_category[txn.category or "Прочее"] += amount

    top_category = max(by_category.items(), key=lambda kv: kv[1])[0] if by_category else None
    return {
        "period": year_month,
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(income - expense, 2),
        "transactions": count,
        "top_expense_category": top_category,
        "active_goals": len(get_goals(db, active_only=True, user_id=user_id)),
    }


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
            sent_at=utcnow(),
        )
    )
    db.commit()


def run_user_notifications(db: Session, user: User) -> dict[str, int]:
    """Проверяет условия для пользователя, шлёт недостающие уведомления, дедупит.

    Возвращает счётчики реально отправленного (без дублей).
    """
    month = utcnow().strftime("%Y-%m")
    sent = {"goal_deadline": 0, "budget_overrun": 0, "digest": 0}

    for goal, days_left in goals_near_deadline(db, user.id):
        key = f"goal_deadline:{goal.id}:{month}"
        if was_notified(db, user.id, key):
            continue
        email_service.send_goal_deadline_reminder(
            user.email, goal.name, days_left,
            float(goal.current_amount), float(goal.target_amount), user.display_name,
        )
        record_notification(db, user.id, "goal_deadline", key)
        create_notification(
            db, user_id=user.id, type="goal_deadline",
            title="Дедлайн цели приближается",
            body=f"До дедлайна цели «{goal.name}» осталось дней: {days_left}",
            link="/goals",
        )
        notify_telegram_if_linked(
            user, f"Дедлайн цели «{goal.name}» через {days_left} дн."
        )
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
        create_notification(
            db, user_id=user.id, type="budget_overrun",
            title="Превышен бюджет",
            body=f"Расходы по категории «{budget['category']}» превысили лимит",
            link="/budgets",
        )
        notify_telegram_if_linked(
            user, f"Превышен бюджет по категории «{budget['category']}»"
        )
        sent["budget_overrun"] += 1

    # Месячный дайджест за прошлый завершённый месяц (если были операции).
    prev = _previous_month()
    digest_key = f"digest:{prev}"
    if not was_notified(db, user.id, digest_key):
        digest = build_monthly_digest(db, user.id, prev)
        if digest["transactions"] > 0:
            email_service.send_digest(user.email, digest, user.display_name)
            record_notification(db, user.id, "digest", digest_key)
            create_notification(
                db, user_id=user.id, type="digest",
                title="Месячный отчёт готов",
                body=(
                    f"Сводка за {prev}: доход {digest['income']:.0f}, "
                    f"расход {digest['expense']:.0f}, чистыми {digest['net']:.0f}"
                ),
                link="/planning",
            )
            notify_telegram_if_linked(
                user, f"Месячный отчёт за {prev} готов — загляните в FINPILOT."
            )
            sent["digest"] += 1

    return sent


def run_all_notifications(db: Session) -> dict[str, int]:
    """Оркестратор для cron: проходит по всем пользователям с email."""
    totals = {"goal_deadline": 0, "budget_overrun": 0, "digest": 0, "users": 0}
    for user in db.query(User).filter(User.email.isnot(None)).all():
        res = run_user_notifications(db, user)
        totals["goal_deadline"] += res["goal_deadline"]
        totals["budget_overrun"] += res["budget_overrun"]
        totals["digest"] += res["digest"]
        totals["users"] += 1
    return totals
