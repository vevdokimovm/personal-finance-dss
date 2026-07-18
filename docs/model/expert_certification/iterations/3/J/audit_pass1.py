"""Statistical audit of expert_portraits_v3 for dataset_review.md."""
import json
import math
import statistics as st
from collections import Counter, defaultdict
from datetime import date

from engine import validate, flow_cents

CUTOFF = date(2026, 7, 16)


def q(xs, ps=(0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1)):
    xs = sorted(xs)
    n = len(xs)
    return {p: xs[min(n - 1, int(p * (n - 1)))] for p in ps}


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(xs), rank(ys))


lines, raws = [], []
for i in range(1, 5):
    with open(f"part{i}.jsonl") as f:
        for raw in f:
            rec = json.loads(raw)
            if rec.get("__meta__"):
                continue
            lines.append(rec)
            raws.append(raw)

valid = []
for rec in lines:
    p = validate(rec)
    if p:
        p["id"] = rec["id"]
        valid.append(p)

print(f"lines={len(lines)} valid={len(valid)} invalid={len(lines)-len(valid)}")

inc = [p["income"] for p in valid]
exp = [p["expense"] for p in valid]
bq = [p["bliq"] for p in valid]
rb = [p["r_bench"] for p in valid]
fl = [flow_cents(p) / 100 for p in valid]
print("\n== (а) дескриптивы ==")
for name, xs in [("income", inc), ("expense", exp), ("bliq", bq),
                 ("flow", fl), ("r_bench", rb)]:
    print(f"{name}: mean={st.mean(xs):.1f} med={st.median(xs):.1f} "
          f"sd={st.pstdev(xs):.1f} q={ {k: round(v,3) for k,v in q(xs).items()} }")

print("risk:", dict(Counter(p["risk"] for p in valid)))
print("n_debts:", dict(Counter(len(p["obligations"]) for p in valid)))
print("n_goals:", dict(Counter(len(p["goals"]) for p in valid)))

print("\n== (б) распределения ==")
neg = sum(1 for f in fl if f < 0)
zero = sum(1 for f in fl if f == 0)
print(f"deficit share: {neg}/{len(fl)} = {neg/len(fl):.1%}; flow==0: {zero}")
ei = [e / i for e, i in zip(exp, inc) if i > 0]
print("expense/income ratio q:", {k: round(v, 3) for k, v in q(ei).items()})
zero_inc = sum(1 for x in inc if x == 0)
zero_bliq = sum(1 for x in bq if x == 0)
print(f"income==0: {zero_inc}, bliq==0: {zero_bliq}")
li = [math.log10(x) for x in inc if x > 0]
print(f"log10(income): mean={st.mean(li):.3f} sd={st.pstdev(li):.3f} "
      f"skew_raw_income={(st.mean(inc)-st.median(inc))/st.pstdev(inc):.3f}")

print("\n== (в) корреляции ==")
pairs = [("income~expense", inc, exp), ("income~bliq", inc, bq),
         ("income~flow", inc, fl),
         ("risk~bliq", [p["risk"] for p in valid], bq),
         ("risk~r_bench", [p["risk"] for p in valid], rb),
         ("income~r_bench", inc, rb)]
for name, a, b in pairs:
    print(f"{name}: pearson={pearson(a,b):.3f} spearman={spearman(a,b):.3f}")
dti = [(sum(o["payment"] for o in p["obligations"]) / p["income"])
       for p in valid if p["income"] > 0]
print("DTI q:", {k: round(v, 3) for k, v in q(dti).items()})
print(f"DTI>0.4: {sum(1 for d in dti if d>0.4)/len(dti):.1%}; "
      f"DTI>0.8: {sum(1 for d in dti if d>0.8)/len(dti):.1%}")

print("\n== (г) реалистичность кредитов ==")
rate_by_name = defaultdict(list)
amt_by_name = defaultdict(list)
terms = []
nonamort = 0
tot_debts = 0
for p in valid:
    for o in p["obligations"]:
        tot_debts += 1
        # name lost in normalize; re-read below
for rec in lines:
    p = validate(rec)
    if not p:
        continue
    for o in rec["obligations"]:
        nm = str(o.get("name"))
        rate_by_name[nm].append(o["interest_rate"])
        amt_by_name[nm].append(o["amount"])
        A, r, pay = o["amount"], o["interest_rate"], o["monthly_payment"]
        if A > 0 and pay > 0:
            i = r / 12
            if i == 0:
                terms.append(A / pay)
            elif pay <= A * i:
                nonamort += 1
            else:
                terms.append(-math.log(1 - A * i / pay) / math.log(1 + i))
print(f"total debts: {tot_debts}, non-amortizing (pay<=interest): {nonamort} "
      f"({nonamort/tot_debts:.1%})")
