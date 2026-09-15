#!/usr/bin/env python3
"""Extended statistics for expert_portraits_v3 per coordinator checklist (section 5, item 6)."""
import gzip
import json
import math
from collections import Counter, defaultdict

from scipy import stats as sps

UPLOADS = "/mnt/user-data/uploads"
PARTS = [f"{UPLOADS}/expert_portraits_v3_part{i}_jsonl.gz" for i in range(1, 5)]


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def quantiles(xs, points):
    xs = sorted(xs)
    out = {}
    for label, p in points:
        k = (len(xs) - 1) * p
        lo, hi = math.floor(k), math.ceil(k)
        out[label] = xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
    return out


QPTS = [("min", 0), ("p10", .1), ("p50", .5), ("p90", .9), ("p99", .99), ("max", 1)]


def describe(xs):
    n = len(xs)
    mean = sum(xs) / n
    m2 = sum((x - mean) ** 2 for x in xs) / n
    m3 = sum((x - mean) ** 3 for x in xs) / n
    m4 = sum((x - mean) ** 4 for x in xs) / n
    sd = math.sqrt(m2)
    out = {"n": n, "mean": mean, "sd": sd,
           "skew": m3 / m2 ** 1.5 if m2 > 0 else None,
           "kurt_ex": m4 / m2 ** 2 - 3 if m2 > 0 else None}
    out.update(quantiles(xs, QPTS))
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy), 3)


def corr_matrix(named, fn):
    keys = list(named)
    return {a: {b: fn(named[a], named[b]) for b in keys} for a in keys}


V = load_jsonl("valid_dump.jsonl")
D = load_jsonl("debts_dump.jsonl")
G = load_jsonl("goals_dump.jsonl")

inc = [v["inc"] for v in V]
exp = [v["exp"] for v in V]
pay = [v["pay_total"] for v in V]
bliq = [v["bliq"] for v in V]
gsum = [v["goal_target_sum"] for v in V]
F = [v["F"] for v in V]
rb = [v["rb"] for v in V]

S = {}

S["desc"] = {
    "income": describe(inc), "expense": describe(exp),
    "debt_payments": describe(pay), "bliq": describe(bliq),
    "goal_target_sum": describe(gsum), "free_flow": describe(F),
    "n_debts": describe([float(v["n_debts"]) for v in V]),
    "n_goals": describe([float(v["n_goals"]) for v in V]),
}

named = {"inc": inc, "exp": exp, "pay": pay, "bliq": bliq, "gsum": gsum}
S["pearson"] = corr_matrix(named, pearson)
rk = {k: ranks(v) for k, v in named.items()}
S["spearman"] = corr_matrix(rk, pearson)


def ks_lognorm(xs):
    lx = [math.log(x) for x in xs if x > 0]
    mu = sum(lx) / len(lx)
    sd = math.sqrt(sum((v - mu) ** 2 for v in lx) / (len(lx) - 1))
    st = sps.kstest(lx, "norm", args=(mu, sd))
    return {"n": len(lx), "mu": round(mu, 4), "sigma": round(sd, 4),
            "D": round(float(st.statistic), 4), "p": float(st.pvalue)}


p99_inc = quantiles(inc, [("p99", .99)])["p99"]
S["ks_lognorm_income"] = {
    "full": ks_lognorm(inc),
    "trimmed_le_p99": ks_lognorm([x for x in inc if 0 < x <= p99_inc]),
}

S["r_bench"] = {"n_unique": len({round(x, 6) for x in rb}),
                "min": round(min(rb), 4), "max": round(max(rb), 4)}

dated_ml = [g["ml"] for g in G if g["dated"] and g["ml"] is not None]
n_dated = max(1, len(dated_ml))
S["deadline_buckets"] = {
    "null_share": round(1 - sum(g["dated"] for g in G) / len(G), 4),
    "le3_share_of_dated": round(sum(1 for m in dated_ml if m <= 3) / n_dated, 4),
    "m4_12": round(sum(1 for m in dated_ml if 3 < m <= 12) / n_dated, 4),
    "m13_36": round(sum(1 for m in dated_ml if 12 < m <= 36) / n_dated, 4),
    "m37_120": round(sum(1 for m in dated_ml if 36 < m <= 120) / n_dated, 4),
    "gt120": sum(1 for m in dated_ml if m > 120),
}

prog = [g["cur"] / g["target"] for g in G if g["target"] > 0]
S["readiness_buckets"] = {
    "lt25": round(sum(1 for p in prog if p < .25) / len(prog), 4),
    "b25_50": round(sum(1 for p in prog if .25 <= p < .5) / len(prog), 4),
    "b50_75": round(sum(1 for p in prog if .5 <= p < .75) / len(prog), 4),
    "b75_100": round(sum(1 for p in prog if .75 <= p < 1) / len(prog), 4),
    "ge100": round(sum(1 for p in prog if p >= 1) / len(prog), 4),
}

pdn = [(v["pay_total"] / v["inc"]) if v["inc"] > 0 else None for v in V]
debtors = [x for v, x in zip(V, pdn) if v["n_debts"] > 0 and x is not None]
S["pdn_buckets_all"] = {
    "zero_debt": round(sum(1 for v in V if v["n_debts"] == 0) / len(V), 4),
    "le30": round(sum(1 for x in debtors if x <= .3) / len(V), 4),
    "b30_50": round(sum(1 for x in debtors if .3 < x <= .5) / len(V), 4),
    "b50_80": round(sum(1 for x in debtors if .5 < x <= .8) / len(V), 4),
    "gt80": round(sum(1 for x in debtors if x > .8) / len(V), 4),
}
S["pdn_gt80_share_of_debtors"] = round(
    sum(1 for x in debtors if x > .8) / len(debtors), 4)

