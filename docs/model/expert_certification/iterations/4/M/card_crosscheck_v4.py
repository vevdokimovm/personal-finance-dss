#!/usr/bin/env python3
"""Programmatic crosscheck JSONL <-> markdown cards (brief §4.5).

Deterministic random sample of positions (seed 20260718); cards are matched
positionally (k-th card <-> k-th data line), ids verified, every numeric field
compared with format-aware tolerances (cards round rates to 0.1 p.p.).
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from engine_v4 import BASE_CONFIG, Runner

CARD_RE = re.compile(r"^### (\S+) · риск (\S+)[^·]*· безрисковая ставка ([\d.]+)%",
                     re.M)
MONEY = r"([-\d\s.,]+?|!.*?!)"


def to_num(s: str):
    s = s.strip().replace(" ", "").replace(" ", "").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_card(block: str) -> dict:
    head = re.search(r"^### (\S+) · риск (\S+).*?безрисковая ставка (\S+?)%",
                     block, re.S)
    out: dict = {"id": head.group(1) if head else None,
                 "risk": head.group(2) if head else None,
                 "r_bench_pct": head.group(3) if head else None}
    m = re.search(r"Доход (.+?) ₽/мес · Расходы (.+?) ₽/мес · Накопления (.+?) ₽",
                  block)
    if m:
        out["income"], out["expense"], out["bliq"] = m.group(1), m.group(2), m.group(3)
    debts = []
    dm = re.search(r"Кредиты: (.+?)(?:\nЦели:|\Z)", block, re.S)
    if dm and "нет" != dm.group(1).strip():
        for item in re.finditer(
                r"«(.*?)» — остаток (.+?) ₽, ставка (.+?)%?, платёж (.+?) ₽/мес",
                dm.group(1)):
            debts.append({"name": item.group(1), "amount": item.group(2),
                          "rate_pct": item.group(3), "payment": item.group(4)})
    out["debts"] = debts
    goals = []
    gm = re.search(r"Цели: (.+)\Z", block, re.S)
    if gm and gm.group(1).strip() != "нет":
        for item in re.finditer(
                r"«(.*?)» — (.+?) ₽ \(накоплено (.+?)\), (дедлайн (\S+)|без дедлайна)",
                gm.group(1)):
            deadline = item.group(5)
            goals.append({"name": item.group(1), "target": item.group(2),
                          "current": item.group(3),
                          "deadline": deadline.rstrip(";,.") if deadline else None})
    out["goals"] = goals
    return out


def close(card_val: str, json_val, tol: float = 0.005) -> bool:
    num = to_num(card_val) if isinstance(card_val, str) else card_val
    if num is None or not isinstance(json_val, (int, float)) \
            or isinstance(json_val, bool):
        return None
    return abs(num - float(json_val)) <= tol


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parts", nargs="+", required=True)
    ap.add_argument("--cards", required=True)
    ap.add_argument("--aux-dir", default="aux")
    ap.add_argument("--sample", type=int, default=12)
    args = ap.parse_args()

    lines = Runner(BASE_CONFIG, args.parts).load_lines()
    text = Path(args.cards).read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=### )", text)
    blocks = [b for b in blocks if b.startswith("### ")]

    rng = random.Random(20260718)
    positions = sorted(set(rng.sample(range(len(lines)), args.sample))
                       | {0, len(lines) - 1})

    report = {"n_cards": len(blocks), "n_lines": len(lines),
              "positions": positions, "checks": []}
    mismatches = 0
    for pos in positions:
        card = parse_card(blocks[pos])
        try:
            obj = json.loads(lines[pos])
        except ValueError:
            obj = None
        entry = {"position": pos, "card_id": card["id"],
                 "json_id": obj.get("id") if isinstance(obj, dict) else None,
                 "fields_checked": 0, "fields_ok": 0, "diffs": []}
        if not isinstance(obj, dict):
            entry["diffs"].append("json_not_parseable")
            report["checks"].append(entry)
            continue

        def chk(label: str, ok) -> None:
            if ok is None:
                return
            entry["fields_checked"] += 1
            if ok:
                entry["fields_ok"] += 1
            else:
                entry["diffs"].append(label)

        chk("id", card["id"] == obj.get("id"))
        chk("income", close(card.get("income"), obj.get("income_total")))
        chk("expense", close(card.get("expense"), obj.get("expense_total")))
        chk("bliq", close(card.get("bliq"), obj.get("bliq")))
        risk_num = to_num(card["risk"]) if card["risk"] else None
        if risk_num is not None and isinstance(obj.get("risk_tolerance"), int):
            chk("risk", int(risk_num) == obj["risk_tolerance"])
        rb = to_num(card["r_bench_pct"]) if card["r_bench_pct"] else None
        if rb is not None and isinstance(obj.get("r_bench"), (int, float)):
            chk("r_bench", abs(rb / 100 - obj["r_bench"]) <= 0.0006)
        jd = obj.get("obligations") or []
        chk("n_debts", len(card["debts"]) == len(jd))
        for cd, od in zip(card["debts"], jd):
            if not isinstance(od, dict):
                continue
            chk("debt.name", cd["name"] == od.get("name"))
            chk("debt.amount", close(cd["amount"], od.get("amount")))
            chk("debt.payment", close(cd["payment"], od.get("monthly_payment")))
            rate = to_num(cd["rate_pct"])
            if rate is not None and isinstance(od.get("interest_rate"), (int, float)) \
                    and not isinstance(od.get("interest_rate"), bool):
                chk("debt.rate", abs(rate / 100 - od["interest_rate"]) <= 0.0006)
        jg = obj.get("goals") or []
        chk("n_goals", len(card["goals"]) == len(jg))
        for cg, og in zip(card["goals"], jg):
            if not isinstance(og, dict):
                continue
            chk("goal.name", cg["name"] == og.get("name"))
            chk("goal.target", close(cg["target"], og.get("target_amount")))
            chk("goal.current", close(cg["current"], og.get("current_amount")))
            dl = og.get("deadline", "MISSING")
            if cg["deadline"] is None:
                chk("goal.deadline", dl is None)
            else:
                chk("goal.deadline", cg["deadline"] == dl)
        if entry["diffs"]:
            mismatches += 1
        report["checks"].append(entry)

    report["cards_with_diffs"] = mismatches
    aux = Path(args.aux_dir)
    aux.mkdir(parents=True, exist_ok=True)
    with open(aux / "crosscheck.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"n_cards": len(blocks), "sampled": len(positions),
                      "cards_with_diffs": mismatches}, ensure_ascii=False))
    for c in report["checks"]:
        print(c["position"], c["card_id"], f"{c['fields_ok']}/{c['fields_checked']}",
              c["diffs"] if c["diffs"] else "OK")


if __name__ == "__main__":
    main()
