"""FINPILOT expert-certification round 4 — independent scoring engine.

Deterministic, object-oriented implementation of the methodology frozen in
``expert_methodology_v4.md``. Processes all 12 000 portraits positionally
(one answer row per input row, input order preserved) and emits the three
core artefacts. Constants live in :class:`Constants` and are overridable so the
sensitivity study can re-run the same rows with a single shifted knob.

Python 3 only. PEP 8. No side effects on import.
"""

from __future__ import annotations

import csv
import datetime as _dt
import gzip
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

FROZEN = _dt.date(2026, 7, 18)
_DAYS_PER_MONTH = 30.44


# --------------------------------------------------------------------------- #
# Constants (frozen before processing; see expert_methodology_v4.md §10)       #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Constants:
    reserve_months: Dict[int, int] = field(
        default_factory=lambda: {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}
    )
    starter_months: int = 1
    dear_spread: float = 0.03
    toxic_abs: float = 0.35
    toxic_spread: float = 0.20
    invalid_rate: float = 3.00
    lump_min: float = 5000.0
    goal_close_frac: float = 0.85
    urgent_months: int = 12
    surplus_buffer: float = 1.25
    reserve_fill_months: int = 12
    surplus_inv_share: Dict[int, float] = field(
        default_factory=lambda: {1: 0.20, 2: 0.40, 3: 0.60, 4: 0.80, 5: 1.00}
    )
    stress_magnitude: float = 1e8