lm = [v["bliq"] / v["needs"] for v in V if v["needs"] > 0]
S["liquidity_buckets"] = {
    "lt1": round(sum(1 for x in lm if x < 1) / len(lm), 4),
    "m1_3": round(sum(1 for x in lm if 1 <= x < 3) / len(lm), 4),
    "m3_6": round(sum(1 for x in lm if 3 <= x < 6) / len(lm), 4),
    "m6_12": round(sum(1 for x in lm if 6 <= x < 12) / len(lm), 4),
    "ge12": round(sum(1 for x in lm if x >= 12) / len(lm), 4),
}

S["fcf_sign"] = {
    "neg": round(sum(1 for f in F if f < 0) / len(F), 4),
    "b0_30k": round(sum(1 for f in F if 0 <= f < 30000) / len(F), 4),
    "ge30k": round(sum(1 for f in F if f >= 30000) / len(F), 4),
}

terms = [d["term_m"] for d in D if d["term_m"]]
S["annuity_terms"] = {
    "n_with_term": len(terms),
    "share_lt6": round(sum(1 for t in terms if t < 6) / len(terms), 5),
    "share_gt360": round(sum(1 for t in terms if t > 360) / len(terms), 5),
    "min_m": round(min(terms), 2), "max_m": round(max(terms), 1),
    "nonamort_n": sum(1 for d in D if d["nonamort"]),
}

S["catalog_cases"] = {
    "income_zero": sum(1 for x in inc if x == 0),
    "expense_zero": sum(1 for x in exp if x == 0),
    "overdue_goals": sum(1 for g in G if g["overdue"]),
    "target_eq_current": sum(
        1 for g in G if g["target"] > 0 and abs(g["cur"] - g["target"]) < 0.005),
    "overfunded_goals": sum(
        1 for g in G if g["target"] > 0 and g["cur"] > g["target"] + 0.005),
    "rate_eq_bench_exact": sum(1 for d in D if abs(d["rate"] - d["rb"]) < 1e-9),
}


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


kvals = []
for path in PARTS:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(r, dict) or r.get("__meta__"):
                continue
            income = r.get("income_total")
            goals = r.get("goals")
            if not (is_num(income) and income > 0 and isinstance(goals, list)):
                continue
            for g0 in goals:
                if isinstance(g0, dict):
                    t = g0.get("target_amount")
                    if is_num(t) and t > 0:
                        kvals.append(t / (income * 12))

S["goal_k"] = {"n": len(kvals)}
S["goal_k"].update({k2: round(v2, 4) for k2, v2 in quantiles(kvals, QPTS).items()})
S["goal_k"]["share_in_02_5"] = round(
    sum(1 for k2 in kvals if .2 - 1e-9 <= k2 <= 5 + 1e-9) / len(kvals), 4)
S["goal_k"]["share_gt5"] = round(sum(1 for k2 in kvals if k2 > 5 + 1e-9) / len(kvals), 4)
S["goal_k"]["share_lt02"] = round(sum(1 for k2 in kvals if k2 < .2 - 1e-9) / len(kvals), 4)

S["extremes"] = {
    "income_gt_1e7": sum(1 for x in inc if x > 1e7),
    "income_gt_1e8": sum(1 for x in inc if x > 1e8),
    "income_ge_1e9": sum(1 for x in inc if x >= 1e9),
    "bliq_gt_1e8": sum(1 for x in bliq if x > 1e8),
    "bliq_ge_1e9": sum(1 for x in bliq if x >= 1e9),
    "debt_amount_gt_1e8": sum(1 for d in D if d["amount"] > 1e8),
    "goal_target_gt_1e8": sum(1 for g in G if g["target"] > 1e8),
    "records_any_field_ge_1e8": sum(
        1 for v in V if v["inc"] >= 1e8 or v["exp"] >= 1e8 or v["bliq"] >= 1e8
        or v["debt_total"] >= 1e8 or v["goal_target_sum"] >= 1e8),
}

trip = Counter((round(v["inc"], 2), round(v["exp"], 2), round(v["bliq"], 2)) for v in V)
S["meta_pairs"] = {"exact_triple_collisions": sum(c - 1 for c in trip.values() if c > 1)}

by_eb = defaultdict(list)
for v in V:
    by_eb[(round(v["exp"], 2), round(v["bliq"], 2))].append(v["inc"])
m1 = 0
for xs in by_eb.values():
    if len(xs) > 1:
        xs = sorted(xs)
        for i in range(len(xs) - 1):
            for j in range(i + 1, len(xs)):
                if xs[i] > 0 and abs(xs[j] / xs[i] - 1.01) < 1e-3:
                    m1 += 1
S["meta_pairs"]["m1_income_plus1pct"] = m1

by_ie = defaultdict(list)
for v in V:
    by_ie[(round(v["inc"], 2), round(v["exp"], 2))].append(v["bliq"])
m4 = 0
for xs in by_ie.values():
    if len(xs) > 1:
        xs = sorted(xs)
        for i in range(len(xs) - 1):
            for j in range(i + 1, len(xs)):
                if xs[i] > 0 and abs(xs[j] / xs[i] - 1.01) < 1e-3:
                    m4 += 1
S["meta_pairs"]["m4_bliq_plus1pct"] = m4

sig = defaultdict(set)
for v in V:
    if v["inc"] > 0:
        sig[(round(v["exp"] / v["inc"], 6), round(v["bliq"] / v["inc"], 6),
             round(v["rb"], 6), v["rt"], v["n_debts"], v["n_goals"])].add(round(v["inc"], 2))
S["meta_pairs"]["m5_scale_groups"] = sum(1 for s in sig.values() if len(s) > 1)

print(json.dumps(S, ensure_ascii=False, indent=1))
