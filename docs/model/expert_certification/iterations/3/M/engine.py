#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expert decision engine for portraits v3 (full §5 protocol deliverables).

Reproduces the frozen round-3 methodology decisions exactly (control:
re-derived compact CSV must match expert_answers_v3.csv line by line),
and additionally emits the rich per-portrait plan set:
recommendations_v3.jsonl.gz, summary_v3.csv, aggregate_report_v3.md.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import random
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import date


class Methodology:
    ASOF = date(2026, 7, 16)
    RES_MONTHS = {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}
    FLOOR_MONTHS = 1
    CHEAP_SPREAD = 0.02
    TOX_ABS = 0.25
    TOX_SPREAD = 0.10
    MATERIAL = 10_000
    GOAL_SHARE = {1: 0.60, 2: 0.50, 3: 0.40, 4: 0.30, 5: 0.20}
    MDAYS = 30.4375
    PDN_HIGH = 0.40
    EQUITY_SPLIT = {1: (20, 80), 2: (35, 65), 3: (50, 50), 4: (70, 30), 5: (85, 15)}

    @classmethod
    def cheap_threshold(cls, r_bench: float) -> float:
        return r_bench + cls.CHEAP_SPREAD

    @classmethod
    def toxic_threshold(cls, r_bench: float) -> float:
        return max(cls.TOX_ABS, r_bench + cls.TOX_SPREAD)

    @classmethod
    def months_left(cls, deadline: date) -> int:
        days = (deadline - cls.ASOF).days
        if days <= 0:
            return 1
        return max(1, math.ceil(days / cls.MDAYS))

    @classmethod
    def horizon_instrument(cls, months: int | None, risk: int) -> str:
        if months is None:
            eq, bo = cls.EQUITY_SPLIT[risk]
            return f"смешанный портфель акции/облигации {eq}/{bo}"
        if months <= 12:
            return "вклад / накопительный счёт"
        if months <= 36:
            return "ОФЗ / корп. облигации ИГ короткой дюрации"
        eq, bo = cls.EQUITY_SPLIT[risk]
        return f"смешанный портфель акции/облигации {eq}/{bo}"


@dataclass
class Obligation:
    name: str
    amount: float
    rate: float
    payment: float


@dataclass
class Goal:
    name: str
    target: float
    current: float
    deadline: date | None


@dataclass
class Portrait:
    id: str
    income: float
    expense: float
    bliq: float
    r_bench: float
    risk: int
    obligations: list[Obligation]
    goals: list[Goal]


@dataclass
class InvalidRecord:
    id: str
    reason: str


