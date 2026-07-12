"""Подготовка входных данных алгоритма СППР (этап 1 pipeline ВКР)."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Union

Item = Union[dict[str, Any], Any]


def _get(item: Item, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_transaction(item: Item) -> Item:
    if not isinstance(item, dict):
        return item
    transaction_type = str(item.get("type", "")).lower()
    if transaction_type not in {"income", "expense"}:
        transaction_type = "expense"
    return {
        **item,
        "amount": _to_float(item.get("amount", 0.0)),
        "category": item.get("category", "Без категории"),
        "type": transaction_type,
        "date": item.get("date"),
    }


def _normalize_obligation(item: Item) -> Item:
    if not isinstance(item, dict):
        return item
    return {
        **item,
        "amount": _to_float(item.get("amount", 0.0)),
        "interest_rate": _to_float(item.get("interest_rate", 0.0)),
        "term": int(item.get("term", 0) or 0),
        "monthly_payment": _to_float(item.get("monthly_payment", 0.0)),
    }


def _normalize_goal(item: Item) -> Item:
    if not isinstance(item, dict):
        return item
    return {
        **item,
        "target_amount": _to_float(item.get("target_amount", 0.0)),
        "current_amount": _to_float(item.get("current_amount", 0.0)),
        "category": item.get("category", "material"),
    }


def _normalize_liquid_asset(item: Item) -> Item:
    if not isinstance(item, dict):
        return item
    return {
        **item,
        "amount": _to_float(item.get("amount", 0.0)),
        "interest_rate": _to_float(item.get("interest_rate", 0.0)),
    }


def is_active_goal(item: Item) -> bool:
    target = _to_float(_get(item, "target_amount", 0.0))
    current = _to_float(_get(item, "current_amount", 0.0))
    return target > current


def _tx_within_period(t: Item, cutoff, now) -> bool:
    """Транзакция в пределах окна [cutoff, now]. Записи без валидной даты НЕ
    отбрасываются (обратная совместимость с тестами, где дата не задаётся)."""
    d = t.get("date") if isinstance(t, dict) else getattr(t, "date", None)
    if d is None:
        return True
    try:
        if getattr(d, "tzinfo", None) is not None and getattr(cutoff, "tzinfo", None) is None:
            cutoff = cutoff.replace(tzinfo=d.tzinfo)
        elif getattr(d, "tzinfo", None) is None and getattr(cutoff, "tzinfo", None) is not None:
            d = d.replace(tzinfo=cutoff.tzinfo)
        return d >= cutoff
    except Exception:
        return True


def prepare_data(
    transactions: list[Item],
    obligations: list[Item],
    goals: list[Item],
    liquid_assets: list[Item] | None = None,
    period_days: int | None = 30,
    now=None,
) -> dict[str, list[Item]]:
    """Нормализация данных для расчёта.

    period_days фильтрует транзакции до последних N дней — «месячные» показатели
    (доход/расход) считаются за текущий месяц, а не за всю историю (иначе доход
    накопленный за годы схлопывался бы в один месяц). None — без фильтра.
    Историю для прогноза строить отдельно из ПОЛНОГО списка (build_monthly_history).
    """
    if period_days is not None:
        from app.utils.time import utcnow
        now = now or utcnow()
        cutoff = now - timedelta(days=period_days)
        transactions = [t for t in transactions if _tx_within_period(t, cutoff, now)]

    prepared_transactions = [_normalize_transaction(t) for t in transactions]
    prepared_obligations = [_normalize_obligation(o) for o in obligations]
    prepared_goals = [_normalize_goal(g) for g in goals]
    active_goals = [g for g in prepared_goals if is_active_goal(g)]
    prepared_liquid = [_normalize_liquid_asset(a) for a in (liquid_assets or [])]

    return {
        "transactions": prepared_transactions,
        "obligations": prepared_obligations,
        "goals": prepared_goals,
        "active_goals": active_goals,
        "liquid_assets": prepared_liquid,
    }
