"""Programmatic statistical profile of portraits_12000.jsonl (checklist а–з)."""

from __future__ import annotations

import json
import math
from datetime import date

import numpy as np
import pandas as pd
from scipy import stats

SRC = "/mnt/user-data/uploads/portraits_12000.jsonl"
OUT = "/home/claude/finpilot_eval/stats.json"
AS_OF = date(2026, 7, 8)
PCTS = [10, 50, 90, 99]


def describe(series: pd.Series) -> dict:
    s = series.dropna()
    q = np.percentile(s, PCTS) if len(s) else [math.nan] * 4
    return {"n": int(len(s)), "mean": float(s.mean()), "std": float(s.std()),
            "min": float(s.min()), "p10": float(q[0]), "p50": float(q[1]),
            "p90": float(q[2]), "p99": float(q[3]), "max": float(s.max()),
            "skew": float(stats.skew(s)), "kurtosis": float(stats.kurtosis(s))}


def load() -> tuple:
    rows, loans, goals = [], [], []
    for line in open(SRC):
        r = json.loads(line)
        e = r["engine"]
        payments = sum(o["monthly_payment"] for o in e["obligations"])
        row = {"id": r["id"], "kind": r["kind"], "income": e["income_total"],
               "expense": e["expense_total"], "bliq": e["bliq"],
               "r_bench": e["r_bench"], "risk": e["risk_tolerance"],
               "l_min": e["l_min"], "n_loans": len(e["obligations"]),
               "n_goals": len(e["goals"]), "payments": payments,
               "debt_total": sum(o["amount"] for o in e["obligations"]),
               "goal_target_sum": sum(g["target_amount"] for g in e["goals"]),
               "goal_current_sum": sum(g["current_amount"] for g in e["goals"])}
        row["outflow"] = row["expense"] + payments
        row["fcf"] = row["income"] - row["outflow"]
        row["dsti"] = payments / row["income"] if row["income"] > 0 else math.nan
        row["liq_m"] = row["bliq"] / row["outflow"] if row["outflow"] > 0 else math.nan
        rows.append(row)
        for o in e["obligations"]:
            loans.append({"kind": r["kind"], "amount": o["amount"],
                          "rate": o["interest_rate"], "payment": o["monthly_payment"],
                          "r_bench": e["r_bench"]})
        dls = []
        for g in e["goals"]:
            months = None
            if g["deadline"]:
                months = (date.fromisoformat(g["deadline"]) - AS_OF).days / 30.4375
                dls.append(g["deadline"])
            goals.append({"kind": r["kind"], "target": g["target_amount"],
                          "current": g["current_amount"], "months": months,
                          "ready": (g["current_amount"] / g["target_amount"]
                                    if g["target_amount"] > 0 else math.nan)})
        row["unique_deadlines"] = len(set(dls))
    return pd.DataFrame(rows), pd.DataFrame(loans), pd.DataFrame(goals)


def annuity_consistency(loans: pd.DataFrame) -> dict:
    res = {"n_loans": int(len(loans)), "interest_only": 0,
           "consistent_tol_0.1pct": 0, "consistent_tol_1pct": 0,
           "rate_eq_bench_exact": 0}
    for row in loans.itertuples():
        i = row.rate / 12.0
        if abs(row.rate - row.r_bench) < 1e-12:
            res["rate_eq_bench_exact"] += 1
        if row.payment <= row.amount * i + 1e-9:
            res["interest_only"] += 1
            continue
        n = (-math.log(1 - i * row.amount / row.payment) / math.log(1 + i)
             if i > 0 else row.amount / row.payment)
        n_int = round(n)
        if not 6 <= n_int <= 360:
            continue
        p_ref = (row.amount * i / (1 - (1 + i) ** -n_int)
                 if i > 0 else row.amount / n_int)
        err = abs(p_ref - row.payment) / row.payment
        if err < 0.001:
            res["consistent_tol_0.1pct"] += 1
        if err < 0.01:
            res["consistent_tol_1pct"] += 1
    return res


def buckets(series: pd.Series, edges: list, labels: list) -> dict:
    out = {label: 0 for label in labels + ["undefined"]}
    for v in series:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            out["undefined"] += 1
            continue
        for edge, label in zip(edges, labels):
            if v < edge:
                out[label] += 1
                break
        else:
            out[labels[-1]] += 1
    return out


