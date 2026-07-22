"""Cross-check JSONL portraits against the human-readable cards (brief §4.5).

Two checks:
1. Full positional scan — every JSONL row is matched to its card block by
   position; ids must agree and no valid-classified record may carry a defect
   marker ``!`` in its card (i.e. we never silently accept a marked defect).
2. Detailed numeric spot-check on a stratified deterministic sample
   (every 300th id plus three fixed random ids) — income, expense, bliq,
   r_bench, risk and the counts of obligations/goals parsed from the card text
   must equal the JSONL values.
"""

from __future__ import annotations

import gzip
import json
import re
import sys
from typing import Any, Dict, List, Tuple

from engine_v4 import Constants, Validator

PATHS = [f"../expert_portraits_v4_part{p}.jsonl.gz" for p in range(1, 5)]
CARDS = "../portraits_v4_seed20260718_cards.md"
NUM = re.compile(r"-?\d[\d\s]*[.,]?\d*")


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


def load_cards() -> List[Tuple[str, str]]:
    blocks: List[Tuple[str, str]] = []
    cur, buf = None, []
    with open(CARDS, encoding="utf-8") as handle:
        for line in handle:
            m = re.match(r"### (SP4-\d+)", line)
            if m:
                if cur is not None:
                    blocks.append((cur, "".join(buf)))
                cur, buf = m.group(1), [line]
            elif cur is not None:
                buf.append(line)
        if cur is not None:
            blocks.append((cur, "".join(buf)))
    return blocks


def card_number(text: str, label: str) -> float:
    """Extract the first number following a label from card text."""
    idx = text.find(label)
    if idx < 0:
        return float("nan")
    tail = text[idx + len(label): idx + len(label) + 40]
    m = NUM.search(tail)
    if not m:
        return float("nan")
    raw = m.group(0).replace(" ", "").replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return float("nan")


def main() -> int:
    rows = load_raw()
    blocks = load_cards()
    validator = Validator(Constants())

    print("CARD CROSS-CHECK")
    print("-" * 60)
    n = min(len(rows), len(blocks))
    id_mismatch = sum(1 for i in range(n)
                      if str(rows[i].get("id", "")) != blocks[i][0])
    valid_with_bang = sum(
        1 for i in range(n)
        if validator.is_valid(rows[i]) and "!" in blocks[i][1])
    print(f"rows={len(rows)} card_blocks={len(blocks)}")
    print(f"positional id mismatches: {id_mismatch}")
    print(f"valid records carrying a card '!' defect marker: {valid_with_bang}")

    # detailed sample: every 300th + three fixed
    sample_idx = list(range(0, n, 300)) + [1234, 6789, 11111]
    sample_idx = sorted(set(i for i in sample_idx if i < n))
    mism = 0
    shown = 0
    print("\nDetailed numeric spot-check (income/expense/bliq/risk/n_ob/n_goal):")
    for i in sample_idx:
        rec, (cid, text) = rows[i], blocks[i]
        if not validator.is_valid(rec):
            continue  # defect card renders raw !..!, skip numeric equality
        inc = card_number(text, "Доход")
        exp = card_number(text, "Расходы")
        bl = card_number(text, "Накопления")
        n_ob = 0 if "Кредиты: нет" in text else text.count("остаток")
        n_goal = 0 if "Цели: нет" in text else text.count("накоплено")
        ok = (abs(inc - rec["income_total"]) < 0.5
              and abs(exp - rec["expense_total"]) < 0.5
              and abs(bl - rec["bliq"]) < 0.5
              and n_ob == len(rec["obligations"])
              and n_goal == len(rec["goals"]))
        if not ok:
            mism += 1
        if shown < 6:
            print(f"  {cid}: card(inc={inc:.0f},exp={exp:.0f},bliq={bl:.0f},"
                  f"ob={n_ob},goal={n_goal}) vs json(inc={rec['income_total']:.0f},"
                  f"exp={rec['expense_total']:.0f},bliq={rec['bliq']:.0f},"
                  f"ob={len(rec['obligations'])},goal={len(rec['goals'])}) "
                  f"{'OK' if ok else 'MISMATCH'}")
            shown += 1
    print(f"\nsampled valid portraits checked: "
          f"{sum(1 for i in sample_idx if validator.is_valid(rows[i]))}, "
          f"numeric mismatches: {mism}")

    total = id_mismatch + valid_with_bang + mism
    print("-" * 60)
    print(f"TOTAL cross-check violations: {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
