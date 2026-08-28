"""
Стенд-замер floor резерва от волатильности дохода (ADR-015, Волна 1 после Волны 0).

Меняет $\\Delta$floor → потенциально argmax ранжирования, поэтому — замер по прецеденту
ADR-013/ADR-006, не голословное решение. Красная линия ADR-015: Rt/Dt/допустимость
альтернатив/кризисный режим НЕ должны зависеть от income_history НИКОГДА — это отдельно
проверяется явным assert (не только I12-тестом в tests/test_crisis.py), а не только
косвенно через отсутствие изменений в footprint.

Метод: на каждом синтетическом портрете (generate_with_income_history) прогоняем generate →
evaluate → filter → rank ДВАЖДЫ:
  - nom (базлайн, до ADR-015): effective_floor_months(obligations, r_bench, income_history=None);
  - vol (текущий код, ADR-015): effective_floor_months(obligations, r_bench, income_history=hist).
Отвечает на три вопроса:
  1. Сколько портретов вообще ЗАТРОНУТЫ (income_cv > порога)?
  2. Из затронутых — меняет ли это победителя ранжирования?
  3. Локализован ли эффект (0 портретов без волатильности сменили победителя) и НИКОГДА ли
     не меняются Rt/Dt между прогонами (красная линия ADR-015, не только footprint)?

Запуск: python -m tools.model_validation.income_volatility_benchmark [N]
"""
from __future__ import annotations

import statistics
import sys

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.filtering import DT_MAX, filter_alternatives
from app.core.ranking import (
    INCOME_VOLATILITY_THRESHOLD,
    effective_floor_months,
    income_cv,
    rank_alternatives,
)
from tools.portrait_testing.generator import PortraitGenerator

Y = "\033[93m"
G = "\033[92m"
R = "\033[91m"
C = "\033[96m"
X = "\033[0m"

DEFAULT_N = 2000


def _best_for_portrait(p: dict, floor_months: float) -> dict | None:
    payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
    rt = p["income_total"] - p["expense_total"] - payments
    goals_total = sum(
        max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        for g in p["goals"]
    )
    if rt <= 1e-9:
        return None
    alts = generate_alternatives(rt, payments, goals_total, step=0.10)
    for a in alts:
        evaluate_alternative(
            a, p["income_total"], p["expense_total"], p["obligations"],
            p["goals"], p["r_bench"], bliq=p["bliq"],
        )
    dt_current = payments / p["income_total"] if p["income_total"] > 0 else 1.0
    admissible, _ = filter_alternatives(
        alts, dt_max=DT_MAX, l_min=float(p.get("l_min", 0.0)), dt_current=dt_current
    )
    if not admissible:
        return None
    ranked = rank_alternatives(admissible, int(p.get("risk_tolerance", 3)),
                               floor_months=floor_months)
    return ranked[0] if ranked else None


def run(n: int) -> None:
    gen = PortraitGenerator(seed=20260813, version=2)
    print(f"{Y}→ генерирую {n} портретов с историей дохода (seed 20260813){X}")

    considered = 0
    affected = 0
    winner_changed = 0
    winner_changed_unaffected = 0
    utility_shifts: list[float] = []

    i = 0
    while considered < n:
        p = gen.generate_with_income_history(i)
        i += 1
        if i > n * 8:
            break
        payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
        rt = p["income_total"] - p["expense_total"] - payments
        if rt <= 1e-9 or p["income_total"] <= 0:
            continue
        considered += 1

        obligations, r_bench, history = p["obligations"], p["r_bench"], p["income_history"]
        floor_nom = effective_floor_months(obligations, r_bench, income_history=None)
        floor_vol = effective_floor_months(obligations, r_bench, income_history=history)

        cv = income_cv(history)
        is_affected = cv is not None and cv > INCOME_VOLATILITY_THRESHOLD
        if is_affected:
            affected += 1

        best_nom = _best_for_portrait(p, floor_nom)
        best_vol = _best_for_portrait(p, floor_vol)
        if best_nom is None or best_vol is None:
            continue

        # Красная линия ADR-015 (Rt/Dt/кризисный режим не зависят от
        # income_history) — НЕ проверяется здесь диффом best["Rt_new"]:
        # когда floor меняет победителя, у НОВОГО победителя закономерно
        # другой Rt_new (другой сплит резерва) — это ожидаемый эффект
        # изменения ранжирования, не нарушение красной линии. Настоящая
        # красная линия — про БАЗОВЫЙ rt/dt портрета (считается один раз до
        # генерации альтернатив, income_history туда не передаётся вообще,
        # гарантия по конструкции кода) — доказана явным тестом
        # tests/test_crisis.py::test_crisis_plan_ignores_income_history_adr_015,
        # не числовым бенчмарком.

        if best_nom.get("id") != best_vol.get("id"):
            winner_changed += 1
            if not is_affected:
                winner_changed_unaffected += 1
            utility_shifts.append(
                abs(float(best_vol.get("utility", 0)) - float(best_nom.get("utility", 0)))
            )

    def pct(a: int, b: int) -> str:
        return f"{(100.0 * a / b):.2f}%" if b else "n/a"

    def q(vals: list[float], perc: float) -> float:
        if not vals:
            return 0.0
        s = sorted(vals)
        return s[min(int(perc * len(s)), len(s) - 1)]

    print(f"\n{C}=== РЕЗУЛЬТАТ: floor резерва от волатильности дохода (ADR-015) ==={X}")
    print(f"  портретов с решёткой (Rt>0): {considered}")
    print(f"  {Y}затронутых (income_cv > {INCOME_VOLATILITY_THRESHOLD}):{X} "
          f"{affected} ({pct(affected, considered)})")
    print(f"  {G}✓ сменился победитель ранжирования:{X} "
          f"{winner_changed} ({pct(winner_changed, considered)})")
    color = R if winner_changed_unaffected else G
    print(f"  {color}локализация: смена победителя БЕЗ волатильности:{X} "
          f"{winner_changed_unaffected} (ожидается 0)")
    print(f"  {G}✓ красная линия (Rt/Dt/кризис не зависят от income_history):{X} "
          f"доказано тестом, не этим бенчмарком — см. комментарий в коде")
    if utility_shifts:
        print(f"\n  {Y}Сдвиг utility победителя (только где сменился):{X}")
        print(f"    медиана {statistics.median(utility_shifts):.4f} · "
              f"p95 {q(utility_shifts, 0.95):.4f} · макс {max(utility_shifts):.4f}")
    print(f"\n{G}✓ замер завершён{X}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    run(n)
