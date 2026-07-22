"""Самоаудит датасета v5 — координаторская проверка ДО раздачи экспертам.

Урок итерации 4: три раунда подряд эксперты находили в датасете то, что
координатор мог найти сам за один прогон статистики. Каждый такой промах стоил
раунда: часть их сил уходила в ревью данных вместо содержательных решений.

Скрипт считает ровно те десять приёмочных проверок, которые перечислены в
`docs/model/expert_certification/testset_methodology.md` §3, плюс агрегаты, по
которым эксперты раунда 4 предъявляли претензии (P1-P10 у каждого).

Печатает JSON. Ничего не чинит — только измеряет: чинить надо генератор.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter, defaultdict

from tools.portrait_testing.generator_v5 import (
    GOAL_NAME_RANGES_V5,
    K_GOAL_MAX,
    K_GOAL_MIN,
    PSK_RATE_CAP,
    PortraitGeneratorV5,
    UNBOUNDED_GOAL_NAMES,
    products_for_rate,
)

SEED = 20260722
N = 12000
STRESS_KINDS = frozenset({"magnitude_stress", "magnitude_whale",
                          "whale_thin_cushion"})


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _spearman(xs: list[float], ys: list[float]) -> float:
    def ranks(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx)
                    * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def _pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs)
                    * sum((b - my) ** 2 for b in ys))
    return num / den if den else 0.0


def audit(seed: int = SEED, n: int = N) -> dict:
    gen = PortraitGeneratorV5(seed=seed, n=n)
    portraits = [gen.generate(i) for i in range(n)]
    rows = [gen.expert_row(i) for i in range(n)]
    meta = gen.meta()

    valid = [p for p in portraits if p["layer"] != "D"]
    population = [p for p in valid
                  if p["layer"] not in ("E",) and p["kind"] not in STRESS_KINDS]

    out: dict = {"seed": seed, "n": n}

    # --- §3.9 слепота экспорта -------------------------------------------
    leak_fields = {"layer", "kind", "family", "pair_id", "pair_role",
                   "pair_relation", "expected_error", "id_override"}
    out["blindness"] = {
        "design_labels_in_expert_rows": sorted(
            f for r in rows[:200] for f in r if f in leak_fields),
        "foreign_id_prefixes": sorted({r["id"].split("-")[0] for r in rows}
                                      - {"SP5"}),
        "duplicate_id_groups": sum(
            1 for c in Counter(r["id"] for r in rows).values() if c > 1),
        "duplicate_group_sizes": sorted(
            {c for c in Counter(r["id"] for r in rows).values() if c > 1}),
    }

    # --- §3.10 точность границ -------------------------------------------
    exact = Counter()
    for p in population:
        income, expense = p.get("income_total"), p.get("expense_total")
        if not (_num(income) and _num(expense)):
            continue
        pays = sum(o["monthly_payment"] for o in (p.get("obligations") or ())
                   if _num(o.get("monthly_payment")))
        if income - expense - pays == 0.0:
            exact["fcf_exact_zero"] += 1
        if income > 0 and pays / income == 0.40:
            exact["pdn_exact_040"] += 1
        for g in p.get("goals") or ():
            if _num(g.get("target_amount")) and \
                    g.get("target_amount") == g.get("current_amount"):
                exact["target_eq_current"] += 1
    out["boundary_exactness"] = dict(exact)

    # --- §3.5 продуктовая согласованность --------------------------------
    prod = {"loans": 0, "rate_outside_any_product": 0,
            "above_psk_cap_outside_d": 0, "amount_outside_spec": 0,
            "name_product_mismatch": 0}
    psk_edge_hist = Counter()
    for p in valid:
        for o in p.get("obligations") or ():
            rate, amount = o.get("interest_rate"), o.get("amount")
            if not (_num(rate) and _num(amount)):
                continue
            prod["loans"] += 1
            fits = products_for_rate(rate)
            if not fits:
                prod["rate_outside_any_product"] += 1
            if rate > PSK_RATE_CAP:
                prod["above_psk_cap_outside_d"] += 1
            if rate >= 2.80:
                psk_edge_hist[round(rate, 3)] += 1
            from tools.portrait_testing.generator_v5 import LOAN_PRODUCTS
            in_spec = any(LOAN_PRODUCTS[k]["amount"][0] <= amount
                          <= LOAN_PRODUCTS[k]["amount"][1] for k in fits)
            if fits and not in_spec:
                prod["amount_outside_spec"] += 1
            names = {LOAN_PRODUCTS[k]["name"] for k in fits}
            if fits and o.get("name") not in names:
                prod["name_product_mismatch"] += 1
    prod["amount_outside_spec_share"] = (
        round(prod["amount_outside_spec"] / prod["loans"], 4)
        if prod["loans"] else 0.0)
    prod["declared_out_of_spec_share"] = meta["loan_amount_out_of_spec_share"]
    out["product_consistency"] = prod
    out["psk_edge_histogram"] = dict(sorted(psk_edge_hist.items()))

    # --- §3.6 имя <-> сумма цели, фактический k --------------------------
    ks: list[float] = []
    name_violations = Counter()
    horizons: list[float] = []
    goal_targets: list[float] = []
    for p in population:
        income = p.get("income_total")
        goals = p.get("goals") or []
        for g in goals:
            t = g.get("target_amount")
            if not _num(t):
                continue
            goal_targets.append(float(t))
            name = g.get("name")
            if name in GOAL_NAME_RANGES_V5 and name not in UNBOUNDED_GOAL_NAMES:
                lo, hi = GOAL_NAME_RANGES_V5[name]
                if t > hi * 1.05:
                    name_violations[name] += 1
            dl = g.get("deadline")
            if hasattr(dl, "year"):
                horizons.append((dl - gen.frozen_today).days / 365.25)
        if _num(income) and income > 0 and goals:
            total = sum(g["target_amount"] for g in goals
                        if _num(g.get("target_amount")))
            if total > 0:
                ks.append(total / (income * 12.0))
    out["goals"] = {
        "k_actual_range": [round(min(ks), 4), round(max(ks), 4)],
        "k_declared_range": [K_GOAL_MIN, K_GOAL_MAX],
        "k_in_spec": min(ks) >= K_GOAL_MIN * 0.9 and max(ks) <= K_GOAL_MAX * 1.1,
        "name_cap_violations": dict(name_violations),
        "horizon_years": {
            "min": round(min(horizons), 2), "max": round(max(horizons), 2),
            "share_over_10y": round(
                sum(1 for h in horizons if h >= 10) / len(horizons), 4),
            "share_over_20y": round(
                sum(1 for h in horizons if h >= 20) / len(horizons), 4),
        },
    }

    # --- §3.8 обрезанные хвосты ------------------------------------------
    top = Counter(goal_targets).most_common(3)
    out["tails"] = {
        "most_repeated_goal_targets": [[v, c] for v, c in top],
        "max_goal_target": round(max(goal_targets), 2),
        "pile_up_detected": any(c > 5 for _, c in top),
    }

    # --- §3.3 доли диагностических состояний -----------------------------
    status = Counter()
    lt_bands = Counter()
    for p in valid:
        income, expense, bliq = (p.get("income_total"), p.get("expense_total"),
                                 p.get("bliq"))
        if not (_num(income) and _num(expense) and _num(bliq)):
            continue
        pays = sum(o["monthly_payment"] for o in (p.get("obligations") or ())
                   if _num(o.get("monthly_payment")))
        fcf = income - expense - pays
        status["deficit" if fcf < 0 else "ok"] += 1
        lt = bliq / expense if expense > 0 else float("inf")
        band = ("<1" if lt < 1 else "1-2" if lt < 2 else "2-3" if lt < 3
                else "3-6" if lt < 6 else ">=6")
        lt_bands[band] += 1
    out["diagnostic_shares"] = {
        "flow": {k: round(v / sum(status.values()), 4)
                 for k, v in status.items()},
        "lt_bands": {k: round(v / sum(lt_bands.values()), 4)
                     for k, v in sorted(lt_bands.items())},
    }

    # --- §3.2 корреляции: Пирсон против Спирмена -------------------------
    inc, exp, pay, goal_sum = [], [], [], []
    for p in population:
        income, expense = p.get("income_total"), p.get("expense_total")
        if not (_num(income) and _num(expense)):
            continue
        inc.append(float(income))
        exp.append(float(expense))
        pay.append(sum(o["monthly_payment"]
                       for o in (p.get("obligations") or ())
                       if _num(o.get("monthly_payment"))))
        goal_sum.append(sum(g["target_amount"] for g in (p.get("goals") or ())
                            if _num(g.get("target_amount"))))
    out["correlations_population_only"] = {
        "income~expense": {"spearman": round(_spearman(inc, exp), 3),
                           "pearson": round(_pearson(inc, exp), 3)},
        "income~payments": {"spearman": round(_spearman(inc, pay), 3),
                            "pearson": round(_pearson(inc, pay), 3)},
        "income~goals_sum": {"spearman": round(_spearman(inc, goal_sum), 3),
                             "pearson": round(_pearson(inc, goal_sum), 3)},
    }
    out["income_distribution_population_only"] = {
        "median": round(statistics.median(inc), 2),
        "mean": round(statistics.fmean(inc), 2),
        "p95": round(sorted(inc)[int(0.95 * len(inc))], 2),
        "max": round(max(inc), 2),
        "mean_to_median": round(statistics.fmean(inc)
                                / statistics.median(inc), 2),
    }

    # --- §3.7 мощность страт ---------------------------------------------
    fam = Counter(p.get("family") for p in portraits if p["layer"] == "C")
    kinds = Counter(p["kind"] for p in portraits)
    out["power"] = {
        "layers": dict(Counter(p["layer"] for p in portraits)),
        "c_families": dict(fam),
        "families_below_385": {k: v for k, v in fam.items() if v < 385},
        "risk_profiles": dict(Counter(p["risk_tolerance"] for p in valid
                                      if isinstance(p.get("risk_tolerance"),
                                                    int))),
        "kinds_below_30": {k: v for k, v in kinds.items() if v < 30},
    }

    # --- §3.3 джиттер: круглые числа выдают дизайн ------------------------
    d_share = out["power"]["layers"].get("D", 0) / n
    out["design_fingerprints"] = {
        "defect_share": round(d_share, 5),
        "defect_share_is_round": abs(d_share * 1000 - round(d_share * 1000))
        < 1e-9,
        "kind_volumes_distinct": len({v for v in kinds.values()}),
        "kind_volumes_total": len(kinds),
    }

    # --- слой D: покрытие полей и составные --------------------------------
    d_rows = [p for p in portraits if p["layer"] == "D"]
    fields = Counter((p.get("expected_error") or ":").split(":")[0]
                     for p in d_rows)
    out["defect_layer"] = {
        "total": len(d_rows),
        "distinct_fields": len(fields),
        "fields": dict(fields),
        "composite_share": round(
            sum(1 for p in d_rows if p["kind"].startswith("composite_"))
            / len(d_rows), 4),
    }

    # --- слой E: пары -----------------------------------------------------
    pairs = defaultdict(dict)
    for p in portraits:
        if p.get("pair_relation"):
            pairs[p["pair_id"]][p["pair_role"]] = p
    out["metamorphic"] = {
        "pairs": len(pairs),
        "complete_pairs": sum(1 for v in pairs.values()
                              if set(v) == {"base", "twin"}),
        "relations": dict(Counter(v["base"]["pair_relation"]
                                  for v in pairs.values()
                                  if "base" in v)),
    }
    return out


def main() -> int:
    print(json.dumps(audit(), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
