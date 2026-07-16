"""Independent financial expert allocation engine.

Processes 12,000 client portraits and produces a strict CSV verdict per the
round-2 expert brief. Methodology constants are fixed below, before any data
processing, and applied uniformly to every portrait.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

AS_OF = date(2026, 7, 11)

TARGET_MONTHS = {1: 6.0, 2: 5.0, 3: 4.0, 4: 3.0, 5: 3.0}
TOXIC_SPREAD = 0.10
COSTLY_SPREAD = 0.02
DEADLINE_CARVE_SHARE = 0.40
COSTLY_DEBT_SHARE = 0.60
DEFAULT_GOAL_HORIZON_M = 60
LUMP_ABS_MIN = 10_000.0
LUMP_REL_MIN = 0.25
DEFAULT_RISK = 2
DEFAULT_BENCH = 0.15


def safe_num(value: object, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def safe_pos(value: object) -> float:
    return max(0.0, safe_num(value))


def months_until(deadline: object) -> float | None:
    if deadline is None:
        return None
    try:
        d = date.fromisoformat(str(deadline))
    except ValueError:
        return None
    if d <= AS_OF:
        return 1.0
    return max(1.0, math.ceil((d - AS_OF).days / 30.4375))


@dataclass
class Debt:
    amount: float
    rate: float
    payment: float

    def tier(self, bench: float) -> str:
        monthly_interest = self.amount * self.rate / 12.0
        growing = self.payment < monthly_interest * 0.999
        interest_only = self.payment <= monthly_interest * 1.01
        if growing or self.rate >= bench + TOXIC_SPREAD:
            return "toxic"
        if interest_only and self.rate >= bench:
            return "toxic"
        if self.rate >= bench + COSTLY_SPREAD:
            return "costly"
        return "hold"


@dataclass
class Goal:
    gap: float
    months: float | None

    @property
    def required_monthly(self) -> float:
        horizon = self.months if self.months is not None else DEFAULT_GOAL_HORIZON_M
        return self.gap / horizon if self.gap > 0 else 0.0


@dataclass
class Portrait:
    pid: str
    income: float
    expense: float
    bliq: float
    bench: float
    risk: int
    debts: list
    goals: list

    @classmethod
    def parse(cls, record: dict) -> "Portrait":
        body = record.get("engine", record)
        debts = []
        for o in body.get("obligations") or []:
            if isinstance(o, dict):
                debts.append(Debt(safe_pos(o.get("amount")),
                                  safe_pos(o.get("interest_rate")),
                                  safe_pos(o.get("monthly_payment"))))
        goals = []
        for g in body.get("goals") or []:
            if isinstance(g, dict):
                gap = safe_pos(g.get("target_amount")) - safe_pos(g.get("current_amount"))
                goals.append(Goal(max(0.0, gap), months_until(g.get("deadline"))))
        risk = body.get("risk_tolerance")
        risk = risk if isinstance(risk, int) and 1 <= risk <= 5 else DEFAULT_RISK
        bench = safe_num(body.get("r_bench"), DEFAULT_BENCH)
        if not 0.0 < bench <= 1.0:
            bench = DEFAULT_BENCH
        return cls(str(record.get("id", "")), safe_pos(body.get("income_total")),
                   safe_pos(body.get("expense_total")), safe_pos(body.get("bliq")),
                   bench, risk, debts, goals)


class Advisor:
    """Deterministic allocation policy of the independent expert."""

    def advise(self, p: Portrait) -> dict:
        mp_total = sum(d.payment for d in p.debts)
        fcf = p.income - p.expense - mp_total
        if fcf < 0:
            return self._deficit_row(p, mp_total)
        return self._ok_row(p, fcf, mp_total)

    def _deficit_row(self, p: Portrait, mp_total: float) -> dict:
        order = sorted(p.debts,
                       key=lambda d: (d.payment / d.amount) if d.amount > 0 else math.inf,
                       reverse=True)
        bliq_left, mp_left, paid = p.bliq, mp_total, 0.0
        for d in order:
            if p.income - p.expense - mp_left >= 0:
                break
            if d.amount <= bliq_left:
                bliq_left -= d.amount
                mp_left -= d.payment
                paid += d.amount
        solvent = p.income - p.expense - mp_left >= 0
        cushioned = bliq_left >= p.expense + mp_left
        lump = int(paid) if (paid > 0 and solvent and cushioned) else 0
        return self._row(p.pid, "deficit", 0, 0, 0, 0, lump)

    def _ok_row(self, p: Portrait, fcf: float, mp_total: float) -> dict:
        essential = p.expense + mp_total
        target = TARGET_MONTHS[p.risk] * essential
        toxic_bal = sum(d.amount for d in p.debts if d.tier(p.bench) == "toxic")
        costly_bal = sum(d.amount for d in p.debts if d.tier(p.bench) == "costly")

        lump, bliq = 0.0, p.bliq
        toxic_kill = min(max(0.0, bliq - essential), toxic_bal)
        lump += toxic_kill
        bliq -= toxic_kill
        toxic_bal -= toxic_kill

        excess = max(0.0, bliq - target)
        if excess >= max(LUMP_ABS_MIN, LUMP_REL_MIN * essential):
            lump += excess
            bliq -= excess
            spend = excess
            take = min(spend, costly_bal)
            costly_bal -= take
            spend -= take
            for g in sorted(p.goals, key=lambda g: g.months if g.months is not None else math.inf):
                take = min(spend, g.gap)
                g.gap -= take
                spend -= take

        req_deadline = sum(g.required_monthly for g in p.goals if g.months is not None)
        req_total = sum(g.required_monthly for g in p.goals)

        budget = int(fcf)
        rem = budget
        res = min(rem, int(math.ceil(max(0.0, essential - bliq))))
        rem -= res
        d1 = min(rem, int(toxic_bal))
        rem -= d1
        goal = min(int(DEADLINE_CARVE_SHARE * rem), int(math.ceil(req_deadline)))
        rem -= goal
        d2 = min(int(COSTLY_DEBT_SHARE * rem), int(costly_bal))
        rem -= d2
        res2 = min(rem, int(math.ceil(max(0.0, target - bliq))))
        rem -= res2
        topup = min(rem, max(0, int(math.ceil(req_total)) - goal))
        rem -= topup
        return self._row(p.pid, "ok", res + res2, d1 + d2, goal + topup, rem, int(lump))

    @staticmethod
    def _row(pid: str, status: str, res: int, debt: int, goal: int, inv: int,
             lump: int) -> dict:
        if status == "deficit" or (res == debt == goal == inv == 0):
            dom = "none"
        else:
            best = max(debt, res, goal + inv)
            dom = "debt" if debt == best else ("reserve" if res == best else "goals+")
        return {"id": pid, "status": status, "dom": dom, "res": res, "debt": debt,
                "goal": goal, "inv": inv, "lump": lump}


def load_records(paths: list) -> list:
    records = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            records.extend(json.loads(line) for line in handle if line.strip())
    return records


def main() -> None:
    uploads = Path("/mnt/user-data/uploads")
    paths = [uploads / f"expert_portraits_v2_part{i}_jsonl.gz" for i in range(1, 5)]
    records = load_records(paths)
    advisor = Advisor()
    out_path = Path("/home/claude/expert_allocation_v2.csv")
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "status", "dom", "res",
                                                    "debt", "goal", "inv", "lump"])
        writer.writeheader()
        for record in records:
            writer.writerow(advisor.advise(Portrait.parse(record)))
    print(f"written: {out_path} rows={len(records)}")


if __name__ == "__main__":
    main()