class Validator:
    @staticmethod
    def _num(x) -> tuple[float | None, str | None]:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            return None, "type"
        if not math.isfinite(x):
            return None, "nan"
        if x < 0:
            return None, "neg"
        return float(x), None

    @classmethod
    def parse(cls, rec) -> Portrait | InvalidRecord:
        rid = str(rec.get("id", "")) if isinstance(rec, dict) else ""
        if not isinstance(rec, dict):
            return InvalidRecord(rid, "not_object")
        for k in ("id", "income_total", "expense_total", "obligations", "goals",
                  "bliq", "r_bench", "risk_tolerance"):
            if k not in rec:
                return InvalidRecord(rid, f"missing:{k}")
        if not isinstance(rec["id"], str) or not rec["id"]:
            return InvalidRecord(rid, "type:id")
        vals = {}
        for k in ("income_total", "expense_total", "bliq", "r_bench"):
            v, err = cls._num(rec[k])
            if err:
                return InvalidRecord(rid, f"{err}:{k}")
            vals[k] = v
        rt = rec["risk_tolerance"]
        if isinstance(rt, bool):
            return InvalidRecord(rid, "type:risk_tolerance")
        if isinstance(rt, float) and rt.is_integer():
            rt = int(rt)
        if not isinstance(rt, int):
            return InvalidRecord(rid, "type:risk_tolerance")
        if not 1 <= rt <= 5:
            return InvalidRecord(rid, "domain:risk_tolerance")
        if not isinstance(rec["obligations"], list):
            return InvalidRecord(rid, "type:obligations")
        if not isinstance(rec["goals"], list):
            return InvalidRecord(rid, "type:goals")
        obligations = []
        for o in rec["obligations"]:
            if not isinstance(o, dict):
                return InvalidRecord(rid, "type:obligation")
            for k in ("name", "amount", "interest_rate", "monthly_payment"):
                if k not in o:
                    return InvalidRecord(rid, f"missing:obligation.{k}")
            if not isinstance(o["name"], str):
                return InvalidRecord(rid, "type:obligation.name")
            a, e1 = cls._num(o["amount"])
            r, e2 = cls._num(o["interest_rate"])
            p, e3 = cls._num(o["monthly_payment"])
            for e, f in ((e1, "amount"), (e2, "interest_rate"), (e3, "monthly_payment")):
                if e:
                    return InvalidRecord(rid, f"{e}:obligation.{f}")
            obligations.append(Obligation(o["name"], a, r, p))
        goals = []
        for g in rec["goals"]:
            if not isinstance(g, dict):
                return InvalidRecord(rid, "type:goal")
            for k in ("name", "target_amount", "current_amount", "deadline"):
                if k not in g:
                    return InvalidRecord(rid, f"missing:goal.{k}")
            if not isinstance(g["name"], str):
                return InvalidRecord(rid, "type:goal.name")
            t, e1 = cls._num(g["target_amount"])
            c, e2 = cls._num(g["current_amount"])
            for e, f in ((e1, "target_amount"), (e2, "current_amount")):
                if e:
                    return InvalidRecord(rid, f"{e}:goal.{f}")
            d = g["deadline"]
            dd = None
            if d is not None:
                if not isinstance(d, str):
                    return InvalidRecord(rid, "type:goal.deadline")
                try:
                    dd = date.fromisoformat(d)
                except ValueError:
                    return InvalidRecord(rid, "date:goal.deadline")
            goals.append(Goal(g["name"], t, c, dd))
        return Portrait(rec["id"], vals["income_total"], vals["expense_total"],
                        vals["bliq"], vals["r_bench"], rt, obligations, goals)


@dataclass
class Recommendation:
    id: str
    status: str
    dom: str = "none"
    res: int = 0
    debt: int = 0
    goal: int = 0
    inv: int = 0
    lump: int = 0
    flags: list = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)
    debt_plan: list = field(default_factory=list)
    lump_sum_plan: list = field(default_factory=list)
    monthly_plan: list = field(default_factory=list)
    goal_plan: list = field(default_factory=list)
    verdict: str = ""

    def compact_row(self) -> tuple:
        return (self.id, self.status, self.dom, self.res, self.debt,
                self.goal, self.inv, self.lump)

    def to_json(self) -> str:
        payload = {"id": self.id, "status": self.status, "dom": self.dom,
                   "flags": self.flags, "diagnostics": self.diagnostics,
                   "debt_plan": self.debt_plan,
                   "lump_sum_plan": self.lump_sum_plan,
                   "monthly_plan": self.monthly_plan,
                   "goal_plan": self.goal_plan,
                   "totals": {"res": self.res, "debt": self.debt,
                              "goal": self.goal, "inv": self.inv,
                              "lump": self.lump},
                   "verdict": self.verdict}
        return json.dumps(payload, ensure_ascii=False)


def _fmt(x: float) -> str:
    return f"{int(round(x)):,}".replace(",", " ")


def _r2(x: float | None):
    return None if x is None else round(x, 2)


