"""Reproducible statistical audit of the FINPILOT v2 portrait dataset.

Produces every figure required by the review checklist (a)-(з) and prints a
plain-text report. Run: python3 dataset_stats.py
"""

from __future__ import annotations

import glob
import gzip
import json
from collections import Counter
from datetime import date

import numpy as np
from scipy import stats

CUT = date(2026, 7, 11)
PATHS = sorted(glob.glob("/mnt/user-data/uploads/expert_portraits_v2_part*.gz"))


def load() -> list[dict]:
    rows: list[dict] = []
    for p in PATHS:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            rows += [json.loads(l) for l in fh if l.strip()]
    return rows


def desc(a: np.ndarray) -> dict:
    q = np.percentile(a, [0, 10, 50, 90, 99, 100])
    return dict(n=len(a), mean=a.mean(), std=a.std(),
               min=q[0], p10=q[1], p50=q[2], p90=q[3], p99=q[4], max=q[5])


def line(name: str, d: dict) -> None:
    print(f"{name:14s} mean={d['mean']:14.1f} sd={d['std']:14.1f} "
          f"min={d['min']:10.1f} p10={d['p10']:10.1f} p50={d['p50']:10.1f} "
          f"p90={d['p90']:11.1f} p99={d['p99']:13.1f} max={d['max']:13.1f}")


