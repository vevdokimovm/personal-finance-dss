"""Independent expert allocation engine for dataset v3 (round 3).

Implements the methodology fixed in expert_methodology_v3.md verbatim.
Stdlib only, streaming, one output row per input line in input order.
"""

import csv
import gzip
import json
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path


CUTOFF_DATE = date(2026, 7, 16)
CUSHION_MONTHS = {1: 6, 2: 6, 3: 5, 4: 4, 5: 3}
TOXIC_SPREAD = 0.06
EXPENSIVE_SPREAD = 0.02
LUMP_MIN_BLOCK = 10_000
LUMP_MIN_INVEST = 50_000
ID_RE = re.compile(r"SP3-\d{5}")

SHARES = {
    # (debt_class, cushion_low): (res, debt)
    ("toxic", True): (0.25, 0.65),
    ("toxic", False): (0.00, 0.85),
    ("expensive", True): (0.40, 0.45),
    ("expensive", False): (0.00, 0.70),
    ("clean", True): (0.60, 0.00),
    ("clean", False): (0.00, 0.00),
}


@dataclass
class Decision:
    """One CSV output row."""

    row_id: str
    status: str
    dom: str = "none"
    res: int = 0
    debt: int = 0
    goal: int = 0
    inv: int = 0
    lump: int = 0

    def as_row(self) -> list:
        return [self.row_id, self.status, self.dom,
                self.res, self.debt, self.goal, self.inv, self.lump]


@dataclass
class RunStats:
    """Counters collected during the pass."""

    total: int = 0
    ok: int = 0
    deficit: int = 0
    invalid: int = 0
    invalid_reasons: dict = field(default_factory=dict)
    sum_violations: int = 0
    dom_counts: dict = field(default_factory=dict)
    lump_positive: int = 0

    def bump_reason(self, reason: str) -> None:
        self.invalid_reasons[reason] = self.invalid_reasons.get(reason, 0) + 1


class Validator:
    """Defect detection per methodology §6."""

    RECORD_FIELDS = ("id", "income_total", "expense_total", "obligations",
                     "goals", "bliq", "r_bench", "risk_tolerance")
    OBLIGATION_FIELDS = ("id", "name", "amount", "interest_rate",
                         "monthly_payment")
    GOAL_FIELDS = ("id", "name", "target_amount", "current_amount", "deadline")

    @staticmethod
    def is_number(value) -> bool:
        return (isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value))

    @classmethod
    def money_ok(cls, value) -> bool:
        return cls.is_number(value) and value >= 0

    @staticmethod
    def parse_deadline(value):
        """Return (ok, date_or_none)."""
        if value is None:
            return True, None
        if not isinstance(value, str):
            return False, None
        try:
            return True, date.fromisoformat(value)
        except ValueError:
            try:
                return True, datetime.fromisoformat(value).date()
            except ValueError:
                return False, None

    @classmethod
    def check(cls, record) -> str | None:
        """Return defect reason or None if the record is valid."""
        if not isinstance(record, dict):
            return "not_an_object"
        for name in cls.RECORD_FIELDS:
            if name not in record:
                return f"missing_field:{name}"
        for name in ("income_total", "expense_total", "bliq", "r_bench"):
            if not cls.money_ok(record[name]):
                return f"bad_number:{name}"
        risk = record["risk_tolerance"]
        if isinstance(risk, bool) or not isinstance(risk, int) \
                or risk not in CUSHION_MONTHS:
            if not (isinstance(risk, float) and risk in CUSHION_MONTHS
                    and float(risk).is_integer()):
                return "bad_risk_tolerance"
        if not isinstance(record["obligations"], list):
            return "obligations_not_list"
        for item in record["obligations"]:
            if not isinstance(item, dict):
                return "obligation_not_object"
            for name in cls.OBLIGATION_FIELDS:
                if name not in item:
                    return f"obligation_missing:{name}"
            for name in ("amount", "interest_rate", "monthly_payment"):
                if not cls.money_ok(item[name]):
                    return f"obligation_bad_number:{name}"
        if not isinstance(record["goals"], list):
            return "goals_not_list"
        for item in record["goals"]:
            if not isinstance(item, dict):
                return "goal_not_object"
            for name in cls.GOAL_FIELDS:
                if name not in item:
                    return f"goal_missing:{name}"
            for name in ("target_amount", "current_amount"):
                if not cls.money_ok(item[name]):
                    return f"goal_bad_number:{name}"
            ok, _ = cls.parse_deadline(item["deadline"])
            if not ok:
                return "goal_bad_deadline"
        return None