class DecisionEngine:
    def __init__(self, m: type[Methodology] = Methodology):
        self.m = m

    def solve(self, p: Portrait) -> Recommendation:
        m = self.m
        rec = Recommendation(p.id, "ok")
        pay_sum = sum(o.payment for o in p.obligations)
        burn = p.expense + pay_sum
        fcf = p.income - p.expense - pay_sum
        target = m.RES_MONTHS[p.risk] * burn
        floor = m.FLOOR_MONTHS * burn
        cheap = m.cheap_threshold(p.r_bench)
        toxic = m.toxic_threshold(p.r_bench)
        pdn = pay_sum / p.income if p.income > 0 else None
        rec.diagnostics = {
            "fcf": _r2(fcf), "pdn": None if pdn is None else round(pdn, 4),
            "monthly_burn": _r2(burn), "bliq": _r2(p.bliq),
            "liquidity_months": _r2(p.bliq / burn) if burn > 0 else None,
            "reserve_floor": _r2(floor), "reserve_target": _r2(target),
            "thr_cheap": round(cheap, 4), "thr_toxic": round(toxic, 4),
        }
        rec.flags = self._flags(p, fcf, pdn, toxic)

        debts = sorted(({"o": o, "a": o.amount, "lump": 0.0, "monthly": 0}
                        for o in p.obligations if o.amount > 0),
                       key=lambda d: -d["o"].rate)
        goals = [{"g": g, "c": g.current, "lump": 0.0, "monthly": 0} for g in p.goals]
        bliq = p.bliq
        lump = 0.0

        if fcf < 0:
            rec.status = "deficit"
            bcur = burn
            for d in debts:
                if d["o"].rate <= cheap or d["a"] <= 0:
                    continue
                b_after = bcur - d["o"].payment
                if bliq - d["a"] >= m.FLOOR_MONTHS * b_after:
                    amount = d["a"]
                    bliq -= amount
                    lump += amount
                    bcur = b_after
                    d["a"] = 0.0
                    d["lump"] = amount
                    rec.lump_sum_plan.append(
                        {"step": "deficit_payoff", "target": d["o"].name,
                         "amount": _r2(amount)})
            rec.lump = int(lump)
            self._fill_debt_plan(rec, debts, cheap, toxic)
            self._fill_goal_plan(rec, goals)
            rec.verdict = self._verdict(rec, fcf)
            return rec

        for d in debts:
            if d["a"] <= 0 or d["o"].rate < toxic:
                continue
            avail = bliq - floor
            if avail <= 0:
                break
            pay = min(avail, d["a"])
            if pay == d["a"] or pay >= m.MATERIAL:
                d["a"] -= pay
                bliq -= pay
                lump += pay
                d["lump"] += pay
                rec.lump_sum_plan.append(
                    {"step": "toxic_payoff", "target": d["o"].name,
                     "amount": _r2(pay)})
        for d in debts:
            if d["a"] <= 0 or not (cheap < d["o"].rate < toxic):
                continue
            avail = bliq - target
            if avail <= 0:
                break
            pay = min(avail, d["a"])
            if pay == d["a"] or pay >= m.MATERIAL:
                d["a"] -= pay
                bliq -= pay
                lump += pay
                d["lump"] += pay
                rec.lump_sum_plan.append(
                    {"step": "expensive_payoff", "target": d["o"].name,
                     "amount": _r2(pay)})
        for g in sorted((g for g in goals if g["g"].deadline is not None),
                        key=lambda g: g["g"].deadline):
            need = g["g"].target - g["c"]
            avail = bliq - target
            if need <= 0 or avail <= 0:
                continue
            pay = min(avail, need)
            if pay == need or pay >= m.MATERIAL:
                g["c"] += pay
                bliq -= pay
                lump += pay
                g["lump"] += pay
                rec.lump_sum_plan.append(
                    {"step": "goal_topup", "target": g["g"].name,
                     "amount": _r2(pay)})
        excess = bliq - target
        if excess >= m.MATERIAL:
            bliq -= excess
            lump += excess
            rec.lump_sum_plan.append(
                {"step": "park_excess",
                 "target": Methodology.horizon_instrument(None, p.risk),
                 "amount": _r2(excess)})

        rem = int(fcf)
        res = debt = goal_amt = inv = 0
        a = min(rem, int(max(0.0, floor - bliq)))
        if a > 0:
            rec.monthly_plan.append({"bucket": "reserve_floor", "amount": a,
                                     "instrument": "накопительный счёт / фонд денежного рынка"})
        res += a
        rem -= a
        tox_amt = int(sum(d["a"] for d in debts if d["o"].rate >= toxic))
        a = min(rem, tox_amt)
        if a > 0:
            rec.monthly_plan.append({"bucket": "debt_toxic", "amount": a,
                                     "instrument": "досрочное погашение (аваланш)"})
            self._spread_monthly(debts, a, lambda d: d["o"].rate >= toxic)
        debt += a
        rem -= a
        a = min(rem, max(0, int(max(0.0, target - bliq)) - res))
        if a > 0:
            rec.monthly_plan.append({"bucket": "reserve_target", "amount": a,
                                     "instrument": "накопительный счёт / фонд денежного рынка"})
        res += a
        rem -= a
        exp_amt = int(sum(d["a"] for d in debts if cheap < d["o"].rate < toxic))
        a = min(rem, exp_amt)
        if a > 0:
            rec.monthly_plan.append({"bucket": "debt_expensive", "amount": a,
                                     "instrument": "досрочное погашение (аваланш)"})
            self._spread_monthly(debts, a, lambda d: cheap < d["o"].rate < toxic)
        debt += a
        rem -= a
        for g in sorted((g for g in goals
                         if g["g"].deadline is not None and g["g"].target > g["c"]),
                        key=lambda g: g["g"].deadline):
            if rem <= 0:
                break
            need = int(g["g"].target - g["c"])
            if need <= 0:
                continue
            months = Methodology.months_left(g["g"].deadline)
            nm = math.ceil(need / months)
            a = min(rem, nm)
            g["monthly"] += a
            rec.monthly_plan.append(
                {"bucket": "goal_deadline", "target": g["g"].name, "amount": a,
                 "instrument": Methodology.horizon_instrument(months, p.risk)})
            goal_amt += a
            rem -= a
        if rem > 0:
            bess = int(sum(max(0.0, g["g"].target - g["c"])
                           for g in goals if g["g"].deadline is None))
            if bess > 0:
                a = min(int(round(rem * m.GOAL_SHARE[p.risk])), bess, rem)
                if a > 0:
                    rec.monthly_plan.append(
                        {"bucket": "goal_perpetual", "amount": a,
                         "instrument": Methodology.horizon_instrument(None, p.risk)})
                    self._spread_perpetual(goals, a)
                goal_amt += a
                inv += rem - a
                if rem - a > 0:
                    rec.monthly_plan.append(
                        {"bucket": "invest", "amount": rem - a,
                         "instrument": Methodology.horizon_instrument(None, p.risk)})
            else:
                inv += rem
                rec.monthly_plan.append(
                    {"bucket": "invest", "amount": rem,
                     "instrument": Methodology.horizon_instrument(None, p.risk)})
            rem = 0
        buckets = {"debt": debt, "reserve": res, "goals+": goal_amt + inv}
        if debt == 0 and res == 0 and goal_amt + inv == 0:
            dom = "none"
        else:
            best = max(buckets.values())
            dom = next(k for k in ("debt", "reserve", "goals+") if buckets[k] == best)
        assert res + debt + goal_amt + inv <= max(0, int(fcf))
        rec.dom = dom
        rec.res, rec.debt, rec.goal, rec.inv = res, debt, goal_amt, inv
        rec.lump = int(lump)
        self._fill_debt_plan(rec, debts, cheap, toxic)
        self._fill_goal_plan(rec, goals)
        rec.verdict = self._verdict(rec, fcf)
        return rec

    @staticmethod
    def _spread_monthly(debts: list, amount: int, pred) -> None:
        for d in debts:
            if amount <= 0:
                break
            if not pred(d) or d["a"] <= 0:
                continue
            take = min(amount, int(d["a"]))
            d["monthly"] += take
            amount -= take

    @staticmethod
    def _spread_perpetual(goals: list, amount: int) -> None:
        pool = [g for g in goals
                if g["g"].deadline is None and g["g"].target - g["c"] > 0]
        need_total = sum(g["g"].target - g["c"] for g in pool)
        left = amount
        for i, g in enumerate(pool):
            share = (amount * (g["g"].target - g["c"]) / need_total
                     if need_total > 0 else 0)
            take = left if i == len(pool) - 1 else min(left, int(share))
            g["monthly"] += take
            left -= take

    def _flags(self, p: Portrait, fcf: float, pdn: float | None,
               toxic: float) -> list:
        f = []
        if p.income == 0:
            f.append("zero_income")
        if p.expense == 0:
            f.append("zero_expenses")
        if p.bliq == 0:
            f.append("zero_bliq")
        if not p.obligations:
            f.append("no_debts")
        if not p.goals:
            f.append("no_goals")
        if fcf < 0:
            f.append("deficit_flow")
        if pdn is not None and pdn > self.m.PDN_HIGH:
            f.append("pdn_high")
        if any(o.amount > 0 and o.rate >= toxic for o in p.obligations):
            f.append("toxic_debt")
        if any(o.amount > 0 and o.payment < o.amount * o.rate / 12
               for o in p.obligations):
            f.append("negative_amortization")
        if any(g.deadline is not None and (g.deadline - self.m.ASOF).days <= 0
               for g in p.goals):
            f.append("overdue_deadline")
        if any(g.current > g.target for g in p.goals):
            f.append("overfunded_goal")
        return f

    def _fill_debt_plan(self, rec: Recommendation, debts: list,
                        cheap: float, toxic: float) -> None:
        for d in debts:
            o = d["o"]
            cls = ("toxic" if o.rate >= toxic
                   else "expensive" if o.rate > cheap else "cheap")
            if d["lump"] and d["a"] <= 0:
                action = "закрыть разовым платежом из ликвидности"
            elif d["lump"]:
                action = "частично погасить разово, остаток — аваланш из потока"
            elif d["monthly"]:
                action = "гасить ускоренно из месячного потока (аваланш)"
            elif cls == "cheap":
                action = "гасить по графику: ставка не выше бенчмарк+2 пп"
            else:
                action = "по графику; в очереди аваланша за более дорогими"
            rec.debt_plan.append(
                {"name": o.name, "amount": _r2(o.amount),
                 "rate": round(o.rate, 4), "class": cls,
                 "lump_payoff": _r2(d["lump"]), "monthly_extra": d["monthly"],
                 "action": action})

    def _fill_goal_plan(self, rec: Recommendation, goals: list) -> None:
        for g in goals:
            gg = g["g"]
            need = gg.target - g["c"]
            months = (Methodology.months_left(gg.deadline)
                      if gg.deadline is not None else None)
            required = (math.ceil(max(0, int(need)) / months)
                        if months is not None and need > 0 else 0)
            if gg.current > gg.target:
                state = "overfunded"
            elif need <= 0:
                state = "funded"
            elif months is None:
                state = "accumulating" if g["monthly"] > 0 else "paused"
            else:
                state = "on_track" if g["monthly"] >= required else "underfunded"
            rec.goal_plan.append(
                {"name": gg.name, "target": _r2(gg.target),
                 "current_after_lump": _r2(g["c"]),
                 "deadline": gg.deadline.isoformat() if gg.deadline else None,
                 "months_left": months, "required_monthly": required,
                 "allocated_monthly": g["monthly"],
                 "lump_topup": _r2(g["lump"]), "state": state})

    @staticmethod
    def _verdict(rec: Recommendation, fcf: float) -> str:
        if rec.status == "deficit":
            base = f"Дефицит потока {_fmt(-fcf)} ₽/мес"
            if rec.lump > 0:
                base += f"; разово закрыто долгов на {_fmt(rec.lump)} ₽ из ликвидности"
            else:
                base += "; безопасных разовых погашений нет"
            return base + "; приоритет — восстановление положительного потока."
        focus = {"debt": "фокус — ускоренное гашение дорогих долгов",
                 "reserve": "фокус — доведение подушки до целевой",
                 "goals+": "фокус — цели и долгосрочные инвестиции",
                 "none": "свободный поток нулевой — держать текущий курс"}[rec.dom]
        base = f"Профиль устойчив (FCF {_fmt(fcf)} ₽/мес); {focus}"
        if rec.lump > 0:
            base += f"; разово задействовано {_fmt(rec.lump)} ₽ ликвидности"
        return base + "."


