"""Statistical review of the v2 portrait dataset (12 000 records).

Computes every figure for dataset_review.md programmatically:
descriptives, correlations, distribution shapes, categorical counts,
derived diagnostics, boundary-case census, annuity consistency,
metamorphic-pair detection, md-card spot check.
"""

import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date

import numpy as np
from scipy import stats

AS_OF = date(2026, 7, 11)


def load(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def desc(name: str, arr) -> str:
    a = np.asarray(arr, dtype=float)
    if a.size == 0:
        return f"{name}: EMPTY"
    q = np.percentile(a, [10, 50, 90, 99])
    return (
        f"{name}: n={a.size} mean={a.mean():.2f} sd={a.std():.2f} "
        f"min={a.min():.2f} p10={q[0]:.2f} p50={q[1]:.2f} "
        f"p90={q[2]:.2f} p99={q[3]:.2f} max={a.max():.2f} "
        f"skew={stats.skew(a):.2f} kurt={stats.kurtosis(a):.2f}"
    )


def months_between(d: date) -> float:
    return (d - AS_OF).days / 30.44


def implied_term(amount: float, rate: float, pay: float) -> float | None:
    if pay <= 0:
        return None
    i = rate / 12.0
    if i == 0:
        return amount / pay
    if pay <= amount * i:
        return math.inf
    return math.log(pay / (pay - amount * i)) / math.log(1.0 + i)


def main(path: str, md_path: str) -> None:
    recs = load(path)
    n = len(recs)
    print(f"== RECORDS: {n} ==")

    income = np.array([r["income_total"] for r in recs])
    expense = np.array([r["expense_total"] for r in recs])
    bliq = np.array([r["bliq"] for r in recs])
    pays = np.array([sum(o["monthly_payment"] for o in r["obligations"])
                     for r in recs])
    debts = np.array([sum(o["amount"] for o in r["obligations"])
                      for r in recs])
    targets = np.array([sum(g["target_amount"] for g in r["goals"])
                        for r in recs])
    currents = np.array([sum(g["current_amount"] for g in r["goals"])
                         for r in recs])
    n_obl = np.array([len(r["obligations"]) for r in recs])
    n_goals = np.array([len(r["goals"]) for r in recs])
    risk = np.array([r["risk_tolerance"] for r in recs])
    rbench = np.array([r["r_bench"] for r in recs])
    fcf = income - expense - pays

    print("\n== (a) DESCRIPTIVES (per record) ==")
    for name, arr in [
        ("income", income), ("expense", expense), ("sum_pay", pays),
        ("sum_debt_body", debts), ("bliq", bliq), ("sum_goal_target", targets),
        ("sum_goal_current", currents), ("fcf", fcf),
        ("n_obligations", n_obl), ("n_goals", n_goals),
    ]:
        print(desc(name, arr))

    loan_amt, loan_rate, loan_pay = [], [], []
    for r in recs:
        for o in r["obligations"]:
            loan_amt.append(o["amount"])
            loan_rate.append(o["interest_rate"])
            loan_pay.append(o["monthly_payment"])
    g_target, g_current = [], []
    for r in recs:
        for g in r["goals"]:
            g_target.append(g["target_amount"])
            g_current.append(g["current_amount"])
    print("\n== (a) DESCRIPTIVES (per loan / per goal) ==")
    print(desc("loan_amount", loan_amt))
    print(desc("loan_rate", loan_rate))
    print(desc("loan_payment", loan_pay))
    print(desc("goal_target", g_target))
    print(desc("goal_current", g_current))

    def corr_block(mask, label):
        cols = {"income": income, "expense": expense, "sum_pay": pays,
                "bliq": bliq, "sum_target": targets}
        names = list(cols)
        m = np.vstack([cols[c][mask] for c in names])
        pearson = np.corrcoef(m)
        spear = stats.spearmanr(m.T).statistic
        print(f"\n== (b) CORRELATIONS [{label}] n={mask.sum()} ==")
        print("cols:", names)
        print("Pearson:\n", np.round(pearson, 3))
        print("Spearman:\n", np.round(spear, 3))

    full = np.ones(n, dtype=bool)
    core = (income > 0) & (income < 1e7) & (expense > 0)
    corr_block(full, "FULL SET")
    corr_block(core, "CORE income>0,<1e7 & expense>0")

    holders = n_obl > 0
    sp_all = stats.spearmanr(pays[holders], income[holders])
    pe_all = stats.pearsonr(pays[holders], income[holders])
    ch = holders & core
    sp_core = stats.spearmanr(pays[ch], income[ch])
    print(f"\npay~income among loan holders: n={holders.sum()} "
          f"spearman={sp_all.statistic:.3f} (p={sp_all.pvalue:.1e}) "
          f"pearson={pe_all.statistic:.3f}; core spearman={sp_core.statistic:.3f}")

    print("\n== (c) SHAPE / LOG-NORMALITY OF INCOME ==")
    for label, mask in [("income>0 FULL", income > 0),
                        ("income CORE", core)]:
        li = np.log(income[mask])
        mu, sd = li.mean(), li.std(ddof=1)
        ks = stats.kstest(li, "norm", args=(mu, sd))
        print(f"{label}: n={mask.sum()} log-mean={mu:.3f} log-sd={sd:.3f} "
              f"KS={ks.statistic:.4f} p={ks.pvalue:.2e} "
              f"(params estimated -> Lilliefors-type, p optimistic)")

    print("\n== (d) CATEGORICAL / COUNTS ==")
    print("risk_tolerance:", dict(sorted(Counter(risk.tolist()).items())))
    print("r_bench:", dict(sorted(Counter(np.round(rbench, 4).tolist()).items())))
    print("n_obligations:", dict(sorted(Counter(n_obl.tolist()).items())))
    print("n_goals:", dict(sorted(Counter(n_goals.tolist()).items())))

    horizon = Counter()
    readiness = Counter()
    deadline_today = past_due = exact_full = overfunded = 0
    for r in recs:
        for g in r["goals"]:
            t, c = g["target_amount"], g["current_amount"]
            if t > 0:
                ratio = c / t
                if ratio > 1:
                    readiness["overfunded>100%"] += 1
                elif ratio == 1:
                    readiness["exactly 100%"] += 1
                elif ratio >= 0.75:
                    readiness["75-100%"] += 1
                elif ratio >= 0.5:
                    readiness["50-75%"] += 1
                elif ratio >= 0.25:
                    readiness["25-50%"] += 1
                else:
                    readiness["0-25%"] += 1
            if c > t:
                overfunded += 1
            if c == t:
                exact_full += 1
            if g["deadline"] is None:
                horizon["null"] += 1
                continue
            d = date.fromisoformat(g["deadline"])
            if d == AS_OF:
                deadline_today += 1
            m = months_between(d)
            if m < 0:
                horizon["past_due"] += 1
                past_due += 1
            elif m <= 3:
                horizon["0-3m"] += 1
            elif m <= 12:
                horizon["3-12m"] += 1
            elif m <= 36:
                horizon["1-3y"] += 1
            elif m <= 60:
                horizon["3-5y"] += 1
            elif m <= 120:
                horizon["5-10y"] += 1
            else:
                horizon[">10y"] += 1
    print("deadline horizons:", dict(horizon))
    print(f"deadline==today: {deadline_today}  past_due: {past_due}")
    print("goal readiness:", dict(readiness))
    print(f"goals target==current exactly: {exact_full}  overfunded: {overfunded}")

    inc_pos = income > 0
    k_goal = []
    for r in recs:
        if r["income_total"] > 0:
            for g in r["goals"]:
                k_goal.append(g["target_amount"] / (12 * r["income_total"]))
    k_goal = np.array(k_goal)
    out_k = ((k_goal < 0.2) | (k_goal > 5)).mean() if k_goal.size else 0
    print(f"goal scale k=target/annual_income: n={k_goal.size} "
          f"p50={np.median(k_goal):.2f} share outside [0.2,5]: {out_k:.1%} "
          f"(k<0.2: {(k_goal < 0.2).mean():.1%}, k>5: {(k_goal > 5).mean():.1%})")

    print("\n== (e) DERIVED DIAGNOSTICS ==")
    pdn = np.where(inc_pos, pays / np.where(inc_pos, income, 1), np.inf)
    pdn_h = pdn[holders]
    b = Counter()
    for v in pdn_h:
        if not np.isfinite(v):
            b["inf (income=0)"] += 1
        elif v <= 0.3:
            b["<=0.30"] += 1
        elif v <= 0.4:
            b["0.30-0.40"] += 1
        elif v <= 0.5:
            b["0.40-0.50"] += 1
        elif v <= 0.8:
            b["0.50-0.80"] += 1
        else:
            b[">0.80"] += 1
    print(f"PDN buckets among {holders.sum()} loan holders:", dict(b))
    fin = np.isfinite(pdn_h)
    print(f"PDN among holders: p50={np.median(pdn_h[fin]):.3f} "
          f"p90={np.percentile(pdn_h[fin], 90):.3f} "
          f"share>0.5={(pdn_h[fin] > 0.5).mean():.1%} "
          f"share>0.8={(pdn_h[fin] > 0.8).mean():.1%}")

    burn = expense + pays
    liq_m = np.where(burn > 0, bliq / np.where(burn > 0, burn, 1), np.inf)
    lb = Counter()
    for v in liq_m:
        if not np.isfinite(v):
            lb["inf (burn=0)"] += 1
        elif v < 1:
            lb["<1m"] += 1
        elif v < 3:
            lb["1-3m"] += 1
        elif v < 6:
            lb["3-6m"] += 1
        elif v < 12:
            lb["6-12m"] += 1
        else:
            lb[">=12m"] += 1
    print("liquidity months buckets:", dict(lb))
    print(f"FCF sign: neg={(fcf < 0).mean():.1%} zero={(fcf == 0).mean():.2%} "
          f"pos={(fcf > 0).mean():.1%}")

    print("\n== BOUNDARY-CASE CENSUS (layer C signatures) ==")
    big = max(income.max(), expense.max(), bliq.max(),
              debts.max() if debts.size else 0)
    any_big = np.zeros(n, dtype=bool)
    for i, r in enumerate(recs):
        vals = [r["income_total"], r["expense_total"], r["bliq"],
                *(o["amount"] for o in r["obligations"]),
                *(g["target_amount"] for g in r["goals"])]
        any_big[i] = any(v >= 1e9 for v in vals)
    print(f"zero income: {(income == 0).sum()}  zero expense: {(expense == 0).sum()}  "
          f"both zero: {((income == 0) & (expense == 0)).sum()}")
    print(f"zero expense WITH loans: {((expense == 0) & holders).sum()}")
    print(f"records with any field >= 1e9: {any_big.sum()}  global max: {big:.2e}")
    print(f"no goals: {(n_goals == 0).sum()}  no loans: {(n_obl == 0).sum()}  "
          f"neither: {((n_goals == 0) & (n_obl == 0)).sum()}")
    rate_eq_bench = sum(
        1 for r in recs for o in r["obligations"]
        if abs(o["interest_rate"] - r["r_bench"]) < 1e-9
    )
    print(f"loans with rate == r_bench exactly: {rate_eq_bench}")

    print("\n== ANNUITY CONSISTENCY (per loan) ==")
    total = io_cnt = zero_pay = short_t = long_t = ok_cnt = 0
    rate_cap = Counter()
    for r in recs:
        for o in r["obligations"]:
            total += 1
            rate_cap[round(o["interest_rate"], 4)] += 1
            t = implied_term(o["amount"], o["interest_rate"],
                             o["monthly_payment"])
            if t is None:
                zero_pay += 1
            elif t == math.inf:
                io_cnt += 1
            elif t < 5.5:
                short_t += 1
            elif t > 366:
                long_t += 1
            else:
                ok_cnt += 1
    print(f"loans total: {total}")
    print(f"consistent term 6-360m: {ok_cnt} ({ok_cnt / total:.1%})")
    print(f"interest-only/never amortize (pay<=interest): {io_cnt} "
          f"({io_cnt / total:.1%})")
    print(f"implied term <6m: {short_t} ({short_t / total:.1%})  "
          f">360m: {long_t} ({long_t / total:.1%})  zero payment: {zero_pay}")
    top_rates = rate_cap.most_common(8)
    print("top loan rates:", [(f"{k:.2%}", v) for k, v in top_rates])
    print(f"loans at max rate 35.00%: {rate_cap.get(0.35, 0)} "
          f"({rate_cap.get(0.35, 0) / total:.1%})")

    print("\n== METAMORPHIC PAIR DETECTION (layer E) ==")
    def sig_goals(r):
        return tuple(sorted((round(g["target_amount"], 2),
                             round(g["current_amount"], 2),
                             g["deadline"] or "") for g in r["goals"]))

    def sig_loans(r, with_rate=True):
        return tuple(sorted(
            (round(o["amount"], 2),
             round(o["interest_rate"], 4) if with_rate else 0,
             round(o["monthly_payment"], 2)) for o in r["obligations"]))

    def count_pairs(keyfun, valfun, lo, hi, label):
        groups = defaultdict(list)
        for r in recs:
            groups[keyfun(r)].append(valfun(r))
        pairs = 0
        for vals in groups.values():
            if len(vals) < 2:
                continue
            vals.sort()
            for a, c in zip(vals, vals[1:]):
                if a > 0 and lo <= c / a <= hi:
                    pairs += 1
        print(f"{label}: candidate pairs = {pairs}")
        return pairs

    count_pairs(
        lambda r: (r["risk_tolerance"], round(r["expense_total"], 2),
                   round(r["bliq"], 2), sig_loans(r), sig_goals(r)),
        lambda r: r["income_total"], 1.001, 1.05, "M1 income +~1%")
    count_pairs(
        lambda r: (r["risk_tolerance"], round(r["income_total"], 2),
                   round(r["expense_total"], 2), sig_loans(r), sig_goals(r)),
        lambda r: r["bliq"], 1.001, 1.05, "M4 bliq +~1%")

    exact_dupes = n - len({json.dumps(r, sort_keys=True) for r in recs})
    print(f"exact duplicate records: {exact_dupes}")

    print("\n== MD-CARD SPOT CHECK (3 random portraits) ==")
    rng = random.Random(20260711)
    sample = rng.sample(recs, 3)
    md = open(md_path, encoding="utf-8").read()

    def num(s):
        return float(re.sub(r"[\s\u00a0\u202f]", "", s))

    for r in sample:
        m = re.search(
            rf"### {re.escape(r['id'])} .*?\n(.*?)(?=\n### |\Z)",
            md, re.S)
        block = m.group(0) if m else ""
        gm = re.search(
            r"Доход ([\d\s\u00a0\u202f.,]+) ₽/мес · Расходы "
            r"([\d\s\u00a0\u202f.,]+) ₽/мес · Накопления "
            r"([\d\s\u00a0\u202f.,]+) ₽", block)
        ok = (gm and abs(num(gm.group(1)) - r["income_total"]) < 0.01
              and abs(num(gm.group(2)) - r["expense_total"]) < 0.01
              and abs(num(gm.group(3)) - r["bliq"]) < 0.01)
        n_loans_md = 0 if "Кредиты: нет" in block else block.count("остаток")
        n_goals_md = 0 if "Цели: нет" in block else block.count("«goal")
        struct_ok = (n_loans_md == len(r["obligations"])
                     and n_goals_md == len(r["goals"]))
        print(f"{r['id']}: numbers_match={bool(ok)} "
              f"structure_match={struct_ok} "
              f"(loans md/json {n_loans_md}/{len(r['obligations'])}, "
              f"goals {n_goals_md}/{len(r['goals'])})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
