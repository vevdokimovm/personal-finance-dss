#!/usr/bin/env python3
"""Independent expert allocator — portraits v3 (12,000 records).
Implements rules fixed in expert_methodology_v3.md BEFORE processing."""
import csv, gzip, json, math, time
from datetime import datetime, date
from collections import Counter

SNAP = date(2026, 7, 16)
K_CUSHION = {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}
CHEAP_SP, TOXIC_SP = 0.02, 0.10
MINBUF_M, DEF_BUF_M = 1.0, 2.0
NEAR_M, PLACE_MIN, RATE_MAX = 3, 50_000, 3.0
GOAL_SHARE_PRE = 0.4
TOX_RES_SHARE, EXP_RES_SHARE = 0.3, 0.5

FILES = [f"/mnt/user-data/uploads/expert_portraits_v3_part{i}_jsonl.gz" for i in (1, 2, 3, 4)]
OUT_CSV = "/home/claude/expert_answers_v3.csv"
DUMP_VALID = "/home/claude/valid_dump.jsonl"
DUMP_DEBTS = "/home/claude/debts_dump.jsonl"
DUMP_GOALS = "/home/claude/goals_dump.jsonl"
RUN_INFO = "/home/claude/run_info.json"


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def pdate(s):
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None


def validate(o):
    """-> (parsed | None, reason)"""
    if not isinstance(o, dict):
        return None, "not_object"
    for f in ("id", "income_total", "expense_total", "obligations", "goals",
              "bliq", "r_bench", "risk_tolerance"):
        if f not in o:
            return None, f"missing:{f}"
    if not isinstance(o["id"], str) or not o["id"]:
        return None, "bad_id"
    for f in ("income_total", "expense_total", "bliq"):
        if not is_num(o[f]):
            return None, f"type:{f}"
        if o[f] < 0:
            return None, f"neg:{f}"
    if not is_num(o["r_bench"]):
        return None, "type:r_bench"
    if o["r_bench"] < 0:
        return None, "neg:r_bench"
    rt = o["risk_tolerance"]
    if isinstance(rt, bool):
        return None, "type:risk_tolerance"
    if isinstance(rt, float):
        if not rt.is_integer():
            return None, "type:risk_tolerance"
        rt = int(rt)
    if not isinstance(rt, int):
        return None, "type:risk_tolerance"
    if not 1 <= rt <= 5:
        return None, "range:risk_tolerance"
    if not isinstance(o["obligations"], list):
        return None, "type:obligations"
    if not isinstance(o["goals"], list):
        return None, "type:goals"
    debts = []
    for d in o["obligations"]:
        if not isinstance(d, dict):
            return None, "obligation:not_object"
        for f in ("name", "amount", "interest_rate", "monthly_payment"):
            if f not in d:
                return None, f"obligation:missing:{f}"
        if not isinstance(d["name"], str):
            return None, "obligation:type:name"
        for f in ("amount", "interest_rate", "monthly_payment"):
            if not is_num(d[f]):
                return None, f"obligation:type:{f}"
            if d[f] < 0:
                return None, f"obligation:neg:{f}"
        if d["interest_rate"] > RATE_MAX:
            return None, "obligation:rate_gt_300pct"
        debts.append({"name": d["name"], "amount": float(d["amount"]),
                      "rate": float(d["interest_rate"]), "pay": float(d["monthly_payment"])})
    goals = []
    for g in o["goals"]:
        if not isinstance(g, dict):
            return None, "goal:not_object"
        for f in ("name", "target_amount", "current_amount", "deadline"):
            if f not in g:
                return None, f"goal:missing:{f}"
        if not isinstance(g["name"], str):
            return None, "goal:type:name"
        for f in ("target_amount", "current_amount"):
            if not is_num(g[f]):
                return None, f"goal:type:{f}"
            if g[f] < 0:
                return None, f"goal:neg:{f}"
        dl, dd = g["deadline"], None
        if dl is not None:
            if not isinstance(dl, str):
                return None, "goal:type:deadline"
            dd = pdate(dl)
            if dd is None:
                return None, "goal:bad_date"
        goals.append({"name": g["name"], "target": float(g["target_amount"]),
                      "cur": float(g["current_amount"]), "dl": dd})
    return {"id": o["id"], "inc": float(o["income_total"]), "exp": float(o["expense_total"]),
            "debts": debts, "goals": goals, "bliq": float(o["bliq"]),
            "rb": float(o["r_bench"]), "rt": rt}, "ok"


