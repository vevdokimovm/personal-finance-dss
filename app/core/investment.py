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

# ADR-014 (2026-08-13), вариант B: единственный налоговый механизм в модели
# до этой ноты — множитель НДФЛ внутри r_bench (§10.2 канона), применяется
# только к Avalanche-бенчмарку. Инвестиционный транш налоговый статус счёта
# не знает вовсе (нет входа в user_prefs) — нота информационная, общий совет,
# не персонализированный расчёт. Не меняет механику транша (депозит/
# облигации/акции по риск-профилю остаются как есть) — тот же класс решения,
# что DEPOSIT_INSURANCE_NOTE. Полный налоговый слой (учёт типа ИИС, остатка
# лимита года, пересчёт эффективной доходности) — вариант C ADR-014,
# отдельное решение, не эта нота.
IIS_NOTE = (
    "Взносы на индивидуальный инвестиционный счёт (ИИС) до 400 000 ₽ в год дают право "
    "на налоговый вычет 13% — если счёт ещё не открыт, для этой суммы может быть выгоден."
)

# ADR-017 (2026-08-13): продолжение ADR-014 — реальный расчёт вычета для типа А,
# не просто упоминание льготы. Только тип А: закон однозначен (вычет = 13% от
# взносов, потолок 400 000 ₽/год), правила ИИС-3 имеют переходные положения,
# которые не берёмся кодировать без риска выдать неверную цифру (см. ADR-017,
# вариант D, отклонён). Диагностика ПОСЛЕ ранжирования — не входит в выбор
# альтернативы, красная линия ADR-017 (как у ADR-016).
IIS_ANNUAL_LIMIT = 400_000.0
IIS_DEDUCTION_RATE = 0.13


def estimate_iis_deduction(
    amount: float, iis_type: str, contributed_this_year: float = 0.0
) -> dict[str, float] | None:
    """Вычет ИИС типа А — детерминированный факт закона, не мнение экспертизы.

    None: не тип А, сумма транша <= 0, или лимит года уже исчерпан
    (contributed_this_year >= 400 000). Не выдумывает цифру для типа Б/ИИС-3.
    """
    if iis_type != "A" or amount <= 0:
        return None
    remaining_limit = max(0.0, IIS_ANNUAL_LIMIT - max(0.0, contributed_this_year))
    eligible = min(amount, remaining_limit)
    if eligible <= 0:
        return None
    return {
        "eligible_amount": money(eligible),
        "deduction": money(eligible * IIS_DEDUCTION_RATE),
    }


# Иллюстрация сложного процента (2026-08-13, обсуждение с владельцем по итогам
# опроса ЦА): ставки — НЕ прогноз, НЕ рекомендация инструмента, НЕ привязаны к
# конкретному классу активов из build_shelf_split/EQUITY_SHARE_BY_PROFILE и не
# зависят от риск-профиля — единая иллюстрация «как работает сложный процент»
# для любого пользователя. Порядок величины (5/8/12%) — общий ориентир (ближе к
# консервативному/среднему/оптимистичному сценарию накопления), не измерение и
# не консенсус экспертизы. Обязателен дисклеймер при показе пользователю
# (39-ФЗ, `docs/legal/terms-of-service.md` п.4.2 — не индивидуальная
# инвестиционная рекомендация).
GROWTH_ILLUSTRATION_YEARS = [5, 10, 20]
GROWTH_ILLUSTRATION_RATES = [0.05, 0.08, 0.12]


def project_compound_growth(
    amount: float,
    years: list[int] | None = None,
    rates: list[float] | None = None,
) -> list[dict[str, float]] | None:
    """Сложный процент: amount * (1+rate)^years для каждой пары (rate, years).

    None при amount <= 0 — иллюстрировать нечего. Чистая функция, не входит ни
    в выбор альтернативы, ни в решение модели — та же красная линия, что у
    estimate_iis_deduction (ADR-017): диагностика, не совет.
    """
    if amount <= 0:
        return None
    years = years if years is not None else GROWTH_ILLUSTRATION_YEARS
    rates = rates if rates is not None else GROWTH_ILLUSTRATION_RATES
    return [
        {"rate": rate, "years": y, "future_value": money(amount * (1 + rate) ** y)}
        for rate in rates
        for y in years
    ]


# Полный G5 (v3.2.0): инструмент зависит от горизонта. Короткий горизонт не
# терпит просадок — акции исключаются независимо от риск-профиля.
HORIZON_SHORT_MONTHS = 12.0
HORIZON_MID_MONTHS = 36.0


def instrument_for_horizon(months_left: float | None) -> str:
    """Полка инструмента для накопления под конкретный срок (G5, v3.2.0)."""
    if months_left is not None and months_left < HORIZON_SHORT_MONTHS:
        return "депозит / накопительный счёт (горизонт меньше года — без просадок)"
    if months_left is not None and months_left < HORIZON_MID_MONTHS:
        return "депозит и облигации (ОФЗ) поровну (горизонт 1–3 года)"
    return "профильный микс: депозит / облигации / акции (горизонт от 3 лет)"


def build_shelf_split(amount: float, risk_tolerance: int) -> dict[str, float]:
    """Разбивка суммы по профильной полке: депозит / облигации / акции.

    Сумма компонентов сходится с amount до копейки (остаток — в облигации).
    """
    equity_share = EQUITY_SHARE_BY_PROFILE.get(
        risk_tolerance, EQUITY_SHARE_BY_PROFILE[3]
    )
    equity = money(amount * equity_share)
    non_equity = amount - equity
    deposits = money(non_equity / 2)
    bonds = money(amount - equity - deposits)
    return {"deposits": deposits, "bonds": bonds, "equity": equity}


def annotate_investment_tranche(
    alt: dict[str, Any],
    bliq: float,
    expense_total: float,
    lt_target: float,
    risk_tolerance: int,
    iis_type: str = "none",
    iis_contributed_this_year: float = 0.0,
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
    split = build_shelf_split(invest, risk_tolerance)

    iis_estimate = estimate_iis_deduction(invest, iis_type, iis_contributed_this_year)
    if iis_estimate is not None:
        note = (
            f"{DEPOSIT_INSURANCE_NOTE} При взносе {iis_estimate['eligible_amount']:,.0f} ₽ "
            f"на ИИС типа А вычет составит {iis_estimate['deduction']:,.0f} ₽ (13%)."
        )
    else:
        note = f"{DEPOSIT_INSURANCE_NOTE} {IIS_NOTE}"

    alt["investment_tranche"] = {
        "amount": invest,
        "cushion_part": money(x_res - invest),
        "split": split,
        "equity_share": equity_share,
        "note": note,
        "iis_deduction_estimate": iis_estimate,
        "growth_illustration": project_compound_growth(invest),
    }
    return alt