UPLOADS = "/mnt/user-data/uploads"
OUT = "/mnt/user-data/outputs"


class Runner:
    PARTS = [f"{UPLOADS}/expert_portraits_v3_part{i}_jsonl.gz" for i in (1, 2, 3, 4)]
    CARDS = f"{UPLOADS}/portraits_v3_seed20260716_cards.md"
    FROZEN = f"{OUT}/expert_answers_v3.csv"
    ID_RE = re.compile(r'"id"\s*:\s*"([^"]*)"')

    def __init__(self):
        self.engine = DecisionEngine()
        self.recs: list[Recommendation] = []
        self.portraits: dict[int, Portrait] = {}

    def run(self) -> None:
        t0 = time.time()
        for path in self.PARTS:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for ln, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except Exception:
                        m = self.ID_RE.search(line)
                        rid = m.group(1) if m else ""
                        self.recs.append(self._invalid(rid, "bad_json"))
                        continue
                    if ln == 1 and isinstance(raw, dict) and raw.get("__meta__") is True:
                        continue
                    parsed = Validator.parse(raw)
                    if isinstance(parsed, InvalidRecord):
                        self.recs.append(self._invalid(parsed.id, parsed.reason))
                        continue
                    self.portraits[len(self.recs)] = parsed
                    self.recs.append(self.engine.solve(parsed))
        controls = self._controls()
        self._write_outputs(controls, time.time() - t0)

    @staticmethod
    def _invalid(rid: str, reason: str) -> Recommendation:
        r = Recommendation(rid, "invalid")
        r.flags = [f"invalid:{reason}"]
        r.verdict = f"Запись отбракована ({reason}); рекомендации не выдаются."
        return r

    def _controls(self) -> dict:
        c = {}
        with open(self.FROZEN, newline="", encoding="utf-8") as f:
            frozen = list(csv.reader(f))[1:]
        assert len(frozen) == len(self.recs)
        diffs = sum(1 for row, rec in zip(frozen, self.recs)
                    if tuple(row) != tuple(map(str, rec.compact_row())))
        c["frozen_csv_diffs"] = diffs
        drift = []
        lump_viol = cons_viol = 0
        for i, rec in enumerate(self.recs):
            if rec.status == "invalid":
                continue
            p = self.portraits[i]
            fcf = p.income - p.expense - sum(o.payment for o in p.obligations)
            s4 = rec.res + rec.debt + rec.goal + rec.inv
            expected = max(0, int(fcf))
            if s4 != expected and rec.status == "ok":
                cons_viol += 1
            drift.append(max(0.0, fcf) - s4 if rec.status == "ok" else 0.0)
            if rec.lump > p.bliq + 0.5:
                lump_viol += 1
        c["conservation_violations"] = cons_viol
        c["max_truncation_drift_rub"] = round(max(drift), 8) if drift else 0
        c["lump_over_bliq"] = lump_viol
        c["card_checks"] = self._card_checks()
        return c

    def _card_checks(self) -> list:
        rng = random.Random(20260717)
        valid_idx = [i for i in self.portraits]
        picks = rng.sample(valid_idx, 3)
        text = open(self.CARDS, encoding="utf-8").read()
        results = []
        for i in picks:
            p = self.portraits[i]
            m = re.search(
                rf"### {re.escape(p.id)} · риск (\d).*?\n"
                rf"Доход ([\d\s\u00a0\u202f]+\.?\d*) ₽/мес · "
                rf"Расходы ([\d\s\u00a0\u202f]+\.?\d*) ₽/мес · "
                rf"Накопления ([\d\s\u00a0\u202f]+\.?\d*) ₽", text)
            if not m:
                results.append({"id": p.id, "match": False, "reason": "card_not_found"})
                continue

            def num(s: str) -> float:
                return float(re.sub(r"[\s\u00a0\u202f]", "", s))
            ok = (int(m.group(1)) == p.risk
                  and abs(num(m.group(2)) - p.income) < 0.01
                  and abs(num(m.group(3)) - p.expense) < 0.01
                  and abs(num(m.group(4)) - p.bliq) < 0.01)
            results.append({"id": p.id, "match": ok})
        return results

    def _write_outputs(self, controls: dict, elapsed: float) -> None:
        with gzip.open(f"{OUT}/recommendations_v3.jsonl.gz", "wt",
                       encoding="utf-8") as f:
            for rec in self.recs:
                f.write(rec.to_json() + "\n")
        with open(f"{OUT}/summary_v3.csv", "w", newline="",
                  encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "status", "dom", "flags", "fcf", "pdn",
                        "monthly_burn", "bliq", "liquidity_months",
                        "reserve_target", "n_debts", "debt_total", "n_goals",
                        "res", "debt", "goal", "inv", "lump"])
            for i, rec in enumerate(self.recs):
                d = rec.diagnostics
                p = self.portraits.get(i)
                w.writerow([rec.id, rec.status, rec.dom, "|".join(rec.flags),
                            d.get("fcf", ""), d.get("pdn", ""),
                            d.get("monthly_burn", ""), d.get("bliq", ""),
                            d.get("liquidity_months", ""),
                            d.get("reserve_target", ""),
                            len(p.obligations) if p else "",
                            _r2(sum(o.amount for o in p.obligations)) if p else "",
                            len(p.goals) if p else "",
                            rec.res, rec.debt, rec.goal, rec.inv, rec.lump])
        self._write_report(controls, elapsed)
        print(json.dumps({"controls": controls, "elapsed_s": round(elapsed, 2),
                          "rows": len(self.recs)}, ensure_ascii=False, indent=1))

    def _write_report(self, controls: dict, elapsed: float) -> None:
        st = Counter(r.status for r in self.recs)
        dm = Counter(r.dom for r in self.recs)
        fl = Counter(f for r in self.recs for f in r.flags)
        lump_steps = Counter(e["step"] for r in self.recs for e in r.lump_sum_plan)
        lump_sums = Counter()
        for r in self.recs:
            for e in r.lump_sum_plan:
                lump_sums[e["step"]] += e["amount"]
        tot = {k: sum(getattr(r, k) for r in self.recs)
               for k in ("res", "debt", "goal", "inv", "lump")}
        m = Methodology
        L = []
        A = L.append
        A("# Aggregate report — полный протокол §5, portraits v3\n")
        A(f"Срез данных: {m.ASOF.isoformat()} (дата датасета, консистентно с "
          "раундом 3). Обработка: программная, полная, детерминированная; "
          f"{len(self.recs)} записей за {elapsed:.2f} с.\n")
        A("## Допущения по схеме входа")
        A("Схема v3 не содержит полей `kind`, `index`, `engine`, `l_min` и "
          "суб-`id` кредитов/целей из универсального промпта §5. Принято: "
          "`l_min` = 1 месячный бюджет B (константа FLOOR_MONTHS замороженной "
          "методологии); чек-лист (е) «валидация меток kind» неприменим — "
          "аналог выполнен в dataset_review.md через имена кредитов; кредиты и "
          "цели идентифицируются именем и позицией. Решения и суммы — строго "
          "по замороженной методологии раунда 3 (expert_methodology_v3.md); "
          "новое здесь — только отчётный слой: инструменты по горизонту и "
          "разбивка акции/облигации. Суммы он не меняет.\n")
        A("## Константы")
        A("| параметр | значение |")
        A("|---|---|")
        A(f"| Подушка по риску 1–5, мес | {m.RES_MONTHS} |")
        A(f"| Минимум ликвидности | {m.FLOOR_MONTHS} × B |")
        A(f"| «Дешёвый» долг | ставка ≤ r_bench + {m.CHEAP_SPREAD:.0%} |")
        A(f"| «Токсичный» долг | ставка ≥ max({m.TOX_ABS:.0%}, r_bench + {m.TOX_SPREAD:.0%}) |")
        A(f"| Порог существенности разовой операции | {m.MATERIAL:,} ₽ |".replace(",", " "))
        A(f"| Доля остатка на бессрочные цели по риску | {m.GOAL_SHARE} |")
        A(f"| Порог высокого ПДН (флаг) | {m.PDN_HIGH} |")
        A(f"| Акции/облигации по риску (отчётный слой) | {m.EQUITY_SPLIT} |")
        A("| Инструменты по горизонту (отчётный слой) | ≤12 мес: вклад/накопительный; "
          "13–36: ОФЗ/корп. ИГ; >36 и бессрочные: смешанный портфель |")
        A("")
        A("## Распределения")
        A(f"- Статусы: {dict(st)}")
        A(f"- Доминанты: {dict(dm)}")
        A(f"- Флаги: {dict(fl.most_common())}")
        A("")
        A("## Агрегаты, ₽")
        A(f"- Месячные бакеты: res {_fmt(tot['res'])} · debt {_fmt(tot['debt'])} "
          f"· goal {_fmt(tot['goal'])} · inv {_fmt(tot['inv'])}")
        A(f"- Разовые операции: всего {_fmt(tot['lump'])}, по шагам: "
          + "; ".join(f"{k} — {v} шт., {_fmt(lump_sums[k])} ₽"
                      for k, v in lump_steps.most_common()))
        A("")
        A("## Контроли")
        A(f"1. Воспроизведение замороженного CSV раунда 3: "
          f"**{controls['frozen_csv_diffs']} расхождений** из {len(self.recs)} строк.")
        A(f"2. Сохранение сумм (ok-строки): res+debt+goal+inv == ⌊max(0, FCF)⌋ — "
          f"**{controls['conservation_violations']} нарушений**; максимальный "
          f"остаток целочисленного усечения {controls['max_truncation_drift_rub']} ₽ "
          "(SP3-00843: FCF математически 5 463, в двоичном float 5 462.999…998; "
          "усечение по замороженному правилу отдаёт 5 462 ₽ — консерватизм ≤ 1 ₽ на строку).")
        A(f"3. lump ≤ доступной ликвидности: **{controls['lump_over_bliq']} нарушений**.")
        A("4. Сверка JSONL ↔ карточки (3 случайных, seed 20260717): "
          + "; ".join(f"{c['id']} — {'совпало' if c['match'] else 'РАСХОЖДЕНИЕ'}"
                      for c in controls["card_checks"]) + ".")
        A("")
        A("## Файлы поставки")
        A("`recommendations_v3.jsonl.gz` (полные планы + вердикты), "
          "`summary_v3.csv` (плоские метрики), `engine_v3.py` (движок), "
          "`expert_answers_v3.csv` (компакт, раунд 3, заморожен), "
          "`expert_methodology_v3.md`, `dataset_review.md` — без изменений.")
        with open(f"{OUT}/aggregate_report_v3.md", "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    Runner().run()
