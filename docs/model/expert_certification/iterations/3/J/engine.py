"""Independent expert allocation engine, round 3.

Implements expert_methodology_v3.md exactly. One output row per input line.
"""
import csv
import gzip
import json
import math
import re
import time
from datetime import date

CUTOFF = date(2026, 7, 16)
PARTS = [f"part{i}.jsonl" for i in range(1, 5)]

RESERVE_MONTHS = {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}
INV_SHARE = {1: 0.10, 2: 0.25, 3: 0.40, 4: 0.60, 5: 0.75}
EXPENSIVE_SPREAD = 0.015
TOXIC_RATE = 0.30
RATE_MAX = 3.0
LUMP_PLACEMENT_MIN = 50_000.0
LUMP_PLACEMENT_MO_SHARE = 0.2


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) \
        and math.isfinite(v)


def parse_deadline(s):
    """Return date or raise ValueError. None stays None."""
    if s is None:
        return None
    if not isinstance(s, str):
        raise ValueError("deadline type")
    return date.fromisoformat(s)


def months_left(d):
    days = (d - CUTOFF).days
    if days <= 0:
        return 1
    return max(1, math.ceil(days / 30.4375))


def validate(rec):
    """Return normalized dict or None if defective."""
    if not isinstance(rec, dict):
        return None
    for k in ("id", "income_total", "expense_total", "obligations",
              "goals", "bliq", "r_bench", "risk_tolerance"):
        if k not in rec:
            return None
    for k in ("income_total", "expense_total", "bliq", "r_bench"):
        if not is_num(rec[k]) or rec[k] < 0:
            return None
    if rec["r_bench"] > RATE_MAX:
        return None
    rt = rec["risk_tolerance"]
    if not is_num(rt) or rt != int(rt) or int(rt) not in (1, 2, 3, 4, 5):
        return None
    if not isinstance(rec["obligations"], list) or not isinstance(rec["goals"], list):
        return None
    obligations = []
    for o in rec["obligations"]:
        if not isinstance(o, dict):
            return None
        for k in ("amount", "interest_rate", "monthly_payment"):
            if k not in o or not is_num(o[k]) or o[k] < 0:
                return None
        if o["interest_rate"] > RATE_MAX:
            return None
        obligations.append({
            "amount": float(o["amount"]),
            "rate": float(o["interest_rate"]),
            "payment": float(o["monthly_payment"]),
        })
    goals = []
    for g in rec["goals"]:
        if not isinstance(g, dict):
            return None
        for k in ("target_amount", "current_amount"):
            if k not in g or not is_num(g[k]) or g[k] < 0:
                return None
        try:
            dl = parse_deadline(g.get("deadline"))
        except ValueError:
            return None
        goals.append({
            "target": float(g["target_amount"]),
            "current": float(g["current_amount"]),
            "deadline": dl,
        })
    return {
        "income": float(rec["income_total"]),
        "expense": float(rec["expense_total"]),
        "bliq": float(rec["bliq"]),
        "r_bench": float(rec["r_bench"]),
        "risk": int(rt),
        "obligations": obligations,
        "goals": goals,
    }


def deficit_lump(p):
    """Full debt closures from bliq keeping >= 1x expense_total liquidity."""
    avail = p["bliq"]
    floor = p["expense"]
    debts = sorted(
        (o for o in p["obligations"] if o["amount"] > 0),
        key=lambda o: o["payment"] / o["amount"],
        reverse=True,
    )
    lump = 0.0
    for o in debts:
        if avail - o["amount"] >= floor:
            lump += o["amount"]
            avail -= o["amount"]
    return lump


def ok_lumps(p):
    """Return (lump_total, surviving_obligations, surviving_goals, bliq_after)."""
    mo = p["expense"] + sum(o["payment"] for o in p["obligations"])
    target = RESERVE_MONTHS[p["risk"]] * mo
    bliq = p["bliq"]
    lump = 0.0
    survivors = [dict(o) for o in p["obligations"]]

    # 1. Toxic debts from funds above the 1xMO emergency floor (partial OK).
    avail = max(0.0, bliq - mo)
    for o in sorted(survivors, key=lambda x: x["rate"], reverse=True):
        if o["rate"] >= TOXIC_RATE and o["amount"] > 0 and avail > 0:
            pay = min(avail, o["amount"])
            o["amount"] -= pay
            avail -= pay
            bliq -= pay
            lump += pay

    # 2. Expensive (non-toxic) debts: full closure from excess above target.
    excess = max(0.0, bliq - target)
    exp_thr = p["r_bench"] + EXPENSIVE_SPREAD
    for o in sorted(survivors, key=lambda x: x["rate"], reverse=True):
        if TOXIC_RATE > o["rate"] >= exp_thr and 0 < o["amount"] <= excess:
            excess -= o["amount"]
            bliq -= o["amount"]
            lump += o["amount"]
            o["amount"] = 0.0

    # 3. Dated goals: full closure from remaining excess, nearest deadline first.
    goals = [dict(g) for g in p["goals"]]
    dated = sorted(
        (g for g in goals if g["deadline"] is not None
         and g["target"] - g["current"] > 0),
        key=lambda g: (months_left(g["deadline"]), g["target"] - g["current"]),
    )
    for g in dated:
        need = g["target"] - g["current"]
        if 0 < need <= excess:
            excess -= need
            bliq -= need
            lump += need
            g["current"] = g["target"]

    # 4. Placement of remaining excess above target reserve.
    if excess >= max(LUMP_PLACEMENT_MIN, LUMP_PLACEMENT_MO_SHARE * mo):
        lump += excess
        bliq -= excess

    survivors = [o for o in survivors]
    return lump, survivors, goals, bliq


