"""
Инвестиционный транш (модель v3.1.0): терминальный сток резерва (G5-минимум).

Дефект G5 независимой экспертизы: терминальным стоком модели была «вечная
подушка» — на портретах «нет целей + подушка полна» модель клала 91.9% потока
в резерв, а все четыре экспертных движка — 91.3–95.8% в инвестиции по
риск-профилю, называя для каждого рубля конкретную полку.

Минимум для продукта (диапазоны, в которых сходятся все 4 эксперта): поток,
направленный в резерв СВЕРХ целевой подушки Lt*(risk), семантически является
инвестиционным траншем. Доля акций растёт с профилем 0% → 80%; неакционная
часть делится поровну между депозитом/накопительным счётом и облигациями
(ОФЗ). Вклады страхуются АСВ — лимит 1.4 млн ₽ на банк, нота в текстовом слое.

Механику распределения (решётка 66 альтернатив, инварианты сумм) транш не
меняет: это разметка смысла поверх x_reserve, а не четвёртое направление.
"""
from __future__ import annotations

from typing import Any

from app.core.money import money

# Доля акций в инвестиционном миксе по профилю риска (консенсусный коридор
# экспертизы: 0% у консервативного → ~60–80% у агрессивного).
EQUITY_SHARE_BY_PROFILE: dict[int, float] = {
    1: 0.0,
    2: 0.2,
    3: 0.4,
    4: 0.6,
    5: 0.8,
}

DEPOSIT_INSURANCE_NOTE = (
    "Вклады и накопительные счета страхуются АСВ — до 1.4 млн ₽ на один банк; "
    "суммы сверх лимита имеет смысл разложить по разным банкам."
)


def annotate_investment_tranche(
    alt: dict[str, Any],
    bliq: float,
    expense_total: float,
    lt_target: float,
    risk_tolerance: int,
) -> dict[str, Any]:
    """Размечает инвестиционную часть резервного потока альтернативы.

    cushion_part — добор подушки до целевого Lt* (остаётся резервом);
    amount       — транш сверх цели: инвестиции по профильному миксу.
    При Σe = 0 целевая подушка не определена — разметка не выполняется.
    """
    x_res = float(alt.get("x_reserve", 0))
    if x_res <= 0 or expense_total <= 0:
        alt["investment_tranche"] = None
        return alt

    cushion_gap = max(0.0, lt_target * expense_total - bliq)
    invest = money(max(0.0, x_res - cushion_gap))
    if invest <= 0:
        alt["investment_tranche"] = None
        return alt

    equity_share = EQUITY_SHARE_BY_PROFILE.get(
        risk_tolerance, EQUITY_SHARE_BY_PROFILE[3]
    )
    equity = money(invest * equity_share)
    non_equity = invest - equity
    deposits = money(non_equity / 2)
    bonds = money(invest - equity - deposits)  # остаток — чтобы сумма сошлась

    alt["investment_tranche"] = {
        "amount": invest,
        "cushion_part": money(x_res - invest),
        "split": {
            "deposits": deposits,   # депозит / накопительный счёт
            "bonds": bonds,         # ОФЗ / облигации
            "equity": equity,       # акции (индексный портфель)
        },
        "equity_share": equity_share,
        "note": DEPOSIT_INSURANCE_NOTE,
    }
    return alt
