"""FINPILOT benchmark — independent expert allocation engine.

A deterministic personal-finance advisor for the Russian market, mid-2026.
Constants are fixed a priori (see AdvisorConfig) and applied uniformly to
every portrait. No fitting to the dataset; rules encode professional
judgement only. Output matches the CSV contract of expert_brief_v2.md:

    id,status,dom,res,debt,goal,inv,lump

Environment note: r_bench (risk-free / deposit alternative) sits at 10-20%,
so the governing arbitrage is "prepay a loan only if its rate exceeds the
risk-free rate" — otherwise cash is better left earning r_bench.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable


CUT_DATE = date(2026, 7, 11)


@dataclass(frozen=True)
class AdvisorConfig:
    """All decision constants, frozen before any data is seen."""

    # Emergency fund target, in months of (expense + mandatory debt service),
    # thinner for more risk-tolerant clients.
    cushion_months: dict[int, int] = field(
        default_factory=lambda: {1: 6, 2: 6, 3: 5, 4: 4, 5: 3}
    )
    # Starter cushion that must exist before anything but survival.
    floor_months: float = 1.0
    # A loan is "expensive" / worth prepaying if rate > r_bench + spread.
    expensive_spread: float = 0.0
    # A lump may fully close a goal whose deadline is within this horizon.
    goal_nearterm_months: int = 12
    # Conceptual equity share by risk profile (documented; not needed for the
    # single inv figure the CSV asks for, but fixes the allocation policy).
    equity_share: dict[int, float] = field(
        default_factory=lambda: {1: 0.10, 2: 0.25, 3: 0.45, 4: 0.65, 5: 0.85}
    )


@dataclass
class Portrait:
    pid: str
    income: float
    expense: float
    bliq: float
    r_bench: float
    risk: int
    obligations: list[dict]
    goals: list[dict]

    @classmethod
    def from_json(cls, obj: dict) -> "Portrait":
        return cls(
            pid=obj["id"],
            income=float(obj["income_total"]),
            expense=float(obj["expense_total"]),
            bliq=float(obj["bliq"]),
            r_bench=float(obj["r_bench"]),
            risk=int(obj["risk_tolerance"]),
            obligations=list(obj.get("obligations", [])),
            goals=list(obj.get("goals", [])),
        )


@dataclass
class Recommendation:
    pid: str
    status: str
    dom: str
    res: int
    debt: int
    goal: int
    inv: int
    lump: int

    def as_csv_row(self) -> str:
        return (
            f"{self.pid},{self.status},{self.dom},"
            f"{self.res},{self.debt},{self.goal},{self.inv},{self.lump}"
        )


class AdvisorEngine:
    """Applies the fixed ruleset to a single portrait."""

    def __init__(self, config: AdvisorConfig | None = None) -> None:
        self.cfg = config or AdvisorConfig()

    # ---- diagnostics -------------------------------------------------
    def _debt_service(self, p: Portrait) -> float:
        return sum(float(o["monthly_payment"]) for o in p.obligations)

    def _free_cash_flow(self, p: Portrait) -> float:
        return p.income - p.expense - self._debt_service(p)

    def _target_cushion(self, p: Portrait) -> float:
        months = self.cfg.cushion_months[p.risk]
        return months * (p.expense + self._debt_service(p))

    def _expensive_loans(self, p: Portrait) -> list[dict]:
        thr = p.r_bench + self.cfg.expensive_spread
        loans = [o for o in p.obligations if float(o["interest_rate"]) > thr]
        return sorted(loans, key=lambda o: float(o["interest_rate"]), reverse=True)

    def _months_to(self, deadline: str | None) -> float | None:
        if not deadline:
            return None
        try:
            d = date.fromisoformat(deadline)
        except (ValueError, TypeError):
            return None
        return (d - CUT_DATE).days / 30.4375

    # ---- lump moves from the liquid cushion --------------------------
    def _lump(self, p: Portrait, deficit: bool) -> int:
        deployable = p.bliq - self._target_cushion(p)
        if p.income <= 0 or deployable <= 0:
            return 0  # zero income -> preserve runway; no excess -> keep cushion

        used = 0.0
        remaining = deployable

        # 1) retire expensive debt from the excess (guaranteed arbitrage win)
        for loan in self._expensive_loans(p):
            if remaining <= 0:
                break
            pay = min(remaining, float(loan["amount"]))
            used += pay
            remaining -= pay

        if deficit:
            return int(round(used))  # for deficit clients, deleverage only

        # 2) close a near-term, almost-funded goal if it fits the excess
        for g in p.goals:
            if remaining <= 0:
                break
            gap = max(0.0, float(g["target_amount"]) - float(g["current_amount"]))
            m = self._months_to(g.get("deadline"))
            if gap > 0 and m is not None and m <= self.cfg.goal_nearterm_months:
                if gap <= remaining:
                    used += gap
                    remaining -= gap

        # 3) deploy the rest of the excess into investments
        used += max(0.0, remaining)
        return int(round(used))

    # ---- monthly free-cash-flow waterfall ----------------------------
    def _allocate_flow(self, p: Portrait, fcf: float) -> tuple[int, int, int, int]:
        remaining = fcf
        res = debt = goal = inv = 0.0

        outflow = p.expense + self._debt_service(p)
        floor = self.cfg.floor_months * outflow
        target = self._target_cushion(p)

        # 1) starter cushion
        if p.bliq < floor:
            add = min(remaining, floor - p.bliq)
            res += add
            remaining -= add

        # 2) expensive debt (avalanche) — prepay while flow lasts
        if self._expensive_loans(p) and remaining > 0:
            debt += remaining
            remaining = 0.0

        # 3) top the cushion up to full target
        if remaining > 0 and p.bliq + res < target:
            add = min(remaining, target - (p.bliq + res))
            res += add
            remaining -= add

        # 4) dated goals — required monthly contribution to hit the deadline
        if remaining > 0:
            need = 0.0
            for g in p.goals:
                gap = max(0.0, float(g["target_amount"]) - float(g["current_amount"]))
                m = self._months_to(g.get("deadline"))
                if gap > 0 and m is not None:
                    need += gap / max(1.0, m)  # overdue -> catch up within a month
            if need > 0:
                add = min(remaining, need)
                goal += add
                remaining -= add

        # 5) surplus -> investments
        if remaining > 0:
            inv += remaining
            remaining = 0.0

        return self._round_split(fcf, res, debt, goal, inv)

    @staticmethod
    def _round_split(
        fcf: float, res: float, debt: float, goal: float, inv: float
    ) -> tuple[int, int, int, int]:
        cap = int(fcf)  # never allocate more than the (floored) free flow
        vals = [int(round(x)) for x in (res, debt, goal, inv)]
        drift = sum(vals) - cap
        if drift > 0:  # trim rounding overflow from the largest bucket
            i = max(range(4), key=lambda k: vals[k])
            vals[i] = max(0, vals[i] - drift)
        return tuple(vals)  # type: ignore[return-value]

    # ---- public ------------------------------------------------------
    def evaluate(self, p: Portrait) -> Recommendation:
        fcf = self._free_cash_flow(p)
        deficit = p.income <= 0 or fcf < 0

        if deficit:
            return Recommendation(
                pid=p.pid, status="deficit", dom="none",
                res=0, debt=0, goal=0, inv=0, lump=self._lump(p, deficit=True),
            )

        res, debt, goal, inv = self._allocate_flow(p, fcf)
        goals_plus = goal + inv
        buckets = {"debt": debt, "reserve": res, "goals+": goals_plus}
        dom = max(buckets, key=buckets.get) if max(buckets.values()) > 0 else "none"
        return Recommendation(
            pid=p.pid, status="ok", dom=dom,
            res=res, debt=debt, goal=goal, inv=inv, lump=self._lump(p, deficit=False),
        )


def load_portraits(paths: Iterable[str]) -> list[Portrait]:
    out: list[Portrait] = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            out.extend(Portrait.from_json(json.loads(l)) for l in fh if l.strip())
    return out


def run(paths: Iterable[str], engine: AdvisorEngine | None = None) -> list[Recommendation]:
    eng = engine or AdvisorEngine()
    return [eng.evaluate(p) for p in load_portraits(paths)]
