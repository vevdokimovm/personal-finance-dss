"""
Стенд-замер ре-роутинга остатка целевого бакета в резерв (G7-остаток, ADR-009).

Задача помечена в ROADMAP §6.1 как «исследование, меняет семантику решётки, делать
с замером на стенде». Отвечает на три вопроса владельца:

  1. СКОЛЬКО денег ре-роутинг спасает от «испарения»? До ADR-009 остаток целевого
     бакета (x_goals сверх потребности целей) не шёл ни в цели, ни в резерв — терялся
     из плана. Считаем, сколько ₽ рекомендованный план теперь доводит до подушки.
  2. МЕНЯЕТ ли ре-роутинг рекомендацию? Lt' входит и в floor_level (G6), и в SAW-
     полезность (крит. ликвидности) — переток может сменить победителя ранжирования.
  3. СКОЛЬКО автономии реально добавляется? Lt' победителя с перетоком минус без.

Метод: на каждом портрете v2 (seed 20260702) прогоняем цикл generate → evaluate →
filter → rank ДВАЖДЫ:
  - eff  (ADR-009, текущий код): Lt' = (Bliq + x_reserve_effective) / Σe;
  - nom  (базлайн, до ADR-009):  Lt' = (Bliq + x_reserve_nominal)  / Σe.
Допустимость (Rt≥0, ПДН, L_min) от Lt не зависит (L_min по умолчанию 0) → множество
допустимых одно, различается только ранжирование.

Запуск: python -m tools.model_validation.goal_remainder_reroute_benchmark [N]
"""
from __future__ import annotations

import copy
import gzip
import json
import statistics
import sys
from pathlib import Path

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


def _effective_split(alt: dict) -> tuple[int, int, int]:
    x_obl = round(float(alt.get("x_obl_effective", alt.get("x_obligations", 0))))
    x_res = round(float(alt.get("x_reserve_effective", alt.get("x_reserve", 0))))
    goals = round(sum(float(v) for v in (alt.get("goal_allocation", {}) or {}).values()))
    return (x_obl, x_res, goals)


def _best_under_lt(alts: list[dict], mode: str, portrait: dict) -> dict | None:
    """Отранжировать копию альтернатив под Lt режима (eff|nom) и вернуть победителя."""
    expenses = portrait["expense_total"]
    bliq = portrait["bliq"]
    pool = copy.deepcopy(alts)
    for a in pool:
        if mode == "nom":
            x_res_nom = float(a.get("x_reserve", 0))
            a["Lt_new"] = round((bliq + x_res_nom) / expenses, 4) if expenses > 0 else 0.0
        # eff — оставляем Lt_new как есть (уже с перетоком)
    payments = sum(float(o.get("monthly_payment", 0)) for o in portrait["obligations"])
    dt_current = payments / portrait["income_total"] if portrait["income_total"] > 0 else 1.0
    admissible, _ = filter_alternatives(
        pool, dt_max=DT_MAX, l_min=float(portrait.get("l_min", 0.0)), dt_current=dt_current
    )
    if not admissible:
        return None
    ranked = rank_alternatives(admissible, int(portrait.get("risk_tolerance", 3)))
    return ranked[0] if ranked else None


def run(n: int) -> None:
    portraits = _load_portraits(n)
    print(f"{Y}→ загружено {len(portraits)} портретов v2 (seed 20260702){X}")

    considered = 0            # портреты с реальной решёткой (Rt>0, есть цели)
    winner_changed = 0        # сменился id рекомендованной альтернативы
    advice_changed = 0        # сменился эффективный сплит рекомендации
    rerouted_any = 0          # у победителя eff есть переток остатка целей → резерв
    reroute_amounts: list[float] = []   # ₽ перетока у победителя eff (только >0)
    lt_lifts: list[float] = []          # Lt'(eff) − Lt'(nom) у победителя eff

    for p in portraits:
        payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
        rt = p["income_total"] - p["expense_total"] - payments
        if rt <= 1e-9:
            continue
        goals_total = sum(_remaining(g) for g in p["goals"])
        if goals_total <= 0:
            continue  # нет целевого бакета — нечему перетекать

        considered += 1
        alts = generate_alternatives(rt, payments, goals_total, step=0.10)
        for a in alts:
            evaluate_alternative(
                a, p["income_total"], p["expense_total"], p["obligations"],
                p["goals"], p["r_bench"], bliq=p["bliq"],
            )

        best_eff = _best_under_lt(alts, "eff", p)
        best_nom = _best_under_lt(alts, "nom", p)
        if best_eff is None or best_nom is None:
            continue

        if best_eff.get("id") != best_nom.get("id"):
            winner_changed += 1
        if _effective_split(best_eff) != _effective_split(best_nom):
            advice_changed += 1

        reroute = float(best_eff.get("x_goals_unused", 0))
        if reroute > 0.5:
            rerouted_any += 1
            reroute_amounts.append(reroute)

        expenses = p["expense_total"]
        lt_eff = float(best_eff.get("Lt_new", 0))
        x_res_nom = float(best_eff.get("x_reserve", 0))
        lt_nom = (p["bliq"] + x_res_nom) / expenses if expenses > 0 else 0.0
        if lt_eff - lt_nom > 1e-6:
            lt_lifts.append(lt_eff - lt_nom)

    def pct(a: int, b: int) -> str:
        return f"{(100.0 * a / b):.2f}%" if b else "n/a"

    def q(vals: list[float], p: float) -> float:
        if not vals:
            return 0.0
        s = sorted(vals)
        return s[min(int(p * len(s)), len(s) - 1)]

    print(f"\n{C}=== РЕЗУЛЬТАТ: ре-роутинг остатка целевого бакета в резерв ==={X}")
    print(f"  портретов с решёткой (Rt>0, есть цели): {considered}")
    print(f"  {G}✓ рекомендация сменила победителя:{X} "
          f"{winner_changed} ({pct(winner_changed, considered)})")
    print(f"  {G}✓ сменился эффективный совет (сплит):{X} "
          f"{advice_changed} ({pct(advice_changed, considered)})")
    print(f"  {G}✓ у победителя есть переток целей → резерв:{X} "
          f"{rerouted_any} ({pct(rerouted_any, considered)})")
    if reroute_amounts:
        print(f"\n  {Y}Спасено от испарения (₽, только портреты с перетоком):{X}")
        print(f"    медиана {statistics.median(reroute_amounts):,.0f} · "
              f"p95 {q(reroute_amounts, 0.95):,.0f} · макс {max(reroute_amounts):,.0f}")
        print(f"    сумма по выборке: {sum(reroute_amounts):,.0f} ₽")
    if lt_lifts:
        print(f"\n  {Y}Прирост автономии Lt' у победителя (мес, где переток был):{X}")
        print(f"    медиана {statistics.median(lt_lifts):.2f} · "
              f"p95 {q(lt_lifts, 0.95):.2f} · макс {max(lt_lifts):.2f}")
    print(f"\n{G}✓ замер завершён{X}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    run(n)
