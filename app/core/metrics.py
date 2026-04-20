from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Union


NumberLike = Union[int, float]
Item = Union[dict[str, Any], Any]


def get_value(item: Item, field_name: str, default: NumberLike = 0) -> Any:
    if isinstance(item, dict):
        return item.get(field_name, default)
    return getattr(item, field_name, default)


def to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def sum_transaction_amounts(transactions: Iterable[Item], transaction_type: str) -> float:
    total = 0.0
    for transaction in transactions:
        if str(get_value(transaction, "type", "")).lower() == transaction_type:
            total += to_float(get_value(transaction, "amount", 0.0))
    return total


def calculate_income_total(transactions: Iterable[Item]) -> float:
    return sum_transaction_amounts(transactions, "income")


def calculate_expense_total(transactions: Iterable[Item]) -> float:
    return sum_transaction_amounts(transactions, "expense")


def sum_obligation_payments(obligations: Iterable[Item]) -> float:
    return sum(
        to_float(get_value(obligation, "monthly_payment", 0.0))
        for obligation in obligations
    )


def calculate_cft(transactions: Iterable[Item]) -> float:
    income_total = calculate_income_total(transactions)
    expense_total = calculate_expense_total(transactions)
    return income_total - expense_total


def calculate_rt(cash_flow: float, obligation_payments: float) -> float:
    return cash_flow - obligation_payments


def calculate_lt(available_resource: float, total_expense_load: float) -> float:
    return available_resource / total_expense_load if total_expense_load > 0 else 0.0


def calculate_dt(obligation_payments: float, total_income: float) -> float:
    return obligation_payments / total_income if total_income > 0 else 0.0
