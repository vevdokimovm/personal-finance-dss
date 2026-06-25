"""Сервисный слой советов по расходам (мат-модель v3.0.0).

Берёт расходные транзакции пользователя за окно последних N месяцев,
конвертирует их в ExpenseRecord и прогоняет через SpendingAdvisor.
Связующее звено между ORM/БД и чистым ядром app.core.spending_advice.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.spending_advice import ExpenseRecord, SpendingAdvisor
from app.database.crud import get_transactions


def _min_period(months: int) -> str:
    """Нижняя граница окна в формате YYYY-MM (включительно), N месяцев назад."""
    now = datetime.now()
    index = now.year * 12 + (now.month - 1) - max(0, months - 1)
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


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
        ))

    current_period = datetime.now().strftime("%Y-%m")
    periods = sorted({r.period for r in records})
    if current_period not in periods:
        current_period = periods[-1] if periods else current_period

    stats = advisor.analyze(records, current_period)
    advice = advisor.generate_advice(records, current_period)
    merchant_insights = advisor.analyze_merchants(records, current_period)
    trends = advisor.analyze_trends(records, current_period)

    return {
        "current_period": current_period,
        "months_window": months,
        "months_with_data": len(periods),
        "advice": [asdict(a) for a in advice],
        "stats": [asdict(s) for s in stats],
        "merchant_insights": [asdict(m) for m in merchant_insights],
        "temporal_patterns": [asdict(t) for t in trends],
        "total_potential_saving": round(sum(a.potential_saving for a in advice), 2),
    }