print("implied term (months) q:", {k: round(v, 1) for k, v in q(terms).items()})
print(f"term>360m: {sum(1 for t in terms if t>360)/len(terms):.1%}")
for nm in sorted(rate_by_name, key=lambda n: -len(rate_by_name[n])):
    rs = rate_by_name[nm]
    am = amt_by_name[nm]
    print(f"  {nm}: n={len(rs)} rate med={st.median(rs):.3f} "
          f"[{min(rs):.3f}..{max(rs):.3f}] amount med={st.median(am):,.0f}")
mort2 = sum(1 for p in valid if sum(
    1 for rec in [None]) )  # placeholder
mort_cnt = 0
for rec in lines:
    p = validate(rec)
    if p and sum(1 for o in rec["obligations"]
                 if str(o.get("name")) == "Ипотека") >= 2:
        mort_cnt += 1
print(f"portraits with 2+ mortgages: {mort_cnt}")

print("\n== (г2) реалистичность целей ==")
tgt, hor, prog = [], [], []
overdue = 0
tot_goals = 0
unreach = 0
for p in valid:
    P = 0.0
    for g in p["goals"]:
        tot_goals += 1
        tgt.append(g["target"])
        if g["target"] > 0:
            prog.append(min(1.0, g["current"] / g["target"]))
        if g["deadline"]:
            d = (g["deadline"] - CUTOFF).days
            hor.append(d / 365.25)
            if d < 0:
                overdue += 1
            m = max(1, math.ceil(d / 30.4375)) if d > 0 else 1
            P += max(0.0, g["target"] - g["current"]) / m
    f = flow_cents(p) / 100
    if P > max(0.0, f):
        unreach += 1
print(f"goals total: {tot_goals}; overdue deadline: {overdue} "
      f"({overdue/max(1,tot_goals):.1%} of goals)")
print("target q:", {k: round(v) for k, v in q(tgt).items()})
print("horizon years q:", {k: round(v, 2) for k, v in q(hor).items()})
print("progress q:", {k: round(v, 2) for k, v in q(prog).items()})
print(f"portraits where dated-goal pressure > flow: {unreach}/{len(valid)} "
      f"= {unreach/len(valid):.1%}")
tin = [t / (i * 12) for t, i in zip(
    [g["target"] for p in valid for g in p["goals"]],
    [p["income"] for p in valid for g in p["goals"]]) if i > 0]
print("target / annual income q:", {k: round(v, 2) for k, v in q(tin).items()})

print("\n== (д) граничные кейсы ==")
print(f"flow==0 exactly: {zero}")
exact_dti = sum(1 for p in valid if p["income"] > 0 and abs(
    sum(o["payment"] for o in p["obligations"]) / p["income"] - 0.4) < 1e-9)
print(f"DTI == 0.40 exactly: {exact_dti}")
bmo = 0
for p in valid:
    mo = p["expense"] + sum(o["payment"] for o in p["obligations"])
    if mo > 0 and abs(p["bliq"] / mo - round(p["bliq"] / mo)) < 1e-9 and p["bliq"] > 0:
        bmo += 1
print(f"bliq == integer x MO exactly: {bmo}")
rate59 = sum(1 for p in valid for o in p["obligations"] if o["rate"] >= 0.55)
print(f"debts with rate>=55%: {rate59}")
print(f"max income: {max(inc):,.0f}; max bliq: {max(bq):,.0f}; "
      f"min positive income: {min(x for x in inc if x>0):,.0f}")
big = sorted(valid, key=lambda p: -p["income"])[:3]
print("top incomes:", [(p["id"], round(p["income"])) for p in big])

print("\n== (е) целостность ==")
ids = Counter(rec.get("id") for rec in lines)
dups = {k: v for k, v in ids.items() if v > 1}
allspace = {f"SP3-{i:05d}" for i in range(12000)}
missing = allspace - set(ids)
print(f"unique ids: {len(ids)}, dup ids: {len(dups)}, "
      f"missing from SP3-00000..11999: {len(missing)}")
print("missing sample:", sorted(missing)[:5])
# where do dup copies sit
pos = defaultdict(list)
for n, rec in enumerate(lines):
    if rec.get("id") in dups:
        pos[rec["id"]].append(n)
gaps = [b - a for a, b in (v for v in pos.values() if len(v) == 2)]
print("dup pair index gaps q:", {k: v for k, v in q(gaps, (0, .5, 1)).items()})
# defect date variants
badd = Counter()
for rec in lines:
    for g in rec.get("goals", []) if isinstance(rec.get("goals"), list) else []:
        d = g.get("deadline") if isinstance(g, dict) else None
        if isinstance(d, str):
            try:
                date.fromisoformat(d)
            except Exception:
                badd[d] += 1
print("bad date variants:", dict(badd))
