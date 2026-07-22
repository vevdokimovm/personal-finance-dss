"""Self-validation of the written answer files (brief §4.4).

Independently re-reads ``expert_allocations_v4.csv``, ``summary_v4.csv`` and
``recommendations_v4.jsonl.gz`` from disk and checks them against the raw input:
format, enums, completeness, positional id contract, budget conservation
(monthly ≤ max(0, floor(fcf)); lump ≤ bliq), invalid/deficit zeroing, dom
consistency, and cross-file agreement. Exit code is non-zero on any violation.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from typing import Any, Dict, List

from engine_v4 import Constants, Validator

PATHS = [f"../expert_portraits_v4_part{p}.jsonl.gz" for p in range(1, 5)]
STATUS = {"ok", "deficit", "invalid"}
DOM = {"debt", "reserve", "goals+", "none"}


def load_raw() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in PATHS:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                rec = json.loads(line)
                if isinstance(rec, dict) and rec.get("__meta__"):
                    continue
                rows.append(rec)
    return rows


def load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    rows = load_raw()
    alloc = load_csv("expert_allocations_v4.csv")
    summ = load_csv("summary_v4.csv")
    recs = []
    with gzip.open("recommendations_v4.jsonl.gz", "rt", encoding="utf-8") as h:
        for line in h:
            recs.append(json.loads(line))

    validator = Validator(Constants())
    checks: Dict[str, int] = {}

    def add(name: str, ok: bool) -> None:
        checks[name] = checks.get(name, 0) + (0 if ok else 1)

    checks["row_count_alloc"] = 0 if len(alloc) == 12000 else 1
    checks["row_count_summary"] = 0 if len(summ) == 12000 else 1
    checks["row_count_recs"] = 0 if len(recs) == 12000 else 1

    header_ok = list(alloc[0].keys()) == [
        "id", "status", "dom", "res", "debt", "goal", "inv", "lump", "confidence"]
    checks["header"] = 0 if header_ok else 1

    for i, (rec, a, s, r) in enumerate(zip(rows, alloc, summ, recs)):
        rid = str(rec.get("id", f"ROW-{i}"))
        add("id_order", a["id"] == rid or a["id"].startswith("ROW-"))
        add("crossfile_id", a["id"] == s["id"] == r["id"])
        add("crossfile_status", a["status"] == s["status"] == r["status"])
        add("enum_status", a["status"] in STATUS)
        add("enum_dom", a["dom"] in DOM)
        res, debt, goal, inv, lump = (int(a["res"]), int(a["debt"]),
                                      int(a["goal"]), int(a["inv"]), int(a["lump"]))
        conf = int(a["confidence"])
        add("enum_conf", 1 <= conf <= 5)
        add("nonneg", min(res, debt, goal, inv, lump) >= 0)
        add("crossfile_buckets",
            (res, debt, goal, inv, lump) ==
            (int(s["res"]), int(s["debt"]), int(s["goal"]), int(s["inv"]), int(s["lump"])))

        valid = validator.is_valid(rec)
        if not valid:
            add("invalid_status", a["status"] == "invalid")
            add("invalid_zero", (res, debt, goal, inv, lump) == (0, 0, 0, 0, 0))
            add("invalid_dom", a["dom"] == "none")
            continue

        income = float(rec["income_total"])
        expense = float(rec["expense_total"])
        bliq = float(rec["bliq"])
        pay = sum(o["monthly_payment"] for o in rec["obligations"])
        fcf = income - expense - pay
        cap = max(0, math.floor(fcf))
        add("budget_monthly", res + debt + goal + inv <= cap)
        add("budget_lump", lump <= bliq + 1e-6)
        add("status_sign", a["status"] == ("deficit" if fcf < 0 else "ok"))
        if fcf < 0:
            add("deficit_zero_monthly", (res, debt, goal, inv) == (0, 0, 0, 0))
        groups = {"debt": debt, "reserve": res, "goals+": goal + inv}
        mx = max(groups.values())
        add("dom_consistency",
            groups.get(a["dom"], 0) == mx if mx > 0 else a["dom"] == "none")

    print("SELF-VALIDATION of written answer files")
    print("-" * 50)
    total = 0
    for name, fails in sorted(checks.items()):
        total += fails
        flag = "OK" if fails == 0 else f"FAIL x{fails}"
        print(f"  {name:24s}: {flag}")
    print("-" * 50)
    print(f"TOTAL violations: {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
