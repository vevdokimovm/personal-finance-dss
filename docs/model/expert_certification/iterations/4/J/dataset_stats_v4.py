"""Statistical audit of the v4 portrait dataset (brief §7, two passes).

Pass 1 — population: descriptive stats, Pearson/Spearman correlations,
distribution shape (skew, kurtosis, KS-lognormal on income), categorical and
count distributions.

Pass 2 — boundaries & structure: boundary-state census, annuity/product
consistency, rate distribution and PSK ceiling, goal realism, integrity
(NaN, duplicate ids split into broken vs valid pairs, extra/missing fields).

Prints a labelled report to stdout. Reuses the frozen ``Validator`` from
``engine_v4`` so the valid/invalid split is identical to the scoring run.
"""

from __future__ import annotations

import datetime as _dt
import gzip
import json
import math
from collections import Counter
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats

from engine_v4 import Constants, Validator

FROZEN = _dt.date(2026, 7, 18)
PATHS = [f"../expert_portraits_v4_part{p}.jsonl.gz" for p in range(1, 5)]

PRODUCT_SPEC = {
    "Ипотека": {"rate": (0.06, 0.19), "term": (120, 360), "amt": (1e6, 3e7)},
    "Автокредит": {"rate": (0.10, 0.25), "term": (12, 84), "amt": (3e5, 5e6)},
    "Потребительский кредит": {"rate": (0.16, 0.35), "term": (12, 84), "amt": (3e4, 3e6)},
    "Кредитная карта": {"rate": (0.20, 0.40), "term": (6, 36), "amt": (1e4, 5e5)},
    "Рассрочка": {"rate": (0.0, 0.05), "term": (3, 24), "amt": (5e3, 3e5)},
    "Заём МФО": {"rate": (0.50, 2.92), "term": (1, 12), "amt": (5e3, 1e5)},
}
PSK_CEIL = 2.92


def load_raw() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in PATHS:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                rec = json.loads(line)
                if isinstance(rec, dict) and rec.get("__meta__"):
                    continue
                rows.append(rec)
    return rows


def describe(name: str, values: List[float]) -> str:
    a = np.array(values, dtype=float)
    q = np.percentile(a, [10, 50, 90, 99])
    return (f"{name:14s} n={len(a):5d} mean={a.mean():14,.0f} sd={a.std():14,.0f} "
            f"min={a.min():12,.0f} p10={q[0]:12,.0f} p50={q[1]:12,.0f} "
            f"p90={q[2]:14,.0f} p99={q[3]:15,.0f} max={a.max():16,.0f}")


def annuity_term(amount: float, rate: float, payment: float) -> Optional[float]:
    i = rate / 12.0
    if payment <= 0:
        return None
    if i <= 0:
        return amount / payment
    if payment <= i * amount:
        return None  # interest-only or growing: no finite amortisation
    return -math.log(1 - i * amount / payment) / math.log(1 + i)