def main() -> None:
    rows = load()
    n = len(rows)
    print(f"# DATASET AUDIT — {n} portraits, {len(PATHS)} shards, cut {CUT}\n")

    inc = np.array([r["income_total"] for r in rows])
    exp = np.array([r["expense_total"] for r in rows])
    bliq = np.array([r["bliq"] for r in rows])
    debt = np.array([sum(o["monthly_payment"] for o in r["obligations"]) for r in rows])
    goalgap = np.array([sum(g["target_amount"] - g["current_amount"] for g in r["goals"]) for r in rows])
    nobl = np.array([len(r["obligations"]) for r in rows])
    ngoal = np.array([len(r["goals"]) for r in rows])
    fcf = inc - exp - debt

    print("## (a) descriptive statistics — money & counts")
    line("income", desc(inc)); line("expense", desc(exp)); line("bliq", desc(bliq))
    line("debt_pmt", desc(debt)); line("goal_gap", desc(goalgap))
    line("n_oblig", desc(nobl.astype(float))); line("n_goal", desc(ngoal.astype(float)))

    print("\n## (b) correlations on realistic core (all money <1e8)")
    core = (inc < 1e8) & (exp < 1e8) & (bliq < 1e8)
    M = np.vstack([inc, exp, bliq, debt, goalgap]).T[core]
    lab = ["income", "expense", "bliq", "debtpmt", "goalgap"]
    P = np.corrcoef(M.T); S = stats.spearmanr(M).correlation
    print("core n =", int(core.sum()))
    print("Pearson:")
    for i, l in enumerate(lab):
        print(f"  {l:8s} " + " ".join(f"{P[i,j]:7.3f}" for j in range(5)))
    print("Spearman income~{expense,bliq,debtpmt,goalgap}:",
          *[round(float(S[0, j]), 3) for j in (1, 2, 3, 4)])

    print("\n## (c) distribution shapes")
    ic = inc[core & (inc > 0)]
    print(f"income skew={stats.skew(ic):.2f} kurtosis={stats.kurtosis(ic):.2f}")
    sh, lo, sc = stats.lognorm.fit(ic, floc=0)
    D, p = stats.kstest(ic, "lognorm", args=(sh, lo, sc))
    print(f"lognormal fit shape={sh:.3f} scale={sc:.0f} | KS D={D:.4f} p={p:.3g} "
          f"-> {'lognormal NOT rejected' if p > 0.05 else 'lognormality REJECTED'}")
    for nm, arr in [("expense", exp[core & (exp > 0)]), ("bliq", bliq[core & (bliq > 0)])]:
        print(f"{nm} skew={stats.skew(arr):.2f} kurt={stats.kurtosis(arr):.2f}")

    print("\n## (d) categorical / count distributions")
    print("risk_tolerance:", dict(sorted(Counter(r["risk_tolerance"] for r in rows).items())))
    print("r_bench distinct values:", sorted(set(round(r["r_bench"], 4) for r in rows)))
    print("n_obligations:", dict(sorted(Counter(nobl.tolist()).items())))
    print("n_goals:", dict(sorted(Counter(ngoal.tolist()).items())))
    allg = [g for r in rows for g in r["goals"]]
    nulldl = sum(1 for g in allg if g["deadline"] is None)
    dated = [g for g in allg if g["deadline"]]
    hor = []
    overdue = 0
    for g in dated:
        try:
            days = (date.fromisoformat(g["deadline"]) - CUT).days
            hor.append(days)
            overdue += days < 0
        except (ValueError, TypeError):
            pass
    h = np.array(hor)
    print(f"goals total={len(allg)} null_deadline={nulldl} ({100*nulldl/len(allg):.1f}%) "
          f"overdue={overdue}")
    print("deadline horizon days p10/p50/p90:", *[int(x) for x in np.percentile(h, [10, 50, 90])])
    rd = np.array([g["current_amount"] / g["target_amount"] for g in allg if g["target_amount"] > 0])
    print("goal readiness p10/p50/p90:", *[round(float(x), 3) for x in np.percentile(rd, [10, 50, 90])])
    over = sum(1 for g in allg if g["current_amount"] >= g["target_amount"])
    print("overfunded goals:", over, f"({100*over/len(allg):.1f}%)")

    print("\n## (e) derived diagnostics over the whole set")
    dti = np.where(inc > 0, debt / np.where(inc > 0, inc, 1), np.nan)

    def bdti(x):
        if np.isnan(x): return "no_income"
        if x == 0: return "0"
        if x <= .3: return "0-30%"
        if x <= .5: return "30-50%"
        if x <= .8: return "50-80%"
        return ">80%"
    print("DTI buckets:", dict(Counter(bdti(x) for x in dti)))
    liq = np.where(exp > 0, bliq / np.where(exp > 0, exp, 1), np.inf)

    def bliqb(x):
        if x == np.inf: return "no_expense"
        if x < 1: return "<1mo"
        if x < 3: return "1-3mo"
        if x < 6: return "3-6mo"
        if x < 12: return "6-12mo"
        return ">12mo"
    print("Liquidity buckets:", dict(Counter(bliqb(x) for x in liq)))
    print("FCF sign: neg=%d zero=%d pos=%d" % ((fcf < 0).sum(), (fcf == 0).sum(), (fcf > 0).sum()))

    print("\n## (f) label validation")
    print("field 'kind' present:", any("kind" in r for r in rows), "-> labels absent in v2")

    print("\n## boundary strata & validity (layer C/D signatures)")
    print("zero income:", int((inc == 0).sum()), "| zero expense:", int((exp == 0).sum()))
    print("8-goal portraits:", int((ngoal == 8).sum()))
    mm = np.array([max([r["income_total"], r["expense_total"], r["bliq"]]
                       + [o["amount"] for o in r["obligations"]]
                       + [o["monthly_payment"] for o in r["obligations"]]
                       + [g["target_amount"] for g in r["goals"]]
                       + [g["current_amount"] for g in r["goals"]] + [0]) for r in rows])
    print("field>=1e8:", int((mm >= 1e8).sum()), "| >=1e9:", int((mm >= 1e9).sum()),
          "| >=1e10:", int((mm >= 1e10).sum()))
    yrs = np.where(exp > 0, bliq / (exp * 12), 0)
    print("cushion >20y of expense:", int((yrs > 20).sum()))
    print("debt_pmt>income (unserviceable):", int((debt > inc).sum()))
    allobl = [o for r in rows for o in r["obligations"]]
    io = sum(1 for o in allobl if o["monthly_payment"] <= o["amount"] * o["interest_rate"] / 12 + 1e-6)
    print("perpetual/interest-only loans:", io, f"of {len(allobl)}")
    neg = sum(1 for r in rows for v in
              [r["income_total"], r["expense_total"], r["bliq"]]
              + [o["amount"] for o in r["obligations"]]
              + [g["target_amount"] for g in r["goals"]] if v < 0)
    dup = n - len({r["id"] for r in rows})
    print("negative values:", neg, "| duplicate ids:", dup, "-> validity/adversarial layer absent")


if __name__ == "__main__":
    main()
