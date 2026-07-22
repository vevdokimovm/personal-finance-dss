#!/usr/bin/env python3
"""Independent financial expert engine, round 4 (dataset v4).

Direct programmatic implementation of ``expert_methodology_v4.md``:
validity rules, diagnostics, lump-sum ladder, monthly waterfall,
deterministic confidence scoring and one-line verdicts.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any, Optional

CUTOFF = date(2026, 7, 18)
DAYS_PER_MONTH = 30.4375
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
NUMSTR_RE = re.compile(r"^[\s\d.,'`’+\-−]+$")
ID_RE = re.compile(r"^SP4-\d{5}$")

TOP_REQUIRED = ("id", "income_total", "expense_total", "obligations",
                "goals", "bliq", "r_bench", "risk_tolerance")
OBLIG_REQUIRED = ("name", "amount", "interest_rate", "monthly_payment")
GOAL_REQUIRED = ("name", "target_amount", "current_amount", "deadline")


@dataclass(frozen=True)
class Config:
    """Frozen methodology constants (C-block)."""

    reserve_months: tuple = (6.0, 5.0, 4.0, 3.0, 3.0)
    floor_months: float = 1.0
    spread_expensive: float = 0.02
    toxic_rate: float = 0.45
    min_lump: float = 10_000.0
    min_toxic_partial: float = 1_000.0
    debt_share: float = 0.50
    reserve_build_months: float = 12.0
    pdn_elevated: float = 0.30
    pdn_overload: float = 0.50
    pdn_critical: float = 0.80
    deficit_runway_months: float = 3.0
    whale_income: float = 5_000_000.0
    stress_magnitude: float = 1e9
    rate_garbage: float = 3.0
    rate_suspicious: float = 2.92
    r_bench_max: float = 1.0
    equity_share: tuple = (0.0, 0.2, 0.4, 0.6, 0.8)


BASE_CONFIG = Config()

SENSITIVITY_VARIANTS = [
    ("S1a spread_expensive -20%", {"spread_expensive": 0.016}),
    ("S1b spread_expensive +20%", {"spread_expensive": 0.024}),
    ("S2a toxic_rate -20%", {"toxic_rate": 0.36}),
    ("S2b toxic_rate +20%", {"toxic_rate": 0.54}),
    ("S3a reserve_months x0.8", {"reserve_months": (4.8, 4.0, 3.2, 2.4, 2.4)}),
    ("S3b reserve_months x1.2", {"reserve_months": (7.2, 6.0, 4.8, 3.6, 3.6)}),
    ("S4a min_lump -20%", {"min_lump": 8_000.0}),
    ("S4b min_lump +20%", {"min_lump": 12_000.0}),
    ("S5a pdn_overload -20%", {"pdn_overload": 0.40}),
    ("S5b pdn_overload +20%", {"pdn_overload": 0.60}),
    ("S6a debt_share -20%", {"debt_share": 0.40}),
    ("S6b debt_share +20%", {"debt_share": 0.60}),
    ("S7a floor_months -20%", {"floor_months": 0.8}),
    ("S7b floor_months +20%", {"floor_months": 1.2}),
]

GROSS = "gross"
NEAR = "near_miss"


def rub0(x: float) -> str:
    """Format rubles with space thousands separators, no decimals."""
    return f"{x:,.0f}".replace(",", " ")


@dataclass
class Debt:
    name: str
    amount: float
    rate: float
    payment: float
    cls: str = "cheap"
    interest_only: bool = False
    suspicious: bool = False
    lump_paid: float = 0.0
    monthly_extra: int = 0

    @property
    def alive(self) -> bool:
        return self.amount > 0.004


@dataclass
class Goal:
    name: str
    target: float
    current: float
    deadline: Optional[date]
    has_deadline: bool = False
    lump_added: float = 0.0
    planned: int = 0
    required: float = 0.0
    months_left: Optional[float] = None
    immediate: bool = False

    @property
    def remaining(self) -> float:
        return max(0.0, self.target - self.current)

    @property
    def done(self) -> bool:
        return self.remaining <= 0.004


@dataclass
class Record:
    """One input line: either a parsed valid portrait or a defect."""

    idx: int
    rid: str
    valid: bool
    defects: list
    defect_class: str
    income: float = 0.0
    expense: float = 0.0
    debts: list = None
    goals: list = None
    bliq: float = 0.0
    r_bench: float = 0.0
    risk: int = 3
    extra_fields: bool = False
    empty_name: bool = False
    raw: dict = None


class RecordParser:
    """Validity rules of methodology §3 (brief §2), with assumption counters."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.assumption_hits: Counter = Counter()
        self.defect_counts: Counter = Counter()

    def parse_line(self, idx: int, line: str) -> Record:
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            self.assumption_hits["A14_parse_error_line"] += 1
            self.defect_counts["parse_error"] += 1
            return Record(idx, "", False, ["parse_error"], GROSS)
        if not isinstance(obj, dict):
            self.defect_counts["root_not_object"] += 1
            return Record(idx, "", False, ["root_not_object"], GROSS)
        return self.parse_obj(idx, obj)

    def parse_obj(self, idx: int, obj: dict) -> Record:
        defects: list = []
        classes: list = []
        rid = obj.get("id")
        rid_echo = rid if isinstance(rid, str) else ""

        for key in TOP_REQUIRED:
            if key not in obj:
                defects.append(f"missing_key:{key}")
                classes.append(GROSS)
        if "id" in obj and not isinstance(rid, str):
            defects.append("bad_type:id")
            classes.append(self._numlike_class(rid))
        if isinstance(rid, str) and not ID_RE.match(rid):
            self.assumption_hits["A20_id_pattern_not_validated"] += 1

        income = self._money(obj, "income_total", defects, classes)
        expense = self._money(obj, "expense_total", defects, classes)
        bliq = self._money(obj, "bliq", defects, classes)
        r_bench = self._rate_field(obj, "r_bench", defects, classes,
                                   0.0, self.cfg.r_bench_max, "A5_r_bench_range")
        risk = self._risk(obj, defects, classes)

        debts = self._obligations(obj, defects, classes)
        goals = self._goals(obj, defects, classes)

        extra = set(obj) - set(TOP_REQUIRED)
        if extra:
            self.assumption_hits["A3_extra_fields_tolerated"] += 1

        if defects:
            for d in defects:
                self.defect_counts[d.split(":")[0]] += 1
            cls = NEAR if classes and all(c == NEAR for c in classes) else GROSS
            return Record(idx, rid_echo, False, defects, cls, raw=obj)

        empty_name = any(d.name == "" for d in debts) or any(g.name == "" for g in goals)
        if empty_name:
            self.assumption_hits["A4_empty_name_tolerated"] += 1

        return Record(idx, rid_echo, True, [], "", income, expense, debts,
                      goals, bliq, r_bench, risk, bool(extra), empty_name, obj)

    def _numlike_class(self, v: Any) -> str:
        if isinstance(v, bool):
            self.assumption_hits["A1_bool_in_numeric"] += 1
            return NEAR
        if isinstance(v, str):
            if v.strip() == "":
                return NEAR
            if NUMSTR_RE.match(v) and re.search(r"\d", v):
                self.assumption_hits["A2_numeric_string"] += 1
                return NEAR
        return GROSS

    def _number(self, container: dict, key: str, defects: list,
                classes: list) -> Optional[float]:
        if key not in container:
            return None
        v = container[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            defects.append(f"bad_type:{key}")
            classes.append(self._numlike_class(v))
            return None
        f = float(v)
        if not math.isfinite(f):
            defects.append(f"not_finite:{key}")
            classes.append(GROSS)
            return None
        return f

    def _money(self, container: dict, key: str, defects: list,
               classes: list) -> float:
        f = self._number(container, key, defects, classes)
        if f is None:
            return 0.0
        if f < 0:
            defects.append(f"negative:{key}")
            classes.append(GROSS)
            self.assumption_hits["A16_negative_money_invalid"] += 1
            return 0.0
        return f

    def _rate_field(self, container: dict, key: str, defects: list,
                    classes: list, lo: float, hi: float,
                    assumption: str) -> float:
        f = self._number(container, key, defects, classes)
        if f is None:
            return 0.0
        if f < lo or f > hi:
            defects.append(f"range:{key}")
            if key == "interest_rate" and lo <= 3.0 < f <= 3.5:
                classes.append(NEAR)
            else:
                classes.append(GROSS)
            self.assumption_hits[assumption] += 1
            return 0.0
        return f

    def _risk(self, obj: dict, defects: list, classes: list) -> int:
        if "risk_tolerance" not in obj:
            return 3
        v = obj["risk_tolerance"]
        if isinstance(v, bool):
            defects.append("bad_type:risk_tolerance")
            classes.append(NEAR)
            return 3
        if isinstance(v, float) and v.is_integer():
            self.assumption_hits["A15_float_integral_risk"] += 1
            v = int(v)
        if not isinstance(v, int):
            defects.append("bad_type:risk_tolerance")
            classes.append(self._numlike_class(v))
            return 3
        if not 1 <= v <= 5:
            defects.append("range:risk_tolerance")
            classes.append(GROSS)
            return 3
        return v

    def _obligations(self, obj: dict, defects: list, classes: list) -> list:
        if "obligations" not in obj:
            return []
        items = obj["obligations"]
        if not isinstance(items, list):
            defects.append("bad_type:obligations")
            classes.append(GROSS)
            return []
        debts = []
        for it in items:
            if not isinstance(it, dict):
                defects.append("obligation_not_dict")
                classes.append(GROSS)
                continue
            for key in OBLIG_REQUIRED:
                if key not in it:
                    defects.append(f"missing_key:obligation.{key}")
                    classes.append(GROSS)
            name = it.get("name")
            if "name" in it and not isinstance(name, str):
                defects.append("bad_type:obligation.name")
                classes.append(GROSS)
                name = ""
            amount = self._money(it, "amount", defects, classes)
            payment = self._money(it, "monthly_payment", defects, classes)
            rate = self._rate_field(it, "interest_rate", defects, classes,
                                    0.0, self.cfg.rate_garbage,
                                    "A6_rate_above_300_garbage")
            debts.append(Debt(name if isinstance(name, str) else "",
                              amount, rate, payment))
        return debts

    def _goals(self, obj: dict, defects: list, classes: list) -> list:
        if "goals" not in obj:
            return []
        items = obj["goals"]
        if not isinstance(items, list):
            defects.append("bad_type:goals")
            classes.append(GROSS)
            return []
        goals = []
        for it in items:
            if not isinstance(it, dict):
                defects.append("goal_not_dict")
                classes.append(GROSS)
                continue
            for key in ("name", "target_amount", "current_amount"):
                if key not in it:
                    defects.append(f"missing_key:goal.{key}")
                    classes.append(GROSS)
            if "deadline" not in it:
                defects.append("missing_key:goal.deadline")
                classes.append(GROSS)
                self.assumption_hits["A9_deadline_key_missing_invalid"] += 1
            name = it.get("name")
            if "name" in it and not isinstance(name, str):
                defects.append("bad_type:goal.name")
                classes.append(GROSS)
                name = ""
            target = self._money(it, "target_amount", defects, classes)
            current = self._money(it, "current_amount", defects, classes)
            deadline, has_dl = self._deadline(it, defects, classes)
            goals.append(Goal(name if isinstance(name, str) else "",
                              target, current, deadline, has_dl))
        return goals

    def _deadline(self, it: dict, defects: list,
                  classes: list) -> tuple:
        if "deadline" not in it:
            return None, False
        v = it["deadline"]
        if v is None:
            return None, False
        if not isinstance(v, str):
            defects.append("bad_type:goal.deadline")
            classes.append(self._numlike_class(v))
            return None, False
        m = DATE_RE.match(v)
        if not m:
            defects.append("bad_format:goal.deadline")
            classes.append(GROSS)
            self.assumption_hits["A7_strict_iso_date_only"] += 1
            return None, False
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            defects.append("impossible_date:goal.deadline")
            classes.append(NEAR)
            self.assumption_hits["A7_strict_iso_date_only"] += 1
            return None, False
        return d, True


@dataclass
class Result:
    """Full decision for one input row."""

    rec: Record
    status: str
    dom: str
    res: int = 0
    debt: int = 0
    goal: int = 0
    inv: int = 0
    lump: int = 0
    confidence: int = 5
    flags: list = None
    diagnostics: dict = None
    debt_plan: list = None
    lump_plan: list = None
    monthly_plan: list = None
    goal_plan: list = None
    verdict: str = ""
    situation: str = ""


class DecisionEngine:
    """Methodology §§4-7: lump ladder, waterfall, confidence, verdict."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.assumption_hits: Counter = Counter()

    def evaluate(self, rec: Record) -> Result:
        if not rec.valid:
            conf = 3 if rec.defect_class == NEAR else 5
            verdict = ("Дефект выгрузки (" + "; ".join(sorted(set(rec.defects))[:3])
                       + "): запись не читается как финансовые данные — не оцениваю, вернуть на выверку.")
            return Result(rec, "invalid", "none", confidence=conf,
                          flags=["invalid_record"] + sorted(set(rec.defects)),
                          diagnostics={}, debt_plan=[], lump_plan=[],
                          monthly_plan=[], goal_plan=[], verdict=verdict,
                          situation="invalid")

        cfg = self.cfg
        debts = [replace(d) for d in rec.debts]
        goals = [replace(g) for g in rec.goals]
        self._classify(debts, rec.r_bench)

        pay = sum(d.payment for d in debts)
        burn = rec.expense + pay
        fcf = rec.income - burn
        pdn = self._pdn(rec.income, pay)
        r_months = cfg.reserve_months[rec.risk - 1]
        reserve_target0 = r_months * burn
        floor0 = cfg.floor_months * burn
        liq_months = (rec.bliq / burn) if burn > 0 else math.inf

        status = "ok" if fcf >= 0 else "deficit"
        flags = self._flags(rec, debts, goals, fcf, pdn, burn,
                            reserve_target0, floor0)

        border_lump = [False]
        lump_plan, bliq2 = self._lump_ladder(
            rec, debts, goals, status, fcf, border_lump)
        lump_total = int(math.floor(sum(m["amount"] for m in lump_plan) + 1e-9))

        pay2 = sum(d.payment for d in debts if d.alive or d.payment > 0)
        burn2 = rec.expense + pay2
        fcf2 = rec.income - burn2

        self._goal_math(goals)

        res = debt = goal_b = inv = 0
        monthly_plan: list = []
        if status == "ok":
            budget = int(math.floor(max(0.0, fcf) + 1e-9))
            res, debt, goal_b, inv, monthly_plan = self._waterfall(
                rec, debts, goals, bliq2, burn2, budget)

        dom = self._dom(res, debt, goal_b, inv)
        goal_plan = self._goal_plan(goals, rec)
        if any(gp.get("achievable") is False for gp in goal_plan):
            flags.append("goal_unachievable")

        debt_plan = self._debt_plan(debts)
        conf = self._confidence(rec, debts, fcf, pdn, reserve_target0,
                                border_lump[0], goals, flags)
        diagnostics = {
            "fcf": round(fcf, 2),
            "pdn": None if math.isinf(pdn) else round(pdn, 4),
            "monthly_burn": round(burn, 2),
            "liquidity_months": None if math.isinf(liq_months) else round(liq_months, 2),
            "reserve_target": round(reserve_target0, 2),
            "reserve_floor": round(floor0, 2),
            "bliq_after_lump": round(bliq2, 2),
            "burn_after_lump": round(burn2, 2),
            "fcf_after_lump": round(fcf2, 2),
        }
        verdict = self._verdict(rec, status, fcf, fcf2, pdn, debts, goals,
                                lump_plan, res, debt, goal_b, inv, liq_months)
        situation = self._situation(status, debts, rec, reserve_target0)
        return Result(rec, status, dom, res, debt, goal_b, inv, lump_total,
                      conf, flags, diagnostics, debt_plan, lump_plan,
                      monthly_plan, goal_plan, verdict, situation)

    def _classify(self, debts: list, r_bench: float) -> None:
        for d in debts:
            if not d.alive:
                d.cls = "closed"
                continue
            expensive = d.rate >= r_bench + self.cfg.spread_expensive
            d.interest_only = d.payment <= d.amount * d.rate / 12.0 + 1e-9
            d.suspicious = self.cfg.rate_suspicious < d.rate <= self.cfg.rate_garbage
            if d.rate >= self.cfg.toxic_rate or (expensive and d.interest_only):
                d.cls = "toxic"
            elif expensive:
                d.cls = "expensive"
            else:
                d.cls = "cheap"

    @staticmethod
    def _pdn(income: float, pay: float) -> float:
        if income > 0:
            return pay / income
        return math.inf if pay > 0 else 0.0

    def _flags(self, rec: Record, debts: list, goals: list, fcf: float,
               pdn: float, burn: float, target: float, floor0: float) -> list:
        cfg = self.cfg
        f = []
        if rec.income == 0:
            f.append("zero_income")
        if rec.expense == 0:
            f.append("zero_expense")
        if burn == 0:
            f.append("zero_burn")
        if abs(fcf) < 0.005:
            f.append("zero_flow")
        if math.isinf(pdn):
            f.append("pdn_infinite")
        elif pdn >= cfg.pdn_critical:
            f.append("pdn_critical")
        elif pdn >= cfg.pdn_overload:
            f.append("pdn_overload")
        elif pdn >= cfg.pdn_elevated:
            f.append("pdn_elevated")
        if rec.bliq == 0:
            f.append("no_cushion")
        elif rec.bliq < floor0:
            f.append("below_floor")
        if rec.bliq < target:
            f.append("cushion_below_target")
        if target > 0 and rec.bliq > 2 * target:
            f.append("cushion_excess")
        alive = [d for d in debts if d.alive]
        if any(d.cls == "toxic" for d in alive):
            f.append("toxic_debt")
        if any(d.suspicious for d in alive):
            f.append("suspicious_rate")
        if any(d.interest_only for d in alive):
            f.append("interest_only")
        if any((not d.alive) and d.payment > 0 for d in debts):
            f.append("zero_balance_paying")
            self.assumption_hits["A8_zero_balance_paying_literal"] += 1
        if not debts:
            f.append("debt_free")
        elif alive and all(d.cls == "cheap" for d in alive):
            f.append("cheap_debt_only")
        if any(d.cls == "expensive" for d in alive):
            f.append("expensive_debt")
        if not goals:
            f.append("no_goals")
        for g in goals:
            if g.has_deadline and g.deadline < CUTOFF and not g.done:
                f.append("overdue_goal")
                self.assumption_hits["A17_overdue_goal_immediate"] += 1
                break
        if any(g.has_deadline and g.deadline == CUTOFF for g in goals):
            f.append("deadline_today")
        if any(g.done and g.current <= g.target + 0.004 for g in goals):
            f.append("goal_done")
        if any(g.current > g.target + 0.004 for g in goals):
            f.append("overfunded_goal")
            self.assumption_hits["A18_overfunded_no_action"] += 1
        if any(not g.has_deadline for g in goals):
            f.append("perpetual_goal")
        if rec.income >= cfg.whale_income:
            f.append("whale_income")
        money = ([rec.income, rec.expense, rec.bliq]
                 + [d.amount for d in debts] + [g.target for g in goals])
        if any(v >= cfg.stress_magnitude for v in money):
            f.append("stress_magnitude")
        if rec.empty_name:
            f.append("empty_name")
        return f

    def _lump_ladder(self, rec: Record, debts: list, goals: list,
                     status: str, fcf: float,
                     border: list) -> tuple:
        cfg = self.cfg
        moves: list = []
        bliq = rec.bliq

        def burn_now() -> float:
            return rec.expense + sum(d.payment for d in debts
                                     if d.alive or d.payment > 0)

        def note_candidate(amount: float) -> None:
            if 0.8 * cfg.min_lump <= amount <= 1.2 * cfg.min_lump:
                border[0] = True

        for d in sorted([x for x in debts if x.alive and x.cls == "toxic"],
                        key=lambda x: -x.rate):
            floor_amt = cfg.floor_months * burn_now()
            avail = bliq - floor_amt
            if avail <= 0:
                continue
            amt = min(d.amount, avail)
            note_candidate(amt)
            if amt >= d.amount - 0.005:
                bliq -= d.amount
                moves.append({"action": "close_debt", "target": d.name,
                              "amount": round(d.amount, 2),
                              "note": f"токсичный {d.rate:.0%}, платёж −{rub0(d.payment)} ₽/мес"})
                d.lump_paid = d.amount
                d.amount = 0.0
                d.payment = 0.0
            elif amt >= cfg.min_toxic_partial:
                bliq -= amt
                d.amount -= amt
                d.lump_paid = amt
                moves.append({"action": "partial_debt", "target": d.name,
                              "amount": round(amt, 2),
                              "note": f"частично, токсичный {d.rate:.0%}"})

        if status == "ok":
            for d in sorted([x for x in debts if x.alive and x.cls == "expensive"],
                            key=lambda x: -x.rate):
                pay_wo = sum(x.payment for x in debts
                             if (x.alive or x.payment > 0) and x is not d)
                new_burn = rec.expense + pay_wo
                new_target = cfg.reserve_months[rec.risk - 1] * new_burn
                note_candidate(d.amount)
                if d.amount >= cfg.min_lump and bliq - d.amount >= new_target:
                    bliq -= d.amount
                    moves.append({"action": "close_debt", "target": d.name,
                                  "amount": round(d.amount, 2),
                                  "note": f"дорогой {d.rate:.0%} > бенчмарк, платёж −{rub0(d.payment)} ₽/мес"})
                    d.lump_paid = d.amount
                    d.amount = 0.0
                    d.payment = 0.0

            target_now = cfg.reserve_months[rec.risk - 1] * burn_now()
            dated = sorted([g for g in goals if g.has_deadline and not g.done],
                           key=lambda g: g.deadline)
            perpetual = sorted([g for g in goals if not g.has_deadline and not g.done],
                               key=lambda g: g.remaining)
            for g in dated + perpetual:
                cost = g.remaining
                note_candidate(cost)
                if cost >= cfg.min_lump and bliq - cost >= target_now:
                    bliq -= cost
                    g.lump_added = cost
                    g.current = g.target
                    moves.append({"action": "close_goal", "target": g.name,
                                  "amount": round(cost, 2),
                                  "note": "цель закрыта из излишка накоплений"})
            surplus = bliq - target_now
            nearest = next((g for g in dated if not g.done), None)
            if nearest is not None and surplus >= cfg.min_lump:
                amt = min(surplus, nearest.remaining)
                if amt >= cfg.min_lump:
                    bliq -= amt
                    nearest.lump_added += amt
                    nearest.current += amt
                    moves.append({"action": "fund_goal", "target": nearest.name,
                                  "amount": round(amt, 2),
                                  "note": "частичное пополнение ближайшей цели из излишка"})
                    surplus = bliq - target_now
            if surplus >= cfg.min_lump:
                amt = math.floor(surplus)
                bliq -= amt
                moves.append({"action": "invest_surplus", "target": "инвестиции",
                              "amount": round(float(amt), 2),
                              "note": self._invest_note(rec.risk)})
        else:
            candidates = sorted([x for x in debts if x.alive and x.cls == "expensive"],
                                key=lambda x: -x.rate)
            chosen = None
            for k in range(1, len(candidates) + 1):
                prefix = candidates[:k]
                prefix_ids = {id(d) for d in prefix}
                cost = sum(d.amount for d in prefix)
                pay_left = sum(x.payment for x in debts
                               if (x.alive or x.payment > 0)
                               and id(x) not in prefix_ids)
                new_burn = rec.expense + pay_left
                new_fcf = rec.income - new_burn
                if (new_fcf >= 0 and bliq - cost >= cfg.deficit_runway_months * new_burn
                        and cost > 0):
                    chosen = prefix
                    break
            if chosen:
                self.assumption_hits["A12_deficit_l2_fix"] += 1
                for d in chosen:
                    note_candidate(d.amount)
                    bliq -= d.amount
                    moves.append({"action": "close_debt", "target": d.name,
                                  "amount": round(d.amount, 2),
                                  "note": f"выводит бюджет из дефицита, платёж −{rub0(d.payment)} ₽/мес"})
                    d.lump_paid = d.amount
                    d.amount = 0.0
                    d.payment = 0.0
        return moves, bliq

    def _invest_note(self, risk: int) -> str:
        eq = self.cfg.equity_share[risk - 1]
        if eq == 0:
            return "излишек — в депозиты/ОФЗ под бенчмарк"
        return (f"излишек: ~{eq:.0%} индексные фонды, остальное депозиты/ОФЗ")

    def _goal_math(self, goals: list) -> None:
        for g in goals:
            if g.done:
                continue
            if not g.has_deadline:
                continue
            days = (g.deadline - CUTOFF).days
            months = days / DAYS_PER_MONTH
            g.months_left = round(months, 2)
            if months < 1:
                g.immediate = True
                g.required = g.remaining
            else:
                g.required = g.remaining / months

    def _waterfall(self, rec: Record, debts: list, goals: list,
                   bliq2: float, burn2: float, budget: int) -> tuple:
        cfg = self.cfg
        res = debt = goal_b = inv = 0
        plan: list = []
        f_rem = budget
        alive = [d for d in debts if d.alive]
        toxic = [d for d in alive if d.cls == "toxic"]
        expensive = [d for d in alive if d.cls == "expensive"]
        if f_rem <= 0:
            return 0, 0, 0, 0, []
        if toxic:
            debt = f_rem
            top = max(toxic, key=lambda d: d.rate)
            top.monthly_extra = debt
            plan.append({"bucket": "debt", "amount": debt,
                         "note": f"весь поток — на токсичный «{top.name}» ({top.rate:.0%})"})
            return res, debt, goal_b, inv, plan
        floor_amt = cfg.floor_months * burn2
        if bliq2 < floor_amt:
            take = min(f_rem, int(math.ceil(floor_amt - bliq2)))
            if take > 0:
                res += take
                f_rem -= take
                plan.append({"bucket": "reserve", "amount": take,
                             "note": "добор несгораемого пола подушки (1 мес)"})
        if f_rem > 0 and expensive:
            take = int(math.floor(f_rem * cfg.debt_share))
            if take > 0:
                debt += take
                f_rem -= take
                top = max(expensive, key=lambda d: d.rate)
                top.monthly_extra = take
                plan.append({"bucket": "debt", "amount": take,
                             "note": f"досрочно по лавине: «{top.name}» ({top.rate:.0%})"})
        if f_rem > 0:
            target_amt = cfg.reserve_months[rec.risk - 1] * burn2
            gap = target_amt - (bliq2 + res)
            if gap > 0:
                take = min(f_rem, int(math.ceil(gap / cfg.reserve_build_months)))
                if take > 0:
                    res += take
                    f_rem -= take
                    plan.append({"bucket": "reserve", "amount": take,
                                 "note": "добор подушки до целевой за ~12 мес"})
        dated = sorted([g for g in goals if g.has_deadline and not g.done],
                       key=lambda g: g.deadline)
        for g in dated:
            if f_rem <= 0:
                break
            need = int(math.ceil(g.required))
            take = min(f_rem, need)
            if take > 0:
                g.planned = take
                goal_b += take
                f_rem -= take
        if goal_b > 0:
            plan.append({"bucket": "goals", "amount": goal_b,
                         "note": "взносы по датированным целям (ближайший дедлайн — первым)"})
        if f_rem > 0:
            perpetual = [g for g in goals if not g.has_deadline and not g.done]
            if rec.risk <= 2 and any(d.alive for d in debts):
                debt += f_rem
                plan.append({"bucket": "debt", "amount": f_rem,
                             "note": "остаток — в долг (консервативный профиль)"})
                f_rem = 0
            elif perpetual:
                half = f_rem // 2
                share = half // len(perpetual) if perpetual else 0
                for g in perpetual:
                    g.planned += share
                goal_b += half
                inv += f_rem - half
                plan.append({"bucket": "goals", "amount": half,
                             "note": "бессрочные цели — из остатка"})
                plan.append({"bucket": "invest", "amount": f_rem - half,
                             "note": self._invest_note(rec.risk)})
                f_rem = 0
            else:
                inv += f_rem
                plan.append({"bucket": "invest", "amount": f_rem,
                             "note": self._invest_note(rec.risk)})
                f_rem = 0
        return res, debt, goal_b, inv, plan

    @staticmethod
    def _dom(res: int, debt: int, goal_b: int, inv: int) -> str:
        buckets = [("debt", debt), ("reserve", res), ("goals+", goal_b + inv)]
        best = max(buckets, key=lambda kv: kv[1])
        if best[1] <= 0:
            return "none"
        for name, val in buckets:
            if val == best[1]:
                return name
        return "none"

    def _goal_plan(self, goals: list, rec: Record) -> list:
        out = []
        for g in goals:
            entry = {
                "name": g.name,
                "deadline": g.deadline.isoformat() if g.has_deadline else None,
                "target": round(g.target, 2),
                "current": round(g.current - g.lump_added, 2),
                "remaining_after_lump": round(g.remaining, 2),
                "months_left": g.months_left,
                "required_monthly": round(g.required, 2) if g.has_deadline else None,
                "planned_monthly": g.planned,
                "lump": round(g.lump_added, 2),
                "closed_by_lump": bool(g.lump_added and g.done),
            }
            if g.done:
                entry["achievable"] = True
                entry["note"] = ("закрыта разовым ходом" if g.lump_added
                                 else "уже профинансирована")
            elif not g.has_deadline:
                entry["achievable"] = None
                if g.planned > 0:
                    eta = g.remaining / g.planned
                    entry["note"] = f"бессрочная, при текущем темпе ~{eta:.0f} мес"
                else:
                    entry["note"] = "бессрочная, финансируется по остаточному принципу"
            else:
                achievable = g.planned >= math.floor(g.required) and not g.immediate
                if g.immediate:
                    achievable = False
                entry["achievable"] = achievable
                if g.immediate:
                    entry["note"] = "дедлайн наступил/просрочен — закрыть немедленно нельзя, пересмотреть срок или сумму"
                elif achievable:
                    entry["note"] = "в графике при плановом взносе"
                else:
                    entry["note"] = "взнос ниже требуемого — дедлайн под угрозой, пересмотреть срок/сумму"
            out.append(entry)
        return out

    @staticmethod
    def _debt_plan(debts: list) -> list:
        out = []
        for d in debts:
            if d.lump_paid and not d.alive:
                action = "close_from_savings"
            elif d.lump_paid:
                action = "partial_from_savings"
            elif not d.alive:
                action = "already_closed"
            elif d.cls == "toxic":
                action = "kill_first_refinance_if_possible"
            elif d.cls == "expensive" and d.monthly_extra > 0:
                action = "accelerate_avalanche"
            elif d.cls == "expensive":
                action = "accelerate_when_cash_frees"
            else:
                action = "keep_schedule"
            out.append({"name": d.name,
                        "amount": round(d.amount + d.lump_paid, 2),
                        "rate": d.rate, "payment": round(d.payment, 2),
                        "class": d.cls, "action": action,
                        "monthly_extra": d.monthly_extra})
        return out

    def _confidence(self, rec: Record, debts: list, fcf: float, pdn: float,
                    reserve_target: float, border_lump: bool,
                    goals: list, flags: list) -> int:
        cfg = self.cfg
        score = 5
        if abs(fcf) <= max(2000.0, 0.03 * rec.income):
            score -= 1
        if rec.income > 0 and not math.isinf(pdn) and abs(pdn - cfg.pdn_overload) <= 0.05:
            score -= 1
        thr = rec.r_bench + cfg.spread_expensive
        if any(abs(d.rate - thr) <= 0.015 for d in debts if d.alive or d.lump_paid):
            score -= 1
        if any(abs(d.rate - cfg.toxic_rate) <= 0.03 for d in debts if d.alive or d.lump_paid):
            score -= 1
        if reserve_target > 0 and abs(rec.bliq - reserve_target) <= 0.15 * reserve_target:
            score -= 1
        if border_lump:
            score -= 1
        if "overdue_goal" in flags:
            score -= 1
        if any(f in flags for f in ("zero_balance_paying", "suspicious_rate",
                                    "overfunded_goal")):
            score -= 1
        return max(1, min(5, score))

    def _verdict(self, rec: Record, status: str, fcf: float, fcf2: float,
                 pdn: float, debts: list, goals: list, lump_plan: list,
                 res: int, debt: int, goal_b: int, inv: int,
                 liq_months: float) -> str:
        pdn_txt = "∞" if math.isinf(pdn) else f"{pdn:.0%}"
        closed = [m for m in lump_plan if m["action"] == "close_debt"]
        alive = [d for d in debts if d.alive]
        toxic = [d for d in alive if d.cls == "toxic"]
        if status == "deficit":
            base = f"Дефицит {rub0(-fcf)} ₽/мес (ПДН {pdn_txt})"
            if closed and fcf2 >= 0:
                total = sum(m["amount"] for m in closed)
                return (base + f": из подушки закрыть долги на {rub0(total)} ₽ — "
                        f"поток выходит в +{rub0(fcf2)} ₽/мес.")
            runway = "" if math.isinf(liq_months) else f", подушки на {liq_months:.1f} мес"
            extra = "; токсичный долг гасим из подушки в первую очередь" if any(
                m for m in lump_plan) else ""
            return (base + runway
                    + ": режим экономии, реструктуризация/рефинансирование и поиск дохода"
                    + extra + ".")
        if toxic:
            t = max(toxic, key=lambda d: d.rate)
            return (f"Пожар: токсичный «{t.name}» под {t.rate:.0%} — весь свободный поток "
                    f"({rub0(debt)} ₽/мес) на его погашение, параллельно рефинансирование.")
        parts = []
        if closed:
            total = sum(m["amount"] for m in closed)
            parts.append(f"из накоплений закрыть долги на {rub0(total)} ₽")
        goal_lumps = [m for m in lump_plan if m["action"] in ("close_goal", "fund_goal")]
        if goal_lumps:
            parts.append("часть излишка — в цели")
        invest_lump = [m for m in lump_plan if m["action"] == "invest_surplus"]
        if invest_lump:
            parts.append(f"излишек подушки {rub0(invest_lump[0]['amount'])} ₽ разместить")
        month_parts = []
        if debt:
            month_parts.append(f"{rub0(debt)} — досрочно в долг")
        if res:
            month_parts.append(f"{rub0(res)} — в резерв")
        if goal_b:
            month_parts.append(f"{rub0(goal_b)} — в цели")
        if inv:
            month_parts.append(f"{rub0(inv)} — в инвестиции")
        lead = "; ".join(parts)
        month = ", ".join(month_parts) if month_parts else "поток нулевой — держать график"
        head = "Здоровый бюджет" if pdn < self.cfg.pdn_overload else f"ПДН {pdn_txt} — высокий"
        sep = "; " if lead else ""
        return f"{head}: {lead}{sep}помесячно {month} (ПДН {pdn_txt})."

    def _situation(self, status: str, debts: list, rec: Record,
                   reserve_target: float) -> str:
        alive = [d for d in debts if d.alive or d.lump_paid]
        has_toxic = any(d.cls == "toxic" for d in alive)
        has_exp = any(d.cls == "expensive" for d in alive)
        if status == "deficit":
            return "deficit+toxic" if has_toxic else "deficit"
        if has_toxic:
            return "toxic"
        if has_exp:
            if rec.bliq >= reserve_target:
                return "expensive_fat_cushion"
            return "expensive_thin_cushion"
        if any(d.alive for d in debts):
            return "cheap_only"
        if rec.goals:
            return "debt_free_goals"
        return "debt_free_plain"


class Runner:
    """Loads parts, applies the engine, writes the answer files."""

    def __init__(self, cfg: Config, parts: list) -> None:
        self.cfg = cfg
        self.parts = parts

    def load_lines(self) -> list:
        lines: list = []
        for path in self.parts:
            opener = gzip.open if str(path).endswith(".gz") else open
            with opener(path, "rt", encoding="utf-8") as fh:
                first = fh.readline()
                try:
                    meta = json.loads(first)
                    is_meta = isinstance(meta, dict) and meta.get("__meta__")
                except ValueError:
                    is_meta = False
                if not is_meta:
                    lines.append(first.rstrip("\n"))
                for line in fh:
                    line = line.rstrip("\n")
                    if line:
                        lines.append(line)
        return lines

    def run(self) -> tuple:
        parser = RecordParser(self.cfg)
        engine = DecisionEngine(self.cfg)
        lines = self.load_lines()
        records = [parser.parse_line(i, ln) for i, ln in enumerate(lines)]
        id_counts = Counter(r.rid for r in records if r.rid)
        results = []
        for rec in records:
            result = engine.evaluate(rec)
            if rec.rid and id_counts[rec.rid] > 1:
                result.flags.append("duplicate_id")
                parser.assumption_hits["A13_duplicate_rows_independent"] += 1
            results.append(result)
        hits = parser.assumption_hits + engine.assumption_hits
        return results, hits, parser.defect_counts

    @staticmethod
    def write_allocations(results: list, path: Path) -> None:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("id,status,dom,res,debt,goal,inv,lump,confidence\n")
            for r in results:
                fh.write(f"{r.rec.rid},{r.status},{r.dom},{r.res},{r.debt},"
                         f"{r.goal},{r.inv},{r.lump},{r.confidence}\n")

    def write_summary(self, results: list, path: Path) -> None:
        cols = ("id,status,dom,flags,fcf,pdn,monthly_burn,bliq,"
                "liquidity_months,reserve_target,n_debts,debt_total,n_goals,"
                "res,debt,goal,inv,lump")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(cols + "\n")
            for r in results:
                if r.status == "invalid":
                    fh.write(f"{r.rec.rid},invalid,none,{'|'.join(r.flags)},"
                             "0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")
                    continue
                d = r.diagnostics
                pdn = d["pdn"]
                pdn_s = "99.0" if pdn is None else f"{pdn:.4f}"
                liq = d["liquidity_months"]
                liq_s = "999.0" if liq is None else f"{min(liq, 999.0):.2f}"
                rec = r.rec
                n_debts = len(rec.debts)
                debt_total = sum(x.amount + x.lump_paid for x in rec.debts)
                fh.write(f"{rec.rid},{r.status},{r.dom},{'|'.join(r.flags)},"
                         f"{d['fcf']:.2f},{pdn_s},{d['monthly_burn']:.2f},"
                         f"{rec.bliq:.2f},{liq_s},{d['reserve_target']:.2f},"
                         f"{n_debts},{debt_total:.2f},{len(rec.goals)},"
                         f"{r.res},{r.debt},{r.goal},{r.inv},{r.lump}\n")

    @staticmethod
    def write_recommendations(results: list, path: Path) -> None:
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            for r in results:
                obj = {
                    "id": r.rec.rid,
                    "status": r.status,
                    "dom": r.dom,
                    "confidence": r.confidence,
                    "flags": r.flags,
                    "diagnostics": r.diagnostics,
                    "debt_plan": r.debt_plan,
                    "lump_sum_plan": r.lump_plan,
                    "monthly_plan": r.monthly_plan,
                    "goal_plan": r.goal_plan,
                    "totals": {
                        "monthly_total": r.res + r.debt + r.goal + r.inv,
                        "lump_total": r.lump,
                    },
                    "verdict": r.verdict,
                }
                fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def paper_recompute(raw: dict, cfg: Config) -> dict:
    """Independent straight-line recompute of §§4-5 for the manual check.

    Deliberately shares no code with DecisionEngine; assumes a valid record.
    """
    income = float(raw["income_total"])
    expense = float(raw["expense_total"])
    bliq = float(raw["bliq"])
    r_bench = float(raw["r_bench"])
    risk = int(raw["risk_tolerance"])
    debts = [dict(name=o["name"], amount=float(o["amount"]),
                  rate=float(o["interest_rate"]),
                  payment=float(o["monthly_payment"]))
             for o in raw["obligations"]]
    goals = []
    for g in raw["goals"]:
        dl = g["deadline"]
        goals.append(dict(name=g["name"], target=float(g["target_amount"]),
                          current=float(g["current_amount"]),
                          deadline=date.fromisoformat(dl) if dl else None))

    def cls(d: dict) -> str:
        if d["amount"] <= 0.004:
            return "closed"
        exp = d["rate"] >= r_bench + cfg.spread_expensive
        io_flag = d["payment"] <= d["amount"] * d["rate"] / 12.0 + 1e-9
        if d["rate"] >= cfg.toxic_rate or (exp and io_flag):
            return "toxic"
        return "expensive" if exp else "cheap"

    for d in debts:
        d["cls"] = cls(d)
    pay = sum(d["payment"] for d in debts)
    burn = expense + pay
    fcf = income - burn
    status = "ok" if fcf >= 0 else "deficit"
    lump = 0.0

    def burn_now() -> float:
        return expense + sum(d["payment"] for d in debts)

    for d in sorted([x for x in debts if x["cls"] == "toxic" and x["amount"] > 0.004],
                    key=lambda x: -x["rate"]):
        avail = bliq - cfg.floor_months * burn_now()
        if avail <= 0:
            continue
        amt = min(d["amount"], avail)
        if amt >= d["amount"] - 0.005:
            bliq -= d["amount"]
            lump += d["amount"]
            d["amount"] = 0.0
            d["payment"] = 0.0
        elif amt >= cfg.min_toxic_partial:
            bliq -= amt
            lump += amt
            d["amount"] -= amt

    if status == "ok":
        for d in sorted([x for x in debts if x["cls"] == "expensive" and x["amount"] > 0.004],
                        key=lambda x: -x["rate"]):
            new_burn = expense + sum(x["payment"] for x in debts if x is not d)
            if (d["amount"] >= cfg.min_lump
                    and bliq - d["amount"] >= cfg.reserve_months[risk - 1] * new_burn):
                bliq -= d["amount"]
                lump += d["amount"]
                d["amount"] = 0.0
                d["payment"] = 0.0
        target = cfg.reserve_months[risk - 1] * burn_now()
        dated = sorted([g for g in goals if g["deadline"] and g["target"] - g["current"] > 0.004],
                       key=lambda g: g["deadline"])
        perpetual = sorted([g for g in goals if not g["deadline"] and g["target"] - g["current"] > 0.004],
                           key=lambda g: g["target"] - g["current"])
        for g in dated + perpetual:
            cost = g["target"] - g["current"]
            if cost >= cfg.min_lump and bliq - cost >= target:
                bliq -= cost
                lump += cost
                g["current"] = g["target"]
        surplus = bliq - target
        nearest = next((g for g in dated if g["target"] - g["current"] > 0.004), None)
        if nearest is not None and surplus >= cfg.min_lump:
            amt = min(surplus, nearest["target"] - nearest["current"])
            if amt >= cfg.min_lump:
                bliq -= amt
                lump += amt
                nearest["current"] += amt
        surplus = bliq - target
        if surplus >= cfg.min_lump:
            amt = math.floor(surplus)
            bliq -= amt
            lump += amt
    else:
        cand = sorted([x for x in debts if x["cls"] == "expensive" and x["amount"] > 0.004],
                      key=lambda x: -x["rate"])
        for k in range(1, len(cand) + 1):
            prefix = cand[:k]
            prefix_ids = {id(d) for d in prefix}
            cost = sum(d["amount"] for d in prefix)
            new_burn = expense + sum(x["payment"] for x in debts
                                     if id(x) not in prefix_ids)
            if (income - new_burn >= 0 and cost > 0
                    and bliq - cost >= cfg.deficit_runway_months * new_burn):
                for d in prefix:
                    bliq -= d["amount"]
                    lump += d["amount"]
                    d["amount"] = 0.0
                    d["payment"] = 0.0
                break

    res = debt_b = goal_b = inv = 0
    if status == "ok":
        f = int(math.floor(max(0.0, fcf) + 1e-9))
        burn2 = burn_now()
        alive = [d for d in debts if d["amount"] > 0.004]
        if f > 0 and any(d["cls"] == "toxic" for d in alive):
            debt_b = f
            f = 0
        elif f > 0:
            floor_amt = cfg.floor_months * burn2
            if bliq < floor_amt:
                take = min(f, int(math.ceil(floor_amt - bliq)))
                res += take
                f -= take
            if f > 0 and any(d["cls"] == "expensive" for d in alive):
                take = int(math.floor(f * cfg.debt_share))
                debt_b += take
                f -= take
            if f > 0:
                gap = cfg.reserve_months[risk - 1] * burn2 - (bliq + res)
                if gap > 0:
                    take = min(f, int(math.ceil(gap / cfg.reserve_build_months)))
                    res += take
                    f -= take
            dated = sorted([g for g in goals if g["deadline"] and g["target"] - g["current"] > 0.004],
                           key=lambda g: g["deadline"])
            for g in dated:
                if f <= 0:
                    break
                rem = g["target"] - g["current"]
                days = (g["deadline"] - CUTOFF).days
                months = days / DAYS_PER_MONTH
                need = rem if months < 1 else rem / months
                take = min(f, int(math.ceil(need)))
                goal_b += take
                f -= take
            if f > 0:
                perpetual = [g for g in goals if not g["deadline"] and g["target"] - g["current"] > 0.004]
                if risk <= 2 and alive:
                    debt_b += f
                elif perpetual:
                    goal_b += f // 2
                    inv += f - f // 2
                else:
                    inv += f
                f = 0
    buckets = [("debt", debt_b), ("reserve", res), ("goals+", goal_b + inv)]
    top = max(buckets, key=lambda kv: kv[1])
    dom = "none" if top[1] <= 0 else next(n for n, v in buckets if v == top[1])
    return {"status": status, "dom": dom, "res": res, "debt": debt_b,
            "goal": goal_b, "inv": inv, "lump": int(math.floor(lump + 1e-9))}


def cmd_run(args: argparse.Namespace) -> None:
    runner = Runner(BASE_CONFIG, args.parts)
    results, hits, defects = runner.run()
    out = Path(args.out_dir)
    aux = Path(args.aux_dir)
    out.mkdir(parents=True, exist_ok=True)
    aux.mkdir(parents=True, exist_ok=True)
    runner.write_allocations(results, out / "expert_allocations_v4.csv")
    runner.write_summary(results, out / "summary_v4.csv")
    runner.write_recommendations(results, out / "recommendations_v4.jsonl.gz")
    status_c = Counter(r.status for r in results)
    dom_c = Counter(r.dom for r in results)
    situation_c = Counter(r.situation for r in results)
    conf_c = Counter(r.confidence for r in results)
    flag_c = Counter(f for r in results for f in (r.flags or []))
    lump_rows = sum(1 for r in results if r.lump > 0)
    with open(aux / "run_summary.json", "w", encoding="utf-8") as fh:
        json.dump({"n": len(results), "status": dict(status_c),
                   "dom": dict(dom_c), "situation": dict(situation_c),
                   "confidence": {str(k): v for k, v in conf_c.items()},
                   "flags": dict(flag_c), "lump_rows": lump_rows,
                   "assumption_hits": dict(hits),
                   "defect_counts": dict(defects)},
                  fh, ensure_ascii=False, indent=1)
    print(json.dumps({"n": len(results), "status": dict(status_c),
                      "dom": dict(dom_c), "lump_rows": lump_rows},
                     ensure_ascii=False))


def cmd_sensitivity(args: argparse.Namespace) -> None:
    base_runner = Runner(BASE_CONFIG, args.parts)
    base_results, _, _ = base_runner.run()
    base = [(r.status, r.dom, r.situation) for r in base_results]
    report = []
    for label, overrides in SENSITIVITY_VARIANTS:
        cfg = replace(BASE_CONFIG, **overrides)
        results, _, _ = Runner(cfg, args.parts).run()
        dom_changed = status_changed = 0
        situations: Counter = Counter()
        for (b_status, b_dom, b_sit), r in zip(base, results):
            if r.dom != b_dom:
                dom_changed += 1
                situations[b_sit] += 1
            if r.status != b_status:
                status_changed += 1
        report.append({"variant": label,
                       "dom_changed": dom_changed,
                       "dom_changed_pct": round(100.0 * dom_changed / len(base), 2),
                       "status_changed": status_changed,
                       "top_situations": situations.most_common(3)})
        print(label, dom_changed, status_changed)
    with open(Path(args.aux_dir) / "sensitivity.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)


def cmd_opinions(args: argparse.Namespace) -> None:
    runner = Runner(BASE_CONFIG, args.parts)
    lines = runner.load_lines()
    parser = RecordParser(BASE_CONFIG)
    engine = DecisionEngine(BASE_CONFIG)
    picks = list(range(0, len(lines), args.step))
    out = []
    for pos in picks:
        rec = parser.parse_line(pos, lines[pos])
        result = engine.evaluate(rec)
        paper = None
        match = None
        if rec.valid:
            paper = paper_recompute(json.loads(lines[pos]), BASE_CONFIG)
            match = (paper["status"] == result.status
                     and paper["dom"] == result.dom
                     and paper["res"] == result.res
                     and paper["debt"] == result.debt
                     and paper["goal"] == result.goal
                     and paper["inv"] == result.inv
                     and paper["lump"] == result.lump)
        try:
            raw_obj: Any = json.loads(lines[pos])
        except ValueError:
            raw_obj = lines[pos][:400]
        out.append({
            "position": pos,
            "id": rec.rid,
            "raw": raw_obj,
            "status": result.status, "dom": result.dom,
            "res": result.res, "debt": result.debt, "goal": result.goal,
            "inv": result.inv, "lump": result.lump,
            "confidence": result.confidence,
            "flags": result.flags,
            "diagnostics": result.diagnostics,
            "lump_plan": result.lump_plan,
            "monthly_plan": result.monthly_plan,
            "goal_plan": result.goal_plan,
            "debt_plan": result.debt_plan,
            "verdict": result.verdict,
            "paper": paper,
            "paper_match": match,
        })
    with open(Path(args.aux_dir) / "opinions.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("opinions:", len(out), "paper_mismatches:",
          sum(1 for o in out if o["paper_match"] is False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["run", "sensitivity", "opinions"])
    ap.add_argument("--parts", nargs="+", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--aux-dir", default="aux")
    ap.add_argument("--step", type=int, default=300)
    args = ap.parse_args()
    if args.mode == "run":
        cmd_run(args)
    elif args.mode == "sensitivity":
        cmd_sensitivity(args)
    else:
        cmd_opinions(args)


if __name__ == "__main__":
    main()
