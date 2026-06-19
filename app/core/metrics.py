"""
Базовые показатели финансового состояния FINPILOT.

Принятая архитектура показателей (refined model v3.0):
    CFt = It − Σej                            чистый денежный поток
    Rt  = CFt − ΣPl,t                         свободный РЕСУРС (поток после обязательств)
    Lt  = Lreserve / Σej                      ЛИКВИДНОСТЬ — месяцы автономии (stock-based)
    Dt  = ΣPl,t / It                          долговая нагрузка (ПДН Банка России)
    BLR = (Bt + Bliq) / Σej                   диагностический индикатор ликвидности (Greninger 1996)
    Bt  = Σ current_amount по целям           накопления на счетах целей

Ключевое отличие refined-модели (v3.0): ресурс Rt — это ПОТОК, а ликвидность Lt — это
ЗАПАС (месяцы жизни на подушке). Раньше Lt = Rt/(Σej+ΣP) был линейной функцией
Rt → два из четырёх критериев свёртки несли одну и ту же информацию (r≈0.9998).
Stock-based Lt ортогонален Rt: Rt реагирует на досрочку долга, Lt — на пополнение
резерва. Это восстанавливает реальную работу профилей риска в SAW-свёртке.
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


def calculate_lt(liquid_reserve: float, expense_total: float) -> float:
    """
    Lt = ликвидная подушка / Σej — месяцы автономии (stock-based).

    Сколько месяцев пользователь проживёт на ликвидном резерве без дохода.
    Stock-based по своей природе: зависит от запаса ликвидности, а не от
    свободного потока Rt. Это делает критерий ликвидности ОРТОГОНАЛЬНЫМ ресурсу
    Rt в свёртке полезности (раньше Lt = Rt/(Σej+ΣP) был линейно зависим от Rt,
    что давало вырожденную пару коллинеарных критериев). Норма по Greninger
    et al. (1996): 2.5–6 месяцев.
    """
    return liquid_reserve / expense_total if expense_total > 0 else 0.0


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
