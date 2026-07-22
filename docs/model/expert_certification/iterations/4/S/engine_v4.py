"""Independent financial expert engine, round 4 (dataset v4).

Implements the methodology fixed in expert_methodology_v4.md BEFORE data
processing. Deterministic, positional contract: one output row per input row.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import gzip
import json
import math
import re
from pathlib import Path

CUTOFF_DATE = dt.date(2026, 7, 18)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAYS_PER_MONTH = 30.4375

REQUIRED_RECORD_KEYS = (
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
)
REQUIRED_DEBT_KEYS = ("name", "amount", "interest_rate", "monthly_payment")
REQUIRED_GOAL_KEYS = ("name", "target_amount", "current_amount", "deadline")


class ParsedNanError(ValueError):
    """Raised when a JSON line contains NaN/Infinity tokens."""


def _reject_constant(_token: str) -> float:
    raise ParsedNanError("NaN/Infinity token in JSON")


@dataclasses.dataclass
class Constants:
    """All methodology constants. Fixed before processing; overridable only
    for the sensitivity study (separate runs)."""

    cheap_spread: float = 0.02          # r <= r_bench + spread -> cheap
    toxic_rate: float = 0.45            # r >= toxic_rate -> toxic
    garbage_rate: float = 3.00          # r > garbage_rate -> invalid record
    reserve_months: tuple = (6.0, 5.0, 4.0, 3.0, 3.0)   # by risk 1..5
    reserve_scale: float = 1.0          # sensitivity knob on reserve target
    min_reserve_months: float = 1.0
    floor_toxic_months: float = 1.0
    min_move: float = 10_000.0          # min partial lump move, RUB
    pdn_elevated: float = 0.30
    pdn_high: float = 0.50
    pdn_critical: float = 0.80
    min_reserve_fill_months: float = 3.0
    target_reserve_fill_months: float = 6.0
    goal_cap_with_debt: float = 0.5
    debt_share_while_reserve_low: float = 0.7
    urgent_goal_window_days: int = 365
    overdue_rebase_months: int = 12
    near_rate_band: float = 0.02        # confidence: rate near class border
    near_reserve_low: float = 0.8
    near_reserve_high: float = 1.2
    near_flow_share: float = 0.05

    def reserve_target_months(self, risk: int) -> float:
        return self.reserve_months[risk - 1] * self.reserve_scale


@dataclasses.dataclass
class Debt:
    name: str
    amount: float
    rate: float
    payment: float
    klass: str = ""          # cheap | expensive | toxic
    lump_payoff: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.amount - self.lump_payoff)

    @property
    def monthly_interest(self) -> float:
        return self.amount * self.rate / 12.0


@dataclasses.dataclass
class Goal:
    name: str
    target: float
    current: float
    deadline: dt.date | None
    overdue: bool = False
    lump_funding: float = 0.0
    monthly_alloc: float = 0.0
    months_left: int | None = None

    @property
    def gap(self) -> float:
        return max(0.0, self.target - self.current - self.lump_funding)

    @property
    def surplus(self) -> float:
        return max(0.0, self.current - self.target)


@dataclasses.dataclass
class Portrait:
    id: str
    income: float
    expense: float
    debts: list
    goals: list
    bliq: float
    r_bench: float
    risk: int


@dataclasses.dataclass
class Decision:
    id: str
    status: str
    dom: str
    res: int = 0
    debt: int = 0
    goal: int = 0
    inv: int = 0
    lump: int = 0
    confidence: int = 5
    flags: list = dataclasses.field(default_factory=list)
    diagnostics: dict = dataclasses.field(default_factory=dict)
    debt_plan: list = dataclasses.field(default_factory=list)
    lump_sum_plan: list = dataclasses.field(default_factory=list)
    monthly_plan: list = dataclasses.field(default_factory=list)
    goal_plan: list = dataclasses.field(default_factory=list)
    verdict: str = ""

    def csv_row(self) -> list:
        return [self.id, self.status, self.dom, self.res, self.debt,
                self.goal, self.inv, self.lump, self.confidence]


class Validator:
    """Parses a raw JSONL line into a Portrait or an invalid verdict."""

    def __init__(self, constants: Constants):
        self.constants = constants

    @staticmethod
    def _is_number(value) -> bool:
        return (isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value))

    def parse_line(self, line: str):
        """Return (portrait, None) or (None, reason)."""
        try:
            raw = json.loads(line, parse_constant=_reject_constant)
        except (json.JSONDecodeError, ParsedNanError):
            return None, "unparseable_json"
        if not isinstance(raw, dict):
            return None, "not_an_object"
        return self.parse_record(raw)

    def parse_record(self, raw: dict):
        for key in REQUIRED_RECORD_KEYS:
            if key not in raw:
                return None, f"missing_key:{key}"
        if not isinstance(raw["id"], str):
            return None, "bad_type:id"
        for key in ("income_total", "expense_total", "bliq", "r_bench"):
            if not self._is_number(raw[key]):
                return None, f"bad_type:{key}"
            if raw[key] < 0:
                return None, f"negative:{key}"
        risk = raw["risk_tolerance"]
        if isinstance(risk, bool) or not isinstance(risk, int):
            return None, "bad_type:risk_tolerance"
        if not 1 <= risk <= 5:
            return None, "out_of_domain:risk_tolerance"
        if raw["r_bench"] > 1.0:
            return None, "out_of_domain:r_bench"
        if not isinstance(raw["obligations"], list):
            return None, "bad_type:obligations"
        if not isinstance(raw["goals"], list):
            return None, "bad_type:goals"

        debts = []
        for item in raw["obligations"]:
            if not isinstance(item, dict):
                return None, "bad_type:obligation_item"
            for key in REQUIRED_DEBT_KEYS:
                if key not in item:
                    return None, f"missing_key:obligation.{key}"
            if not isinstance(item["name"], str):
                return None, "bad_type:obligation.name"
            for key in ("amount", "interest_rate", "monthly_payment"):
                if not self._is_number(item[key]):
                    return None, f"bad_type:obligation.{key}"
                if item[key] < 0:
                    return None, f"negative:obligation.{key}"
            if item["interest_rate"] > self.constants.garbage_rate:
                return None, "garbage_rate_gt_300pct"
            debts.append(Debt(item["name"], float(item["amount"]),
                              float(item["interest_rate"]),
                              float(item["monthly_payment"])))

        goals = []
        for item in raw["goals"]:
            if not isinstance(item, dict):
                return None, "bad_type:goal_item"
            for key in REQUIRED_GOAL_KEYS:
                if key not in item:
                    return None, f"missing_key:goal.{key}"
            if not isinstance(item["name"], str):
                return None, "bad_type:goal.name"
            for key in ("target_amount", "current_amount"):
                if not self._is_number(item[key]):
                    return None, f"bad_type:goal.{key}"
                if item[key] < 0:
                    return None, f"negative:goal.{key}"
            deadline = item["deadline"]
            parsed_deadline = None
            if deadline is not None:
                if not isinstance(deadline, str) or not DATE_RE.match(deadline):
                    return None, "bad_deadline_format"
                try:
                    parsed_deadline = dt.date.fromisoformat(deadline)
                except ValueError:
                    return None, "bad_deadline_calendar"
            goals.append(Goal(item["name"], float(item["target_amount"]),
                              float(item["current_amount"]), parsed_deadline))

        portrait = Portrait(
            id=raw["id"], income=float(raw["income_total"]),
            expense=float(raw["expense_total"]), debts=debts, goals=goals,
            bliq=float(raw["bliq"]), r_bench=float(raw["r_bench"]), risk=risk,
        )
        return portrait, None


class Advisor:
    """Deterministic decision engine over a validated Portrait."""

    def __init__(self, constants: Constants):
        self.c = constants

    # ------------------------------------------------------------------
    def decide(self, portrait: Portrait) -> Decision:
        c = self.c
        p = portrait
        payments = sum(d.payment for d in p.debts)
        fcf = p.income - p.expense - payments
        burn = p.expense + payments
        pdn = self._pdn(payments, p.income)
        reserve_target = c.reserve_target_months(p.risk) * burn
        min_reserve = c.min_reserve_months * burn
        liquidity_months = self._liquidity_months(p.bliq, burn)

        self._classify_debts(p)
        self._prepare_goals(p)
        flags = self._base_flags(p, fcf, burn, pdn, reserve_target)

        decision = Decision(id=p.id, status="ok", dom="none", flags=flags)
        decision.diagnostics = {
            "fcf": round(fcf, 2), "pdn": round(min(pdn, 999.0), 4),
            "monthly_burn": round(burn, 2), "bliq": round(p.bliq, 2),
            "liquidity_months": round(min(liquidity_months, 999.0), 2),
            "reserve_target": round(reserve_target, 2),
            "min_reserve": round(min_reserve, 2),
            "r_bench": p.r_bench, "risk": p.risk,
            "n_debts": len(p.debts), "n_goals": len(p.goals),
            "debt_total": round(sum(d.amount for d in p.debts), 2),
        }

        deficit = fcf < 0
        decision.status = "deficit" if deficit else "ok"

        lump_total = self._lump_moves(p, decision, burn, reserve_target,
                                      deficit)
        if not deficit:
            self._monthly_waterfall(p, decision, fcf, reserve_target,
                                    min_reserve, lump_total)
        decision.lump = int(math.floor(lump_total))
        decision.dom = self._dominant(decision)
        self._goal_plan(p, decision)
        self._debt_plan(p, decision)
        decision.confidence = self._confidence(p, decision, fcf, burn,
                                               reserve_target)
        decision.verdict = self._verdict(p, decision, fcf)
        self._final_flags(decision)
        return decision

    # ------------------------------------------------------------------
    @staticmethod
    def _pdn(payments: float, income: float) -> float:
        if income > 0:
            return payments / income
        return 999.0 if payments > 0 else 0.0

    @staticmethod
    def _liquidity_months(bliq: float, burn: float) -> float:
        if burn > 0:
            return bliq / burn
        return 999.0 if bliq > 0 else 0.0

    def _classify_debts(self, p: Portrait) -> None:
        for debt in p.debts:
            if debt.rate >= self.c.toxic_rate:
                debt.klass = "toxic"
            elif debt.rate > p.r_bench + self.c.cheap_spread:
                debt.klass = "expensive"
            else:
                debt.klass = "cheap"

    def _prepare_goals(self, p: Portrait) -> None:
        for goal in p.goals:
            if goal.deadline is None:
                continue
            days = (goal.deadline - CUTOFF_DATE).days
            if days < 0:
                goal.overdue = True
                goal.months_left = self.c.overdue_rebase_months
            else:
                goal.months_left = max(1, math.ceil(days / DAYS_PER_MONTH))

    def _base_flags(self, p: Portrait, fcf: float, burn: float, pdn: float,
                    reserve_target: float) -> list:
        c = self.c
        flags = []
        if p.income == 0:
            flags.append("zero_income")
        if burn == 0:
            flags.append("zero_burn")
        if fcf == 0:
            flags.append("zero_flow")
        if pdn > c.pdn_critical:
            flags.append("pdn_critical")
        elif pdn > c.pdn_high:
            flags.append("pdn_gt_05")
        if any(d.klass == "toxic" for d in p.debts):
            flags.append("toxic_debt")
        if p.bliq == 0:
            flags.append("no_reserve")
        elif burn > 0 and p.bliq < c.min_reserve_months * burn:
            flags.append("reserve_below_min")
        for debt in p.debts:
            if debt.amount == 0:
                flags.append("zero_balance_debt")
            elif 0 < debt.payment <= debt.monthly_interest:
                flags.append("interest_only_debt")
        for goal in p.goals:
            if goal.overdue and goal.gap > 0:
                flags.append("goal_overdue")
            if goal.deadline == CUTOFF_DATE:
                flags.append("deadline_today")
            if goal.target == goal.current or goal.target == 0:
                flags.append("goal_completed")
            if goal.surplus > 0:
                flags.append("goal_overfunded")
        return sorted(set(flags))

    # ------------------------------------------------------------------
    def _lump_moves(self, p: Portrait, decision: Decision, burn: float,
                    reserve_target: float, deficit: bool) -> float:
        c = self.c
        floor_toxic = c.floor_toxic_months * burn
        floor_normal = reserve_target
        spent = 0.0

        def excess(floor: float) -> float:
            return max(0.0, p.bliq - spent - floor)

        # L1: toxic debts, avalanche, above the 1-month floor.
        for debt in self._avalanche(p.debts, "toxic"):
            room = excess(floor_toxic)
            if room <= 0:
                break
            move = min(room, debt.amount)
            if move < debt.amount and move < c.min_move:
                continue
            debt.lump_payoff = move
            spent += move
            decision.lump_sum_plan.append(self._move(
                "toxic_debt_payoff", debt.name, move, debt.remaining == 0))

        # L2: expensive debts, avalanche, above the full reserve target.
        for debt in self._avalanche(p.debts, "expensive"):
            room = excess(floor_normal)
            if room <= 0:
                break
            move = min(room, debt.amount)
            if move < debt.amount and move < c.min_move:
                continue
            debt.lump_payoff = move
            spent += move
            decision.lump_sum_plan.append(self._move(
                "expensive_debt_payoff", debt.name, move, debt.remaining == 0))

        if deficit:
            return spent

        # L3: urgent dated goals (deadline within 12 months, incl. overdue).
        urgent = [g for g in p.goals
                  if g.deadline is not None and g.gap > 0
                  and (g.overdue or (g.deadline - CUTOFF_DATE).days
                       <= c.urgent_goal_window_days)]
        urgent.sort(key=lambda g: g.deadline)
        for goal in urgent:
            room = excess(floor_normal)
            if room <= 0:
                break
            move = min(room, goal.gap)
            if move < goal.gap and move < c.min_move:
                continue
            goal.lump_funding += move
            spent += move
            decision.lump_sum_plan.append(self._move(
                "urgent_goal_funding", goal.name, move, goal.gap == 0))

        # L4: place the remaining surplus above the reserve target.
        room = excess(floor_normal)
        if room >= c.min_move:
            spent += room
            decision.lump_sum_plan.append(self._move(
                "surplus_placement", self._placement_name(p.risk), room, True))
        return spent

    @staticmethod
    def _avalanche(debts: list, klass: str) -> list:
        picked = [d for d in debts if d.klass == klass and d.amount > 0]
        return sorted(picked, key=lambda d: (-d.rate, -d.amount))

    @staticmethod
    def _move(kind: str, target: str, amount: float, closes: bool) -> dict:
        return {"kind": kind, "target": target,
                "amount": round(amount, 2), "closes": closes}

    @staticmethod
    def _placement_name(risk: int) -> str:
        names = {1: "вклад/накопительный счёт", 2: "вклады + ОФЗ",
                 3: "ОФЗ + индексный фонд (40% акций)",
                 4: "ОФЗ + индексный фонд (60% акций)",
                 5: "индексный фонд (80% акций) + ОФЗ"}
        return names[risk]

    # ------------------------------------------------------------------
    def _monthly_waterfall(self, p: Portrait, decision: Decision, fcf: float,
                           reserve_target: float, min_reserve: float,
                           lump_total: float) -> None:
        c = self.c
        if fcf <= 0:
            return
        bliq_after = p.bliq - lump_total
        rem = fcf
        res = debt = goal = inv = 0.0

        # W1: emergency minimum reserve (1 month of burn) over ~3 months.
        if bliq_after < min_reserve:
            take = min(rem, (min_reserve - bliq_after)
                       / c.min_reserve_fill_months)
            res += take
            rem -= take

        toxic_left = [d for d in p.debts
                      if d.klass == "toxic" and d.remaining > 0]
        expensive_left = [d for d in p.debts
                          if d.klass == "expensive" and d.remaining > 0]

        if toxic_left and rem > 0:
            # W2: everything remaining goes to toxic debt.
            debt += rem
            rem = 0.0
        else:
            # W3: dated goals by required monthly contribution.
            dated = [g for g in p.goals
                     if g.deadline is not None and g.gap > 0]
            dated.sort(key=lambda g: g.deadline)
            if dated and rem > 0:
                cap = rem * (c.goal_cap_with_debt if expensive_left else 1.0)
                budget = cap
                for g in dated:
                    if budget <= 0:
                        break
                    req = g.gap / g.months_left
                    take = min(req, budget)
                    g.monthly_alloc = take
                    goal += take
                    budget -= take
                rem -= goal
            if expensive_left and rem > 0:
                # W4: expensive debt, optionally co-funding the reserve.
                if bliq_after < reserve_target:
                    share = c.debt_share_while_reserve_low
                    debt += rem * share
                    res += rem * (1.0 - share)
                else:
                    debt += rem
                rem = 0.0
            if rem > 0 and bliq_after < reserve_target:
                # W5: top the reserve up to target over ~6 months.
                take = min(rem, (reserve_target - bliq_after)
                           / c.target_reserve_fill_months)
                res += take
                rem -= take
            if rem > 0:
                # W6: leftover to open-ended goals and investments.
                open_goals = [g for g in p.goals
                              if g.deadline is None and g.gap > 0]
                if open_goals:
                    half = rem / 2.0
                    goal += half
                    share = half / len(open_goals)
                    for g in open_goals:
                        g.monthly_alloc += share
                    inv += rem - half
                else:
                    inv += rem
                rem = 0.0

        decision.res = int(math.floor(res))
        decision.debt = int(math.floor(debt))
        decision.goal = int(math.floor(goal))
        decision.inv = int(math.floor(inv))
        for bucket, amount, note in (
                ("reserve", decision.res, "резерв"),
                ("debt", decision.debt, "досрочное погашение (лавина)"),
                ("goal", decision.goal, "взносы в цели"),
                ("inv", decision.inv, "инвестиции по риск-профилю")):
            if amount > 0:
                decision.monthly_plan.append(
                    {"bucket": bucket, "amount": amount, "note": note})

    # ------------------------------------------------------------------
    @staticmethod
    def _dominant(decision: Decision) -> str:
        buckets = (("debt", decision.debt), ("reserve", decision.res),
                   ("goals+", decision.goal + decision.inv))
        best_name, best_value = "none", 0
        for name, value in buckets:
            if value > best_value:
                best_name, best_value = name, value
        return best_name

    def _goal_plan(self, p: Portrait, decision: Decision) -> None:
        for goal in p.goals:
            entry = {
                "name": goal.name,
                "target": round(goal.target, 2),
                "current": round(goal.current, 2),
                "deadline": goal.deadline.isoformat() if goal.deadline
                else None,
                "gap_after_lump": round(goal.gap, 2),
                "lump_funding": round(goal.lump_funding, 2),
                "monthly_alloc": round(goal.monthly_alloc, 2),
            }
            if goal.surplus > 0:
                entry["note"] = ("цель перефинансирована: излишек "
                                 f"{goal.surplus:.0f} ₽ высвободить в резерв")
                entry["achievable"] = True
            elif goal.gap == 0:
                entry["note"] = "цель закрыта"
                entry["achievable"] = True
            elif goal.deadline is None:
                entry["note"] = "бессрочная: финансируется из остатка потока"
                entry["achievable"] = True
            else:
                req = goal.gap / goal.months_left
                entry["required_monthly"] = round(req, 2)
                entry["months_left"] = goal.months_left
                entry["achievable"] = goal.monthly_alloc >= req - 0.01
                if goal.overdue:
                    entry["note"] = ("дедлайн просрочен: ребейзлайн на "
                                     f"{self.c.overdue_rebase_months} мес")
            decision.goal_plan.append(entry)
        if any(not e.get("achievable", True) for e in decision.goal_plan):
            decision.flags = sorted(set(decision.flags + ["goal_at_risk"]))

    def _debt_plan(self, p: Portrait, decision: Decision) -> None:
        labels = {"cheap": "дешёвый: платить по графику, не гасить досрочно",
                  "expensive": "дорогой: досрочно, лавиной",
                  "toxic": "токсичный: закрыть в первую очередь"}
        for debt in p.debts:
            entry = {"name": debt.name, "rate": debt.rate,
                     "class": debt.klass, "balance": round(debt.amount, 2),
                     "payment": round(debt.payment, 2),
                     "strategy": labels[debt.klass]}
            if debt.lump_payoff > 0:
                entry["lump_payoff"] = round(debt.lump_payoff, 2)
                entry["closed_by_lump"] = debt.remaining == 0
            decision.debt_plan.append(entry)

    # ------------------------------------------------------------------
    def _confidence(self, p: Portrait, decision: Decision, fcf: float,
                    burn: float, reserve_target: float) -> int:
        c = self.c
        penalty = 0
        for debt in p.debts:
            near_cheap = abs(debt.rate - (p.r_bench + c.cheap_spread))
            near_toxic = abs(debt.rate - c.toxic_rate)
            if min(near_cheap, near_toxic) <= c.near_rate_band:
                penalty += 1
                break
        if reserve_target > 0:
            ratio = p.bliq / reserve_target
            if c.near_reserve_low <= ratio <= c.near_reserve_high:
                penalty += 1
        if abs(fcf) < c.near_flow_share * max(p.income, 1.0):
            penalty += 1
        for goal in p.goals:
            if goal.deadline is None or goal.gap <= 0:
                continue
            if goal.overdue or goal.months_left <= 3:
                penalty += 1
                break
        if p.income == 0 or burn == 0:
            penalty += 1
        return max(1, 5 - penalty)

    # ------------------------------------------------------------------
    def _verdict(self, p: Portrait, decision: Decision, fcf: float) -> str:
        closed = [m for m in decision.lump_sum_plan
                  if m["closes"] and m["kind"].endswith("debt_payoff")]
        freed = sum(d.payment for d in p.debts
                    if d.amount > 0 and d.remaining == 0)
        toxic_left = any(d.klass == "toxic" and d.remaining > 0
                         for d in p.debts)
        expensive_left = any(d.klass == "expensive" and d.remaining > 0
                             for d in p.debts)
        parts = []
        if decision.status == "deficit":
            parts.append("Поток отрицательный: сокращать расходы или "
                         "поднимать доход, месячных распределений нет")
            if closed:
                parts.append(f"из подушки закрыть {len(closed)} дорогих/"
                             f"токсичных долгов (освободит {freed:.0f} ₽/мес)")
            elif toxic_left:
                parts.append("токсичный долг реструктурировать в приоритете")
        elif toxic_left:
            parts.append("Пожар: весь свободный поток — на токсичный долг "
                         "до полного закрытия")
        elif expensive_left:
            parts.append("Дорогие долги гасим лавиной досрочно, параллельно "
                         "добираем резерв")
        elif decision.res > 0:
            parts.append("Приоритет — добор подушки до целевой, дальше цели "
                         "и инвестиции")
        elif decision.inv > 0 or decision.goal > 0:
            parts.append("База закрыта: поток в цели и инвестиции по "
                         "риск-профилю")
        elif fcf == 0:
            parts.append("Поток нулевой: жить по графику платежей, резервы "
                         "не трогать")
        else:
            parts.append("Держать текущий курс")
        if "goal_at_risk" in decision.flags:
            parts.append("часть целей к дедлайну недостижима — двигать срок "
                         "или сумму")
        if "goal_overfunded" in decision.flags:
            parts.append("излишек перефинансированных целей высвободить")
        return "; ".join(parts) + "."

    @staticmethod
    def _final_flags(decision: Decision) -> None:
        decision.flags = sorted(set(decision.flags))


class Pipeline:
    """Reads the four blind parts and writes the full answer set."""

    def __init__(self, input_dir: Path, out_dir: Path, constants: Constants):
        self.input_dir = input_dir
        self.out_dir = out_dir
        self.constants = constants
        self.validator = Validator(constants)
        self.advisor = Advisor(constants)

    def input_files(self) -> list:
        pattern = "expert_portraits_v4_part*_jsonl.gz"
        return sorted(self.input_dir.glob(pattern))

    def iter_lines(self):
        for path in self.input_files():
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                for index, line in enumerate(handle):
                    if index == 0 and '"__meta__"' in line:
                        continue
                    yield line

    def decide_line(self, line: str) -> Decision:
        portrait, reason = self.validator.parse_line(line)
        if portrait is None:
            record_id = self._salvage_id(line)
            decision = Decision(id=record_id, status="invalid", dom="none",
                                confidence=5, flags=[f"invalid:{reason}"])
            decision.verdict = ("Запись дефектна, рекомендации не выдаются "
                                f"({reason}).")
            return decision
        return self.advisor.decide(portrait)

    @staticmethod
    def _salvage_id(line: str):
        try:
            raw = json.loads(line, parse_constant=lambda _t: None)
            value = raw.get("id") if isinstance(raw, dict) else None
            return value if isinstance(value, str) else ""
        except json.JSONDecodeError:
            match = re.search(r'"id"\s*:\s*"([^"]+)"', line)
            return match.group(1) if match else ""

    def run(self, write_outputs: bool = True) -> list:
        decisions = [self.decide_line(line) for line in self.iter_lines()]
        seen = {}
        for decision in decisions:
            seen[decision.id] = seen.get(decision.id, 0) + 1
        for decision in decisions:
            if decision.id and seen[decision.id] > 1:
                decision.flags = sorted(set(decision.flags + ["dup_id"]))
        if write_outputs:
            self._write_allocations(decisions)
            self._write_summary(decisions)
            self._write_recommendations(decisions)
        return decisions

    def _write_allocations(self, decisions: list) -> None:
        path = self.out_dir / "expert_allocations_v4.csv"
        with open(path, "w", newline="\n", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["id", "status", "dom", "res", "debt", "goal",
                             "inv", "lump", "confidence"])
            for decision in decisions:
                writer.writerow(decision.csv_row())

    def _write_summary(self, decisions: list) -> None:
        path = self.out_dir / "summary_v4.csv"
        header = ["id", "status", "dom", "flags", "fcf", "pdn",
                  "monthly_burn", "bliq", "liquidity_months",
                  "reserve_target", "n_debts", "debt_total", "n_goals",
                  "res", "debt", "goal", "inv", "lump"]
        with open(path, "w", newline="\n", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            for decision in decisions:
                diag = decision.diagnostics
                writer.writerow([
                    decision.id, decision.status, decision.dom,
                    "|".join(decision.flags),
                    diag.get("fcf", 0), diag.get("pdn", 0),
                    diag.get("monthly_burn", 0), diag.get("bliq", 0),
                    diag.get("liquidity_months", 0),
                    diag.get("reserve_target", 0),
                    diag.get("n_debts", 0), diag.get("debt_total", 0),
                    diag.get("n_goals", 0),
                    decision.res, decision.debt, decision.goal,
                    decision.inv, decision.lump,
                ])

    def _write_recommendations(self, decisions: list) -> None:
        path = self.out_dir / "recommendations_v4.jsonl.gz"
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            for decision in decisions:
                payload = {
                    "id": decision.id, "status": decision.status,
                    "dom": decision.dom, "flags": decision.flags,
                    "diagnostics": decision.diagnostics,
                    "debt_plan": decision.debt_plan,
                    "lump_sum_plan": decision.lump_sum_plan,
                    "monthly_plan": decision.monthly_plan,
                    "goal_plan": decision.goal_plan,
                    "totals": {"res": decision.res, "debt": decision.debt,
                               "goal": decision.goal, "inv": decision.inv,
                               "lump": decision.lump},
                    "verdict": decision.verdict,
                }
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def apply_overrides(constants: Constants, overrides: list) -> Constants:
    for item in overrides:
        key, _, value = item.partition("=")
        if not hasattr(constants, key):
            raise SystemExit(f"unknown constant: {key}")
        current = getattr(constants, key)
        if isinstance(current, tuple):
            parsed = tuple(float(x) for x in value.split(","))
        elif isinstance(current, int) and not isinstance(current, bool):
            parsed = int(value)
        else:
            parsed = float(value)
        setattr(constants, key, parsed)
    return constants


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--set", action="append", default=[],
                        dest="overrides", metavar="CONST=VALUE")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    constants = apply_overrides(Constants(), args.overrides)
    pipeline = Pipeline(args.input_dir, args.out_dir, constants)
    decisions = pipeline.run()
    statuses = {}
    for decision in decisions:
        statuses[decision.status] = statuses.get(decision.status, 0) + 1
    print(f"rows={len(decisions)} statuses={statuses}")


if __name__ == "__main__":
    main()
