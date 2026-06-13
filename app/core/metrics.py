"""
Базовые показатели финансового состояния — формулы 11–13a ВКР Евдокимова В.М.

Принятая архитектура показателей:
    Rt  = It − Σej − ΣPl,t                   форм. 11   (поток)
    Lt  = Rt / (Σej + ΣPl,t)                 форм. 12   (функц. ликвидность для ранжирования)
    Dt  = ΣPl,t / It                         форм. 13   (долговая нагрузка / ПДН ЦБ РФ)
    BLR = (Bt + Bliq) / Σej                  форм. 13a  (диагност. индикатор для UI; Greninger 1996)
    CFt = It − Σej                           форм. 3    (чистый поток)
    Bt  = Σ current_amount по целям                     (баланс на счетах целей)

Принцип «поток vs состояние»:
    Rt — это поток периода;
    Bt и Bliq — состояние счетов.
    Они описывают разные аспекты картины и используются раздельно.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Union


Item = Union[dict[str, Any], Any]


def get_value(item: Item, field_name: str, default: Any = 0) -> Any:
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
        to_float(get_value(o, "monthly_payment", 0.0)) for o in obligations
    )


def sum_liquid_assets(assets: Iterable[Item]) -> float:
    return sum(to_float(get_value(a, "amount", 0.0)) for a in assets)


def calculate_cft(transactions: Iterable[Item]) -> float:
    """CFt = It − Σej  (форм. 3 ВКР)."""
    return calculate_income_total(transactions) - calculate_expense_total(transactions)


def calculate_bt(goals: Iterable[Item]) -> float:
    """Bt = Σ current_amount по целям пользователя."""
    return sum(to_float(get_value(g, "current_amount", 0.0)) for g in goals)


def calculate_rt(cash_flow: float, obligation_payments: float) -> float:
    """
    Rt = CFt − ΣPl,t  (форм. 11 ВКР).
    Свободный поток периода после покрытия обязательных платежей.
    """
    return cash_flow - obligation_payments


def calculate_lt(rt: float, expense_total: float, obligation_payments: float) -> float:
    """
    Lt = Rt / (Σej + ΣPl,t)  (форм. 12 ВКР).
    Безразмерный функциональный коэффициент ликвидности для ранжирования.
    """
    denom = expense_total + obligation_payments
    return rt / denom if denom > 0 else 0.0


def calculate_dt(obligation_payments: float, income_total: float) -> float:
    """
    Dt = ΣPl,t / It  (форм. 13 ВКР).
    Долговая нагрузка — совпадает с ПДН Банка России (Указ. № 4892-У).
    """
    return obligation_payments / income_total if income_total > 0 else 0.0


def calculate_blr(balance: float, liquid_assets: float, expense_total: float) -> float:
    """
    BLR = (Bt + Bliq) / Σej  (форм. 13a ВКР).
    Basic Liquidity Ratio (Greninger et al., 1996) — диагностический индикатор
    в месяцах расходов, не участвует в ранжировании альтернатив.
    Бенчмарк: <1 критично, 1–2.5 слабо, 2.5–6 норма, >6 избыток.
    """
    return (balance + liquid_assets) / expense_total if expense_total > 0 else 0.0


# ── Категоризация BLR для UI ─────────────────────────────────────────────
def classify_blr(blr: float) -> dict[str, str]:
    if blr < 1.0:
        return {"level": "critical", "label": "критично"}
    if blr < 2.5:
        return {"level": "weak", "label": "слабо"}
    if blr < 6.0:
        return {"level": "normal", "label": "норма"}
    return {"level": "surplus", "label": "избыток"}