def main() -> None:
    rows = load_raw()
    validator = Validator(Constants())
    valid = [r for r in rows if validator.is_valid(r)]
    invalid = [r for r in rows if not validator.is_valid(r)]
    print("=" * 78)
    print(f"DATASET v4 — rows={len(rows)} valid={len(valid)} "
          f"invalid={len(invalid)} ({len(invalid)/len(rows)*100:.2f}%)")
    print("=" * 78)

    def pay(r): return sum(o["monthly_payment"] for o in r["obligations"])

    income = [r["income_total"] for r in valid]
    expense = [r["expense_total"] for r in valid]
    payments = [pay(r) for r in valid]
    bliq = [r["bliq"] for r in valid]
    goalsum = [sum(g["target_amount"] for g in r["goals"]) for r in valid]
    fcf = [income[i] - expense[i] - payments[i] for i in range(len(valid))]
    pdn = [payments[i] / income[i] if income[i] > 0 else np.nan
           for i in range(len(valid))]

    print("\n--- PASS 1: POPULATION (valid records) ---")
    print(describe("income", income))
    print(describe("expense", expense))
    print(describe("Σ payments", payments))
    print(describe("bliq", bliq))
    print(describe("Σ goal target", [g for g in goalsum if g > 0]))
    print(describe("fcf", fcf))

    # stress vs whale split
    STRESS = 1e8
    stress = [r for r in valid if r["income_total"] >= STRESS
              or r["bliq"] >= STRESS
              or any(o["amount"] >= STRESS for o in r["obligations"])
              or any(g["target_amount"] >= STRESS for g in r["goals"])]
    whale = [r for r in valid if r not in stress and (r["income_total"] >= 5e6)]
    print(f"\nstress-magnitude records (≥1e8 any field): {len(stress)}")
    print(f"realistic whales (income≥5e6, not stress): {len(whale)}")

    # correlations
    print("\n--- Correlations (income/expense/payments/bliq/goalsum) ---")
    mat = np.array([income, expense, payments, bliq, goalsum])
    labels = ["inc", "exp", "pay", "bliq", "goal"]
    finite = np.all(np.isfinite(mat), axis=0)
    m = mat[:, finite]
    print("Pearson:")
    for i in range(5):
        for j in range(i + 1, 5):
            r_p = stats.pearsonr(m[i], m[j])[0]
            r_s = stats.spearmanr(m[i], m[j])[0]
            print(f"  {labels[i]}-{labels[j]:4s} Pearson={r_p:+.3f} Spearman={r_s:+.3f}")

    # shapes
    print("\n--- Distribution shape ---")
    for nm, arr in [("income", income), ("expense", expense), ("bliq", bliq)]:
        a = np.array(arr, float)
        a = a[a > 0]
        print(f"{nm:8s} skew={stats.skew(a):+.2f} kurtosis={stats.kurtosis(a):+.2f}")
    inc_pos = np.array([x for x in income if x > 0], float)
    logs = np.log(inc_pos)
    ks = stats.kstest((logs - logs.mean()) / logs.std(), "norm")
    print(f"income log-normality KS D={ks.statistic:.4f} p={ks.pvalue:.3g} "
          f"(n>0={len(inc_pos)})")

    # categorical / counts
    print("\n--- Categorical & count distributions ---")
    print("risk_tolerance:", dict(sorted(Counter(r["risk_tolerance"] for r in valid).items())))
    rb = sorted(round(r["r_bench"], 6) for r in valid)
    print(f"r_bench: unique={len(set(rb))} min={rb[0]:.4f} max={rb[-1]:.4f}")
    print("n_debts:", dict(sorted(Counter(len(r["obligations"]) for r in valid).items())))
    print("n_goals:", dict(sorted(Counter(len(r["goals"]) for r in valid).items())))

    print("\n--- PASS 2: BOUNDARIES & STRUCTURE ---")
    zin = sum(1 for r in valid if r["income_total"] == 0)
    zex = sum(1 for r in valid if r["expense_total"] == 0)
    zbl = sum(1 for r in valid if r["bliq"] == 0)
    zfcf = sum(1 for x in fcf if x == 0)
    pv = [p for p in pdn if not np.isnan(p)]
    pdn40 = sum(1 for p in pv if abs(p - 0.40) < 1e-9)
    print(f"zero income={zin} zero expense={zex} zero bliq={zbl} "
          f"exactly-zero fcf={zfcf} PDN==0.40 exact={pdn40}")
    print(f"deficit(fcf<0)={sum(1 for x in fcf if x<0)} "
          f"({sum(1 for x in fcf if x<0)/len(valid)*100:.1f}%)")

    # goal boundaries
    past = today = fut = perp = 0
    horizons: List[int] = []
    over = eq = 0
    for r in valid:
        for g in r["goals"]:
            if g["current_amount"] > g["target_amount"]:
                over += 1
            if abs(g["current_amount"] - g["target_amount"]) < 1e-9:
                eq += 1
            dl = g["deadline"]
            if dl is None:
                perp += 1
            else:
                d = _dt.date.fromisoformat(dl)
                if d < FROZEN:
                    past += 1
                elif d == FROZEN:
                    today += 1
                else:
                    fut += 1
                    horizons.append((d - FROZEN).days)
    print(f"goal deadlines: past={past} today={today} future={fut} perpetual={perp}")
    if horizons:
        h = np.array(horizons)
        print(f"  future horizon days: p50={np.percentile(h,50):.0f} "
              f"p90={np.percentile(h,90):.0f} max={h.max()} "
              f">5yr={sum(1 for x in horizons if x>1826)}")
    print(f"overfunded goals(cur>tgt)={over} exact target==current={eq}")

    # annuity / product consistency
    print("\n--- Annuity & product consistency (valid loans) ---")
    per_prod: Dict[str, List[float]] = {}
    per_rate: Dict[str, List[float]] = {}
    in_spec = Counter()
    tot = Counter()
    io = 0
    above_psk = 0
    total_loans = 0
    for r in valid:
        for o in r["obligations"]:
            total_loans += 1
            nm = o["name"]
            per_rate.setdefault(nm, []).append(o["interest_rate"])
            if o["interest_rate"] > PSK_CEIL:
                above_psk += 1
            term = annuity_term(o["amount"], o["interest_rate"], o["monthly_payment"])
            if term is None:
                io += 1
                continue
            per_prod.setdefault(nm, []).append(term)
            spec = PRODUCT_SPEC.get(nm)
            if spec:
                tot[nm] += 1
                lo, hi = spec["term"]
                if lo * 0.9 <= term <= hi * 1.1:
                    in_spec[nm] += 1
    print(f"total valid loans={total_loans} interest-only/non-amortising={io} "
          f"rate>PSK(2.92)={above_psk}")
    for nm in PRODUCT_SPEC:
        rates = per_rate.get(nm, [])
        terms = per_prod.get(nm, [])
        if not rates:
            continue
        ra = np.array(rates)
        frac = (in_spec[nm] / tot[nm] * 100) if tot[nm] else float("nan")
        tt = np.array(terms) if terms else np.array([np.nan])
        print(f"  {nm:24s} n={len(rates):4d} rate[{ra.min():.3f},{ra.max():.3f}] "
              f"term[{np.nanmin(tt):.0f},{np.nanmax(tt):.0f}]mo in-spec={frac:.1f}%")

    # goal name vs sum realism
    print("\n--- Goal name vs magnitude ---")
    gname_sum: Dict[str, List[float]] = {}
    for r in valid:
        for g in r["goals"]:
            gname_sum.setdefault(g["name"], []).append(g["target_amount"])
    for nm, arr in sorted(gname_sum.items(), key=lambda kv: -len(kv[1])):
        a = np.array(arr)
        print(f"  {nm:26s} n={len(a):5d} median={np.median(a):12,.0f} "
              f"p10={np.percentile(a,10):11,.0f} p90={np.percentile(a,90):13,.0f}")

    # integrity: duplicate ids broken vs valid
    print("\n--- Integrity ---")
    ids = [r.get("id") for r in rows]
    dup_ids = {k: v for k, v in Counter(ids).items() if isinstance(k, str) and v > 1}
    valid_set = {id(r) for r in valid}
    broken_pair = valid_pair = mixed_pair = 0
    for k in dup_ids:
        recs = [r for r in rows if r.get("id") == k]
        flags = [id(r) in valid_set for r in recs]
        if all(flags):
            valid_pair += 1
        elif not any(flags):
            broken_pair += 1
        else:
            mixed_pair += 1
    print(f"duplicate id values={len(dup_ids)} (all ×2) — "
          f"both-valid={valid_pair} both-invalid={broken_pair} mixed={mixed_pair}")
    # field hygiene on valid
    extra = Counter()
    for r in valid:
        for k in r:
            if k not in Validator.TOP_KEYS:
                extra[k] += 1
    print("unexpected top-level keys on valid records:", dict(extra) or "none")
    nan_money = 0
    for r in valid:
        for k in Validator.MONEY_KEYS:
            if isinstance(r[k], float) and (math.isnan(r[k]) or math.isinf(r[k])):
                nan_money += 1
    print("NaN/Inf in money fields on valid records:", nan_money)

    # power: strata ≥385
    print("\n--- Power (strata sizes vs 385 floor) ---")
    for k, v in sorted(Counter(r["risk_tolerance"] for r in valid).items()):
        print(f"  risk={k}: {v} {'OK' if v >= 385 else 'THIN'}")
    fam = {
        "deficit": sum(1 for x in fcf if x < 0),
        "high_pdn(>0.40)": sum(1 for p in pv if p > 0.40),
        "severe_pdn(>0.80)": sum(1 for p in pv if p > 0.80),
        "zero_income": zin,
        "perpetual_goals_rows": sum(
            1 for r in valid if any(g["deadline"] is None for g in r["goals"])),
        "invalid": len(invalid),
    }
    for k, v in fam.items():
        print(f"  {k}: {v} {'OK' if v >= 385 else 'THIN(<385)'}")


if __name__ == "__main__":
    main()
