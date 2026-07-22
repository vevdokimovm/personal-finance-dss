"""Programmatic cross-check: JSONL records vs human-readable cards.

Positional pairing (cards are exported in the same order). Deterministic
seed picks 5 random positions plus one known-defective record.
"""

from __future__ import annotations

import json
import random
import re

from engine_v4 import read_lines

CARDS = "/mnt/user-data/uploads/portraits_v4_seed20260718_cards.md"


def money(x: float) -> str:
    return f"{x:,.2f}".replace(",", " ")


def check_one(rec: dict, card: str) -> list[str]:
    misses: list[str] = []

    def expect(label: str, needle: str) -> None:
        if needle not in card:
            misses.append(f"{label}: '{needle}' not found")

    expect("id", rec["id"])
    for key, label in (("income_total", "Доход"), ("expense_total",
                       "Расходы"), ("bliq", "Накопления")):
        val = rec[key]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            expect(label, money(val))
        else:
            expect(label + " (defect raw)", f"!{val!r}!".replace("'", "'"))
    if isinstance(rec.get("risk_tolerance"), int):
        expect("risk", f"риск {rec['risk_tolerance']}")
    if isinstance(rec.get("r_bench"), float):
        expect("r_bench", f"ставка {rec['r_bench'] * 100:.1f}%")
    for ob in rec.get("obligations", []):
        expect("ob.name", f"«{ob['name']}»")
        for key in ("amount", "monthly_payment"):
            val = ob.get(key)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                expect(f"ob.{key}", money(val))
        rate = ob.get("interest_rate")
        if isinstance(rate, (int, float)) and not isinstance(rate, bool):
            expect("ob.rate", f"{rate * 100:.1f}%")
    for g in rec.get("goals", []):
        expect("goal.name", f"«{g['name']}»")
        for key in ("target_amount", "current_amount"):
            val = g.get(key)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                expect(f"goal.{key}", money(val))
        if "deadline" in g:
            dl = g["deadline"]
            if dl is None:
                expect("goal.deadline", "без дедлайна")
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(dl) or ""):
                expect("goal.deadline", str(dl))
    return misses


def main() -> None:
    lines = read_lines([f"part{i}.jsonl.gz" for i in (1, 2, 3, 4)])
    blocks = open(CARDS, encoding="utf-8").read().split("\n### ")[1:]
    assert len(blocks) == len(lines), (len(blocks), len(lines))

    rng = random.Random(20260718)
    picks = sorted(rng.sample(range(len(lines)), 5))
    picks.append(8)  # known defective record SP4-00008 (visual defect check)

    report = {"cards_total": len(blocks), "jsonl_total": len(lines),
              "checks": []}
    for pos in picks:
        try:
            rec = json.loads(lines[pos])
        except (json.JSONDecodeError, ValueError):
            report["checks"].append({"pos": pos, "result":
                                     "unparseable JSON, skipped"})
            continue
        misses = check_one(rec, blocks[pos])
        report["checks"].append({
            "pos": pos, "id": rec.get("id"),
            "fields_missed": misses, "ok": not misses})
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
