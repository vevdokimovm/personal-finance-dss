"""Инварианты мат-модели v3.0.0 — исполняемая спецификация для свипа.

Каждая проверка возвращает список нарушений вида "I<n>: ...". Пустой список = чисто.
Канон: docs/math_model_v3_0_0.md + app/core (filtering, ranking, alternatives, forecast).
"""
from __future__ import annotations

import math
from typing import Any

from datetime import datetime

from app.core.forecast import monte_carlo_intervals, ses_forecast
from app.core.goals_priority import preallocate_from_bliq
from app.core.ranking import RISK_PROFILES

EPS_MONEY = 0.05
EPS_SHARE = 0.05
DT_MAX = 0.40


def check_static_profiles() -> list[str]:
    """I6: веса профилей — суммы = 1, нестрогая монотонность (плато 2–3 по w_goals)."""
    v: list[str] = []
    for r, p in RISK_PROFILES.items():
        s = p["w_rt"] + p["w_lt"] + p["w_dt"] + p["w_goals"]
        if abs(s - 1.0) > 1e-9:
            v.append(f"I6: профиль {r} — сумма весов {s} != 1")
    order = sorted(RISK_PROFILES)
    for key, increasing in (("w_goals", True), ("w_rt", True), ("w_lt", False), ("w_dt", False)):
        vals = [RISK_PROFILES[r][key] for r in order]
        if increasing:
            ok = all(b >= a for a, b in zip(vals, vals[1:]))
        else:
            ok = all(b <= a for a, b in zip(vals, vals[1:]))
        if not ok:
            v.append(f"I6: {key} не монотонен (нестрого) по профилям: {vals}")
    return v


def _finite_scan(node: Any, path: str, out: list[str]) -> None:
    if isinstance(node, float) and not math.isfinite(node):
        out.append(f"I11: не-конечное число в {path}: {node}")
    elif isinstance(node, dict):
        for k, x in node.items():
            _finite_scan(x, f"{path}.{k}", out)
    elif isinstance(node, list):
        for i, x in enumerate(node[:80]):
            _finite_scan(x, f"{path}[{i}]", out)


def expected_grid_size(portrait: dict[str, Any], today: datetime) -> int:
    """Спецификация |A|: 66 — полная решётка (обе оси активны); вырожденная
    ось схлопывает до 11; обе мертвы — 1 («всё в резерв»); Rt<=0 — 1 (fail-loud).
    Ось целей считается ПОСЛЕ преаллокации подушки (она может закрыть цели)."""
    payments = sum(o["monthly_payment"] for o in portrait["obligations"])
    rt = portrait["income_total"] - portrait["expense_total"] - payments
    if rt <= 1e-9:
        return 1
    _, _, active_goals = preallocate_from_bliq(
        portrait["bliq"], portrait["goals"], today
    )
    goals_total = sum(
        max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        for g in active_goals
    )
    debt_axis = payments > 0
    goal_axis = goals_total > 0
    if debt_axis and goal_axis:
        return 66
    if debt_axis or goal_axis:
        return 11
    return 1