def flow_cents(p):
    """Free monthly flow in integer kopecks — kills binary-float noise."""
    return (round(p["income"] * 100) - round(p["expense"] * 100)
            - sum(round(o["payment"] * 100) for o in p["obligations"]))


def monthly_split(p, flow, obligations, goals, bliq):
    """Split flow into (res, debt, goal, inv) per methodology tables."""
    if flow <= 0:
        return 0, 0, 0, 0
    mo = p["expense"] + sum(o["payment"] for o in obligations)
    target = RESERVE_MONTHS[p["risk"]] * mo
    exp_thr = p["r_bench"] + EXPENSIVE_SPREAD
    live = [o for o in obligations if o["amount"] > 0]
    has_toxic = any(o["rate"] >= TOXIC_RATE for o in live)
    has_exp = any(o["rate"] >= exp_thr for o in live)

    if bliq < mo:
        state = 0
    elif bliq < target:
        state = 1
    else:
        state = 2

    if state == 0:
        if has_toxic:
            f_res, f_debt, f_tier = 0.50, 0.50, 0.0
        elif has_exp:
            f_res, f_debt, f_tier = 0.70, 0.30, 0.0
        else:
            f_res, f_debt, f_tier = 1.0, 0.0, 0.0
    elif state == 1:
        if has_toxic:
            f_res, f_debt, f_tier = 0.30, 0.60, 0.10
        elif has_exp:
            f_res, f_debt, f_tier = 0.40, 0.40, 0.20
        else:
            f_res, f_debt, f_tier = 0.50, 0.0, 0.50
    else:
        if has_toxic:
            f_res, f_debt, f_tier = 0.0, 0.80, 0.20
        elif has_exp:
            f_res, f_debt, f_tier = 0.0, 0.60, 0.40
        else:
            f_res, f_debt, f_tier = 0.0, 0.0, 1.0

    res_f = flow * f_res
    debt_f = flow * f_debt
    tier = flow * f_tier

    active = [g for g in goals if g["target"] - g["current"] > 0]
    dated = [g for g in active if g["deadline"] is not None]
    perpetual = [g for g in active if g["deadline"] is None]
    pressure = sum(
        (g["target"] - g["current"]) / months_left(g["deadline"])
        for g in dated
    )
    goal_f = min(tier, pressure)
    rest = tier - goal_f
    inv_f = 0.0
    if rest > 0:
        if perpetual:
            inv_f = rest * INV_SHARE[p["risk"]]
            goal_f += rest - inv_f
        else:
            inv_f = rest
    if not active:
        inv_f += goal_f
        goal_f = 0.0

    vals = [res_f, debt_f, goal_f, inv_f]
    ints = [int(v) for v in vals]
    budget = int(flow)
    dust = budget - sum(ints)
    if dust > 0:
        idx = max(range(4), key=lambda i: vals[i])
        ints[idx] += dust
    while sum(ints) > budget:
        idx = max(range(4), key=lambda i: ints[i])
        ints[idx] -= sum(ints) - budget
    return tuple(ints)


def dominant(res, debt, goal, inv):
    goals_plus = goal + inv
    if res == 0 and debt == 0 and goals_plus == 0:
        return "none"
    best = max(debt, res, goals_plus)
    if debt == best:
        return "debt"
    if res == best:
        return "reserve"
    return "goals+"


def salvage_id(raw_line):
    m = re.search(r'"id"\s*:\s*"([^"]*)"', raw_line)
    return m.group(1) if m else "UNKNOWN"


def csv_id(rid):
    if any(c in rid for c in ',"\n'):
        return '"' + rid.replace('"', '""') + '"'
    return rid


def process_line(raw_line):
    try:
        rec = json.loads(raw_line)
    except Exception:
        return (salvage_id(raw_line), "invalid", "none", 0, 0, 0, 0, 0)
    if isinstance(rec, dict) and rec.get("__meta__"):
        return None
    rid = rec.get("id") if isinstance(rec, dict) else None
    rid = str(rid) if isinstance(rid, str) else salvage_id(raw_line)
    p = validate(rec)
    if p is None:
        return (rid, "invalid", "none", 0, 0, 0, 0, 0)
    cents = flow_cents(p)
    if cents < 0:
        lump = deficit_lump(p)
        return (rid, "deficit", "none", 0, 0, 0, 0, int(lump))
    flow_rub = cents // 100
    lump, obligations, goals, bliq = ok_lumps(p)
    res, debt, goal, inv = monthly_split(p, flow_rub, obligations, goals, bliq)
    dom = dominant(res, debt, goal, inv)
    return (rid, "ok", dom, res, debt, goal, inv, int(lump))


def main():
    t0 = time.time()
    rows = []
    for part in PARTS:
        with open(part) as f:
            for raw in f:
                out = process_line(raw)
                if out is not None:
                    rows.append(out)
    assert len(rows) == 12000, len(rows)
    with open("/mnt/user-data/outputs/expert_allocations_v3.csv", "w", newline="") as f:
        f.write("id,status,dom,res,debt,goal,inv,lump\n")
        for r in rows:
            f.write(f"{csv_id(r[0])},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]},{r[7]}\n")
    dt = time.time() - t0
    from collections import Counter
    st = Counter(r[1] for r in rows)
    dm = Counter(r[2] for r in rows)
    lumps = [r[7] for r in rows if r[7] > 0]
    print(f"rows: {len(rows)}  time: {dt:.1f}s")
    print("status:", dict(st))
    print("dom:", dict(dm))
    print(f"lump>0: {len(lumps)}, median lump: {sorted(lumps)[len(lumps)//2] if lumps else 0}")


if __name__ == "__main__":
    main()
