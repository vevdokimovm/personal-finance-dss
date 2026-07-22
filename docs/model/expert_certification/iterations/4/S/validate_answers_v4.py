"""Self-validation of the answer set (brief section 4.4).

Checks: strict CSV format, positional id contract, enum domains,
budget conservation (monthly buckets vs fcf, lump vs bliq), status
consistency, dominant-bucket recomputation, cross-file consistency.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from engine_v4 import Constants, Pipeline, Validator

HEADER = "id,status,dom,res,debt,goal,inv,lump,confidence"
STATUSES = {"ok", "deficit", "invalid"}
DOMS = {"debt", "reserve", "goals+", "none"}


def read_csv_strict(path: Path):
    raw = path.read_bytes()
    problems = []
    if b"\r" in raw:
        problems.append("CRLF or CR found")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if lines[0] != HEADER:
        problems.append(f"bad header: {lines[0]!r}")
    rows = [line.split(",") for line in lines[1:]]
    for i, line in enumerate(lines[1:], start=2):
        if " " in line:
            problems.append(f"space at line {i}")
            break
    return rows, problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--answers-dir", type=Path, required=True)
    args = parser.parse_args()

    problems: list = []
    rows, format_problems = read_csv_strict(
        args.answers_dir / "expert_allocations_v4.csv")
    problems += format_problems

    validator = Validator(Constants())
    pipeline = Pipeline(args.input_dir, args.answers_dir, Constants())
    inputs = list(pipeline.iter_lines())
    if len(rows) != len(inputs):
        problems.append(f"row count {len(rows)} != input {len(inputs)}")

    budget_violations = lump_violations = 0
    status_mismatch = dom_mismatch = id_mismatch = enum_bad = 0
    conf_bad = 0
    for line, row in zip(inputs, rows):
        rid, status, dom = row[0], row[1], row[2]
        res, debt, goal, inv, lump = (int(row[3]), int(row[4]), int(row[5]),
                                      int(row[6]), int(row[7]))
        confidence = int(row[8])
        if status not in STATUSES or dom not in DOMS:
            enum_bad += 1
        if not 1 <= confidence <= 5:
            conf_bad += 1
        portrait, _reason = validator.parse_line(line)
        expected_id = (portrait.id if portrait
                       else Pipeline._salvage_id(line))
        if rid != expected_id:
            id_mismatch += 1
        if portrait is None:
            if status != "invalid" or (res, debt, goal, inv, lump) != (
                    0, 0, 0, 0, 0):
                status_mismatch += 1
            continue
        payments = sum(d.payment for d in portrait.debts)
        fcf = portrait.income - portrait.expense - payments
        expected_status = "deficit" if fcf < 0 else "ok"
        if status != expected_status:
            status_mismatch += 1
        if res + debt + goal + inv > max(0.0, fcf) + 1e-6:
            budget_violations += 1
        if lump > portrait.bliq + 1e-6:
            lump_violations += 1
        buckets = (("debt", debt), ("reserve", res), ("goals+", goal + inv))
        best_name, best_value = "none", 0
        for name, value in buckets:
            if value > best_value:
                best_name, best_value = name, value
        if dom != best_name:
            dom_mismatch += 1

    summary_lines = (args.answers_dir / "summary_v4.csv").read_text(
        encoding="utf-8").rstrip("\n").split("\n")
    summary_rows = len(summary_lines) - 1
    jsonl_rows = totals_mismatch = 0
    with gzip.open(args.answers_dir / "recommendations_v4.jsonl.gz", "rt",
                   encoding="utf-8") as handle:
        for row, line in zip(rows, handle):
            jsonl_rows += 1
            payload = json.loads(line)
            expected = {"res": int(row[3]), "debt": int(row[4]),
                        "goal": int(row[5]), "inv": int(row[6]),
                        "lump": int(row[7])}
            if payload["totals"] != expected or payload["id"] != row[0]:
                totals_mismatch += 1

    checks = {
        "csv_rows": len(rows),
        "format_problems": problems,
        "enum_violations": enum_bad,
        "confidence_out_of_range": conf_bad,
        "positional_id_mismatches": id_mismatch,
        "status_mismatches": status_mismatch,
        "dom_mismatches": dom_mismatch,
        "budget_violations_monthly": budget_violations,
        "lump_over_liquidity": lump_violations,
        "summary_rows": summary_rows,
        "jsonl_rows": jsonl_rows,
        "jsonl_totals_mismatch_vs_csv": totals_mismatch,
    }
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    hard_fail = (enum_bad or conf_bad or id_mismatch or status_mismatch
                 or dom_mismatch or budget_violations or lump_violations
                 or totals_mismatch or problems
                 or len(rows) != 12000 or summary_rows != 12000
                 or jsonl_rows != 12000)
    print("RESULT:", "FAIL" if hard_fail else "PASS")


if __name__ == "__main__":
    main()
