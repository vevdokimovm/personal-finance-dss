"""
Генерация и оценка альтернатив распределения свободного ресурса Rt
(этапы 4–4b алгоритма ВКР).

Каждая альтернатива — вектор (x_obl, x_res, x_goals) при xi ≥ 0 и xi1+xi2+xi3 ≤ Rt.
Дискретизация с шагом 20% по stars-and-bars даёт ровно 21 комбинацию:
    C(1/step + 2, 2) = C(7, 2) = 21.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.avalanche import allocate_obligations_avalanche
from app.core.goals_priority import calculate_goals_si, goals_allocation_breakdown


def _alt_name(d: int, r: int, g: int, steps: int) -> str:
    pct = lambda x: int(round(x / steps * 100))
    pd, pr, pg = pct(d), pct(r), pct(g)
    if d == steps:
        return "Всё на погашение долга"
    if r == steps:
        return "Всё в резерв"
    if g == steps:
        return "Всё на цели"
    dominant_value, dominant_label = max(
        (d, "обязательства"), (r, "резерв"), (g, "цели"),
        key=lambda x: x[0],
    )
    if dominant_value / steps >= 0.6:
        return f"Акцент: {dominant_label} ({pd}/{pr}/{pg})"
    if d == r == g:
        return f"Равное распределение ({pd}/{pr}/{pg})"
    return f"Распределение {pd}/{pr}/{pg}"


def generate_alternatives(
    rt: float,
    obligation_payments: float,
    goals_total: float,
    step: float = 0.20,
) -> list[dict[str, Any]]:
    """
    Этап 4 ВКР: генерация множества A = {a1, …, an} через дискретизацию Rt.

    При rt ≤ 0 возвращает одну «дефицитную» альтернативу — кейс Михаила.
    Это математически корректное отражение этапа 4.0:
    распределять нечего, x_obl + x_res + x_goals = R+_t = max(rt, 0) = 0.
    """
    if rt <= 0:
        return [{
            "id": "deficit",
            "name": "Дефицитный бюджет",
            "description": "Расходы и обязательства превышают доходы. Распределять нечего.",
            "x_obligations": 0,
            "x_reserve": 0,
            "x_goals": 0,
            "x_remain": rt,
        }]

    steps = round(1.0 / step)  # = 5 при step=0.20 → 21 альтернатива
    alternatives = []

    for d in range(steps + 1):
        for r in range(steps + 1 - d):
            g = steps - d - r

            if g > 0 and goals_total <= 0:
                continue
            if d > 0 and obligation_payments <= 0:
                continue

            x_obl = round(rt * d * step, 2)
            x_res = round(rt * r * step, 2)
            x_goa = round(rt * g * step, 2)

            name = _alt_name(d, r, g, steps)
            pct = lambda x: int(round(x / steps * 100))
            pd, pr, pg = pct(d), pct(r), pct(g)
            desc_parts = []
            if x_obl > 0:
                desc_parts.append(f"погашение долга {pd}% ({x_obl:,.0f} ₽)")
            if x_res > 0:
                desc_parts.append(f"резерв {pr}% ({x_res:,.0f} ₽)")
            if x_goa > 0:
                desc_parts.append(f"цели {pg}% ({x_goa:,.0f} ₽)")

            alternatives.append({
                "id": f"a{d}{r}{g}",
                "name": name,
                "description": "; ".join(desc_parts) or "Все средства остаются в наличии.",
                "x_obligations": x_obl,
                "x_reserve": x_res,
                "x_goals": x_goa,
            })

    return alternatives


def evaluate_alternative(
    alt: dict[str, Any],
    income_total: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    r_bench: float,
    today: datetime | None = None,
) -> dict[str, Any]:
    """
    Этап 4b ВКР: пересчёт Rt', Lt', Dt', Si для альтернативы.

    Использует доработки:
      — Avalanche-распределение x_obl с OCR-фильтром (форм. 41)
      — Взвешенную обеспеченность целей Si (форм. 15-16)
    Если ни одно обязательство не проходит фильтр r_bench, нераспределённая
    часть x_obl возвращается в x_goals.
    """
    x_obl = float(alt.get("x_obligations", 0))
    x_goals_total = float(alt.get("x_goals", 0))

    # 1. Avalanche: распределение x_obl между конкретными кредитами
    x_obl_eff, new_obls, x_obl_unused = allocate_obligations_avalanche(
        x_obl, obligations, r_bench
    )
    new_obligation_payments = sum(float(o.get("monthly_payment", 0)) for o in new_obls)

    # Объяснимость Avalanche: кто прошёл фильтр, сколько влито, экономия платежа
    _old_by_id = {o.get("id"): o for o in obligations}
    _passed, _skipped = [], []
    for o in new_obls:
        old = _old_by_id.get(o.get("id"), o)
        rate = float(old.get("interest_rate", 0))
        paid_in = round(float(old.get("amount", 0)) - float(o.get("amount", 0)), 2)
        if rate >= r_bench:
            _passed.append({
                "name": old.get("name", ""),
                "interest_rate": rate,
                "paid_in": paid_in,
                "closed": float(o.get("amount", 0)) <= 0,
                "payment_saved": round(float(old.get("monthly_payment", 0)) - float(o.get("monthly_payment", 0)), 2),
            })
        else:
            _skipped.append({"name": old.get("name", ""), "interest_rate": rate})
    alt["avalanche_detail"] = {
        "r_bench": r_bench,
        "passed": sorted(_passed, key=lambda x: -x["interest_rate"]),
        "skipped": _skipped,
        "x_unused_to_goals": round(x_obl_unused, 2),
        "delta_payment": round(
            sum(float(o.get("monthly_payment", 0)) for o in obligations) - new_obligation_payments, 2
        ),
    }

    # Нераспределённая часть x_obl возвращается на цели (форм. 41, шаг 3)
    x_goals_total += x_obl_unused

    # 2. Взвешенная обеспеченность целей
    si, goal_allocation = calculate_goals_si(x_goals_total, goals, today)

    # 3. Базовые показатели после применения альтернативы (форм. 11-13)
    new_rt = income_total - expense_total - new_obligation_payments
    denom_lt = expense_total + new_obligation_payments
    new_lt = new_rt / denom_lt if denom_lt > 0 else 0
    new_dt = new_obligation_payments / income_total if income_total > 0 else 0

    alt["x_obl_effective"] = round(x_obl_eff, 2)
    alt["x_obl_unused"] = round(x_obl_unused, 2)
    alt["obligation_allocation"] = [
        {
            "id": o.get("id"),
            "name": o.get("name", ""),
            "interest_rate": float(o.get("interest_rate", 0)),
            "new_amount": round(float(o.get("amount", 0)), 2),
            "new_payment": round(float(o.get("monthly_payment", 0)), 2),
        }
        for o in new_obls
    ]
    alt["goal_allocation"] = goal_allocation
    alt["goal_breakdown"] = goals_allocation_breakdown(x_goals_total, goals, today)
    alt["Rt_new"] = round(new_rt, 2)
    alt["Lt_new"] = round(new_lt, 4)
    alt["Dt_new"] = round(new_dt, 4)
    alt["Si"] = round(si, 4)
    return alt
