#!/usr/bin/env python3
"""Self-validation of the answer files (brief §4.4): format, budget
conservation, enum discipline, completeness, positional contract.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import re
from pathlib import Path

from engine_v4 import BASE_CONFIG, RecordParser, Runner

HEADER = "id,status,dom,res,debt,goal,inv,lump,confidence"
STATUSES = {"ok", "deficit", "invalid"}
DOMS = {"debt", "reserve", "goals+", "none"}
INT_RE = re.compile(r"^\d+$")


def dom_of(res: int, debt: int, goal: int, inv: int) -> str:
    buckets = [("debt", debt), ("reserve", res), ("goals+", goal + inv)]
    top = max(b[1] for b in buckets)
    if top <= 0:
        return "none"
    return next(name for name, val in buckets if val == top)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parts", nargs="+", required=True)
    ap.add_argument("--answers-dir", default=".")
    ap.add_argument("--aux-dir", default="aux")
    args = ap.parse_args()
    adir = Path(args.answers_dir)

    violations = {k: 0 for k in (
        "header", "row_count", "crlf", "spaces", "bad_status", "bad_dom",
        "bad_int", "bad_confidence", "id_mismatch", "invalid_not_zero",
        "deficit_monthly_not_zero", "budget_exceeded", "lump_exceeds_bliq",
        "dom_inconsistent", "summary_row_count", "summary_mismatch",
        "rec_row_count", "rec_id_mismatch", "rec_totals_mismatch",
        "rec_empty_verdict")}
    notes = []

    raw = open(adir / "expert_allocations_v4.csv", "rb").read()
    if b"\r" in raw:
        violations["crlf"] += 1
    if b" " in raw:
        violations["spaces"] += 1

    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if lines[0] != HEADER:
        violations["header"] += 1
    rows = [ln.split(",") for ln in lines[1:]]
    if len(rows) != 12000:
        violations["row_count"] += 1
        notes.append(f"row_count={len(rows)}")

    runner = Runner(BASE_CONFIG, args.parts)
    src_lines = runner.load_lines()
    parser = RecordParser(BASE_CONFIG)
    records = [parser.parse_line(i, ln) for i, ln in enumerate(src_lines)]

    parsed_rows = []
    for i, parts in enumerate(rows):
        if len(parts) != 9:
            violations["bad_int"] += 1
            continue
        rid, status, dom, res, debt, goal, inv, lump, conf = parts
        ok_ints = all(INT_RE.match(x) for x in (res, debt, goal, inv, lump))
        if not ok_ints:
            violations["bad_int"] += 1
            continue
        if status not in STATUSES:
            violations["bad_status"] += 1
        if dom not in DOMS:
            violations["bad_dom"] += 1
        if not (INT_RE.match(conf) and 1 <= int(conf) <= 5):
            violations["bad_confidence"] += 1
        res, debt, goal, inv, lump = map(int, (res, debt, goal, inv, lump))
        parsed_rows.append((rid, status, dom, res, debt, goal, inv, lump, int(conf)))

        rec = records[i]
        if rid != rec.rid:
            violations["id_mismatch"] += 1
        if status == "invalid":
            if any((res, debt, goal, inv, lump)) or dom != "none":
                violations["invalid_not_zero"] += 1
            continue
        if status == "deficit" and any((res, debt, goal, inv)):
            violations["deficit_monthly_not_zero"] += 1
        if rec.valid:
            pay = sum(d.payment for d in rec.debts)
            fcf = rec.income - rec.expense - pay
            budget = max(0, int(math.floor(fcf + 1e-9)))
            if res + debt + goal + inv > budget:
                violations["budget_exceeded"] += 1
            if lump > rec.bliq + 1e-6:
                violations["lump_exceeds_bliq"] += 1
        if dom != dom_of(res, debt, goal, inv):
            violations["dom_inconsistent"] += 1

    with open(adir / "summary_v4.csv", encoding="utf-8") as fh:
        s_lines = fh.read().rstrip("\n").split("\n")
    s_rows = [ln.split(",") for ln in s_lines[1:]]
    if len(s_rows) != 12000:
        violations["summary_row_count"] += 1
    for (rid, status, dom, res, debt, goal, inv, lump, _conf), srow in zip(
            parsed_rows, s_rows):
        if (srow[0] != rid or srow[1] != status or srow[2] != dom
                or srow[13:18] != [str(res), str(debt), str(goal), str(inv), str(lump)]):
            violations["summary_mismatch"] += 1

    n_rec = 0
    with gzip.open(adir / "recommendations_v4.jsonl.gz", "rt",
                   encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            obj = json.loads(line)
            n_rec += 1
            rid, status, dom, res, debt, goal, inv, lump, _conf = parsed_rows[i]
            if obj["id"] != rid:
                violations["rec_id_mismatch"] += 1
            if (obj["totals"]["monthly_total"] != res + debt + goal + inv
                    or obj["totals"]["lump_total"] != lump
                    or obj["status"] != status or obj["dom"] != dom):
                violations["rec_totals_mismatch"] += 1
            if not obj.get("verdict"):
                violations["rec_empty_verdict"] += 1
    if n_rec != 12000:
        violations["rec_row_count"] += 1

    total = sum(violations.values())
    out = {"violations": violations, "total_violations": total, "notes": notes}
    aux = Path(args.aux_dir)
    aux.mkdir(parents=True, exist_ok=True)
    with open(aux / "validation.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
