"""Dataset audit for portraits v4: two passes per brief section 7.

Pass 1 -- population statistics on valid records.
Pass 2 -- boundary census, product realism, goal realism, integrity.
Emits a JSON report consumed by dataset_review_v4.md and acceptance gates.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as sps

from engine_v4 import CUTOFF_DATE, Constants, Validator

PRODUCT_SPEC = {
    # name fragment: (rate_lo, rate_hi, term_lo_m, term_hi_m, bal_lo, bal_hi)
    "Ипотека": (0.06, 0.19, 120, 360, 1e6, 30e6),
    "Автокредит": (0.10, 0.25, 12, 84, 0.3e6, 5e6),
    "Потребительский": (0.16, 0.35, 12, 84, 0.03e6, 3e6),
    "Кредитная карта": (0.20, 0.40, 6, 36, 0.01e6, 0.5e6),
    "Рассрочка": (0.00, 0.05, 3, 24, 0.005e6, 0.3e6),
    "МФО": (0.50, 2.92, 1, 12, 0.005e6, 0.1e6),
    "Микрозайм": (0.50, 2.92, 1, 12, 0.005e6, 0.1e6),
}
PSK_CEILING = 2.92


def describe(values: list) -> dict:
    if not values:
        return {"n": 0}
    arr = np.asarray(values, dtype=float)
    return {
        "n": int(arr.size), "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "p10": float(np.percentile(arr, 10)),
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "p99": float(np.percentile(arr, 99)),
        "max": float(arr.max()),
        "skew": float(sps.skew(arr)) if arr.size > 2 else 0.0,
        "kurtosis": float(sps.kurtosis(arr)) if arr.size > 3 else 0.0,
    }


def annuity_term_months(balance: float, rate: float, payment: float):
    """Recover remaining term from (balance, annual rate, payment)."""
    if payment <= 0 or balance <= 0:
        return None
    monthly = rate / 12.0
    if monthly == 0:
        return balance / payment
    interest = balance * monthly
    if payment <= interest:
        return math.inf
    return -math.log(1.0 - balance * monthly / payment) / math.log(1.0 + monthly)


def match_product(name: str):
    for fragment, spec in PRODUCT_SPEC.items():
        if fragment.lower() in name.lower():
            return fragment, spec
    return None, None


def iter_raw_lines(input_dir: Path):
    for path in sorted(input_dir.glob("expert_portraits_v4_part*_jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index == 0 and '"__meta__"' in line:
                    continue
                yield line


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    validator = Validator(Constants())
    report: dict = {"pass1": {}, "pass2": {}, "integrity": {}}

    valid, invalid_reasons, invalid_ids = [], Counter(), []
    id_counter = Counter()
    raw_extra_keys = Counter()
    n_lines = 0
    for line in iter_raw_lines(args.input_dir):
        n_lines += 1
        try:
            raw = json.loads(line, parse_constant=lambda t: float("nan"))
            if isinstance(raw, dict) and isinstance(raw.get("id"), str):
                id_counter[raw["id"]] += 1
            if isinstance(raw, dict):
                for key in raw:
                    if key not in ("id", "income_total", "expense_total",
                                   "obligations", "goals", "bliq", "r_bench",
                                   "risk_tolerance"):
                        raw_extra_keys[key] += 1
        except json.JSONDecodeError:
            pass
        portrait, reason = validator.parse_line(line)
        if portrait is None:
            invalid_reasons[reason] += 1
            try:
                raw_id = json.loads(line).get("id")
            except Exception:
                raw_id = None
            invalid_ids.append(raw_id if isinstance(raw_id, str) else "")
        else:
            valid.append(portrait)

    report["integrity"]["total_lines"] = n_lines
    report["integrity"]["valid"] = len(valid)
    report["integrity"]["invalid"] = int(sum(invalid_reasons.values()))
    report["integrity"]["invalid_reasons"] = dict(
        sorted(invalid_reasons.items(), key=lambda kv: -kv[1]))
    report["integrity"]["extra_top_level_keys"] = dict(raw_extra_keys)

    dup_ids = {k: v for k, v in id_counter.items() if v > 1}
    invalid_id_set = set(i for i in invalid_ids if i)
    dup_detail = {"n_dup_ids": len(dup_ids),
                  "n_rows_in_dups": int(sum(dup_ids.values())),
                  "dup_with_invalid_member": sorted(
                      k for k in dup_ids if k in invalid_id_set),
                  "dup_all_valid": sorted(
                      k for k in dup_ids if k not in invalid_id_set)}
    report["integrity"]["dup_ids"] = dup_detail

    # ------------------------------------------------------- pass 1
    income = [p.income for p in valid]
    expense = [p.expense for p in valid]
    payments = [sum(d.payment for d in p.debts) for p in valid]
    bliq = [p.bliq for p in valid]
    goals_sum = [sum(g.target for g in p.goals) for p in valid]
    debt_total = [sum(d.amount for d in p.debts) for p in valid]
    fcf = [p.income - p.expense - sum(d.payment for d in p.debts)
           for p in valid]
    n_debts = [len(p.debts) for p in valid]
    n_goals = [len(p.goals) for p in valid]

    fields = {"income": income, "expense": expense, "payments": payments,
              "bliq": bliq, "goals_target_sum": goals_sum,
              "debt_total": debt_total, "fcf": fcf,
              "n_debts": n_debts, "n_goals": n_goals}
    report["pass1"]["descriptive"] = {k: describe(v) for k, v in fields.items()}

    mat = np.array([income, expense, payments, bliq, goals_sum])
    names = ["income", "expense", "payments", "bliq", "goals_sum"]
    pearson = np.corrcoef(mat)
    spearman = sps.spearmanr(mat.T).statistic
    report["pass1"]["pearson"] = {
        f"{names[i]}~{names[j]}": round(float(pearson[i, j]), 3)
        for i in range(5) for j in range(i + 1, 5)}
    report["pass1"]["spearman"] = {
        f"{names[i]}~{names[j]}": round(float(spearman[i, j]), 3)
        for i in range(5) for j in range(i + 1, 5)}

    pos_income = np.array([x for x in income if x > 0])
    log_inc = np.log(pos_income)
    ks = sps.kstest(log_inc, "norm", args=(log_inc.mean(), log_inc.std()))
    report["pass1"]["income_lognormality"] = {
        "n_pos": int(pos_income.size),
        "ks_stat": round(float(ks.statistic), 4),
        "p_value": float(ks.pvalue),
        "log_skew": round(float(sps.skew(log_inc)), 3),
    }

    report["pass1"]["risk_counts"] = dict(Counter(p.risk for p in valid))
    r_vals = [p.r_bench for p in valid]
    report["pass1"]["r_bench"] = {
        "unique": len(set(r_vals)), "min": min(r_vals), "max": max(r_vals),
        "describe": describe(r_vals)}
    report["pass1"]["n_debts_hist"] = dict(Counter(n_debts))
    report["pass1"]["n_goals_hist"] = dict(Counter(n_goals))

    horizons = Counter()
    readiness = []
    for p in valid:
        for g in p.goals:
            if g.target > 0:
                readiness.append(min(g.current / g.target, 5.0))
            if g.deadline is None:
                horizons["open_ended"] += 1
                continue
            days = (g.deadline - CUTOFF_DATE).days
            if days < 0:
                horizons["overdue"] += 1
            elif days == 0:
                horizons["today"] += 1
            elif days <= 365:
                horizons["<=1y"] += 1
            elif days <= 3 * 365:
                horizons["1-3y"] += 1
            elif days <= 5 * 365:
                horizons["3-5y"] += 1
            else:
                horizons[">5y"] += 1
    report["pass1"]["deadline_horizons"] = dict(horizons)
    report["pass1"]["goal_readiness"] = describe(readiness)

    # ------------------------------------------------------- pass 2
    edge = Counter()
    pdn_edge_examples = []
    for p in valid:
        pay = sum(d.payment for d in p.debts)
        flow = p.income - p.expense - pay
        if p.income == 0:
            edge["zero_income"] += 1
        if p.expense == 0:
            edge["zero_expense"] += 1
        if p.bliq == 0:
            edge["zero_bliq"] += 1
        if flow == 0:
            edge["exact_zero_flow"] += 1
        if flow < 0:
            edge["deficit"] += 1
        if p.income > 0:
            pdn = pay / p.income
            if abs(pdn - 0.40) < 1e-9:
                edge["pdn_exact_040"] += 1
                if len(pdn_edge_examples) < 5:
                    pdn_edge_examples.append(p.id)
            if 0.395 <= pdn <= 0.405:
                edge["pdn_band_0395_0405"] += 1
            if pdn > 0.8:
                edge["pdn_gt_08"] += 1
        if not p.debts and not p.goals:
            edge["no_debts_no_goals"] += 1
        if p.income >= 5e6:
            edge["income_ge_5m"] += 1
        if p.income >= 1e8 or p.bliq >= 1e8:
            edge["stress_magnitude_1e8"] += 1
        for d in p.debts:
            if d.amount == 0:
                edge["debt_zero_balance"] += 1
            if 0 < d.payment <= d.amount * d.rate / 12.0:
                edge["debt_interest_only"] += 1
            if abs(d.rate - p.r_bench) <= 0.005:
                edge["rate_near_bench_05pp"] += 1
        for g in p.goals:
            if g.target == g.current:
                edge["goal_target_eq_current"] += 1
            if g.current > g.target:
                edge["goal_overfunded"] += 1
            if g.deadline == CUTOFF_DATE:
                edge["deadline_today"] += 1
            if g.deadline == CUTOFF_DATE + dt.timedelta(days=1):
                edge["deadline_tomorrow"] += 1
            if g.deadline is not None and g.deadline < CUTOFF_DATE:
                edge["deadline_overdue"] += 1
    report["pass2"]["edge_census"] = dict(sorted(edge.items()))
    report["pass2"]["pdn_040_examples"] = pdn_edge_examples

    products = defaultdict(lambda: {"n": 0, "rates": [], "terms": [],
                                    "balances": [], "rate_out": 0,
                                    "term_out": 0, "balance_out": 0,
                                    "interest_only": 0})
    unmatched_names = Counter()
    rates_all, over_psk = [], 0
    for p in valid:
        for d in p.debts:
            rates_all.append(d.rate)
            if d.rate > PSK_CEILING:
                over_psk += 1
            fragment, spec = match_product(d.name)
            if fragment is None:
                unmatched_names[d.name] += 1
                continue
            bucket = products[fragment]
            bucket["n"] += 1
            bucket["rates"].append(d.rate)
            bucket["balances"].append(d.amount)
            term = annuity_term_months(d.amount, d.rate, d.payment)
            if term is math.inf:
                bucket["interest_only"] += 1
            elif term is not None:
                bucket["terms"].append(term)
            lo_r, hi_r, lo_t, hi_t, lo_b, hi_b = spec
            if not lo_r <= d.rate <= hi_r:
                bucket["rate_out"] += 1
            if term not in (None, math.inf) and not lo_t <= term <= hi_t * 1.02:
                bucket["term_out"] += 1
            if not lo_b <= d.amount <= hi_b:
                bucket["balance_out"] += 1
    product_report = {}
    for name, bucket in products.items():
        product_report[name] = {
            "n": bucket["n"],
            "rate": describe(bucket["rates"]),
            "term_months": describe(bucket["terms"]),
            "balance": describe(bucket["balances"]),
            "rate_out_of_spec": bucket["rate_out"],
            "term_out_of_spec": bucket["term_out"],
            "balance_out_of_spec": bucket["balance_out"],
            "interest_only": bucket["interest_only"],
        }
    report["pass2"]["products"] = product_report
    report["pass2"]["unmatched_product_names"] = dict(unmatched_names)
    report["pass2"]["rates_over_psk_valid_records"] = over_psk
    report["pass2"]["mfo_share_of_debts"] = round(
        sum(1 for r in rates_all if r >= 0.50) / max(1, len(rates_all)), 4)

    goal_names = defaultdict(list)
    k_values = []
    for p in valid:
        total_target = sum(g.target for g in p.goals)
        if p.income > 0 and total_target > 0:
            k_values.append(total_target / (12.0 * p.income))
        for g in p.goals:
            goal_names[g.name].append(g.target)
    report["pass2"]["goal_k_income"] = describe(k_values)
    report["pass2"]["goal_names"] = {
        name: describe(vals) for name, vals in
        sorted(goal_names.items(), key=lambda kv: -len(kv[1]))}

    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1,
                                   default=str), encoding="utf-8")
    print(f"lines={n_lines} valid={len(valid)} "
          f"invalid={sum(invalid_reasons.values())}")
    print(json.dumps(report["integrity"]["invalid_reasons"],
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