# --------------------------------------------------------------------------- #
# Small value helpers                                                          #
# --------------------------------------------------------------------------- #
def is_number(value: Any) -> bool:
    """True for a real (non-bool) int/float."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        _dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def days_to_deadline(deadline: str) -> int:
    return (_dt.date.fromisoformat(deadline) - FROZEN).days


# --------------------------------------------------------------------------- #
# Validation                                                                   #
# --------------------------------------------------------------------------- #
class Validator:
    """Implements the ``invalid`` criterion (methodology §7)."""

    TOP_KEYS = (
        "id", "income_total", "expense_total", "obligations",
        "goals", "bliq", "r_bench", "risk_tolerance",
    )
    MONEY_KEYS = ("income_total", "expense_total", "bliq", "r_bench")

    def __init__(self, const: Constants) -> None:
        self._const = const

    def reasons(self, rec: Dict[str, Any]) -> List[str]:
        out: List[str] = []
        for key in self.TOP_KEYS:
            if key not in rec:
                out.append(f"missing:{key}")
        for key in self.MONEY_KEYS:
            if key in rec:
                val = rec[key]
                if not is_number(val):
                    out.append(f"type:{key}")
                elif val < 0:
                    out.append(f"neg:{key}")
        if "risk_tolerance" in rec:
            rt = rec["risk_tolerance"]
            if not (isinstance(rt, int) and not isinstance(rt, bool)
                    and 1 <= rt <= 5):
                out.append("risk_bad")
        out.extend(self._obligation_reasons(rec.get("obligations")))
        out.extend(self._goal_reasons(rec.get("goals")))
        return out

    def _obligation_reasons(self, obligations: Any) -> List[str]:
        out: List[str] = []
        if obligations is None:
            return out
        if not isinstance(obligations, list):
            return ["type:obligations"]
        for ob in obligations:
            if not isinstance(ob, dict):
                out.append("ob_not_dict")
                continue
            for key in ("name", "amount", "interest_rate", "monthly_payment"):
                if key not in ob:
                    out.append(f"ob_missing:{key}")
            if not is_number(ob.get("amount")) or (
                    is_number(ob.get("amount")) and ob["amount"] < 0):
                out.append("ob_amount")
            if not is_number(ob.get("monthly_payment")) or (
                    is_number(ob.get("monthly_payment"))
                    and ob["monthly_payment"] < 0):
                out.append("ob_payment")
            rate = ob.get("interest_rate")
            if not is_number(rate):
                out.append("ob_rate_type")
            elif rate < 0:
                out.append("ob_rate_neg")
            elif rate > self._const.invalid_rate:
                out.append("ob_rate_high")
            if "name" in ob and not isinstance(ob["name"], str):
                out.append("ob_name_type")
        return out

    def _goal_reasons(self, goals: Any) -> List[str]:
        out: List[str] = []
        if goals is None:
            return out
        if not isinstance(goals, list):
            return ["type:goals"]
        for gl in goals:
            if not isinstance(gl, dict):
                out.append("goal_not_dict")
                continue
            for key in ("name", "target_amount", "current_amount"):
                if key not in gl:
                    out.append(f"goal_missing:{key}")
            if "deadline" not in gl:
                out.append("goal_missing:deadline")
            else:
                dl = gl["deadline"]
                if dl is not None and not is_iso_date(dl):
                    out.append("goal_deadline_bad")
            for key in ("target_amount", "current_amount"):
                if not is_number(gl.get(key)) or (
                        is_number(gl.get(key)) and gl[key] < 0):
                    out.append(f"goal_{key}")
            if "name" in gl and not isinstance(gl["name"], str):
                out.append("goal_name_type")
        return out

    def is_valid(self, rec: Dict[str, Any]) -> bool:
        return not self.reasons(rec)


# --------------------------------------------------------------------------- #
# Domain wrappers                                                              #
# --------------------------------------------------------------------------- #
class Debt:
    __slots__ = ("name", "amount", "rate", "payment", "remaining",
                 "klass", "interest_only", "growing")

    def __init__(self, name: str, amount: float, rate: float,
                 payment: float) -> None:
        self.name = name
        self.amount = float(amount)
        self.rate = float(rate)
        self.payment = float(payment)
        self.remaining = float(amount)
        self.klass = "cheap"
        self.interest_only = False
        self.growing = False


class Goal:
    __slots__ = ("name", "target", "current", "deadline", "remaining",
                 "days", "months_left", "required", "state")

    def __init__(self, name: str, target: float, current: float,
                 deadline: Optional[str]) -> None:
        self.name = name
        self.target = float(target)
        self.current = float(current)
        self.deadline = deadline
        self.remaining = max(0.0, self.target - self.current)
        self.days: Optional[int] = (
            None if deadline is None else days_to_deadline(deadline)
        )
        self.months_left: Optional[int] = None
        self.required = 0.0
        self.state = "underfunded"


# --------------------------------------------------------------------------- #
# Result container                                                             #
# --------------------------------------------------------------------------- #
@dataclass
class Result:
    id: str
    status: str
    dom: str
    res: int = 0
    debt: int = 0
    goal: int = 0
    inv: int = 0
    lump: int = 0
    confidence: int = 5
    flags: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    debt_plan: List[Dict[str, Any]] = field(default_factory=list)
    lump_sum_plan: List[Dict[str, Any]] = field(default_factory=list)
    monthly_plan: List[Dict[str, Any]] = field(default_factory=list)
    goal_plan: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)
    verdict: str = ""

    def csv_row(self) -> List[Any]:
        return [self.id, self.status, self.dom, self.res, self.debt,
                self.goal, self.inv, self.lump, self.confidence]


# --------------------------------------------------------------------------- #
# Planner — the actual expert logic                                            #
# --------------------------------------------------------------------------- #
class Planner:
    def __init__(self, const: Constants) -> None:
        self._c = const

    # -- diagnostics ------------------------------------------------------- #
    def _build_debts(self, rec: Dict[str, Any], r_bench: float) -> List[Debt]:
        debts: List[Debt] = []
        c = self._c
        for ob in rec["obligations"]:
            d = Debt(ob["name"], ob["amount"], ob["interest_rate"],
                     ob["monthly_payment"])
            if d.rate >= c.toxic_abs or d.rate >= r_bench + c.toxic_spread:
                d.klass = "toxic"
            elif d.rate > r_bench + c.dear_spread:
                d.klass = "expensive"
            else:
                d.klass = "cheap"
            monthly_interest = d.amount * d.rate / 12.0
            d.interest_only = d.payment <= monthly_interest + 1e-9
            d.growing = d.payment < monthly_interest - 1e-9
            debts.append(d)
        return debts

    def _build_goals(self, rec: Dict[str, Any]) -> List[Goal]:
        goals: List[Goal] = []
        for gl in rec["goals"]:
            g = Goal(gl["name"], gl["target_amount"], gl["current_amount"],
                     gl["deadline"])
            if g.remaining <= 0:
                g.state = "overfunded" if g.current > g.target else "closed"
            elif g.days is not None and g.days < 0:
                g.state = "overdue"
                g.months_left = 1
                g.required = g.remaining
            elif g.days is not None:
                g.months_left = max(1, round(g.days / _DAYS_PER_MONTH))
                g.required = g.remaining / g.months_left
                if g.days == 0:
                    g.state, g.required = "overdue", g.remaining
                else:
                    g.state = "dated"
            else:
                g.state = "perpetual"
            goals.append(g)
        return goals

    # -- main entry -------------------------------------------------------- #
    def plan(self, rec: Dict[str, Any]) -> Result:
        c = self._c
        income = float(rec["income_total"])
        expense = float(rec["expense_total"])
        bliq = float(rec["bliq"])
        r_bench = float(rec["r_bench"])
        risk = int(rec["risk_tolerance"])

        debts = self._build_debts(rec, r_bench)
        goals = self._build_goals(rec)

        pay_total = sum(d.payment for d in debts)
        burn = expense + pay_total
        fcf = income - expense - pay_total
        pdn = (pay_total / income) if income > 0 else math.inf
        reserve_target = c.reserve_months[risk] * burn
        starter = c.starter_months * burn
        liquidity_months = (bliq / burn) if burn > 0 else math.inf

        res = Result(id=str(rec.get("id", "")), status="ok", dom="none")
        res.diagnostics = {
            "fcf": round(fcf, 2),
            "monthly_burn": round(burn, 2),
            "bliq": round(bliq, 2),
            "pdn": None if math.isinf(pdn) else round(pdn, 4),
            "liquidity_months": (None if math.isinf(liquidity_months)
                                 else round(liquidity_months, 2)),
            "reserve_target": round(reserve_target, 2),
            "starter_reserve": round(starter, 2),
            "n_debts": len(debts),
            "debt_total": round(sum(d.amount for d in debts), 2),
            "n_goals": len(goals),
        }

        flags = self._flags(income, expense, bliq, fcf, pdn, liquidity_months,
                            risk, debts, goals)
        res.flags = flags

        bliq_left, lump_plan = self._lump_moves(
            bliq, starter, reserve_target, debts, goals, risk)
        res.lump_sum_plan = lump_plan
        res.lump = int(sum(item["amount"] for item in lump_plan))

        if fcf > 0:
            buckets = self._monthly_split(
                fcf, bliq_left, starter, reserve_target, debts, goals, risk)
            res.status = "ok"
        else:
            buckets = {"res": 0, "debt": 0, "goal": 0, "inv": 0}
            res.status = "deficit" if fcf < 0 else "ok"

        res.res, res.debt = buckets["res"], buckets["debt"]
        res.goal, res.inv = buckets["goal"], buckets["inv"]
        res.dom = self._dominant(buckets)
        res.monthly_plan = [
            {"bucket": k, "amount": v} for k, v in
            (("reserve", res.res), ("debt", res.debt),
             ("goal", res.goal), ("inv", res.inv)) if v > 0
        ]
        res.debt_plan = self._debt_plan(debts, r_bench)
        res.goal_plan = self._goal_plan(goals)
        res.confidence = self._confidence(
            income, fcf, pdn, liquidity_months, risk, r_bench, debts, goals)
        res.totals = {
            "res": res.res, "debt": res.debt, "goal": res.goal,
            "inv": res.inv, "lump": res.lump,
            "monthly_sum": res.res + res.debt + res.goal + res.inv,
            "fcf_floor": max(0, math.floor(fcf)),
        }
        res.verdict = self._verdict(res, fcf, burn, debts, goals, risk)
        return res

    # -- lump waterfall ---------------------------------------------------- #
    def _lump_moves(self, bliq: float, starter: float, full: float,
                    debts: List[Debt], goals: List[Goal],
                    risk: int) -> Tuple[float, List[Dict[str, Any]]]:
        c = self._c
        plan: List[Dict[str, Any]] = []
        left = bliq

        # 1. toxic debt, down to starter reserve
        for d in sorted([x for x in debts if x.klass == "toxic"],
                        key=lambda x: -x.rate):
            avail = max(0.0, left - starter)
            paid = math.floor(min(avail, d.remaining))
            if paid >= c.lump_min:
                d.remaining -= paid
                if d.remaining < 1.0:
                    d.remaining = 0.0
                left -= paid
                plan.append({"action": "pay_toxic_debt", "name": d.name,
                             "amount": int(paid)})

        # 2. expensive debt, down to full reserve
        for d in sorted([x for x in debts if x.klass == "expensive"],
                        key=lambda x: -x.rate):
            avail = max(0.0, left - full)
            paid = math.floor(min(avail, d.remaining))
            if paid >= c.lump_min:
                d.remaining -= paid
                if d.remaining < 1.0:
                    d.remaining = 0.0
                left -= paid
                plan.append({"action": "pay_expensive_debt", "name": d.name,
                             "amount": int(paid)})

        # 3. close near-complete urgent goals
        for g in sorted([x for x in goals if x.remaining > 0],
                        key=lambda x: (x.days if x.days is not None else 10 ** 9)):
            urgent = g.days is not None and g.days <= c.urgent_months * _DAYS_PER_MONTH
            funded = g.current >= c.goal_close_frac * g.target if g.target > 0 else False
            if urgent and funded:
                avail = max(0.0, left - full)
                paid = math.floor(min(avail, g.remaining))
                if paid >= c.lump_min:
                    g.remaining -= paid
                    if g.remaining < 1.0:
                        g.remaining = 0.0
                    left -= paid
                    g.state = "closed"
                    plan.append({"action": "close_goal", "name": g.name,
                                 "amount": int(paid)})

        # 4. deploy clear surplus
        toxic_left = any(d.klass == "toxic" and d.remaining > 0 for d in debts)
        exp_left = any(d.klass == "expensive" and d.remaining > 0 for d in debts)
        urgent_underfunded = any(
            g.remaining > 0 and g.days is not None
            and g.days <= c.urgent_months * _DAYS_PER_MONTH for g in goals)
        if not toxic_left and not exp_left and not urgent_underfunded:
            keep = c.surplus_buffer * full
            surplus = left - keep
            if surplus >= c.lump_min:
                surplus = float(math.floor(surplus))
                left -= surplus
                where = "invest" if risk >= 3 else "risk_free"
                plan.append({"action": f"deploy_surplus_{where}",
                             "name": "bliq", "amount": int(surplus)})
        return left, plan

    # -- monthly waterfall ------------------------------------------------- #
    def _monthly_split(self, fcf: float, bliq: float, starter: float,
                       full: float, debts: List[Debt], goals: List[Goal],
                       risk: int) -> Dict[str, int]:
        c = self._c
        pool = float(math.floor(fcf))
        b = {"res": 0.0, "debt": 0.0, "goal": 0.0, "inv": 0.0}

        # 1. starter reserve gap
        gap = max(0.0, starter - bliq)
        take = min(pool, gap)
        b["res"] += take
        pool -= take
        reserve_now = bliq + b["res"]

        # 2. toxic prepayment
        toxic_rem = sum(d.remaining for d in debts if d.klass == "toxic")
        take = min(pool, toxic_rem)
        b["debt"] += take
        pool -= take

        # 3. expensive prepayment
        exp_rem = sum(d.remaining for d in debts if d.klass == "expensive")
        take = min(pool, exp_rem)
        b["debt"] += take
        pool -= take

        # 4. full reserve, capped over reserve_fill_months
        gap_full = max(0.0, full - reserve_now)
        cap = gap_full / c.reserve_fill_months
        take = min(pool, cap)
        b["res"] += take
        pool -= take

        # 5. dated / overdue goal minimums, nearest deadline first
        dated = sorted([g for g in goals if g.state in ("dated", "overdue")
                        and g.remaining > 0],
                       key=lambda g: (g.days if g.days is not None else 10 ** 9))
        for g in dated:
            take = min(pool, g.required)
            b["goal"] += take
            pool -= take

        # 6-7. surplus split by risk: inv vs (perpetual goals then reserve)
        if pool > 0:
            inv_part = pool * c.surplus_inv_share[risk]
            other = pool - inv_part
            b["inv"] += inv_part
            perp_rem = sum(g.remaining for g in goals if g.state == "perpetual")
            goal_take = min(other, perp_rem)
            b["goal"] += goal_take
            b["res"] += other - goal_take
            pool = 0.0

        return {k: int(math.floor(v)) for k, v in b.items()}

    # -- reporting helpers ------------------------------------------------- #
    @staticmethod
    def _dominant(buckets: Dict[str, int]) -> str:
        groups = [
            ("debt", buckets["debt"]),
            ("reserve", buckets["res"]),
            ("goals+", buckets["goal"] + buckets["inv"]),
        ]
        best = max(groups, key=lambda kv: kv[1])
        return best[0] if best[1] > 0 else "none"

    def _debt_plan(self, debts: List[Debt], r_bench: float) -> List[Dict[str, Any]]:
        plan = []
        for d in debts:
            if d.klass == "toxic":
                action = "attack_first"
            elif d.klass == "expensive":
                action = "prepay_after_floor"
            else:
                action = "minimum_only"
            plan.append({
                "name": d.name, "amount": round(d.amount, 2),
                "rate": round(d.rate, 4), "spread": round(d.rate - r_bench, 4),
                "class": d.klass, "action": action,
                "remaining_after_lump": round(d.remaining, 2),
                "interest_only": d.interest_only, "growing": d.growing,
            })
        return plan

    def _goal_plan(self, goals: List[Goal]) -> List[Dict[str, Any]]:
        plan = []
        for g in goals:
            plan.append({
                "name": g.name, "target": round(g.target, 2),
                "current": round(g.current, 2),
                "remaining": round(g.remaining, 2), "deadline": g.deadline,
                "months_left": g.months_left,
                "required_monthly": round(g.required, 2),
                "state": g.state,
            })
        return plan

    def _flags(self, income, expense, bliq, fcf, pdn, liq, risk, debts, goals):
        c = self._c
        f: List[str] = []
        if fcf < 0:
            f.append("deficit")
        if fcf == 0:
            f.append("zero_fcf")
        if income == 0:
            f.append("zero_income")
        if expense == 0:
            f.append("zero_expense")
        if bliq == 0:
            f.append("zero_bliq")
        if not math.isinf(pdn) and pdn > 0.80:
            f.append("severe_pdn")
        elif not math.isinf(pdn) and pdn > 0.40:
            f.append("high_pdn")
        if not debts:
            f.append("no_debts")
        if not goals:
            f.append("no_goals")
        if any(d.klass == "toxic" for d in debts):
            f.append("toxic_debt")
        if any(d.klass == "expensive" for d in debts):
            f.append("expensive_debt")
        if any(d.interest_only for d in debts):
            f.append("interest_only")
        if any(d.growing for d in debts):
            f.append("growing_debt")
        if not math.isinf(liq) and liq < c.starter_months:
            f.append("thin_cushion")
        if any(g.state == "overfunded" for g in goals):
            f.append("overfunded_goal")
        if any(g.state == "overdue" for g in goals):
            f.append("overdue_goal")
        if any(g.state == "perpetual" for g in goals):
            f.append("perpetual_goal")
        if any(g.days is not None and 0 < g.days <= c.urgent_months * _DAYS_PER_MONTH
               for g in goals):
            f.append("urgent_goal")
        if (income >= c.stress_magnitude or bliq >= c.stress_magnitude
                or any(d.amount >= c.stress_magnitude for d in debts)
                or any(g.target >= c.stress_magnitude for g in goals)):
            f.append("stress_magnitude")
        return f

    def _confidence(self, income, fcf, pdn, liq, risk, r_bench, debts, goals):
        c = self._c
        score = 5
        if abs(fcf) < max(5000.0, 0.05 * income):
            score -= 2
        if not math.isinf(pdn) and abs(pdn - 0.40) < 0.03:
            score -= 1
        bounds = [r_bench + c.dear_spread, c.toxic_abs, r_bench + c.toxic_spread]
        if any(any(abs(d.rate - bnd) < 0.02 for bnd in bounds) for d in debts):
            score -= 1
        if not math.isinf(liq) and abs(liq - c.reserve_months[risk]) < 0.5:
            score -= 1
        if any(g.days is not None and g.days <= 31 for g in goals):
            score -= 1
        if any(d.interest_only or d.growing for d in debts):
            score -= 1
        return max(1, min(5, score))

    def _verdict(self, res, fcf, burn, debts, goals, risk):
        parts: List[str] = []
        if res.status == "deficit":
            parts.append(f"Дефицит потока {fcf:,.0f} ₽/мес — режем расходы или "
                         f"реструктурируем долг".replace(",", " "))
        else:
            dom_ru = {"debt": "досрочное гашение долга", "reserve": "подушку",
                      "goals+": "цели и инвестиции", "none": "—"}[res.dom]
            if res.dom == "none":
                parts.append("Поток около нуля — свободных денег на манёвр почти нет")
            else:
                parts.append(f"Профицит: приоритет — {dom_ru}")
        if any(item["action"] == "pay_toxic_debt" for item in res.lump_sum_plan):
            parts.append("из подушки гасим токсичный долг")
        elif any(item["action"] == "pay_expensive_debt" for item in res.lump_sum_plan):
            parts.append("из излишка подушки гасим дорогой долг")
        if any(item["action"] == "close_goal" for item in res.lump_sum_plan):
            parts.append("закрываем почти готовую срочную цель разово")
        if any(item["action"].startswith("deploy_surplus") for item in res.lump_sum_plan):
            parts.append("избыток подушки размещаем")
        if "severe_pdn" in res.flags:
            parts.append("ПДН критический — приоритет разгрузке долга")
        if "overdue_goal" in res.flags:
            parts.append("есть просроченные цели — пересмотреть сроки")
        return "; ".join(parts) + "."


# --------------------------------------------------------------------------- #
# Engine orchestrator                                                          #
# --------------------------------------------------------------------------- #
class Engine:
    def __init__(self, const: Optional[Constants] = None) -> None:
        self._c = const or Constants()
        self._validator = Validator(self._c)
        self._planner = Planner(self._c)

    @staticmethod
    def load_rows(paths: List[str]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for path in paths:
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

    def process_record(self, rec: Dict[str, Any], index: int) -> Result:
        rid = str(rec.get("id", f"ROW-{index}")) if isinstance(rec, dict) else f"ROW-{index}"
        if not isinstance(rec, dict) or not self._validator.is_valid(rec):
            out = Result(id=rid, status="invalid", dom="none", confidence=5)
            out.flags = ["invalid"]
            out.verdict = "Дефектная запись — оценка не выполняется."
            out.totals = {"res": 0, "debt": 0, "goal": 0, "inv": 0,
                          "lump": 0, "monthly_sum": 0, "fcf_floor": 0}
            return out
        return self._planner.plan(rec)

    def run(self, rows: List[Dict[str, Any]]) -> List[Result]:
        return [self.process_record(rec, i) for i, rec in enumerate(rows)]

    # -- writers ----------------------------------------------------------- #
    @staticmethod
    def write_allocations(results: List[Result], path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["id", "status", "dom", "res", "debt", "goal",
                             "inv", "lump", "confidence"])
            for r in results:
                writer.writerow(r.csv_row())

    @staticmethod
    def write_summary(results: List[Result], path: str) -> None:
        cols = ["id", "status", "dom", "flags", "fcf", "pdn", "monthly_burn",
                "bliq", "liquidity_months", "reserve_target", "n_debts",
                "debt_total", "n_goals", "res", "debt", "goal", "inv", "lump"]
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(cols)
            for r in results:
                d = r.diagnostics
                writer.writerow([
                    r.id, r.status, r.dom, "|".join(r.flags),
                    d.get("fcf", ""), "" if d.get("pdn") is None else d.get("pdn"),
                    d.get("monthly_burn", ""), d.get("bliq", ""),
                    "" if d.get("liquidity_months") is None else d.get("liquidity_months"),
                    d.get("reserve_target", ""), d.get("n_debts", ""),
                    d.get("debt_total", ""), d.get("n_goals", ""),
                    r.res, r.debt, r.goal, r.inv, r.lump,
                ])

    @staticmethod
    def write_recommendations(results: List[Result], path: str) -> None:
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            for r in results:
                obj = {
                    "id": r.id, "status": r.status, "dom": r.dom,
                    "flags": r.flags, "diagnostics": r.diagnostics,
                    "debt_plan": r.debt_plan, "lump_sum_plan": r.lump_sum_plan,
                    "monthly_plan": r.monthly_plan, "goal_plan": r.goal_plan,
                    "totals": r.totals, "verdict": r.verdict,
                }
                handle.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main() -> None:
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    data = os.path.dirname(base)
    paths = [os.path.join(data, f"expert_portraits_v4_part{p}.jsonl.gz")
             for p in range(1, 5)]
    engine = Engine()
    rows = engine.load_rows(paths)
    results = engine.run(rows)
    engine.write_allocations(results, os.path.join(base, "expert_allocations_v4.csv"))
    engine.write_summary(results, os.path.join(base, "summary_v4.csv"))
    engine.write_recommendations(
        results, os.path.join(base, "recommendations_v4.jsonl.gz"))
    print(f"processed rows: {len(results)}")


if __name__ == "__main__":
    main()
