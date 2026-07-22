"""Sensitivity study (brief section 11): rerun the engine shifting one
constant at a time by +-20 percent and compare dom/status/lump vs baseline."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from engine_v4 import Constants, Pipeline

INPUT_DIR = Path("/mnt/user-data/uploads")
SHIFTS = [
    ("cheap_spread", 0.016), ("cheap_spread", 0.024),
    ("toxic_rate", 0.36), ("toxic_rate", 0.54),
    ("reserve_scale", 0.8), ("reserve_scale", 1.2),
    ("min_move", 8_000.0), ("min_move", 12_000.0),
    ("pdn_high", 0.40), ("pdn_high", 0.60),
]


def run(constants: Constants) -> list:
    pipeline = Pipeline(INPUT_DIR, Path("."), constants)
    return pipeline.run(write_outputs=False)


def characterize(base_row, var_row, base_portraits, index) -> str:
    return f"{base_row.dom}->{var_row.dom}"


def main() -> None:
    base = run(Constants())
    report = {}
    for name, value in SHIFTS:
        constants = Constants()
        setattr(constants, name, value)
        variant = run(constants)
        dom_changed = status_changed = lump_changed = 0
        transitions = Counter()
        changed_deficit = changed_liq_band = 0
        for b, v in zip(base, variant):
            if b.status != v.status:
                status_changed += 1
            if b.dom != v.dom:
                dom_changed += 1
                transitions[f"{b.dom}->{v.dom}"] += 1
                if b.status == "deficit":
                    changed_deficit += 1
                target = b.diagnostics.get("reserve_target", 0)
                bliq = b.diagnostics.get("bliq", 0)
                if target > 0 and 0.8 <= bliq / target <= 1.2:
                    changed_liq_band += 1
            if b.lump != v.lump:
                lump_changed += 1
        report[f"{name}={value}"] = {
            "dom_changed": dom_changed,
            "dom_changed_pct": round(100 * dom_changed / len(base), 2),
            "status_changed": status_changed,
            "lump_changed": lump_changed,
            "lump_changed_pct": round(100 * lump_changed / len(base), 2),
            "top_transitions": transitions.most_common(3),
            "changed_rows_in_liq_band_08_12": changed_liq_band,
        }
        print(name, value, report[f"{name}={value}"])
    Path("sensitivity_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