def classify(rate, rb):
    if rate >= rb + TOXIC_SP:
        return 2  # toxic
    if rate > rb + CHEAP_SP:
        return 1  # expensive
    return 0      # cheap


def months_left(dl):
    d = (dl - SNAP).days
    return 0 if d <= 0 else max(1, math.ceil(d / 30.44))


def solve(p):
    inc, exp, bliq, rb, rt = p["inc"], p["exp"], p["bliq"], p["rb"], p["rt"]
    debts = [dict(d) for d in p["debts"]]
    goals = [dict(g) for g in p["goals"]]
    pay0 = sum(d["pay"] for d in debts)
    F = inc - exp - pay0
    needs0 = exp + pay0
    status = "ok" if F >= 0 else "deficit"
    minbuf0 = MINBUF_M * needs0
    target0 = K_CUSHION[rt] * needs0
    lump = 0.0

    def close_check(d):
        if d["amount"] <= 1e-6:
            d["amount"] = 0.0
            d["pay"] = 0.0

    if status == "ok":
        pool = max(0.0, bliq - minbuf0)
        for d in sorted(debts, key=lambda x: -x["rate"]):
            if classify(d["rate"], rb) != 2 or pool <= 0:
                continue
            pay = min(d["amount"], pool)
            d["amount"] -= pay; lump += pay; pool -= pay
            close_check(d)
        pool = max(0.0, bliq - lump - target0)
        for d in sorted(debts, key=lambda x: -x["rate"]):
            if classify(d["rate"], rb) != 1 or pool <= 0:
                continue
            pay = min(d["amount"], pool)
            d["amount"] -= pay; lump += pay; pool -= pay
            close_check(d)
        pool = max(0.0, bliq - lump - target0)
        dated = [g for g in goals if g["dl"] is not None and g["target"] - g["cur"] > 1e-6]
        for g in sorted(dated, key=lambda g: g["dl"]):
            if pool <= 0:
                break
            if months_left(g["dl"]) <= NEAR_M:
                pay = min(g["target"] - g["cur"], pool)
                g["cur"] += pay; lump += pay; pool -= pay
        excess = bliq - lump - target0
        if excess >= PLACE_MIN:
            lump += excess
    else:
        pool = max(0.0, bliq - minbuf0)
        for d in sorted(debts, key=lambda x: -x["rate"]):
            if classify(d["rate"], rb) != 2 or pool <= 0:
                continue
            pay = min(d["amount"], pool)
            d["amount"] -= pay; lump += pay; pool -= pay
            close_check(d)

        def flow():
            return inc - exp - sum(d["pay"] for d in debts)

        pool = max(0.0, bliq - lump - DEF_BUF_M * needs0)
        # full closures, max freed payment per ruble of principal
        for d in sorted([d for d in debts if d["amount"] > 0],
                        key=lambda x: -(x["pay"] / x["amount"])):
            if flow() >= 0:
                break
            if d["amount"] <= pool:
                pool -= d["amount"]; lump += d["amount"]
                d["amount"] = 0.0; d["pay"] = 0.0

    # ---- monthly plan on post-lump state ----
    res = debtA = goal = inv = 0.0
    if F > 0:
        pay_p = sum(d["pay"] for d in debts)
        needs_p = exp + pay_p
        bliq_p = max(0.0, bliq - lump)
        minbuf = MINBUF_M * needs_p
        target = K_CUSHION[rt] * needs_p
        rem = F
        tox = sum(d["amount"] for d in debts if classify(d["rate"], rb) == 2)
        expd = sum(d["amount"] for d in debts if classify(d["rate"], rb) == 1)
        if tox > 1e-6 and rem > 0:
            gap_min = max(0.0, minbuf - bliq_p)
            if gap_min > 0:
                ra = min(TOX_RES_SHARE * rem, gap_min)
                res += ra; rem -= ra
            da = min(rem, tox)
            debtA += da; rem -= da; tox -= da
        if expd > 1e-6 and rem > 0 and tox <= 1e-6:
            gap_t = max(0.0, target - (bliq_p + res))
            if gap_t > 0:
                rb_ = min(EXP_RES_SHARE * rem, gap_t)
                res += rb_; rem -= rb_
            db = min(rem, expd)
            debtA += db; rem -= db; expd -= db
        if rem > 0 and tox <= 1e-6 and expd <= 1e-6:
            gneed = 0.0
            for g in goals:
                if g["dl"] is None:
                    continue
                left = g["target"] - g["cur"]
                if left <= 1e-6:
                    continue
                gneed += left / max(1, months_left(g["dl"]))
            gap = max(0.0, target - (bliq_p + res))
            if gap > 0:
                ga = min(gneed, GOAL_SHARE_PRE * rem)
                goal += ga; gneed -= ga
                rc = min(rem - ga, gap)
                res += rc
                rem -= ga + rc
            if rem > 0:
                gd = min(rem, gneed)
                goal += gd; rem -= gd
                inv += rem; rem = 0.0

    Fi = int(F) if F > 0 else 0
    b = [int(res), int(debtA), int(goal), int(inv)]
    s = sum(b)
    if s > Fi:
        j = max(range(4), key=lambda i: b[i]); b[j] -= s - Fi
    elif Fi > s and s > 0:
        j = max(range(4), key=lambda i: b[i]); b[j] += Fi - s
    if status == "deficit":
        b = [0, 0, 0, 0]
    gp = b[2] + b[3]
    if status == "deficit" or (b[0] == 0 and b[1] == 0 and gp == 0):
        dom = "none"
    elif b[1] >= b[0] and b[1] >= gp:
        dom = "debt"
    elif b[0] >= gp:
        dom = "reserve"
    else:
        dom = "goals+"
    return status, dom, b[0], b[1], b[2], b[3], int(round(lump)), F


