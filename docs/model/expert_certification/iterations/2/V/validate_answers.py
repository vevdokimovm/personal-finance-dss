"""Validate expert_answers_v2.csv against source JSONL: row count, id set,
conservation constraint, deficit consistency, format cleanliness."""

import csv
import gzip
import json
import math
from pathlib import Path

UPLOADS = Path("/mnt/user-data/uploads")
CSV_PATH = Path("/mnt/user-data/outputs/expert_answers_v2.csv")
FILES = [UPLOADS / f"expert_portraits_v2_part{i}_jsonl.gz" for i in range(1, 5)]


def load_fcf() -> dict:
    fcf = {}
    for path in FILES:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                obj = json.loads(line)
                pay = sum(o.get("monthly_payment", 0) or 0
                          for o in obj.get("obligations", []))
                fcf[obj["id"]] = round(obj["income_total"] - obj["expense_total"] - pay, 2)
    return fcf


def main() -> None:
    fcf = load_fcf()
    raw = CSV_PATH.read_bytes()
    assert b"\r" not in raw, "CRLF found"
    lines = raw.decode().splitlines()
    assert lines[0] == "id,status,dom,res,debt,goal,inv,lump", "bad header"
    assert len(lines) == 12001, f"rows: {len(lines)}"
    seen, violations = set(), 0
    dom_ok = {"debt", "reserve", "goals+", "none"}
    with CSV_PATH.open() as fh:
        for row in csv.DictReader(fh):
            pid = row["id"]
            seen.add(pid)
            r, d, g, i = (int(row[k]) for k in ("res", "debt", "goal", "inv"))
            lump = int(row["lump"])
            assert min(r, d, g, i, lump) >= 0, f"negative at {pid}"
            assert row["dom"] in dom_ok, f"bad dom at {pid}"
            f = fcf[pid]
            if row["status"] == "deficit":
                assert f < 0 and r == d == g == i == 0 and row["dom"] == "none", pid
            else:
                assert f >= 0, f"status ok but FCF<0 at {pid}"
                if r + d + g + i > math.floor(f):
                    violations += 1
                if r + d + g + i != math.floor(f):
                    violations += 1
    expected = {f"SP-{n:05d}" for n in range(12000)}
    assert seen == expected, f"id mismatch: {len(seen)} unique"
    print(f"rows=12000 header=ok ids=complete crlf=none "
          f"conservation_violations={violations}")


if __name__ == "__main__":
    main()
