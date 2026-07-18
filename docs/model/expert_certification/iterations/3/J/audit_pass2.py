"""Audit pass 2: §1C boundary census, layer E scan, full §5.6 stats."""
import json
import math
import statistics as st
from collections import Counter, defaultdict
from datetime import date

from engine import validate, flow_cents

CUTOFF = date(2026, 7, 16)

lines = []
for i in range(1, 5):
    with open(f"part{i}.jsonl") as f:
        for raw in f:
            rec = json.loads(raw)
            if rec.get("__meta__"):
                continue
            lines.append(rec)
valid = []
for rec in lines:
    p = validate(rec)
    if p:
        p["id"] = rec["id"]
        valid.append(p)
n = len(valid)

print("== §1C boundary census ==")
c = Counter()
maxgoals_same_dl = 0
max_liq_months = 0.0
for p in valid:
    f = flow_cents(p) / 100
    mo = p["expense"] + sum(o["payment"] for o in p["obligations"])
    if p["income"] == 0:
        c["zero_income"] += 1
    if p["expense"] == 0:
        c["zero_expense"] += 1
    if f < 0:
        c["deficit"] += 1
    if p["income"] > 0 and sum(o["payment"] for o in p["obligations"]) / p["income"] > 0.8:
        c["dti_gt_08"] += 1
    live = [o for o in p["obligations"] if o["amount"] > 0]
    if live and all(o["rate"] < p["r_bench"] for o in live):
        c["only_cheap_debts"] += 1
    for o in live:
        if o["payment"] > 0 and o["payment"] <= o["amount"] * o["rate"] / 12:
            c["interest_only_debts"] += 1
        if o["rate"] == p["r_bench"]:
            c["rate_eq_bench_exact"] += 1
    for g in p["goals"]:
        if g["deadline"] == CUTOFF:
            c["deadline_today"] += 1
        if g["deadline"] and g["deadline"] < CUTOFF and g["current"] < g["target"]:
            c["overdue_underfunded"] += 1
        if g["current"] == g["target"]:
            c["target_eq_current_exact"] += 1
        if g["current"] > g["target"]:
            c["overfunded_goal"] += 1
    dl = Counter(g["deadline"] for g in p["goals"] if g["deadline"])
    if dl:
        maxgoals_same_dl = max(maxgoals_same_dl, max(dl.values()))
    if not p["goals"]:
        c["no_goals"] += 1
    if not p["obligations"]:
        c["no_debts"] += 1
    if mo > 0:
        max_liq_months = max(max_liq_months, p["bliq"] / mo)
    if p["income"] >= 1e9 or p["bliq"] >= 1e9:
        c["sums_1e9"] += 1
for k, v in sorted(c.items()):
    print(f"  {k}: {v}")
print(f"  max goals with same deadline in one portrait: {maxgoals_same_dl}")
print(f"  max liquidity months: {max_liq_months:,.0f}")

print("\n== layer E scan (metamorphic pairs) ==")
by_exp = defaultdict(list)
for idx, p in enumerate(valid):
    by_exp[(p["expense"], p["bliq"])].append(idx)
cand1 = [g for g in by_exp.values() if len(g) > 1]
print("exact (expense,bliq) collisions:", len(cand1))
by_exp2 = defaultdict(list)
for idx, p in enumerate(valid):
    by_exp2[(p["expense"], p["risk"], len(p["obligations"]), len(p["goals"]))].append(idx)
cand2 = sum(1 for g in by_exp2.values() if len(g) > 1)
print("(expense,risk,n_obl,n_goals) collisions:", cand2)
# scale-invariant signature for ×k pairs
sig = defaultdict(list)
for idx, p in enumerate(valid):
    if p["income"] <= 0:
        continue
    s = [round(p["expense"] / p["income"], 6), round(p["bliq"] / p["income"], 6),
         p["risk"], round(p["r_bench"], 6)]
    for o in p["obligations"]:
        s += [round(o["amount"] / p["income"], 6), round(o["rate"], 6)]
    for g in p["goals"]:
        s += [round(g["target"] / p["income"], 6)]
    sig[tuple(s)].append(idx)
scale_pairs = [g for g in sig.values() if len(g) > 1]
print("scale-invariant signature collisions (×k candidates):", len(scale_pairs))

print("\n== §5.6(а) full descriptives ==")
def stats_row(name, xs):
    xs = sorted(xs)
    m = len(xs)
    def pq(p):
        return xs[min(m - 1, int(p * (m - 1)))]
    print(f"{name}: n={m} mean={st.mean(xs):,.1f} sd={st.pstdev(xs):,.1f} "
          f"min={xs[0]:,.1f} p10={pq(.1):,.1f} p50={pq(.5):,.1f} "
          f"p90={pq(.9):,.1f} p99={pq(.99):,.1f} max={xs[-1]:,.1f}")