def main():
    t0 = time.time()
    rows, census, ids = [], Counter(), Counter()
    metas, per_part = [], {}
    fv = open(DUMP_VALID, "w", encoding="utf-8")
    fd = open(DUMP_DEBTS, "w", encoding="utf-8")
    fg = open(DUMP_GOALS, "w", encoding="utf-8")
    verify = []  # (F, res, debt, goal, inv, status)
    for path in FILES:
        n_data = 0
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    o = json.loads(s)
                except Exception:
                    rows.append(["", "invalid", "none", 0, 0, 0, 0, 0])
                    census["json_parse"] += 1
                    n_data += 1
                    continue
                if isinstance(o, dict) and o.get("__meta__") is True:
                    metas.append(o)
                    continue
                n_data += 1
                p, reason = validate(o)
                if p is None:
                    v = o.get("id") if isinstance(o, dict) else None
                    rid = v if isinstance(v, str) else ("" if v is None else str(v))
                    census[reason] += 1
                    rows.append([rid, "invalid", "none", 0, 0, 0, 0, 0])
                    continue
                census["valid"] += 1
                ids[p["id"]] += 1
                st, dom, r_, d_, g_, i_, l_, F = solve(p)
                rows.append([p["id"], st, dom, r_, d_, g_, i_, l_])
                verify.append((F, r_, d_, g_, i_, st))
                pay0 = sum(d["pay"] for d in p["debts"])
                needs0 = p["exp"] + pay0
                fv.write(json.dumps({
                    "id": p["id"], "inc": p["inc"], "exp": p["exp"], "F": F,
                    "bliq": p["bliq"], "rb": p["rb"], "rt": p["rt"],
                    "n_debts": len(p["debts"]),
                    "debt_total": sum(d["amount"] for d in p["debts"]),
                    "pay_total": pay0, "needs": needs0,
                    "max_rate": max((d["rate"] for d in p["debts"]), default=None),
                    "has_tox": any(classify(d["rate"], p["rb"]) == 2 for d in p["debts"]),
                    "has_exp": any(classify(d["rate"], p["rb"]) == 1 for d in p["debts"]),
                    "n_goals": len(p["goals"]),
                    "n_dated": sum(1 for g in p["goals"] if g["dl"] is not None),
                    "n_overdue": sum(1 for g in p["goals"]
                                     if g["dl"] is not None and (g["dl"] - SNAP).days <= 0
                                     and g["target"] - g["cur"] > 1e-6),
                    "goal_target_sum": sum(g["target"] for g in p["goals"]),
                    "dec": {"status": st, "dom": dom, "res": r_, "debt": d_,
                            "goal": g_, "inv": i_, "lump": l_},
                }, ensure_ascii=False) + "\n")
                for d in p["debts"]:
                    r_m = d["rate"] / 12
                    i_m = d["amount"] * r_m
                    term = None
                    if d["pay"] > i_m and d["pay"] > 0 and r_m > 0:
                        term = math.log(d["pay"] / (d["pay"] - i_m)) / math.log(1 + r_m)
                    elif r_m == 0 and d["pay"] > 0:
                        term = d["amount"] / d["pay"]
                    fd.write(json.dumps({
                        "name": d["name"], "rate": d["rate"], "amount": d["amount"],
                        "pay": d["pay"], "rb": p["rb"],
                        "cls": classify(d["rate"], p["rb"]),
                        "nonamort": bool(d["pay"] <= i_m), "term_m": term,
                    }, ensure_ascii=False) + "\n")
                for g in p["goals"]:
                    fg.write(json.dumps({
                        "name": g["name"], "target": g["target"], "cur": g["cur"],
                        "dated": g["dl"] is not None,
                        "ml": months_left(g["dl"]) if g["dl"] else None,
                        "overdue": bool(g["dl"] is not None and (g["dl"] - SNAP).days <= 0),
                    }, ensure_ascii=False) + "\n")
        per_part[path.split("/")[-1]] = n_data
    for h in (fv, fd, fg):
        h.close()

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "status", "dom", "res", "debt", "goal", "inv", "lump"])
        w.writerows(rows)

    # ---- verification ----
    assert len(rows) == 12000, f"rows={len(rows)}"
    bad = 0
    for F, r_, d_, g_, i_, st in verify:
        cap = int(F) if F > 0 else 0
        if st == "ok":
            assert r_ + d_ + g_ + i_ <= cap and min(r_, d_, g_, i_) >= 0
        else:
            assert r_ == d_ == g_ == i_ == 0
    for row in rows:
        assert row[1] in ("ok", "deficit", "invalid") and row[2] in ("debt", "reserve", "goals+", "none")
        assert all(isinstance(x, int) and x >= 0 for x in row[3:])
    dups = {k: v for k, v in ids.items() if v > 1}
    expected = {f"SP3-{i:05d}" for i in range(12000)}
    missing = expected - set(ids)
    status_c = Counter(r[1] for r in rows)
    dom_c = Counter(r[2] for r in rows)
    lump_pos = sum(1 for r in rows if r[7] > 0)
    info = {"elapsed_s": round(time.time() - t0, 2), "per_part": per_part,
            "metas": metas, "census": dict(census), "dups": dups,
            "n_missing_expected_ids": len(missing),
            "missing_sample": sorted(missing)[:20],
            "status": dict(status_c), "dom": dict(dom_c),
            "lump_gt0": lump_pos}
    with open(RUN_INFO, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
