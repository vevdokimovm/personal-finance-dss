"""Cross-check JSONL parts against human-readable cards (brief 4.5).

Deterministic sample (seed 20260718) of valid rows; positional pairing of
card k with input line k. Compares income, expenses, bliq, risk, r_bench,
every debt (name, balance, rate, payment) and every goal (name, target,
current, deadline). Card money is printed to 2 decimals, rates to 0.1 pct.
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

from engine_v4 import Constants, Pipeline, Validator

CARD_RE = re.compile(r"(?m)^### (SP4-[^\s·]+) · риск (\d+)[^·]*· "
                     r"безрисковая ставка ([\d.,]+)%")
MONEY = r"([\d\s\u00a0\u202f]+(?:[.,]\d+)?)"


def to_number(token: str) -> float:
    cleaned = (token.replace("\u00a0", "").replace("\u202f", "")
               .replace(" ", "").replace(",", "."))
    return float(cleaned)


def parse_card(block: str) -> dict:
    header = CARD_RE.search("### " + block)
    card = {"id": header.group(1), "risk": int(header.group(2)),
            "r_bench": to_number(header.group(3)) / 100.0}
    money_line = re.search(
        rf"Доход {MONEY} ₽/мес · Расходы {MONEY} ₽/мес · Накопления {MONEY} ₽",
        block)
    card["income"] = to_number(money_line.group(1))
    card["expense"] = to_number(money_line.group(2))
    card["bliq"] = to_number(money_line.group(3))
    card["debts"], card["goals"] = [], []
    debt_line = re.search(r"(?m)^Кредиты: (.+)$", block)
    if debt_line and debt_line.group(1).strip() != "нет":
        for chunk in debt_line.group(1).split("; "):
            debt = re.match(
                rf"«(.+?)» — остаток {MONEY} ₽, ставка ([\d.,]+)%, "
                rf"платёж {MONEY} ₽/мес", chunk)
            if debt:
                card["debts"].append((debt.group(1),
                                      to_number(debt.group(2)),
                                      to_number(debt.group(3)) / 100.0,
                                      to_number(debt.group(4))))
    goal_line = re.search(r"(?m)^Цели: (.+)$", block)
    if goal_line and goal_line.group(1).strip() != "нет":
        for chunk in goal_line.group(1).split("; "):
            goal = re.match(
                rf"«(.+?)» — {MONEY} ₽ \(накоплено {MONEY}\), (.+)", chunk)
            if goal:
                tail = goal.group(4).strip()
                deadline = None if tail == "без дедлайна" else tail.replace(
                    "дедлайн ", "")
                card["goals"].append((goal.group(1), to_number(goal.group(2)),
                                      to_number(goal.group(3)), deadline))
    return card


def compare(portrait, card) -> list:
    diffs = []

    def close(a, b, tol):
        return abs(a - b) <= tol

    if portrait.id != card["id"]:
        diffs.append(f"id {portrait.id} != {card['id']}")
    if portrait.risk != card["risk"]:
        diffs.append("risk")
    if not close(portrait.r_bench, card["r_bench"], 0.0006):
        diffs.append("r_bench")
    for field in ("income", "expense", "bliq"):
        if not close(getattr(portrait, field if field != "income"
                             else "income"), card[field], 0.01):
            diffs.append(field)
    if len(portrait.debts) != len(card["debts"]):
        diffs.append("n_debts")
    else:
        for debt, ref in zip(portrait.debts, card["debts"]):
            if (debt.name != ref[0] or not close(debt.amount, ref[1], 0.01)
                    or not close(debt.rate, ref[2], 0.0006)
                    or not close(debt.payment, ref[3], 0.01)):
                diffs.append(f"debt:{ref[0]}")
    if len(portrait.goals) != len(card["goals"]):
        diffs.append("n_goals")
    else:
        for goal, ref in zip(portrait.goals, card["goals"]):
            deadline = goal.deadline.isoformat() if goal.deadline else None
            if (goal.name != ref[0] or not close(goal.target, ref[1], 0.01)
                    or not close(goal.current, ref[2], 0.01)
                    or deadline != ref[3]):
                diffs.append(f"goal:{ref[0]}")
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--cards", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=5)
    args = parser.parse_args()

    blocks = re.split(r"(?m)^### ", args.cards.read_text(encoding="utf-8"))[1:]
    pipeline = Pipeline(args.input_dir, Path("."), Constants())
    validator = Validator(Constants())
    lines = list(pipeline.iter_lines())
    assert len(blocks) == len(lines), "card/jsonl row count mismatch"

    valid_positions = [i for i, line in enumerate(lines)
                       if validator.parse_line(line)[0] is not None]
    rng = random.Random(20260718)
    picks = sorted(rng.sample(valid_positions, args.sample))
    failures = 0
    for pos in picks:
        portrait, _ = validator.parse_line(lines[pos])
        card = parse_card(blocks[pos])
        diffs = compare(portrait, card)
        state = "OK" if not diffs else f"DIFF {diffs}"
        if diffs:
            failures += 1
        print(f"pos={pos} id={portrait.id} -> {state}")
    print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures})")


if __name__ == "__main__":
    main()