def check_result(
    portrait: dict[str, Any],
    result: dict[str, Any],
    today: datetime = datetime(2026, 7, 2, 12, 0, 0),
) -> list[str]:
    v: list[str] = []
    income = portrait["income_total"]
    expenses = portrait["expense_total"]
    payments = sum(o["monthly_payment"] for o in portrait["obligations"])
    rt_expected = income - expenses - payments

    total = result["alternatives_total"]
    expected_total = expected_grid_size(portrait, today)
    if total != expected_total:
        v.append(f"I1: |A| = {total}, ожидалось {expected_total} (rt={rt_expected:.2f})")

    if result["admissible_count"] + result["rejected_count"] != total:
        v.append("I2: admissible + rejected != |A|")

    ranked = result.get("ranked", [])
    rejected = result.get("rejected", [])
    for alt in ranked:
        if alt["Rt_new"] < -EPS_MONEY:
            v.append(
                f"I3: допустимая альтернатива с Rt_new={alt['Rt_new']} < 0 ({alt.get('name')})"
            )
        if alt["Dt_new"] > DT_MAX + 5e-5:
            v.append(
                f"I3: допустимая альтернатива с Dt_new={alt['Dt_new']} > 0.40 ({alt.get('name')})"
            )
    for alt in ranked + rejected:
        if total > 1:
            share_sum = (alt.get("x_obligations", 0) + alt.get("x_reserve", 0)
                         + alt.get("x_goals", 0))
            if abs(share_sum - max(rt_expected, 0.0)) > EPS_SHARE:
                v.append(
                    f"I4: сумма долей {share_sum:.2f} != R+ "
                    f"{max(rt_expected, 0):.2f} ({alt.get('name')})"
                )

    best = result.get("best")
    if (result["admissible_count"] == 0) != (best is None):
        v.append("I5: best is None не согласован с admissible_count == 0 (fail-loud)")
    if best is not None:
        if not best.get("is_admissible"):
            v.append("I5: best не является допустимой альтернативой")
        if ranked and abs(best["utility"] - ranked[0]["utility"]) > 1e-9:
            v.append("I5: best.utility != max utility ранжирования")
        detail = best.get("avalanche_detail") or {}
        r_bench = detail.get("r_bench", portrait["r_bench"])
        passed = detail.get("passed", [])
        skipped = detail.get("skipped", [])
        for o in passed:
            if o["interest_rate"] < r_bench - 1e-9:
                v.append(
                    f"I7: досрочка по ставке {o['interest_rate']} < r_bench {r_bench}"
                )
        for o in skipped:
            if o["interest_rate"] >= r_bench - 1e-9:
                v.append(
                    f"I7: пропуск долга со ставкой {o['interest_rate']} >= r_bench {r_bench}"
                )
        rates = [o["interest_rate"] for o in passed]
        if rates != sorted(rates, reverse=True):
            v.append("I7: порядок Avalanche нарушен (не по убыванию ставки)")
        if expenses > 0:
            bliq_after = result["indicators"]["Bliq"]
            lt_expected = (bliq_after + best.get("x_reserve", 0)) / expenses
            if abs(best["Lt_new"] - lt_expected) > 0.002:
                v.append(f"I10: Lt_new={best['Lt_new']} != (Bliq+x_res)/Et={lt_expected:.4f}")

    ind = result["indicators"]
    if income > 0 and abs(ind["Dt"] - payments / income) > 1e-3:
        v.append(f"I10: indicators.Dt={ind['Dt']} != SigmaP/It={payments / income:.4f}")
    if expenses > 0:
        lt_ind = ind["Bliq"] / expenses
        if abs(ind["Lt"] - lt_ind) > 0.002:
            v.append(f"I10: indicators.Lt={ind['Lt']} != Bliq/Et={lt_ind:.4f} (stock-based)")

    _finite_scan({"indicators": ind, "best": best}, "result", v)
    return v


def check_forecast_functions() -> list[str]:
    """I9: SES + Monte-Carlo — длины, порядок перцентилей, детерминизм при seed."""
    v: list[str] = []
    hist = [100.0, 120.0, 90.0, 110.0, 105.0, 130.0]
    for horizon in (1, 3, 6):
        pts = ses_forecast(hist, horizon=horizon)
        if len(pts) != horizon:
            v.append(f"I9: ses_forecast горизонт {horizon} вернул {len(pts)} точек")
        ivs = monte_carlo_intervals(pts, horizon=horizon, seed=42)
        if len(ivs) != horizon:
            v.append(f"I9: monte_carlo горизонт {horizon} вернул {len(ivs)} интервалов")
        for h, iv in enumerate(ivs, start=1):
            if not (iv["p10"] <= iv["p50"] <= iv["p90"]):
                v.append(f"I9: нарушен порядок p10<=p50<=p90 на h={h}: {iv}")
        if ivs != monte_carlo_intervals(pts, horizon=horizon, seed=42):
            v.append(f"I9: monte_carlo недетерминирован при фиксированном seed (h={horizon})")
    flat = ses_forecast([50.0] * 8, horizon=3)
    if any(abs(x - 50.0) > 1e-6 for x in flat):
        v.append(f"I9: SES на константной истории дал {flat}, ожидалась константа")
    return v
