"""Counterfactual-анализ floor 2.0: последствия неприменённой подгонки.

Прогоняет эталон дважды (floor 1.0 — канон; floor 2.0 — отвергнутый максимум
грид-эксперимента, ADR-006) и собирает эмпирику последствий:

  * матрица переходов доминант base -> floor2 по портретам;
  * где floor 2.0 чинит расхождения с консенсусом, а где создаёт новые;
  * срезы затронутых портретов (риск-профиль, зона Lt);
  * split-half устойчивость прироста (чёт/нечет) + биномиальная оценка шума
    отбора максимума из 5 вариантов;
  * конкретные портреты-примеры «совет был -> стал бы» для разбора глазами.

Выход — JSON в stdout; интерпретация — docs/model/floor_counterfactual_analysis.md.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import app.core.ranking as rk
from tools.model_validation.expert_agreement import (
    expert_consensus,
    load_joined,
    model_outcome,
)
from tools.portrait_testing.generator import PortraitGenerator

JOINED = Path("knowledge/model_validation/joined.csv.gz")


def run_pass(rows, floor: float) -> dict[str, dict]:
    rk.RESERVE_FLOOR_MONTHS = floor
    gen = PortraitGenerator(20260702, version=1)
    out = {}
    for r in rows:
        idx = int(r["id"].split("-")[1])
        p = gen.generate(idx)
        o = model_outcome(p)
        if o["status"] != "ok":
            continue
        out[r["id"]] = {
            "dom": o["dom"], "lt": o["lt"], "risk": p["risk_tolerance"],
            "cons": expert_consensus(r),
            "xr": o["xr"], "xg": o["xg"], "invest": o["invest"], "xo": o["xo"],
        }
    return out


def agreement(pass_data: dict, ids=None) -> tuple[int, int]:
    agree = n = 0
    for pid, o in pass_data.items():
        if ids is not None and pid not in ids:
            continue
        if o["cons"] is None:
            continue
        n += 1
        agree += o["dom"] == o["cons"]
    return agree, n


def main() -> None:
    rows = load_joined(JOINED)
    base_floor = rk.RESERVE_FLOOR_MONTHS
    try:
        base = run_pass(rows, 1.0)
        alt = run_pass(rows, 2.0)
    finally:
        rk.RESERVE_FLOOR_MONTHS = base_floor

    # ── Переходы доминант ────────────────────────────────────────────────
    transitions = Counter()
    changed = []
    for pid, b in base.items():
        a = alt.get(pid)
        if a is None or a["dom"] == b["dom"]:
            continue
        transitions[f"{b['dom']} -> {a['dom']}"] += 1
        changed.append((pid, b, a))

    # ── Починенные / сломанные относительно консенсуса ──────────────────
    fixed = [c for c in changed
             if c[1]["cons"] and c[1]["dom"] != c[1]["cons"] and c[2]["dom"] == c[2]["cons"]]
    broken = [c for c in changed
              if c[1]["cons"] and c[1]["dom"] == c[1]["cons"] and c[2]["dom"] != c[2]["cons"]]

    def slices(items):
        by_risk = Counter(b["risk"] for _, b, _ in items)
        by_lt = Counter(
            "<1" if b["lt"] < 1 else ("1-2" if b["lt"] < 2 else ("2-3" if b["lt"] < 3 else ">=3"))
            for _, b, _ in items
        )
        return {"risk": dict(sorted(by_risk.items())), "lt_zone": dict(by_lt)}

    # ── Split-half устойчивость и шум отбора ─────────────────────────────
    even = {pid for pid in base if int(pid.split("-")[1]) % 2 == 0}
    odd = {pid for pid in base if int(pid.split("-")[1]) % 2 == 1}
    a_e, n_e = agreement(base, even)
    c_e, _ = agreement(alt, even)
    a_o, n_o = agreement(base, odd)
    c_o, _ = agreement(alt, odd)
    ag_b, n_all = agreement(base)
    ag_c, _ = agreement(alt)
    p = ag_b / n_all
    sigma_pp = math.sqrt(p * (1 - p) / n_all) * 100          # σ метрики, п.п.
    bias_max5 = 1.163 * sigma_pp                              # E[max Z из 5] ~ 1.163σ

    # ── Примеры для разбора глазами ──────────────────────────────────────
    def example(items, k=3):
        out = []
        for pid, b, a in items[:k]:
            out.append({
                "id": pid, "risk": b["risk"], "lt": round(b["lt"], 2),
                "consensus": b["cons"],
                "base": {"dom": b["dom"], "xr": round(b["xr"]), "xg": round(b["xg"]),
                         "invest": round(b["invest"]), "xo": round(b["xo"])},
                "floor2": {"dom": a["dom"], "xr": round(a["xr"]), "xg": round(a["xg"]),
                           "invest": round(a["invest"]), "xo": round(a["xo"])},
            })
        return out

    print(json.dumps({
        "agreement_base": round(ag_b / n_all * 100, 1),
        "agreement_floor2": round(ag_c / n_all * 100, 1),
        "changed_portraits": len(changed),
        "transitions": dict(transitions.most_common()),
        "fixed_vs_consensus": {"n": len(fixed), **slices(fixed)},
        "broken_vs_consensus": {"n": len(broken), **slices(broken)},
        "neutral_changes": len(changed) - len(fixed) - len(broken),
        "split_half": {
            "even": {"base": round(a_e / n_e * 100, 1), "floor2": round(c_e / n_e * 100, 1)},
            "odd": {"base": round(a_o / n_o * 100, 1), "floor2": round(c_o / n_o * 100, 1)},
        },
        "selection_noise_pp": {
            "sigma_metric": round(sigma_pp, 2),
            "expected_bias_max_of_5": round(bias_max5, 2),
        },
        "examples_fixed": example(fixed),
        "examples_broken": example(broken),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
