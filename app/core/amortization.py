"""
Помесячный график погашения долга: baseline (минимальные платежи) vs
накопительная лавина (ADR-016, канон v3.8.0, §10.5).

В отличие от avalanche.py (форм. 41 — одномоментное распределение x_obl в
текущем месяце), здесь x_obl_monthly применяется КАЖДЫЙ месяц, с каскадом
освободившихся минимальных платежей закрытых долгов на следующий по
приоритету долг из O^target (Bach, 2003) — классическое поведение
debt avalanche.

Диагностика ПОСЛЕ ранжирования/кризисного режима (§9/§12) — чистый read-only
потребитель уже принятого решения, никогда не участвует в допустимости или
argmax (красная линия ADR-016, tests/test_crisis.py).

Срок кредита (term/start_date) НЕ читается — момент погашения является
результатом симуляции, а не входом (обходит массовую незаполненность term/
start_date в реальных данных).

Денежная арифметика внутри `_simulate` — Decimal, не float (v8.19.2). Единственное
место всего денежного контура `app/core` с накопительной арифметикой (до 360 месяцев
подряд) — остальной движок (`alternatives/crisis/surplus/metrics/...`) сознательно
остаётся на float, см. обоснование в `docs/model/model_completion_plan.md` §2.5 и
`docs/research/raw/08_decimal_core_float_map_2026-08-13.md`. Не расширять на весь
модуль без переоценки риска для golden-снапшота (`tests/test_engine_golden.py`).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.core.avalanche import select_avalanche_targets
from app.core.money import money, to_money

# ~30 лет — стандартный максимальный срок ипотечного кредита в РФ. Гарантирует
# терминацию симуляции даже при monthly_payment <= месячные проценты
# (отрицательная/нулевая амортизация) — без капа цикл не завершился бы никогда.
MAX_HORIZON_MONTHS = 360


@dataclass(frozen=True)
class DebtScheduleSummary:
    baseline_months: int
    accelerated_months: int
    baseline_total_interest: float
    accelerated_total_interest: float
    interest_saved: float
    months_saved: int
    horizon_capped: bool
    negative_amortization: bool
    qualifying_debt_count: int


def build_debt_amortization_schedule(
    obligations: list[dict[str, Any]],
    x_obl_monthly: float,
    r_bench: float,
    *,
    horizon_months: int = MAX_HORIZON_MONTHS,
) -> DebtScheduleSummary | None:
    """
    Baseline (только минимальные платежи) vs accelerated (x_obl_monthly +
    каскад освободившихся минимальных платежей закрытых долгов, приоритет —
    O^target из select_avalanche_targets).

    None: obligations пусто, x_obl_monthly <= 0, или ни один долг не проходит
    фильтр r_bench — тот же fail-quiet принцип, что у allocate_obligations_avalanche
    (§10.3): графику ускорения считать нечего.

    Чистая функция — не мутирует входные obligations.
    """
    if not obligations or x_obl_monthly <= 0:
        return None
    targets = select_avalanche_targets(obligations, r_bench)
    if not targets:
        return None
    target_order = [o["id"] for o in targets]

    b_months, b_interest, b_capped, b_neg = _simulate(
        obligations, target_order, extra_monthly=0.0, cascade_freed=False,
        horizon_months=horizon_months,
    )
    a_months, a_interest, a_capped, a_neg = _simulate(
        obligations, target_order, extra_monthly=x_obl_monthly, cascade_freed=True,
        horizon_months=horizon_months,
    )

    return DebtScheduleSummary(
        baseline_months=b_months,
        accelerated_months=a_months,
        baseline_total_interest=money(b_interest),
        accelerated_total_interest=money(a_interest),
        interest_saved=money(b_interest - a_interest),
        months_saved=max(0, b_months - a_months),
        horizon_capped=b_capped or a_capped,
        negative_amortization=b_neg or a_neg,
        qualifying_debt_count=len(targets),
    )


def _simulate(
    obligations: list[dict[str, Any]],
    target_order: list[Any],
    *,
    extra_monthly: float,
    cascade_freed: bool,
    horizon_months: int,
) -> tuple[int, Decimal, bool, bool]:
    """
    Один прогон: месяц за месяцем начисляем проценты на текущий баланс, гасим
    тело минимальным платежом. Освободившийся платёж ЗАКРЫТОГО долга либо
    утекает в свободный поток (baseline, cascade_freed=False), либо каскадом
    идёт в пул текущего месяца (accelerated, cascade_freed=True) — включая
    случай, когда freed пришёл от долга НИЖЕ r_bench: закрытый дешёвый долг
    тоже освобождает деньги на ускорение дорогих, как в любом snowball/
    avalanche-калькуляторе. Пул заливается ТОЛЬКО в target_order (долги
    дешевле r_bench продолжают платиться минимальным платежом, форм. 41 §10.3).

    Денежные величины — Decimal (копейка — минимальный шаг, ROUND_HALF_UP на каждом
    начислении, как в реальной банковской выписке; см. `app/core/money.py`, скилл
    `finpilot-money-format`). Единственное место движка с НАКОПИТЕЛЬНОЙ арифметикой
    (до 360 итераций подряд) — здесь, в отличие от остального `app/core`, ошибка
    округления реально видна пользователю построчно и подрывает сверку с банком.
    Ставка (`rates_m`) остаётся безразмерной величиной, но конвертируется в Decimal
    через `str()`, не через `float(...)/12`, — иначе двоичный шум float всё равно
    просочится в Decimal-домен. `interest`/баланс квантуются до копейки СРАЗУ при
    начислении, не в конце всей симуляции — так `total_interest` — точная сумма уже
    реально начисленных копеечных сумм за каждый месяц, а не одно округление в конце.
    """
    balances = {o["id"]: to_money(o["amount"]) for o in obligations}
    rates_m = {
        o["id"]: Decimal(str(o.get("interest_rate", 0))) / 12 for o in obligations
    }
    payments = {o["id"]: to_money(o.get("monthly_payment", 0)) for o in obligations}
    all_ids = [i for i, bal in balances.items() if bal > 0]

    total_interest = Decimal("0")
    negative_amort = False
    month = 0
    extra = to_money(extra_monthly)

    while any(balances[i] > 0 for i in all_ids) and month < horizon_months:
        month += 1
        freed = Decimal("0")
        for i in all_ids:
            if balances[i] <= 0:
                continue
            interest = to_money(balances[i] * rates_m[i])
            total_interest += interest
            pay = payments[i]
            if pay <= interest:
                negative_amort = True
                principal = Decimal("0")
            else:
                principal = pay - interest
            if principal >= balances[i]:
                freed += pay
                balances[i] = Decimal("0")
            else:
                balances[i] -= principal

        pool = extra + (freed if cascade_freed else Decimal("0"))
        if pool > 0:
            for i in target_order:
                if pool <= 0:
                    break
                if balances.get(i, Decimal("0")) <= 0:
                    continue
                apply = min(pool, balances[i])
                balances[i] -= apply
                pool -= apply

    capped = month >= horizon_months and any(balances[i] > 0 for i in all_ids)
    return month, total_interest, capped, negative_amort
