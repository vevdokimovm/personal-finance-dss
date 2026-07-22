"""Sensitivity of decisions to the expert's own constants (brief §11).

Shifts one constant at a time by ±20% (or nearest sensible step), re-runs the
engine in memory on all rows, and reports the share of valid portraits whose
``dom`` or ``status`` changed versus baseline, plus the observable situations
(baseline flags) most over-represented among the changed portraits.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import List

from engine_v4 import Constants, Engine

PATHS = [f"../expert_portraits_v4_part{p}.jsonl.gz" for p in range(1, 5)]


def shift(base: Constants, field_name: str, factor: float) -> Constants:
    val = getattr(base, field_name)
    if isinstance(val, dict):
        val = {k: v * factor for k, v in val.items()}
    elif field_name == "goal_close_frac":
        val = min(0.999, val * factor)
    else:
        val = val * factor
    return replace(base, **{field_name: val})


def variants() -> List[tuple]:
    base = Constants()
    fields = ["dear_spread", "toxic_abs", "toxic_spread", "reserve_months",
              "lump_min", "surplus_buffer", "goal_close_frac", "invalid_rate"]
    out = []
    for name in fields:
        out.append((f"{name} -20%", shift(base, name, 0.8)))
        out.append((f"{name} +20%", shift(base, name, 1.2)))
    return out


def main() -> None:
    engine = Engine()
    rows = engine.load_rows(PATHS)
    base_res = engine.run(rows)
    base = [(r.status, r.dom, r.lump, r.flags) for r in base_res]
    n_valid = sum(1 for r in base_res if r.status != "invalid")

    print(f"rows={len(rows)} valid={n_valid}")
    print(f"{'variant':22s} {'Δdom%':>7s} {'Δstatus%':>9s} {'Δlump%':>7s}"
          f"  top situations (flags over-rep among changed)")
    print("-" * 110)
    for label, const in variants():
        res = Engine(const).run(rows)
        dom_ch = status_ch = lump_ch = 0
        flag_counter: Counter = Counter()
        for (bs, bd, bl, bf), r in zip(base, res):
            if bs == "invalid" and r.status == "invalid":
                continue
            changed = False
            if bd != r.dom:
                dom_ch += 1
                changed = True
            if bs != r.status:
                status_ch += 1
                changed = True
            if bl != r.lump:
                lump_ch += 1
                changed = True
            if changed:
                for fl in bf:
                    flag_counter[fl] += 1
        denom = n_valid
        top = ", ".join(f"{k}({v})" for k, v in flag_counter.most_common(3))
        print(f"{label:22s} {dom_ch/denom*100:6.2f}% {status_ch/denom*100:8.2f}% "
              f"{lump_ch/denom*100:6.2f}%  {top}")


if __name__ == "__main__":
    main()