class Advisor:
    """Applies methodology §§1-5 to a validated record."""

    def decide(self, record: dict) -> Decision:
        row_id = str(record["id"])
        income = float(record["income_total"])
        expense = float(record["expense_total"])
        obligations = record["obligations"]
        payments = sum(float(o["monthly_payment"]) for o in obligations)
        flow = income - expense - payments
        essentials = expense + payments
        risk = int(record["risk_tolerance"])
        bliq = float(record["bliq"])
        r_bench = float(record["r_bench"])
        target_cushion = CUSHION_MONTHS[risk] * essentials

        toxic_total, expensive_total = self._classify_debt(
            obligations, r_bench)

        status = "ok" if flow >= 0 else "deficit"
        lump, toxic_left, expensive_left, bliq_left = self._lump_moves(
            status=status, flow=flow, bliq=bliq, essentials=essentials,
            target_cushion=target_cushion, risk=risk,
            toxic_total=toxic_total, expensive_total=expensive_total,
            goals=record["goals"])

        decision = Decision(row_id=row_id, status=status, lump=int(lump))
        if status == "deficit" or flow < 1.0:
            # flow in [0, 1) floors to 0 rubles: nothing to allocate.
            return decision

        res, debt, goal, inv = self._monthly_plan(
            flow=flow, bliq_left=bliq_left, target_cushion=target_cushion,
            toxic_left=toxic_left, expensive_left=expensive_left,
            goals=record["goals"])
        decision.res, decision.debt, decision.goal, decision.inv = (
            res, debt, goal, inv)
        decision.dom = self._dominant(res, debt, goal, inv)
        return decision

    @staticmethod
    def _classify_debt(obligations: list, r_bench: float) -> tuple:
        toxic = 0.0
        expensive = 0.0
        for item in obligations:
            amount = float(item["amount"])
            if amount <= 0:
                continue
            rate = float(item["interest_rate"])
            payment = float(item["monthly_payment"])
            interest_only = rate > 0 and payment <= amount * rate / 12.0
            spread = rate - r_bench
            if interest_only or spread >= TOXIC_SPREAD:
                toxic += amount
            elif spread >= EXPENSIVE_SPREAD:
                expensive += amount
        return toxic, expensive

    @staticmethod
    def _months_to(deadline: date) -> int:
        days = (deadline - CUTOFF_DATE).days
        if days <= 0:
            return 1
        return max(1, round(days / 30.44))

    def _goal_monthly_need(self, goals: list) -> float:
        need = 0.0
        for item in goals:
            _, deadline = Validator.parse_deadline(item["deadline"])
            if deadline is None:
                continue
            shortfall = float(item["target_amount"]) - \
                float(item["current_amount"])
            if shortfall <= 0:
                continue
            need += shortfall / self._months_to(deadline)
        return need

    @staticmethod
    def _goal_shortfall_dated(goals: list) -> float:
        total = 0.0
        for item in goals:
            _, deadline = Validator.parse_deadline(item["deadline"])
            if deadline is None:
                continue
            shortfall = float(item["target_amount"]) - \
                float(item["current_amount"])
            if shortfall > 0:
                total += shortfall
        return total

    def _lump_moves(self, status: str, flow: float, bliq: float,
                    essentials: float, target_cushion: float, risk: int,
                    toxic_total: float, expensive_total: float,
                    goals: list) -> tuple:
        lump = 0.0
        bliq_left = bliq
        toxic_left = toxic_total
        expensive_left = expensive_total

        # Step 1: toxic debt payoff, floor 2 months of essentials.
        available = max(0.0, bliq_left - 2.0 * essentials)
        pay = min(available, toxic_left)
        if pay >= LUMP_MIN_BLOCK:
            lump += pay
            bliq_left -= pay
            toxic_left -= pay

        # Step 2: expensive debt payoff.
        floor = 3.0 * essentials if status == "deficit" else target_cushion
        available = max(0.0, bliq_left - floor)
        pay = min(available, expensive_left)
        if pay >= LUMP_MIN_BLOCK:
            lump += pay
            bliq_left -= pay
            expensive_left -= pay

        # Step 3: deploy surplus (ok clients with positive flow, risk 2-5).
        if status == "ok" and flow > 0 and risk >= 2:
            surplus = max(0.0, bliq_left - target_cushion)
            if surplus >= LUMP_MIN_INVEST:
                lump += surplus
                bliq_left -= surplus
        return lump, toxic_left, expensive_left, bliq_left

    def _monthly_plan(self, flow: float, bliq_left: float,
                      target_cushion: float, toxic_left: float,
                      expensive_left: float, goals: list) -> tuple:
        if toxic_left > 0:
            debt_class = "toxic"
        elif expensive_left > 0:
            debt_class = "expensive"
        else:
            debt_class = "clean"
        cushion_low = bliq_left < target_cushion
        res_share, debt_share = SHARES[(debt_class, cushion_low)]

        budget = math.floor(flow)
        debt = min(debt_share * flow, toxic_left + expensive_left)
        res = min(res_share * flow,
                  max(0.0, target_cushion - bliq_left))
        rest = flow - debt - res
        need = self._goal_monthly_need(goals)
        goal = min(need, rest)
        inv = rest - goal

        res, debt, goal, inv = (int(res), int(debt), int(goal), int(inv))
        leftover = budget - (res + debt + goal + inv)
        buckets = {"res": res, "debt": debt, "goal": goal, "inv": inv}
        largest = max(buckets, key=lambda k: (buckets[k],
                                              k == "debt", k == "res"))
        buckets[largest] += leftover
        return buckets["res"], buckets["debt"], buckets["goal"], buckets["inv"]

    @staticmethod
    def _dominant(res: int, debt: int, goal: int, inv: int) -> str:
        goals_plus = goal + inv
        if res == 0 and debt == 0 and goals_plus == 0:
            return "none"
        best = max(debt, res, goals_plus)
        if debt == best:
            return "debt"
        if res == best:
            return "reserve"
        return "goals+"