def main() -> None:
    df, loans, goals = load()
    plain = df[df.kind == "plain"]
    result = {"n_total": int(len(df)), "kinds": df.kind.value_counts().to_dict()}

    money_fields = ["income", "expense", "bliq", "payments", "debt_total",
                    "goal_target_sum", "goal_current_sum", "fcf",
                    "n_loans", "n_goals"]
    result["descriptive_all"] = {f: describe(df[f]) for f in money_fields}
    result["descriptive_plain"] = {f: describe(plain[f]) for f in money_fields}
    result["loan_fields"] = {f: describe(loans[f]) for f in ("amount", "rate", "payment")}
    result["goal_fields"] = {f: describe(goals[f].dropna())
                             for f in ("target", "current", "ready")}

    corr_cols = ["income", "expense", "payments", "bliq", "goal_target_sum"]
    for name, frame in (("all", df), ("plain", plain)):
        result[f"pearson_{name}"] = frame[corr_cols].corr("pearson").round(4).to_dict()
        result[f"spearman_{name}"] = frame[corr_cols].corr("spearman").round(4).to_dict()

    inc = plain.income[plain.income > 0]
    log_inc = np.log(inc)
    ks = stats.kstest(log_inc, "norm", args=(log_inc.mean(), log_inc.std(ddof=1)))
    result["income_lognormality"] = {
        "n": int(len(inc)), "ks_stat": float(ks.statistic), "ks_p": float(ks.pvalue),
        "log_skew": float(stats.skew(log_inc)),
        "log_kurtosis": float(stats.kurtosis(log_inc)),
        "shapiro_note": "KS с оценёнными параметрами (эффект Лиллиефорса: p занижать нельзя, "
                        "но переоценивать значимость тоже)"}

    result["categorical"] = {
        "risk": df.risk.value_counts().sort_index().to_dict(),
        "r_bench_values": df.r_bench.round(4).value_counts().sort_index().to_dict(),
        "l_min_values": df.l_min.value_counts().to_dict(),
        "n_loans": df.n_loans.value_counts().sort_index().to_dict(),
        "n_goals": df.n_goals.value_counts().sort_index().to_dict(),
        "deadline_null_share": float(goals.months.isna().mean()),
        "deadline_horizon_months": buckets(
            goals.months, [3, 12, 36, 84, 1e9],
            ["<3", "3-12", "12-36", "36-84", ">=84"]),
        "goal_readiness_pct": buckets(
            goals.ready * 100, [1e-9, 25, 50, 75, 100 - 1e-9, 100 + 1e-9, 1e9],
            ["0", "(0,25]", "(25,50]", "(50,75]", "(75,100)", "=100", ">100"])}

    for name, frame in (("all", df), ("plain", plain)):
        result[f"derived_{name}"] = {
            "dsti_buckets": buckets(frame.dsti, [0.3, 0.5, 0.8, 1e9],
                                    ["<0.3", "0.3-0.5", "0.5-0.8", ">=0.8"]),
            "liq_buckets": buckets(frame.liq_m, [1, 3, 6, 12, 1e9],
                                   ["<1", "1-3", "3-6", "6-12", ">=12"]),
            "fcf_sign": {"neg": int((frame.fcf < 0).sum()),
                         "zero": int((frame.fcf == 0).sum()),
                         "pos": int((frame.fcf > 0).sum())}}

    med_cols = ["income", "expense", "payments", "dsti", "liq_m", "fcf",
                "n_loans", "n_goals", "bliq"]
    by_kind = df.groupby("kind")
    result["kind_medians"] = {k: {c: (None if pd.isna(v) else round(float(v), 4))
                                  for c, v in row.items()}
                              for k, row in by_kind[med_cols].median().iterrows()}
    result["kind_fcf_neg_share"] = {k: float((g.fcf < 0).mean())
                                    for k, g in by_kind}
    result["kind_dsti80_share"] = {k: float((g.dsti >= 0.8).mean())
                                   for k, g in by_kind}

    cheap = loans[loans.kind == "cheap_debts_only"]
    result["cheap_label_check"] = {
        "n_loans": int(len(cheap)),
        "share_rate_below_bench": float((cheap.rate < cheap.r_bench).mean()),
        "max_spread_over_bench": float((cheap.rate - cheap.r_bench).max())}
    many = df[df.kind == "many_goals"]
    result["many_goals_check"] = {
        "n": int(len(many)),
        "all_have_8": bool((many.n_goals == 8).all()),
        "portraits_with_duplicate_deadlines": int((many.unique_deadlines
                                                   < many.n_goals - 0).sum())}
    funded = goals[goals.kind == "funded_goal"]
    result["funded_label_check"] = {
        "overfunded_goals": int((funded.ready > 1).sum()),
        "exact_equal": int((funded.ready == 1).sum())}

    k_ratio = (plain.goal_target_sum / (12 * plain.income))[plain.n_goals > 0]
    result["goal_scale_k"] = describe(k_ratio)
    result["annuity"] = annuity_consistency(loans)
    result["deadline_range"] = {
        "min": str(goals.months.min()), "max_months": float(goals.months.max()),
        "min_months": float(goals.months.min())}

    with open(OUT, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: result[k] for k in
                      ("annuity", "cheap_label_check", "many_goals_check",
                       "funded_label_check", "income_lognormality",
                       "deadline_range")}, ensure_ascii=False, indent=1))
    print("pearson_plain:", result["pearson_plain"]["income"])
    print("goal_scale_k p50/p99:", result["goal_scale_k"]["p50"],
          result["goal_scale_k"]["p99"])


if __name__ == "__main__":
    main()
