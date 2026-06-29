"""Сервисный слой советов по расходам (мат-модель v3.0.0).

Берёт расходные транзакции пользователя за окно последних N месяцев,
конвертирует их в ExpenseRecord и прогоняет через SpendingAdvisor.
Связующее звено между ORM/БД и чистым ядром app.core.spending_advice.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.goals_priority import _months_left
from app.core.spending_advice import ExpenseRecord, GoalRecord, SpendingAdvisor
from app.database.crud import get_goal_contributions, get_goals, get_transactions
from app.utils.time import utcnow


def _min_period(months: int) -> str:
    """Нижняя граница окна в формате YYYY-MM (включительно), N месяцев назад."""
    now = utcnow()
    index = now.year * 12 + (now.month - 1) - max(0, months - 1)
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


def _goal_records(db: Session, user_id: str | None, months: int,
                  min_period: str, now: datetime) -> list[GoalRecord]:
    """Активные недостигнутые цели → GoalRecord. Темп пополнения — средний за окно
    (сумма взносов в окне / months), дедлайн — канон goals_priority._months_left."""
    records: list[GoalRecord] = []
    for goal in get_goals(db, active_only=True, user_id=user_id):
        if float(goal.current_amount) >= float(goal.target_amount):
            continue
        contributed = sum(
            float(c.amount)
            for c in get_goal_contributions(db, goal.id)
            if c.contribution_date.strftime("%Y-%m") >= min_period
        )
        monthly = contributed / months if months else 0.0
        records.append(GoalRecord(
            name=goal.name,
            target_amount=float(goal.target_amount),
            current_amount=float(goal.current_amount),
            months_to_deadline=_months_left(goal.deadline, now),
            monthly_contribution=monthly,
            priority=goal.priority,
        ))
    return records


def get_spending_advice(
    db: Session,
    user_id: str | None = None,
    months: int = 6,
    advisor: SpendingAdvisor | None = None,
) -> dict:
    advisor = advisor or SpendingAdvisor()
    min_period = _min_period(months)

    records: list[ExpenseRecord] = []
    for txn in get_transactions(db, user_id=user_id):
        if txn.type != "expense":
            continue
        period = txn.date.strftime("%Y-%m")
        if period < min_period:
            continue
        records.append(ExpenseRecord(
            category=txn.category or "Прочее",
            amount=float(txn.amount),
            period=period,
            merchant=txn.description,
            date=txn.date,
        ))

    current_period = utcnow().strftime("%Y-%m")
    periods = sorted({r.period for r in records})
    if current_period not in periods:
        current_period = periods[-1] if periods else current_period

    stats = advisor.analyze(records, current_period)
    advice = advisor.generate_advice(records, current_period)
    merchant_insights = advisor.analyze_merchants(records, current_period)
    trends = advisor.analyze_trends(records, current_period)

    total_saving = round(sum(a.potential_saving for a in advice), 2)
    goals = _goal_records(db, user_id, months, min_period, utcnow())
    goal_impact = advisor.analyze_goal_impact(total_saving, goals)

    return {
        "current_period": current_period,
        "months_window": months,
        "months_with_data": len(periods),
        "advice": [asdict(a) for a in advice],
        "stats": [asdict(s) for s in stats],
        "merchant_insights": [asdict(m) for m in merchant_insights],
        "temporal_patterns": [asdict(t) for t in trends],
        "goal_impact": [asdict(g) for g in goal_impact],
        "total_potential_saving": total_saving,
    }
