"""Independent expert allocation engine, round 2 (12,000 portraits).

Methodology and constants are fixed in expert_methodology_v2.md prior to
processing. Assessment date: 2026-07-11. Amounts RUB, flows monthly,
rates annual. Output: strict CSV `id,status,dom,res,debt,goal,inv,lump`.
"""

import csv
import gzip
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

TODAY = date(2026, 7, 11)
UPLOADS = Path("/mnt/user-data/uploads")
OUTPUT = Path("/mnt/user-data/outputs/expert_answers_v2.csv")
FILES = [UPLOADS / f"expert_portraits_v2_part{i}_jsonl.gz" for i in range(1, 5)]

PREPAY_SPREAD = 0.02
TOXIC_SPREAD = 0.15
TOXIC_ABS_RATE = 0.35
RESERVE_MONTHS = {1: 6.0, 2: 5.0, 3: 4.0, 4: 3.0, 5: 3.0}
L_MIN_MONTHS = 1.0
NEAR_GOAL_DAYS = 366
LUMP_GOAL_DAYS = 731
MIN_INV_TICKET = 10_000
DEFAULT_R_BENCH = 0.13
DAYS_PER_MONTH = 30.44


def safe_num(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or math.isinf(x) or x < 0:
        return None
    return x


def parse_deadline(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


@dataclass
class Debt:
    amount: float | None
    rate: float | None
    payment: float


@dataclass
class Goal:
    need: float
    deadline: date | None


class ExpertEngine:
    """Deterministic allocation of free cash flow and lump-sum moves."""

    def run(self) -> None:
        rows = []
        for path in FILES:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rows.append(self._assess_line(line))
        with OUTPUT.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(["id", "status", "dom", "res", "debt", "goal", "inv", "lump"])
            writer.writerows(rows)
        print(f"written rows: {len(rows)}")

    def _assess_line(self, line: str) -> list:
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            return ["INVALID", "deficit", "none", 0, 0, 0, 0, 0]
        pid = str(raw.get("id", "INVALID"))
        try:
            return self._assess(pid, raw.get("engine", raw))
        except Exception:
            return [pid, "deficit", "none", 0, 0, 0, 0, 0]

    def _assess(self, pid: str, core: dict) -> list:
        income = safe_num(core.get("income_total"))
        expense = safe_num(core.get("expense_total"))
        if income is None or expense is None:
            return [pid, "deficit", "none", 0, 0, 0, 0, 0]
        bliq = safe_num(core.get("bliq")) or 0.0
        r_bench = safe_num(core.get("r_bench"))
        if r_bench is None or not 0.0 < r_bench < 1.0:
            r_bench = DEFAULT_R_BENCH
        risk = core.get("risk_tolerance")
        risk = int(risk) if isinstance(risk, (int, float)) and int(risk) in RESERVE_MONTHS else 3

        debts, payments_sum = self._parse_debts(core.get("obligations"))
        goals = self._parse_goals(core.get("goals"))

        fcf = round(income - expense - payments_sum, 2)
        burn = expense + payments_sum
        l_min = burn * L_MIN_MONTHS
        l_target = burn * RESERVE_MONTHS[risk]

        prepayable = [d for d in debts
                      if d.amount and d.amount > 0 and d.rate is not None
                      and d.rate >= r_bench + PREPAY_SPREAD]
        toxic = [d for d in prepayable
                 if d.rate >= r_bench + TOXIC_SPREAD or d.rate >= TOXIC_ABS_RATE]
        expensive_total = sum(d.amount for d in prepayable)

        if fcf < 0:
            lump = min(max(0.0, bliq - l_min), expensive_total)
            return [pid, "deficit", "none", 0, 0, 0, 0, int(round(lump))]

        res, debt, goal, inv = self._monthly_split(
            fcf, bliq, l_min, l_target, bool(prepayable), bool(toxic), goals)
        lump = self._lump(bliq, l_min, l_target, expensive_total, bool(toxic), goals)
        dom = self._dominant(res, debt, goal, inv)
        return [pid, "ok", dom, res, debt, goal, inv, int(round(lump))]

    def _parse_debts(self, raw: Any) -> tuple[list[Debt], float]:
        debts, total = [], 0.0
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                payment = safe_num(item.get("monthly_payment")) or 0.0
                rate = safe_num(item.get("interest_rate"))
                debts.append(Debt(safe_num(item.get("amount")), rate, payment))
                total += payment
        return debts, total

    def _parse_goals(self, raw: Any) -> list[Goal]:
        goals = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                target = safe_num(item.get("target_amount"))
                if target is None or target <= 0:
                    continue
                current = safe_num(item.get("current_amount")) or 0.0
                goals.append(Goal(max(0.0, target - current),
                                  parse_deadline(item.get("deadline"))))
        return goals

    def _monthly_split(self, fcf: float, bliq: float, l_min: float,
                       l_target: float, has_expensive: bool, has_toxic: bool,
                       goals: list[Goal]) -> tuple[int, int, int, int]:
        f = int(math.floor(fcf))
        if f <= 0:
            return 0, 0, 0, 0
        if bliq < l_min:
            if has_toxic:
                res = f // 2
            elif has_expensive:
                res = int(round(0.7 * f))
            else:
                res = f
            return res, f - res, 0, 0
        if has_expensive:
            res = int(round(0.1 * f)) if bliq < l_target else 0
            near_req = sum(self._required(g) for g in goals
                           if g.need > 0 and g.deadline
                           and (g.deadline - TODAY).days <= NEAR_GOAL_DAYS)
            goal = min(int(near_req), int(0.3 * f), f - res)
            return res, f - res - goal, goal, 0
        res = min(int(0.3 * f), max(0, int(l_target - bliq)))
        rem = f - res
        dated_req = sum(self._required(g) for g in goals if g.need > 0 and g.deadline)
        goal = min(int(dated_req), rem)
        rem2 = rem - goal
        if rem2 > 0 and any(g.need > 0 and g.deadline is None for g in goals):
            add = rem2 // 2
            return res, 0, goal + add, rem2 - add
        return res, 0, goal, rem2

    def _lump(self, bliq: float, l_min: float, l_target: float,
              expensive_total: float, has_toxic: bool,
              goals: list[Goal]) -> float:
        deployable_debt = max(0.0, bliq - (l_min if has_toxic else l_target))
        debt_lump = min(deployable_debt, expensive_total)
        rem = max(0.0, (bliq - l_target) - debt_lump)
        near_gap = sum(g.need for g in goals
                       if g.need > 0 and g.deadline
                       and (g.deadline - TODAY).days <= LUMP_GOAL_DAYS)
        goal_lump = min(rem, near_gap)
        inv_lump = rem - goal_lump
        if inv_lump < MIN_INV_TICKET:
            inv_lump = 0.0
        return debt_lump + goal_lump + inv_lump

    @staticmethod
    def _required(goal: Goal) -> float:
        months = max(1.0, (goal.deadline - TODAY).days / DAYS_PER_MONTH)
        return goal.need / months

    @staticmethod
    def _dominant(res: int, debt: int, goal: int, inv: int) -> str:
        buckets = [("debt", debt), ("reserve", res), ("goals+", goal + inv)]
        name, best = max(buckets, key=lambda b: b[1])
        return name if best > 0 else "none"


if __name__ == "__main__":
    ExpertEngine().run()
