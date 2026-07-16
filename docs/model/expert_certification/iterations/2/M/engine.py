"""Independent expert decision engine for 12 000 financial portraits (round 2).

Implements the methodology fixed in expert_methodology_v2.md.
Output: strict CSV `id,status,dom,res,debt,goal,inv,lump`.
"""

import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date


AS_OF = date(2026, 7, 11)
RESERVE_MONTHS = {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}
EXPENSIVE_SPREAD = 0.02
MIN_LIQ_MONTHS = 3.0
CRIT_LIQ_MONTHS = 1.0
LUMP_GOAL_HORIZON_M = 12


@dataclass
class Loan:
    amount: float
    interest_rate: float
    monthly_payment: float


@dataclass
class Goal:
    target_amount: float
    current_amount: float
    deadline: date | None

    @property
    def remaining(self) -> float:
        return max(0.0, self.target_amount - self.current_amount)

    def months_left(self, as_of: date) -> int | None:
        if self.deadline is None:
            return None
        days = (self.deadline - as_of).days
        return max(1, math.ceil(days / 30.44))


@dataclass
class Portrait:
    pid: str
    income: float
    expense: float
    loans: list[Loan]
    goals: list[Goal]
    bliq: float
    r_bench: float
    risk: int

    @classmethod
    def from_json(cls, obj: dict) -> "Portrait":
        loans = [
            Loan(
                amount=max(0.0, float(o.get("amount", 0) or 0)),
                interest_rate=max(0.0, float(o.get("interest_rate", 0) or 0)),
                monthly_payment=max(0.0, float(o.get("monthly_payment", 0) or 0)),
            )
            for o in (obj.get("obligations") or [])
        ]
        goals = []
        for g in obj.get("goals") or []:
            deadline = None
            raw = g.get("deadline")
            if raw:
                try:
                    deadline = date.fromisoformat(str(raw))
                except ValueError:
                    deadline = None
            goals.append(
                Goal(
                    target_amount=max(0.0, float(g.get("target_amount", 0) or 0)),
                    current_amount=max(0.0, float(g.get("current_amount", 0) or 0)),
                    deadline=deadline,
                )
            )
        risk = obj.get("risk_tolerance", 3)
        risk = int(risk) if risk in (1, 2, 3, 4, 5) else 3
        return cls(
            pid=str(obj.get("id", "")),
            income=max(0.0, float(obj.get("income_total", 0) or 0)),
            expense=max(0.0, float(obj.get("expense_total", 0) or 0)),
            loans=loans,
            goals=goals,
            bliq=max(0.0, float(obj.get("bliq", 0) or 0)),
            r_bench=float(obj.get("r_bench", 0) or 0),
            risk=risk,
        )


@dataclass
class Decision:
    pid: str
    status: str
    dom: str
    res: int
    debt: int
    goal: int
    inv: int
    lump: int

    def to_row(self) -> str:
        return (
            f"{self.pid},{self.status},{self.dom},"
            f"{self.res},{self.debt},{self.goal},{self.inv},{self.lump}"
        )