class Runner:
    """Streams the four parts and writes the CSV."""

    def __init__(self, input_dir: Path, output_csv: Path):
        self.input_dir = input_dir
        self.output_csv = output_csv
        self.validator = Validator()
        self.advisor = Advisor()
        self.stats = RunStats()

    def run(self) -> RunStats:
        parts = sorted(self.input_dir.glob(
            "expert_portraits_v3_part*_jsonl.gz"))
        with open(self.output_csv, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["id", "status", "dom", "res", "debt", "goal", "inv", "lump"])
            for part in parts:
                self._process_part(part, writer)
        return self.stats

    def _process_part(self, part: Path, writer) -> None:
        with gzip.open(part, "rt", encoding="utf-8") as handle:
            for raw in handle:
                raw = raw.strip()
                if not raw:
                    continue
                decision = self._decide_line(raw)
                if decision.status == "skip":
                    continue
                self._account(decision)
                writer.writerow(decision.as_row())

    def _decide_line(self, raw: str) -> Decision:
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            self.stats.bump_reason("json_parse_error")
            return Decision(row_id=self._salvage_id(raw), status="invalid")
        if isinstance(record, dict) and record.get("__meta__") is True:
            return Decision(row_id="__meta__", status="skip")
        reason = self.validator.check(record)
        if reason is not None:
            self.stats.bump_reason(reason)
            row_id = self._salvage_id(raw) if not isinstance(record, dict) \
                or "id" not in record else str(record["id"])
            return Decision(row_id=row_id, status="invalid")
        return self.advisor.decide(record)

    @staticmethod
    def _salvage_id(raw: str) -> str:
        match = ID_RE.search(raw)
        return match.group(0) if match else "UNKNOWN"

    def _account(self, decision: Decision) -> None:
        self.stats.total += 1
        if decision.status == "invalid":
            self.stats.invalid += 1
        elif decision.status == "ok":
            self.stats.ok += 1
        else:
            self.stats.deficit += 1
        self.stats.dom_counts[decision.dom] = \
            self.stats.dom_counts.get(decision.dom, 0) + 1
        if decision.lump > 0:
            self.stats.lump_positive += 1


def main() -> None:
    runner = Runner(Path("/mnt/user-data/uploads"),
                    Path("/home/claude/out/expert_allocations_v3.csv"))
    stats = runner.run()
    print(json.dumps({
        "total": stats.total, "ok": stats.ok, "deficit": stats.deficit,
        "invalid": stats.invalid, "dom": stats.dom_counts,
        "lump_positive": stats.lump_positive,
        "invalid_reasons": stats.invalid_reasons,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
