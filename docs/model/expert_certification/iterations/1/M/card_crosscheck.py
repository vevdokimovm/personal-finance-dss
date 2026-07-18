"""Cross-check JSONL engine values against human-readable cards (seed=42)."""

from __future__ import annotations

import json
import random
import re

UPLOADS = "/mnt/user-data/uploads"
MONTHS_RU = {"январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5,
             "июнь": 6, "июль": 7, "август": 8, "сентябрь": 9,
             "октябрь": 10, "ноябрь": 11, "декабрь": 12}


def rub(text: str) -> float:
    return float(text.replace("\u202f", "").replace("\u00a0", "").replace(" ", ""))


def load_card_blocks(ids: set) -> dict:
    blocks, current, buf = {}, None, []
    with open(f"{UPLOADS}/synthetic_portraits_12000_cards.md") as f:
        for line in f:
            m = re.match(r"## (SP-\d{5}) ", line)
            if m:
                if current in ids:
                    blocks[current] = "".join(buf)
                current, buf = m.group(1), []
            buf.append(line)
        if current in ids:
            blocks[current] = "".join(buf)
    return blocks


def check_portrait(rec: dict, card: str) -> list:
    eng, errors = rec["engine"], []

    def expect(label: str, got: float, want: float, tol: float = 1.0) -> None:
        if abs(got - want) > tol:
            errors.append(f"{label}: card={got} jsonl={want}")

    expect("income", rub(re.search(r"\*\*Доходы — ([\d\s\u202f\u00a0]+) ₽", card).group(1)),
           eng["income_total"])
    expect("expense", rub(re.search(r"\*\*Расходы — ([\d\s\u202f\u00a0]+) ₽", card).group(1)),
           eng["expense_total"])
    bliq_m = re.search(r"\*\*Ликвидная позиция — ([\d\s\u202f\u00a0]+) ₽", card)
    expect("bliq", rub(bliq_m.group(1)), eng["bliq"])
    expect("risk", float(re.search(r"Профиль риска \(1–5\) \| (\d)", card).group(1)),
           eng["risk_tolerance"], 0)
    expect("r_bench", float(re.search(r"r_bench[^|]*\| ([\d.]+) %", card).group(1)),
           eng["r_bench"] * 100, 0.005)

    loans = re.findall(
        r"\|\s*\d+\s*\|[^|]+\|[^|]+\|\s*([\d\s\u202f\u00a0]+)\s*\|"
        r"\s*([\d\s\u202f\u00a0]+)\s*\|\s*([\d.]+)\s*%\s*\|",
        card.split("**Цели накопления**")[0])
    if len(loans) != len(eng["obligations"]):
        errors.append(f"loan count: card={len(loans)} jsonl={len(eng['obligations'])}")
    else:
        for k, (amount, payment, rate) in enumerate(loans):
            ob = eng["obligations"][k]
            expect(f"loan{k}.amount", rub(amount), ob["amount"])
            expect(f"loan{k}.payment", rub(payment), ob["monthly_payment"])
            expect(f"loan{k}.rate", float(rate), ob["interest_rate"] * 100, 0.05)

    goals = re.findall(
        r"\|\s*\d+\s*\|[^|]+\|\s*([\d\s\u202f\u00a0]+)\s*\|\s*([\d\s\u202f\u00a0]+)\s*\|"
        r"[^|]+\|[^|]+\|\s*([^|]+?)\s*\|", card.split("**Цели накопления**")[-1])
    if len(goals) != len(eng["goals"]):
        errors.append(f"goal count: card={len(goals)} jsonl={len(eng['goals'])}")
    else:
        for k, (target, current, deadline) in enumerate(goals):
            goal = eng["goals"][k]
            expect(f"goal{k}.target", rub(target), goal["target_amount"])
            expect(f"goal{k}.current", rub(current), goal["current_amount"])
            if goal["deadline"] is None:
                if "без срока" not in deadline:
                    errors.append(f"goal{k}.deadline: card='{deadline}' jsonl=null")
            else:
                month_name, year = deadline.split()
                want = (int(year), MONTHS_RU[month_name.lower()])
                got = tuple(int(x) for x in goal["deadline"].split("-")[:2])
                if want != got:
                    errors.append(f"goal{k}.deadline: card={want} jsonl={got}")
    return errors


def main() -> None:
    records = [json.loads(line)
               for line in open(f"{UPLOADS}/portraits_12000.jsonl")]
    random.seed(42)
    sample = random.sample(records, 3)
    ids = {r["id"] for r in sample}
    blocks = load_card_blocks(ids)
    for rec in sample:
        errors = check_portrait(rec, blocks[rec["id"]])
        n_checks = 5 + 3 * len(rec["engine"]["obligations"]) + 3 * len(rec["engine"]["goals"])
        status = "OK" if not errors else "MISMATCH"
        print(f"{rec['id']} [{rec['kind']}]: {status}, {n_checks} полей сверено; "
              f"расхождения: {errors or 'нет'}")


if __name__ == "__main__":
    main()
