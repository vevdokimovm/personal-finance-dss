"""Self-validation of round-4 answers: format, enums, budget, completeness."""

from __future__ import annotations

import csv
import gzip
import json
import math

from engine_v4 import Validator, read_lines

EXPECTED_HEADER = ["id", "status", "dom", "res", "debt", "goal", "inv",
                   "lump", "confidence"]
STATUS = {"ok", "deficit", "invalid"}
DOM = {"debt", "reserve", "goals+", "none"}


def main() -> None:
    lines = read_lines([f"part{i}.jsonl.gz" for i in (1, 2, 3, 4)])
    validator = Validator()

    raw = open("expert_allocations_v4.csv", "rb").read()
    crlf = raw.count(b"\r\n")
    spaces = raw.count(b" ")
    rows = list(csv.reader(raw.decode("utf-8").splitlines()))
    header, data = rows[0], rows[1:]

    problems: list[str] = []
    if header != EXPECTED_HEADER:
        problems.append(f"header mismatch: {header}")
    if crlf:
        problems.append(f"CRLF endings: {crlf}")
    if spaces:
        problems.append(f"spaces inside CSV: {spaces}")
    if len(data) != len(lines):
        problems.append(f"row count {len(data)} != input {len(lines)}")

    budget_viol = lump_viol = enum_viol = int_viol = inv_shape_viol = 0
    id_mismatch = 0
    for i, (line, row) in enumerate(zip(lines, data)):
        rid, status, dom = row[0], row[1], row[2]
        try:
            res, debt, goal, inv, lump = (int(x) for x in row[3:8])
            conf = int(row[8])
        except ValueError:
            int_viol += 1
            continue
        if status not in STATUS or dom not in DOM or not 1 <= conf <= 5:
            enum_viol += 1
        if min(res, debt, goal, inv, lump) < 0:
            int_viol += 1
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            rec = None
        defect = validator.check(rec) if rec is not None else "unparseable"
        if defect:
            if (status != "invalid" or dom != "none"
                    or any((res, debt, goal, inv, lump))):
                inv_shape_viol += 1
            continue
        if isinstance(rec.get("id"), str) and rec["id"] != rid:
            id_mismatch += 1
        fcf = (rec["income_total"] - rec["expense_total"]
               - sum(o["monthly_payment"] for o in rec["obligations"]))
        cap = math.floor(max(0.0, fcf))
        if res + debt + goal + inv > cap:
            budget_viol += 1
        if status != ("ok" if fcf >= 0 else "deficit"):
            enum_viol += 1
        if fcf < 0 and (res or debt or goal or inv):
            budget_viol += 1
        if lump > math.floor(rec["bliq"]):
            lump_viol += 1

    n_summary = sum(1 for _ in open("summary_v4.csv")) - 1
    with gzip.open("recommendations_v4.jsonl.gz", "rt") as fh:
        n_rec = sum(1 for _ in fh)

    print(json.dumps({
        "rows": len(data), "input_rows": len(lines),
        "header_ok": header == EXPECTED_HEADER,
        "crlf": crlf, "spaces": spaces,
        "positional_id_mismatch": id_mismatch,
        "enum_violations": enum_viol, "int_violations": int_viol,
        "invalid_shape_violations": inv_shape_viol,
        "budget_violations": budget_viol, "lump_violations": lump_viol,
        "summary_rows": n_summary, "recommendations_rows": n_rec,
        "other_problems": problems,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