pay_sum = [sum(o["payment"] for o in p["obligations"]) for p in valid]
goal_sum = [sum(g["target"] for g in p["goals"]) for p in valid]
stats_row("income", [p["income"] for p in valid])
stats_row("expense", [p["expense"] for p in valid])
stats_row("pay_sum", pay_sum)
stats_row("bliq", [p["bliq"] for p in valid])
stats_row("flow", [flow_cents(p) / 100 for p in valid])
stats_row("goal_target_sum", goal_sum)
stats_row("obl_amount", [o["amount"] for p in valid for o in p["obligations"]])
stats_row("obl_rate", [o["rate"] for p in valid for o in p["obligations"]])
stats_row("obl_payment", [o["payment"] for p in valid for o in p["obligations"]])
stats_row("goal_target", [g["target"] for p in valid for g in p["goals"]])
stats_row("goal_current", [g["current"] for p in valid for g in p["goals"]])
stats_row("r_bench", [p["r_bench"] for p in valid])

print("\n== §5.6(б) correlation matrices ==")
def pearson(xs, ys):
    m = len(xs)
    mx, my = sum(xs) / m, sum(ys) / m
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sx * sy)

def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r

cols = {
    "income": [p["income"] for p in valid],
    "expense": [p["expense"] for p in valid],
    "pay_sum": pay_sum,
    "bliq": [p["bliq"] for p in valid],
    "goal_sum": goal_sum,
}
names = list(cols)
print("Pearson:")
for a in names:
    print("  " + a + ": " + " ".join(f"{pearson(cols[a], cols[b]):+.3f}" for b in names))
print("Spearman:")
rk = {k: ranks(v) for k, v in cols.items()}
for a in names:
    print("  " + a + ": " + " ".join(f"{pearson(rk[a], rk[b]):+.3f}" for b in names))

print("\n== §5.6(в) shapes ==")
def skew_kurt(xs):
    m = st.mean(xs)
    d = [x - m for x in xs]
    m2 = sum(x * x for x in d) / len(xs)
    m3 = sum(x ** 3 for x in d) / len(xs)
    m4 = sum(x ** 4 for x in d) / len(xs)
    return m3 / m2 ** 1.5, m4 / m2 ** 2 - 3

for name in ("income", "expense", "bliq"):
    s, k = skew_kurt(cols[name])
    print(f"{name}: skew={s:.1f} excess_kurtosis={k:.1f}")

def ks_lognormal(xs, label):
    xs = [x for x in xs if x > 0]
    ls = sorted(math.log(x) for x in xs)
    m, sd = st.mean(ls), st.pstdev(ls)
    def ncdf(x):
        return 0.5 * (1 + math.erf((x - m) / (sd * math.sqrt(2))))
    D = 0.0
    m_ = len(ls)
    for i, x in enumerate(ls):
        F = ncdf(x)
        D = max(D, abs(F - (i + 1) / m_), abs(F - i / m_))
    crit = 0.886 / math.sqrt(m_)  # Lilliefors, alpha=0.05
    print(f"KS log({label}): n={m_} D={D:.4f} crit(Lilliefors 5%)={crit:.4f} "
          f"-> {'REJECT lognormal' if D > crit else 'not rejected'}")

ks_lognormal(cols["income"], "income, full")
ks_lognormal([x for x in cols["income"] if 0 < x < 3e6], "income, core<3e6")

print("\n== §5.6(д) derived diagnostics ==")
dti_b = Counter()
liq_b = Counter()
sign = Counter()
for p in valid:
    f = flow_cents(p) / 100
    sign["deficit" if f < 0 else ("zero" if f == 0 else "positive")] += 1
    if p["income"] > 0:
        d = sum(o["payment"] for o in p["obligations"]) / p["income"]
        dti_b["0" if d == 0 else "<0.3" if d < 0.3 else "0.3-0.4" if d < 0.4
              else "0.4-0.5" if d < 0.5 else "0.5-0.8" if d < 0.8 else ">0.8"] += 1
    mo = p["expense"] + sum(o["payment"] for o in p["obligations"])
    if mo > 0:
        l = p["bliq"] / mo
        liq_b["<1" if l < 1 else "1-3" if l < 3 else "3-6" if l < 6
              else "6-12" if l < 12 else ">12"] += 1
print("flow sign:", dict(sign))
print("DTI buckets:", {k: f"{v} ({v/n:.1%})" for k, v in dti_b.items()})
print("liquidity buckets:", {k: f"{v} ({v/n:.1%})" for k, v in liq_b.items()})
gr = [min(1.0, g["current"] / g["target"]) for p in valid
      for g in p["goals"] if g["target"] > 0]
gr_b = Counter("0-25%" if x < .25 else "25-50%" if x < .5 else "50-75%" if x < .75
               else "75-100%" if x < 1 else "100%" for x in gr)
print("goal readiness:", dict(gr_b))
hor_b = Counter()
for p in valid:
    for g in p["goals"]:
        if g["deadline"] is None:
            hor_b["null"] += 1
        else:
            y = (g["deadline"] - CUTOFF).days / 365.25
            hor_b["overdue" if y < 0 else "<1y" if y < 1 else "1-3y" if y < 3
                  else "3-5y" if y < 5 else "5-10y"] += 1
print("deadline horizons:", dict(hor_b))
