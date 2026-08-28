"""
Стенд-замер инфляционной индексации целей дальше ~3 лет (батч 0.1, Волна 0, ADR-013).

Единственная систематическая (не спорная) ошибка карты качества модели
(`docs/model/model_quality_scorecard.md` ось 5/10): цель на 10-30 лет в номинальных
рублях занижена. Меняет $\\Delta_s$ → $S_n(a)$ (§11.3 канона) → потенциально argmax
ранжирования, поэтому — замер по прецеденту ADR-009/ADR-006, не голословное решение.

Метод: на каждом портрете v2 (seed 20260702) прогоняем generate → evaluate → filter →
rank ДВАЖДЫ, переключая `app.core.goals_priority.GOAL_INFLATION_RATE`:
  - nom (базлайн, до батча 0.1): rate = 0.0 — inflated_target_amount тождественна;
  - idx (текущий код, батч 0.1): rate = 0.04 (дефолт модуля).
Отвечает на три вопроса:
  1. Сколько портретов вообще ЗАТРОНУТЫ (есть дедлайновая цель дальше 36 мес)?
  2. Из затронутых — меняет ли индексация победителя ранжирования?
  3. Эффект СКОНЦЕНТРИРОВАН в затронутых портретах, а не размазан по всей выборке
     (иначе это была бы ошибка реализации, а не целевой фикс)?

Запуск: python -m tools.model_validation.goal_inflation_benchmark [N]
"""
from __future__ import annotations

import gzip
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

import app.core.goals_priority as goals_priority
from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.filtering import DT_MAX, filter_alternatives
from app.core.ranking import rank_alternatives

Y = "\033[93m"
G = "\033[92m"
R = "\033[91m"
C = "\033[96m"
X = "\033[0m"

DATASET = Path("knowledge/model_validation/portraits_v2_seed20260702.jsonl.gz")
DEFAULT_N = 2000
REFERENCE_TODAY = datetime(2026, 7, 2)


def _load_portraits(n: int) -> list[dict]:
    out: list[dict] = []
    with gzip.open(DATASET, "rt") as f:
        for line in f:
            out.append(json.loads(line))
            if len(out) >= n:
                break
    return out


def _remaining(g: dict) -> float:
    return max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))


def _has_long_horizon_goal(portrait: dict) -> bool:
    for g in portrait.get("goals", []):
        dl = g.get("deadline")
        if not dl:
            continue
        d = datetime.fromisoformat(dl) if isinstance(dl, str) else dl
        months = (d - REFERENCE_TODAY).days / 30.0
        if months > goals_priority.GOAL_INFLATION_HORIZON_MONTHS:
            return True
    return False


def _effective_split(alt: dict) -> tuple[int, int, int]:
    x_obl = round(float(alt.get("x_obl_effective", alt.get("x_obligations", 0))))
    x_res = round(float(alt.get("x_reserve_effective", alt.get("x_reserve", 0))))
    goals = round(sum(float(v) for v in (alt.get("goal_allocation", {}) or {}).values()))
    return (x_obl, x_res, goals)


def _best_for_portrait(p: dict) -> dict | None:
    payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
    rt = p["income_total"] - p["expense_total"] - payments
    goals_total = sum(_remaining(g) for g in p["goals"])
    if rt <= 1e-9 or goals_total <= 0:
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
    ranked = rank_alternatives(admissible, int(p.get("risk_tolerance", 3)))
    return ranked[0] if ranked else None


def run(n: int) -> None:
    portraits = _load_portraits(n)
    print(f"{Y}→ загружено {len(portraits)} портретов v2 (seed 20260702){X}")

    considered = 0
    affected = 0            # есть цель дальше 36 мес
    winner_changed = 0
    winner_changed_unaffected = 0  # красный флаг, если > 0: эффект не локализован
    advice_changed = 0
    utility_shifts: list[float] = []
    money_shifts: list[float] = []

    original_rate = goals_priority.GOAL_INFLATION_RATE

    for p in portraits:
        payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
        rt = p["income_total"] - p["expense_total"] - payments
        goals_total = sum(_remaining(g) for g in p["goals"])
        if rt <= 1e-9 or goals_total <= 0:
            continue
        considered += 1
        is_affected = _has_long_horizon_goal(p)
        if is_affected:
            affected += 1

        goals_priority.GOAL_INFLATION_RATE = 0.0
        best_nom = _best_for_portrait(p)
        goals_priority.GOAL_INFLATION_RATE = original_rate
        best_idx = _best_for_portrait(p)

        if best_nom is None or best_idx is None:
            continue

        changed = best_nom.get("id") != best_idx.get("id")
        if changed:
            winner_changed += 1
            if not is_affected:
                winner_changed_unaffected += 1
            utility_shifts.append(
                abs(float(best_idx.get("utility", 0)) - float(best_nom.get("utility", 0)))
            )
        if _effective_split(best_nom) != _effective_split(best_idx):
            advice_changed += 1
            split_nom = _effective_split(best_nom)
            split_idx = _effective_split(best_idx)
            money_shifts.append(sum(abs(a - b) for a, b in zip(split_nom, split_idx)))

    goals_priority.GOAL_INFLATION_RATE = original_rate

    def pct(a: int, b: int) -> str:
        return f"{(100.0 * a / b):.2f}%" if b else "n/a"

    def q(vals: list[float], perc: float) -> float:
        if not vals:
            return 0.0
        s = sorted(vals)
        return s[min(int(perc * len(s)), len(s) - 1)]

    horizon = goals_priority.GOAL_INFLATION_HORIZON_MONTHS
    rate_pct = goals_priority.GOAL_INFLATION_RATE * 100
    print(
        f"\n{C}=== РЕЗУЛЬТАТ: инфляционная индексация целей "
        f"(> {horizon:.0f} мес, {rate_pct:.0f}%/год) ==={X}"
    )
    print(f"  портретов с решёткой (Rt>0, есть цели): {considered}")
    print(f"  {Y}затронутых (есть цель дальше {horizon:.0f} мес):{X} "
          f"{affected} ({pct(affected, considered)})")
    print(f"  {G}✓ сменился победитель ранжирования:{X} "
          f"{winner_changed} ({pct(winner_changed, considered)})")
    color = R if winner_changed_unaffected else G
    print(f"  {color}локализация: смена победителя БЕЗ длинной цели:{X} "
          f"{winner_changed_unaffected} (ожидается 0)")
    print(f"  {G}✓ сменился эффективный совет (сплит):{X} "
          f"{advice_changed} ({pct(advice_changed, considered)})")
    if utility_shifts:
        print(f"\n  {Y}Сдвиг utility победителя (только где сменился):{X}")
        print(f"    медиана {statistics.median(utility_shifts):.4f} · "
              f"p95 {q(utility_shifts, 0.95):.4f} · макс {max(utility_shifts):.4f}")
    if money_shifts:
        print(f"\n  {Y}Сдвиг эффективного сплита, ₽ (только где сменился совет):{X}")
        print(f"    медиана {statistics.median(money_shifts):,.0f} · "
              f"p95 {q(money_shifts, 0.95):,.0f} · макс {max(money_shifts):,.0f}")
    print(f"\n{G}✓ замер завершён{X}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    run(n)
