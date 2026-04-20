from __future__ import annotations

from typing import Any, Union


Item = Union[dict[str, Any], Any]


def _get_value(item: Item, field_name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(field_name, default)
    return getattr(item, field_name, default)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_transaction(item: Item) -> Item:
    transaction_type = str(_get_value(item, "type", "")).lower()
    if transaction_type not in {"income", "expense"}:
        transaction_type = "expense"

    if isinstance(item, dict):
        return {
            **item,
            "amount": _to_float(_get_value(item, "amount", 0.0)),
            "category": _get_value(item, "category", "Без категории"),
            "type": transaction_type,
            "date": _get_value(item, "date"),
        }

    return item


def _normalize_obligation(item: Item) -> Item:
    if isinstance(item, dict):
        return {
            **item,
            "monthly_payment": _to_float(_get_value(item, "monthly_payment", 0.0)),
        }

    return item


def _normalize_goal(item: Item) -> Item:
    if isinstance(item, dict):
        return {
            **item,
            "target_amount": _to_float(_get_value(item, "target_amount", 0.0)),
            "current_amount": _to_float(_get_value(item, "current_amount", 0.0)),
        }

    return item


def is_active_goal(item: Item) -> bool:
    target_amount = _to_float(_get_value(item, "target_amount", 0.0))
    current_amount = _to_float(_get_value(item, "current_amount", 0.0))
    return target_amount > current_amount


def prepare_data(
    transactions: list[Item],
    obligations: list[Item],
    goals: list[Item],
) -> dict[str, list[Item]]:
    prepared_transactions = [_normalize_transaction(item) for item in transactions]
    prepared_obligations = [_normalize_obligation(item) for item in obligations]
    prepared_goals = [_normalize_goal(item) for item in goals]
    active_goals = [goal for goal in prepared_goals if is_active_goal(goal)]

    return {
        "transactions": prepared_transactions,
        "obligations": prepared_obligations,
        "goals": prepared_goals,
        "active_goals": active_goals,
    }
