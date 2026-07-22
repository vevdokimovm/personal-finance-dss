#!/usr/bin/env python3
"""Dataset v4 statistical audit: population pass + boundary/structure pass.

Produces the numbers behind ``dataset_review_v4.md`` (brief §7) and the
acceptance gates of ``dataset_acceptance_v4.md`` (brief §8).
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats as sps

from engine_v4 import BASE_CONFIG, CUTOFF, RecordParser, Runner

PRODUCT_SPECS = {
    "mortgage": {"rate": (0.06, 0.19), "term": (120, 360), "amount_hi": 30e6},
    "auto": {"rate": (0.10, 0.25), "term": (12, 84), "amount_hi": 5e6},
    "consumer": {"rate": (0.16, 0.35), "term": (12, 84), "amount_hi": 3e6},
    "card": {"rate": (0.20, 0.40), "term": (6, 36), "amount_hi": 0.5e6},
    "installment": {"rate": (0.00, 0.05), "term": (3, 24), "amount_hi": 0.3e6},
    "mfo": {"rate": (0.50, 2.92), "term": (1, 12), "amount_hi": 0.1e6},
}
RATE_TOL = 0.002
TERM_TOL = 1.2

NAME_MAP = [
    ("ипотек", "mortgage"), ("авто", "auto"), ("потреб", "consumer"),
    ("карт", "card"), ("рассроч", "installment"), ("мфо", "mfo"),
    ("микро", "mfo"), ("займ", "mfo"), ("заём", "mfo"),
]


def product_of(name: str) -> str:
    low = name.lower()
    for key, product in NAME_MAP:
        if key in low:
            return product
    return "other"


def describe(arr: np.ndarray) -> dict:
    if arr.size == 0:
        return {"n": 0}
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "p10": float(np.percentile(arr, 10)),
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "p99": float(np.percentile(arr, 99)),
        "max": float(np.max(arr)),
        "skew": float(sps.skew(arr)),
        "kurtosis": float(sps.kurtosis(arr)),
    }


def recovered_term_months(amount: float, rate: float, payment: float):
    if payment <= 0 or amount <= 0:
        return None
    r = rate / 12.0
    if r == 0:
        return amount / payment
    if payment <= amount * r:
        return math.inf
    return -math.log(1.0 - amount * r / payment) / math.log(1.0 + r)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parts", nargs="+", required=True)
    ap.add_argument("--aux-dir", default="aux")
    args = ap.parse_args()
    aux = Path(args.aux_dir)
    aux.mkdir(parents=True, exist_ok=True)

    runner = Runner(BASE_CONFIG, args.parts)
    lines = runner.load_lines()
    parser = RecordParser(BASE_CONFIG)
    records = [parser.parse_line(i, ln) for i, ln in enumerate(lines)]
    valid = [r for r in records if r.valid]
    invalid = [r for r in records if not r.valid]

    out: dict = {"n_lines": len(lines), "n_valid": len(valid),
                 "n_invalid": len(invalid)}

    # ---------- pass 1: population ----------
    income = np.array([r.income for r in valid])
    expense = np.array([r.expense for r in valid])
    pay = np.array([sum(d.payment for d in r.debts) for r in valid])
    bliq = np.array([r.bliq for r in valid])
    targets = np.array([sum(g.target for g in r.goals) for r in valid])
    fcf = income - expense - pay
    n_debts = np.array([len(r.debts) for r in valid])
    n_goals = np.array([len(r.goals) for r in valid])
    debt_amt = np.array([a for r in valid for a in [d.amount for d in r.debts]])
    debt_pay = np.array([p for r in valid for p in [d.payment for d in r.debts]])
    debt_rate = np.array([d.rate for r in valid for d in r.debts])

    pop_mask = income < BASE_CONFIG.whale_income
    out["describe"] = {
        "income_total": describe(income),
        "income_total_no_whales": describe(income[pop_mask]),
        "expense_total": describe(expense),
        "payments_sum": describe(pay),
        "bliq": describe(bliq),
        "goals_target_sum": describe(targets),
        "fcf": describe(fcf),
        "loan_amount": describe(debt_amt),
        "loan_payment": describe(debt_pay),
        "loan_rate": describe(debt_rate),
        "n_debts": describe(n_debts.astype(float)),
        "n_goals": describe(n_goals.astype(float)),
    }

    fields = {"income": income, "expense": expense, "payments": pay,
              "bliq": bliq, "goals_sum": targets}
    keys = list(fields)
    pearson = {}
    spearman = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            pearson[f"{a}~{b}"] = round(float(sps.pearsonr(fields[a], fields[b])[0]), 4)
            spearman[f"{a}~{b}"] = round(float(sps.spearmanr(fields[a], fields[b])[0]), 4)
    out["pearson"] = pearson
    out["spearman"] = spearman

    pos = income[(income > 0) & pop_mask]
    log_inc = np.log(pos)
    mu, sigma = float(np.mean(log_inc)), float(np.std(log_inc))
    ks = sps.kstest((log_inc - mu) / sigma, "norm")
    out["income_lognormality"] = {
        "n": int(pos.size), "log_mu": mu, "log_sigma": sigma,
        "ks_stat": float(ks.statistic), "ks_pvalue": float(ks.pvalue),
        "log_skew": float(sps.skew(log_inc)),
        "log_kurtosis": float(sps.kurtosis(log_inc)),
    }

    out["risk_dist"] = dict(Counter(r.risk for r in valid))
    rb = np.array([r.r_bench for r in valid])
    out["r_bench"] = {"unique": int(np.unique(rb).size),
                      "min": float(rb.min()), "max": float(rb.max()),
                      "mean": float(rb.mean())}
    out["n_debts_dist"] = dict(Counter(int(x) for x in n_debts))
    out["n_goals_dist"] = dict(Counter(int(x) for x in n_goals))

    horizon = Counter()
    readiness = Counter()
    for r in valid:
        for g in r.goals:
            if g.has_deadline:
                days = (g.deadline - CUTOFF).days
                if days < 0:
                    horizon["past"] += 1
                elif days == 0:
                    horizon["today"] += 1
                elif days <= 90:
                    horizon["0_90d"] += 1
                elif days <= 365:
                    horizon["90d_1y"] += 1
                elif days <= 3 * 365:
                    horizon["1y_3y"] += 1
                elif days <= 5 * 365:
                    horizon["3y_5y"] += 1
                elif days <= 10 * 365:
                    horizon["5y_10y"] += 1
                else:
                    horizon["gt_10y"] += 1
            else:
                horizon["perpetual"] += 1
            if g.target > 0:
                ratio = g.current / g.target
                if ratio == 0:
                    readiness["0"] += 1
                elif ratio < 0.25:
                    readiness["0_25"] += 1
                elif ratio < 0.5:
                    readiness["25_50"] += 1
                elif ratio < 0.75:
                    readiness["50_75"] += 1
                elif ratio < 1:
                    readiness["75_100"] += 1
                elif ratio == 1:
                    readiness["exact_100"] += 1
                else:
                    readiness["over_100"] += 1
    out["deadline_horizon"] = dict(horizon)
    out["goal_readiness"] = dict(readiness)

    # ---------- pass 2: boundaries and structure ----------
    census = {
        "zero_income": int(np.sum(income == 0)),
        "zero_expense": int(np.sum(expense == 0)),
        "zero_bliq": int(np.sum(bliq == 0)),
        "fcf_exact_zero_float": int(np.sum(fcf == 0.0)),
        "fcf_abs_lt_1rub": int(np.sum(np.abs(fcf) < 1.0)),
        "deficit": int(np.sum(fcf < 0)),
        "pdn_exact_040": int(np.sum(np.abs(np.divide(pay, income,
                             out=np.full_like(pay, np.nan), where=income > 0)
                             - 0.40) < 1e-9)),
        "pdn_ge_050": int(np.sum((income > 0) & (pay / np.maximum(income, 1e-9) >= 0.5))),
        "pdn_ge_080": int(np.sum((income > 0) & (pay / np.maximum(income, 1e-9) >= 0.8))),
        "income_ge_5m": int(np.sum(income >= 5e6)),
        "any_field_ge_1e9": sum(1 for r in valid
                                if max([r.income, r.expense, r.bliq]
                                       + [d.amount for d in r.debts]
                                       + [g.target for g in r.goals] or [0]) >= 1e9),
        "no_debts_no_goals": sum(1 for r in valid if not r.debts and not r.goals),
        "target_eq_current_exact": sum(1 for r in valid for g in r.goals
                                       if g.target == g.current),
        "overfunded_goals": sum(1 for r in valid for g in r.goals
                                if g.current > g.target),
        "payment_le_interest": sum(1 for r in valid for d in r.debts
                                   if d.amount > 0
                                   and d.payment <= d.amount * d.rate / 12.0),
        "zero_balance_paying": sum(1 for r in valid for d in r.debts
                                   if d.amount == 0 and d.payment > 0),
        "rate_above_psk_292": sum(1 for r in valid for d in r.debts
                                  if d.rate > 2.92),
    }
    out["census"] = census

    # annuity / product consistency
    prod_stats: dict = defaultdict(lambda: {"n": 0, "rate_ok": 0, "term_ok": 0,
                                            "amount_ok": 0, "all_ok": 0,
                                            "interest_only": 0,
                                            "rates": [], "terms": []})
    examples = []
    for r in valid:
        for d in r.debts:
            if d.amount <= 0:
                continue
            product = product_of(d.name)
            st = prod_stats[product]
            st["n"] += 1
            st["rates"].append(d.rate)
            term = recovered_term_months(d.amount, d.rate, d.payment)
            spec = PRODUCT_SPECS.get(product)
            if term is not None and math.isinf(term):
                st["interest_only"] += 1
            if spec is None:
                continue
            rate_ok = spec["rate"][0] - RATE_TOL <= d.rate <= spec["rate"][1] + RATE_TOL
            term_ok = (term is not None and not math.isinf(term)
                       and term <= spec["term"][1] * TERM_TOL)
            amount_ok = d.amount <= spec["amount_hi"] * TERM_TOL
            st["rate_ok"] += rate_ok
            st["term_ok"] += term_ok
            st["amount_ok"] += amount_ok
            ok = rate_ok and term_ok and amount_ok
            st["all_ok"] += ok
            if term is not None and not math.isinf(term):
                st["terms"].append(term)
            if not ok and len(examples) < 12:
                examples.append({"id": r.rid, "name": d.name,
                                 "amount": d.amount, "rate": d.rate,
                                 "payment": d.payment,
                                 "term_est": None if term is None or math.isinf(term)
                                 else round(term, 1),
                                 "rate_ok": bool(rate_ok),
                                 "term_ok": bool(term_ok),
                                 "amount_ok": bool(amount_ok)})
    prod_out = {}
    for product, st in prod_stats.items():
        entry = {k: st[k] for k in ("n", "rate_ok", "term_ok", "amount_ok",
                                    "all_ok", "interest_only")}
        if st["rates"]:
            entry["rate_min"] = float(min(st["rates"]))
            entry["rate_max"] = float(max(st["rates"]))
        if st["terms"]:
            entry["term_p50"] = float(np.percentile(st["terms"], 50))
            entry["term_p99"] = float(np.percentile(st["terms"], 99))
            entry["term_max"] = float(max(st["terms"]))
        prod_out[product] = entry
    out["products"] = prod_out
    out["product_examples_bad"] = examples

    # goal name vs amount
    goal_name_stats = defaultdict(list)
    for r in valid:
        for g in r.goals:
            goal_name_stats[g.name].append(g.target)
    out["goal_names"] = {
        name: {"n": len(v), "p10": float(np.percentile(v, 10)),
               "p50": float(np.percentile(v, 50)),
               "p90": float(np.percentile(v, 90)),
               "max": float(np.max(v))}
        for name, v in sorted(goal_name_stats.items(),
                              key=lambda kv: -len(kv[1]))
    }
    k_vals = []
    for r in valid:
        if r.income > 0 and r.goals:
            k_vals.append(sum(g.target for g in r.goals) / (12 * r.income))
    k_arr = np.array(k_vals)
    out["goal_k"] = describe(k_arr) if k_arr.size else {"n": 0}
    out["goal_k_share_in_02_5"] = (float(np.mean((k_arr >= 0.2) & (k_arr <= 5.0)))
                                   if k_arr.size else None)

    # integrity: duplicates and defects
    id_counts = Counter(r.rid for r in records if r.rid)
    dups = {rid: c for rid, c in id_counts.items() if c > 1}
    dup_detail = []
    for rid in sorted(dups):
        rows = [r for r in records if r.rid == rid]
        dup_detail.append({"id": rid, "n": len(rows),
                           "validity": [r.valid for r in rows]})
    out["duplicates"] = {"n_ids": len(dups),
                         "n_rows": sum(dups.values()),
                         "detail": dup_detail}
    out["defect_counts"] = dict(parser.defect_counts)
    defect_rows = Counter()
    for r in invalid:
        for d in set(x.split(":")[0] for x in r.defects):
            defect_rows[d] += 1
    out["defect_rows_by_kind"] = dict(defect_rows)
    out["invalid_near_miss"] = sum(1 for r in invalid if r.defect_class == "near_miss")
    out["records_with_extra_fields"] = int(parser.assumption_hits.get(
        "A3_extra_fields_tolerated", 0))

    # strata power (families for §8.7)
    fam = Counter()
    for r, f in zip(valid, fcf):
        fam["ok" if f >= 0 else "deficit"] += 1
        if any(d.rate >= 0.45 for d in r.debts if d.amount > 0):
            fam["toxic_family"] += 1
        if r.income == 0:
            fam["zero_income_family"] += 1
        if not r.debts:
            fam["debt_free"] += 1
        if not r.goals:
            fam["no_goals"] += 1
        if r.bliq == 0:
            fam["zero_cushion"] += 1
        if any(g.has_deadline and g.deadline < CUTOFF for g in r.goals):
            fam["overdue_goal_family"] += 1
    fam["invalid"] = len(invalid)
    out["strata"] = dict(fam)
    out["strata_ge_385"] = {k: v >= 385 for k, v in fam.items()}

    with open(aux / "stats.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("n_lines", "n_valid", "n_invalid")},
                     ensure_ascii=False))
    print("written:", aux / "stats.json")


if __name__ == "__main__":
    main()
