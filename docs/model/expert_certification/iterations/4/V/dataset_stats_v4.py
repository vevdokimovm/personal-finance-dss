"""Dataset audit, round 4: population pass + boundary/structure pass.

Prints a JSON report consumed by dataset_review_v4.md and
dataset_acceptance_v4.md. All numbers are computed programmatically.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy import stats as st

from engine_v4 import CUTOFF, Validator, _parse_iso, read_lines

PRODUCT_SPEC = {
    "Ипотека": (0.06, 0.19, 120, 360, 1e6, 30e6),
    "Автокредит": (0.10, 0.25, 12, 84, 0.3e6, 5e6),
    "Потребительский кредит": (0.16, 0.35, 12, 84, 0.03e6, 3e6),
    "Кредитная карта": (0.20, 0.40, 6, 36, 0.01e6, 0.5e6),
    "Рассрочка": (0.00, 0.05, 3, 24, 0.005e6, 0.3e6),
    "Заём МФО": (0.50, 2.92, 1, 12, 0.005e6, 0.1e6),
}
PSK_CAP = 2.92


def annuity_term(amount: float, rate: float, payment: float) -> float:
    if payment <= 0:
        return math.inf
    r = rate / 12.0
    if r == 0:
        return amount / payment
    if payment <= amount * r:
        return math.inf
    return -math.log(1 - amount * r / payment) / math.log(1 + r)


def describe(arr: np.ndarray) -> dict:
    if len(arr) == 0:
        return {}
    qs = np.percentile(arr, [10, 50, 90, 99])
    return {
        "n": int(len(arr)), "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(np.min(arr)), "p10": float(qs[0]), "p50": float(qs[1]),
        "p90": float(qs[2]), "p99": float(qs[3]), "max": float(np.max(arr)),
        "skew": float(st.skew(arr)), "kurtosis": float(st.kurtosis(arr)),
    }


def main() -> None:
    paths = [f"part{i}.jsonl.gz" for i in (1, 2, 3, 4)]
    lines = read_lines(paths)
    validator = Validator()

    parsed, defects = [], []
    for pos, line in enumerate(lines):
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            defects.append((pos, "unparseable JSON"))
            parsed.append(None)
            continue
        reason = validator.check(rec)
        if reason:
            defects.append((pos, reason))
            parsed.append((rec if isinstance(rec, dict) else None, reason))
        else:
            parsed.append((rec, None))

    valid = [p[0] for p in parsed if p and p[1] is None]
    rep: dict = {"rows_total": len(lines), "valid": len(valid),
                 "invalid": len(defects)}

    reason_bins = Counter()
    for _, reason in defects:
        key = reason.split(":")[0].split("(")[0].strip()[:60]
        reason_bins[key] += 1
    rep["defect_reasons"] = dict(reason_bins.most_common())

    # ---------------------------------------------------- pass 1: population
    inc = np.array([r["income_total"] for r in valid])
    exp = np.array([r["expense_total"] for r in valid])
    pay = np.array([sum(o["monthly_payment"] for o in r["obligations"])
                    for r in valid])
    bliq = np.array([r["bliq"] for r in valid])
    tgt = np.array([sum(g["target_amount"] for g in r["goals"])
                    for r in valid])
    cur = np.array([sum(g["current_amount"] for g in r["goals"])
                    for r in valid])
    fcf = inc - exp - pay
    nd = np.array([len(r["obligations"]) for r in valid])
    ng = np.array([len(r["goals"]) for r in valid])
    rb = np.array([r["r_bench"] for r in valid])
    risk = np.array([int(r["risk_tolerance"]) for r in valid])

    rep["descriptive"] = {
        "income": describe(inc), "expense": describe(exp),
        "payments": describe(pay), "bliq": describe(bliq),
        "goal_target_sum": describe(tgt), "goal_current_sum": describe(cur),
        "fcf": describe(fcf), "n_debts": describe(nd.astype(float)),
        "n_goals": describe(ng.astype(float)), "r_bench": describe(rb),
    }

    fields = {"income": inc, "expense": exp, "payments": pay,
              "bliq": bliq, "goal_target_sum": tgt}
    names = list(fields)
    pear, spear = {}, {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pear[f"{a}~{b}"] = float(st.pearsonr(fields[a], fields[b])[0])
            spear[f"{a}~{b}"] = float(st.spearmanr(fields[a], fields[b])[0])
    rep["pearson"] = pear
    rep["spearman"] = spear

    pos_inc = inc[inc > 0]
    log_inc = np.log(pos_inc)
    mu, sigma = float(np.mean(log_inc)), float(np.std(log_inc, ddof=1))
    ks = st.kstest(log_inc, "norm", args=(mu, sigma))
    core = pos_inc[pos_inc < 5e6]  # exclude whales/stress for the core test
    log_core = np.log(core)
    ks_core = st.kstest(log_core, "norm",
                        args=(float(np.mean(log_core)),
                              float(np.std(log_core, ddof=1))))
    rep["lognormality_income"] = {
        "all": {"n": int(len(log_inc)), "ks_stat": float(ks.statistic),
                "p": float(ks.pvalue)},
        "core_lt_5m": {"n": int(len(log_core)),
                       "ks_stat": float(ks_core.statistic),
                       "p": float(ks_core.pvalue)},
        "note": "params fitted on sample (Lilliefors-biased, p optimistic)",
    }

    rep["risk_counts"] = dict(Counter(risk.tolist()))
    rep["n_debts_hist"] = dict(Counter(nd.tolist()))
    rep["n_goals_hist"] = dict(Counter(ng.tolist()))
    rep["r_bench_unique"] = int(len(np.unique(np.round(rb, 6))))
    rep["r_bench_range"] = [float(rb.min()), float(rb.max())]

    horiz = Counter()
    readiness = Counter()
    dl_census = Counter()
    max_h_days = 0
    for r in valid:
        for g in r["goals"]:
            t, c = g["target_amount"], g["current_amount"]
            if t > 0:
                ratio = c / t
                bucket = ("0" if ratio == 0 else
                          "(0,0.25]" if ratio <= 0.25 else
                          "(0.25,0.5]" if ratio <= 0.5 else
                          "(0.5,0.75]" if ratio <= 0.75 else
                          "(0.75,1)" if ratio < 1 else
                          "==1" if ratio == 1 else ">1")
            else:
                bucket = "target=0"
            readiness[bucket] += 1
            dl = g["deadline"]
            if dl is None:
                horiz["perpetual"] += 1
                continue
            days = (_parse_iso(dl) - CUTOFF).days
            max_h_days = max(max_h_days, days)
            dl_census["past" if days < 0 else
                      "today" if days == 0 else
                      "tomorrow" if days == 1 else "future"] += 1
            m = days / 30.4375
            horiz["past" if days < 0 else "today" if days == 0 else
                  "(0,3m]" if m <= 3 else "(3,12m]" if m <= 12 else
                  "(1,3y]" if m <= 36 else "(3,5y]" if m <= 60 else
                  ">5y"] += 1
    rep["deadline_horizons"] = dict(horiz)
    rep["deadline_census"] = dict(dl_census)
    rep["max_horizon_days"] = max_h_days
    rep["goal_readiness"] = dict(readiness)

    inc_pos_mask = inc > 0
    k = tgt[inc_pos_mask & (tgt > 0)] / (12 * inc[inc_pos_mask & (tgt > 0)])
    rep["goal_k_ratio"] = describe(k) if len(k) else {}

    # ------------------------------------------- pass 2: boundaries & realism
    b = {
        "zero_income": int(np.sum(inc == 0)),
        "zero_expense": int(np.sum(exp == 0)),
        "zero_bliq": int(np.sum(bliq == 0)),
        "fcf_exact_zero": int(np.sum(fcf == 0.0)),
        "fcf_abs_lt_1rub": int(np.sum((np.abs(fcf) < 1) & (fcf != 0))),
        "deficit": int(np.sum(fcf < 0)),
        "pdn_exact_040": 0, "pdn_near_040": 0,
        "target_eq_current": 0, "overfunded": 0,
        "income_ge_5m": int(np.sum(inc >= 5e6)),
        "income_ge_100m": int(np.sum(inc >= 1e8)),
        "no_debts": int(np.sum(nd == 0)),
        "no_goals": int(np.sum(ng == 0)),
        "no_debts_no_goals": int(np.sum((nd == 0) & (ng == 0))),
    }
    for r, income_v, pay_v in zip(valid, inc, pay):
        if income_v > 0 and pay_v > 0:
            pdn = pay_v / income_v
            if abs(pdn - 0.40) < 1e-9:
                b["pdn_exact_040"] += 1
            elif abs(pdn - 0.40) < 0.005:
                b["pdn_near_040"] += 1
        for g in r["goals"]:
            if g["target_amount"] == g["current_amount"]:
                b["target_eq_current"] += 1
            elif g["current_amount"] > g["target_amount"]:
                b["overfunded"] += 1
    rep["boundaries"] = b

    prod = defaultdict(lambda: {"n": 0, "rate_ok": 0, "term_ok": 0,
                                "amount_ok": 0, "interest_only": 0,
                                "rates": [], "terms": []})
    unknown_products = Counter()
    over_psk = over_300 = 0
    for r in valid:
        for o in r["obligations"]:
            name, rate = o["name"], o["interest_rate"]
            amount, payment = o["amount"], o["monthly_payment"]
            if rate > PSK_CAP:
                over_psk += 1
            if rate > 3.0:
                over_300 += 1
            if name not in PRODUCT_SPEC:
                unknown_products[name] += 1
                continue
            lo, hi, tlo, thi, alo, ahi = PRODUCT_SPEC[name]
            p = prod[name]
            p["n"] += 1
            p["rates"].append(rate)
            p["rate_ok"] += int(lo - 1e-9 <= rate <= hi + 1e-9)
            p["amount_ok"] += int(alo <= amount <= ahi)
            term = annuity_term(amount, rate, payment)
            if math.isinf(term):
                p["interest_only"] += 1
            else:
                p["terms"].append(term)
                p["term_ok"] += int(tlo - 0.5 <= term <= thi + 0.5)
    rep["products"] = {}
    for name, p in prod.items():
        rates = np.array(p["rates"])
        terms = np.array(p["terms"]) if p["terms"] else np.array([0.0])
        rep["products"][name] = {
            "n": p["n"],
            "rate_min": float(rates.min()), "rate_max": float(rates.max()),
            "rate_in_spec_pct": round(100 * p["rate_ok"] / p["n"], 2),
            "amount_in_spec_pct": round(100 * p["amount_ok"] / p["n"], 2),
            "term_p50": float(np.median(terms)),
            "term_in_spec_pct": round(
                100 * p["term_ok"] / max(1, len(p["terms"])), 2),
            "interest_only": p["interest_only"],
        }
    rep["unknown_products"] = dict(unknown_products)
    rep["rates_over_psk_cap_valid"] = over_psk
    rep["rates_over_300_valid"] = over_300

    goal_by_name = defaultdict(list)
    for r in valid:
        for g in r["goals"]:
            goal_by_name[g["name"]].append(g["target_amount"])
    rep["goal_amounts_by_name"] = {
        name: {"n": len(v),
               "p10": float(np.percentile(v, 10)),
               "p50": float(np.percentile(v, 50)),
               "p90": float(np.percentile(v, 90)),
               "max": float(np.max(v))}
        for name, v in sorted(goal_by_name.items())}

    ids = Counter()
    id_valid: dict[str, list[bool]] = defaultdict(list)
    for pos, (line, p) in enumerate(zip(lines, parsed)):
        rid = None
        if p and isinstance(p[0], dict) and isinstance(p[0].get("id"), str):
            rid = p[0]["id"]
        if rid:
            ids[rid] += 1
            id_valid[rid].append(p[1] is None)
    dup = {rid: n for rid, n in ids.items() if n > 1}
    dup_both_valid = sum(1 for rid in dup if all(id_valid[rid]))
    dup_with_invalid = len(dup) - dup_both_valid
    rep["dup_ids"] = {
        "groups": len(dup), "rows_involved": sum(dup.values()),
        "groups_all_valid": dup_both_valid,
        "groups_with_invalid": dup_with_invalid,
        "examples": dict(list(dup.items())[:10]),
    }

    extra_top = Counter()
    extra_ob = Counter()
    extra_goal = Counter()
    for r in valid:
        for kkey in r:
            if kkey not in ("id", "income_total", "expense_total",
                            "obligations", "goals", "bliq", "r_bench",
                            "risk_tolerance"):
                extra_top[kkey] += 1
        for o in r["obligations"]:
            for kkey in o:
                if kkey not in ("id", "name", "amount", "interest_rate",
                                "monthly_payment"):
                    extra_ob[kkey] += 1
        for g in r["goals"]:
            for kkey in g:
                if kkey not in ("id", "name", "target_amount",
                                "current_amount", "deadline"):
                    extra_goal[kkey] += 1
    rep["extra_fields"] = {"top": dict(extra_top), "obligation":
                           dict(extra_ob), "goal": dict(extra_goal)}

    strata = {
        "risk_profiles_min": int(min(Counter(risk.tolist()).values())),
        "deficit": int(np.sum(fcf < 0)), "ok": int(np.sum(fcf >= 0)),
        "invalid": len(defects),
    }
    rep["strata_power"] = strata
    rep["defect_positions_first20"] = [p for p, _ in defects[:20]]

    json.dump(rep, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