@dataclass
class ExpertEngine:
    as_of: date = AS_OF
    violations: int = 0
    stats: dict = field(default_factory=dict)

    def decide(self, p: Portrait) -> Decision:
        payments = sum(loan.monthly_payment for loan in p.loans)
        fcf = p.income - p.expense - payments
        burn = p.expense + payments
        target_reserve = self._target_reserve(p, burn)
        expensive = [
            loan for loan in p.loans
            if loan.interest_rate >= p.r_bench + EXPENSIVE_SPREAD
        ]
        expensive_balance = sum(loan.amount for loan in expensive)

        if fcf < 0:
            lump = self._lump_deficit(p, target_reserve)
            return self._pack(p.pid, "deficit", 0.0, 0.0, 0.0, 0.0, lump, fcf)

        res, debt, goal, inv = self._monthly_split(
            p, fcf, burn, target_reserve, expensive_balance
        )
        lump = self._lump_ok(p, target_reserve)
        return self._pack(p.pid, "ok", res, debt, goal, inv, lump, fcf)

    def _target_reserve(self, p: Portrait, burn: float) -> float:
        base = burn if burn > 0 else 0.5 * p.income
        return RESERVE_MONTHS[p.risk] * base

    def _monthly_split(
        self,
        p: Portrait,
        fcf: float,
        burn: float,
        target_reserve: float,
        expensive_balance: float,
    ) -> tuple[float, float, float, float]:
        if fcf <= 0:
            return 0.0, 0.0, 0.0, 0.0
        liq_m = math.inf if burn <= 0 else p.bliq / burn
        has_exp = expensive_balance > 0
        res = debt = 0.0
        rest = 0.0
        if liq_m < CRIT_LIQ_MONTHS:
            debt = 0.3 * fcf if has_exp else 0.0
            res = fcf - debt
        elif liq_m < MIN_LIQ_MONTHS:
            debt = 0.6 * fcf if has_exp else 0.0
            res = fcf - debt
        elif p.bliq < target_reserve:
            if has_exp:
                debt = 0.7 * fcf
                res = fcf - debt
            else:
                res = 0.4 * fcf
                rest = fcf - res
        else:
            if has_exp:
                debt = 0.8 * fcf
                rest = fcf - debt
            else:
                rest = fcf
        overflow = max(0.0, debt - expensive_balance)
        debt -= overflow
        if p.bliq < target_reserve:
            res += overflow
        else:
            rest += overflow
        goal, inv = self._goals_split(p, rest)
        return res, debt, goal, inv

    def _goals_split(self, p: Portrait, avail: float) -> tuple[float, float]:
        if avail <= 0:
            return 0.0, 0.0
        req_dl = sum(
            g.remaining / g.months_left(self.as_of)
            for g in p.goals
            if g.deadline is not None and g.remaining > 0
        )
        goal_dl = min(avail, req_dl)
        leftover = avail - goal_dl
        perp_need = sum(
            g.remaining for g in p.goals
            if g.deadline is None and g.remaining > 0
        )
        goal_perp = min(0.5 * leftover, perp_need) if perp_need > 0 else 0.0
        return goal_dl + goal_perp, leftover - goal_perp

    def _lump_ok(self, p: Portrait, target_reserve: float) -> float:
        return max(0.0, p.bliq - target_reserve)

    def _lump_deficit(self, p: Portrait, target_reserve: float) -> float:
        deployable = max(0.0, p.bliq - target_reserve)
        debt_total = sum(loan.amount for loan in p.loans)
        return min(deployable, debt_total)

    def _pack(
        self,
        pid: str,
        status: str,
        res: float,
        debt: float,
        goal: float,
        inv: float,
        lump: float,
        fcf: float,
    ) -> Decision:
        res_i, debt_i, goal_i, inv_i = (
            int(res), int(debt), int(goal), int(inv)
        )
        if status == "ok" and fcf > 0 and res_i + debt_i + goal_i + inv_i == 0:
            res_i = int(fcf)
        if res_i + debt_i + goal_i + inv_i > max(0.0, fcf):
            self.violations += 1
        dom = self._dominant(status, fcf, res_i, debt_i, goal_i, inv_i)
        self.stats[dom] = self.stats.get(dom, 0) + 1
        self.stats[status] = self.stats.get(status, 0) + 1
        return Decision(pid, status, dom, res_i, debt_i, goal_i, inv_i, int(lump))

    @staticmethod
    def _dominant(
        status: str, fcf: float, res: int, debt: int, goal: int, inv: int
    ) -> str:
        if status == "deficit" or fcf <= 0:
            return "none"
        buckets = {"debt": debt, "reserve": res, "goals+": goal + inv}
        if max(buckets.values()) == 0:
            return "none"
        order = {"debt": 0, "reserve": 1, "goals+": 2}
        return max(buckets, key=lambda k: (buckets[k], -order[k]))


def main(src: str, dst: str) -> None:
    engine = ExpertEngine()
    rows = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            portrait = Portrait.from_json(json.loads(line))
            rows.append(engine.decide(portrait).to_row())
    with open(dst, "w", encoding="utf-8", newline="\n") as out:
        out.write("id,status,dom,res,debt,goal,inv,lump\n")
        out.write("\n".join(rows) + "\n")
    print(f"rows={len(rows)} balance_violations={engine.violations}")
    print(f"stats={engine.stats}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
