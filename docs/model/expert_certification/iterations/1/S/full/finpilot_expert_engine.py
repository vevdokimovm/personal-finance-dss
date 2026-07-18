"""FINPILOT expert engine v2 — protocol-compliant output schema.

Allocation logic is identical to v1 (published and validated prior to receiving
the coordination protocol). This version emits the record layout required by
the expert protocol: status, flags, diagnostics, debt_plan (per obligation),
lump_sum_plan, monthly_plan, goal_plan, verdict.

Methodology constants (fixed before processing):
  reserve floor 3 months of full outflow, target 6 months (flat across risk
  profiles by design: the reserve is a safety instrument, risk appetite feeds
  the investment mix instead); expensive debt = rate > r_bench + 3 pp;
  grey band = [r_bench, r_bench + 3 pp], funded 50/50 from residual;
  cheap debt (rate < r_bench) is never prepaid outside crisis;
  PDN thresholds 30% / 50%; crisis closures require full payoff, post-close
  liquidity >= 1 month of new outflow and balance/payment < current runway;
  cheap debts close in crisis only when runway < 12 months; ASV limit 1.4M RUB;
  valuation date 2026-07-07; goal savings pots are separate from B_liq.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

TODAY = date(2026, 7, 7)
FLOOR_MONTHS = 3.0
TARGET_MONTHS = 6.0
EXPENSIVE_SPREAD = 0.03
CHEAP_CLOSE_RUNWAY = 12.0
CRISIS_MIN_FLOOR_MONTHS = 1.0
ASV_LIMIT = 1_400_000.0
EPS = 0.5

RISK_MIX = {
    1: "депозиты/ОФЗ, без акций",
    2: "депозиты/ОФЗ + до 10% акций (индексный фонд)",
    3: "депозиты/ОФЗ + 20-30% акций (индексный фонд)",
    4: "депозиты/ОФЗ + 30-45% акций (индексный фонд)",
    5: "депозиты/ОФЗ + 45-60% акций (индексный фонд)",
}
RESERVE_INSTRUMENT = "накопительный счёт / депозит до 3 мес с пополнением и снятием"


@dataclass
class Obligation:
    id: int
    name: str
    amount: float
    interest_rate: float
    monthly_payment: float

    @property
    def interest_only(self) -> float:
        return self.amount * self.interest_rate / 12.0

    @property
    def non_amortizing(self) -> bool:
        return self.monthly_payment <= self.interest_only + 1e-9


@dataclass
class Goal:
    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: date | None

    @property
    def funded(self) -> bool:
        return self.current_amount >= self.target_amount - EPS

    @property
    def gap(self) -> float:
        return max(self.target_amount - self.current_amount, 0.0)

    def months_left(self, today: date) -> int | None:
        if self.deadline is None:
            return None
        return max((self.deadline.year - today.year) * 12 + (self.deadline.month - today.month), 0)


@dataclass
class _State:
    income: float
    expenses: float
    r_bench: float
    debts: list[Obligation]
    balances: dict[int, float] = field(default_factory=dict)
    prepaid: dict[int, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.balances = {o.id: o.amount for o in self.debts}
        self.prepaid = {o.id: 0.0 for o in self.debts}

    def open_debts(self) -> list[Obligation]:
        return [o for o in self.debts if self.balances[o.id] > EPS]

    def debt_service(self) -> float:
        return sum(o.monthly_payment for o in self.open_debts())

    def outflow(self) -> float:
        return self.expenses + self.debt_service()

    def fcf(self) -> float:
        return self.income - self.outflow()


def monthly_rate(annual: float) -> float:
    return (1.0 + annual) ** (1.0 / 12.0) - 1.0


def required_monthly(current: float, target: float, months: int, i: float) -> float:
    if current >= target - EPS:
        return 0.0
    if months <= 0:
        return target - current
    growth = (1.0 + i) ** months
    if i <= 0:
        return max((target - current) / months, 0.0)
    return max((target - current * growth) * i / (growth - 1.0), 0.0)


def months_to_reach(current: float, monthly: float, target: float, i: float) -> float | None:
    if current >= target - EPS:
        return 0.0
    if monthly <= EPS:
        if current <= EPS or i <= 0:
            return None
        return math.log(target / current) / math.log(1.0 + i)
    if i <= 0:
        return (target - current) / monthly
    return math.log((target * i + monthly) / (current * i + monthly)) / math.log(1.0 + i)


def band(rate: float, r_bench: float) -> str:
    if rate > r_bench + EXPENSIVE_SPREAD:
        return "expensive"
    if rate >= r_bench:
        return "grey"
    return "cheap"


class ExpertEngine:
    def advise(self, profile: dict) -> dict:
        eng = profile["engine"]
        income = float(eng["income_total"])
        expenses = float(eng["expense_total"])
        bliq = float(eng["bliq"])
        r_bench = float(eng["r_bench"])
        risk = int(eng["risk_tolerance"])
        debts = [
            Obligation(o["id"], o["name"], float(o["amount"]),
                       float(o["interest_rate"]), float(o["monthly_payment"]))
            for o in eng["obligations"]
        ]
        goals = [
            Goal(g["id"], g["name"], float(g["target_amount"]), float(g["current_amount"]),
                 date.fromisoformat(g["deadline"]) if g.get("deadline") else None)
            for g in eng["goals"]
        ]

        st = _State(income, expenses, r_bench, debts)
        flags: list[str] = []
        actions: list[str] = []

        service0 = st.debt_service()
        outflow0 = st.outflow()
        fcf0 = st.fcf()
        pdn0 = service0 / income if income > 0 else None
        cushion0 = bliq / outflow0 if outflow0 > 0 else None
        deployable0 = max(bliq - FLOOR_MONTHS * outflow0, 0.0)

        if income <= EPS:
            flags.append("no_income")
        if expenses <= EPS:
            flags.append("zero_expenses")
        if outflow0 <= EPS:
            flags.append("zero_outflow")
        if fcf0 < -EPS:
            flags.append("negative_fcf")
        if pdn0 is None and service0 > EPS:
            flags.append("debt_with_no_income")
        elif pdn0 is not None and pdn0 > 0.5:
            flags.append("pdn_red_zone")
        elif pdn0 is not None and pdn0 > 0.3:
            flags.append("pdn_elevated")
        non_amort = [o for o in debts if o.non_amortizing]
        if non_amort:
            flags.append("payment_below_interest")
        if bliq > ASV_LIMIT:
            flags.append("above_asv_limit")
        if any(g.funded for g in goals):
            flags.append("goal_already_funded")

        branch = "normal"
        if fcf0 < -EPS:
            bliq_left = self._crisis_repair(st, bliq, actions)
            if st.fcf() >= -EPS:
                branch = "crisis_repaired"
                flags.append("cash_flow_repaired_by_closures")
            else:
                branch = "crisis"
        else:
            bliq_left = bliq

        if branch == "crisis":
            body = self._finalize_crisis(st, bliq_left, goals, risk, actions)
        else:
            body = self._normal_cascade(st, bliq_left, goals, risk, actions, flags)

        (reserve, invest_stock, from_stock, goal_rows, fl_reserve_total,
         fl_debt, fl_goals, invest_flow, grey_flow) = body

        if branch != "crisis" and pdn0 is not None and pdn0 > 0.5 and st.open_debts():
            actions.append(
                f"Рефинансировать оставшиеся кредиты: ПДН {pdn0:.0%} — красная зона"
            )
        for o in non_amort:
            if st.balances[o.id] > EPS:
                actions.append(
                    f"Реструктурировать {o.name}: платёж {round(o.monthly_payment)} ₽ "
                    f"не покрывает проценты ({round(o.interest_only)} ₽/мес)"
                )
        if reserve > ASV_LIMIT:
            actions.append("Разложить резерв по банкам в пределах 1.4 млн ₽ (лимит АСВ)")

        service1 = st.debt_service()
        outflow1 = st.outflow()
        fcf1 = st.fcf()
        pdn1 = service1 / income if income > 0 else None
        cushion1 = reserve / outflow1 if outflow1 > 0 else None

        debt_plan = self._build_debt_plan(st, branch, pdn0, fl_debt, grey_flow, fcf1)
        lump_plan = self._build_lump_plan(st, reserve, from_stock, goals, invest_stock)
        monthly_plan = self._build_monthly_plan(
            fl_reserve_total, fl_debt, fl_goals, grey_flow, invest_flow, goal_rows, risk
        )
        status = self._status(branch, reserve, outflow1, st, goal_rows, invest_stock, invest_flow)
        verdict = self._verdict(status, branch, st, reserve, outflow1, cushion1,
                                goal_rows, invest_flow, invest_stock, risk, fcf1)

        diagnostics = {
            "fcf": round(fcf0, 2),
            "pdn": round(pdn0, 4) if pdn0 is not None else None,
            "debt_service": round(service0, 2),
            "full_outflow": round(outflow0, 2),
            "cushion_months": round(cushion0, 2) if cushion0 is not None else None,
            "floor_reserve": round(FLOOR_MONTHS * outflow0, 2),
            "target_reserve": round(TARGET_MONTHS * outflow0, 2),
            "deployable_surplus": round(deployable0, 2),
            "post": {
                "fcf": round(fcf1, 2),
                "pdn": round(pdn1, 4) if pdn1 is not None else None,
                "full_outflow": round(outflow1, 2),
                "reserve_months": round(cushion1, 2) if cushion1 is not None else None,
            },
        }
        return {
            "id": profile["id"],
            "kind": profile["kind"],
            "status": status,
            "branch": branch,
            "flags": flags,
            "diagnostics": diagnostics,
            "debt_plan": debt_plan,
            "lump_sum_plan": lump_plan,
            "monthly_plan": monthly_plan,
            "goal_plan": goal_rows,
            "actions": actions,
            "verdict": verdict,
        }

    def _crisis_repair(self, st: _State, bliq: float, actions: list[str]) -> float:
        while st.fcf() < -EPS and bliq > EPS:
            deficit = -st.fcf()
            runway = bliq / deficit
            pick = None
            for o in sorted(st.open_debts(), key=lambda d: (-d.interest_rate, d.id)):
                bal = st.balances[o.id]
                if bal > bliq:
                    continue
                new_outflow = st.outflow() - o.monthly_payment
                if bliq - bal < CRISIS_MIN_FLOOR_MONTHS * new_outflow:
                    continue
                if o.monthly_payment <= 0 or bal / o.monthly_payment >= runway:
                    continue
                if o.interest_rate < st.r_bench and runway >= CHEAP_CLOSE_RUNWAY:
                    continue
                pick = o
                break
            if pick is None:
                break
            bal = st.balances[pick.id]
            st.prepaid[pick.id] += bal
            st.balances[pick.id] = 0.0
            bliq -= bal
            actions.append(
                f"Закрыть {pick.name} ({pick.interest_rate:.0%}) из ликвидности: {round(bal)} ₽ — "
                f"освобождает {round(pick.monthly_payment)} ₽/мес"
            )
        return bliq

    def _finalize_crisis(self, st: _State, bliq: float, goals: list[Goal], risk: int,
                         actions: list[str]):
        deficit = -st.fcf()
        runway = bliq / deficit if deficit > 0 else None
        if st.income <= EPS:
            note = f"; резерва хватит на ~{runway:.1f} мес" if runway else ""
            actions.insert(0, "Приоритет — восстановление дохода" + note)
        if st.expenses > EPS:
            actions.append(f"Сократить расходы минимум на {round(deficit)} ₽/мес — выход в ноль")
        if st.open_debts():
            actions.append("Запросить реструктуризацию/кредитные каникулы по оставшимся кредитам")
        if any(not g.funded for g in goals):
            actions.append("Взносы на цели заморозить до восстановления положительного потока")

        i_g = monthly_rate(st.r_bench)
        goal_rows = []
        for g in sorted(goals, key=lambda x: x.id):
            n = g.months_left(TODAY)
            delay = None
            if not g.funded and n is not None:
                reach = months_to_reach(g.current_amount, 0.0, g.target_amount, i_g)
                delay = max(1, math.ceil(reach - n)) if reach is not None else None
            goal_rows.append(self._goal_row(
                g, n, cur=g.current_amount, req=None, alloc=0.0, lump=0.0,
                status="funded" if g.funded else "frozen", delay=delay,
                instrument="исполнить цель" if g.funded else "накопительный счёт",
            ))
            if g.funded and g.current_amount - g.target_amount > EPS:
                actions.append(
                    f"Цель '{g.name}' профинансирована, излишек "
                    f"{round(g.current_amount - g.target_amount)} ₽ — высвободить в резерв"
                )
        return (bliq, 0.0, {g.id: 0.0 for g in goals}, goal_rows,
                0.0, [], [], 0.0, None)

    def _normal_cascade(self, st: _State, bliq: float, goals: list[Goal], risk: int,
                        actions: list[str], flags: list[str]):
        outflow = st.outflow()
        floor = FLOOR_MONTHS * outflow
        target = TARGET_MONTHS * outflow

        reserve = min(bliq, floor)
        surplus = bliq - reserve
        if reserve < floor - EPS:
            flags.append("reserve_below_floor")

        while surplus > EPS:
            expensive = sorted(
                (o for o in st.open_debts() if band(o.interest_rate, st.r_bench) == "expensive"),
                key=lambda d: (-d.interest_rate, d.id),
            )
            if not expensive:
                break
            o = expensive[0]
            pay = min(surplus, st.balances[o.id])
            st.balances[o.id] -= pay
            st.prepaid[o.id] += pay
            surplus -= pay
            if st.balances[o.id] <= EPS:
                actions.append(
                    f"Закрыть {o.name} ({o.interest_rate:.0%}) досрочно: {round(pay)} ₽ — "
                    f"освобождает {round(o.monthly_payment)} ₽/мес"
                )
                outflow = st.outflow()
                floor = FLOOR_MONTHS * outflow
                target = TARGET_MONTHS * outflow
                if reserve > floor:
                    surplus += reserve - floor
                    reserve = floor
            else:
                actions.append(
                    f"Досрочно внести {round(pay)} ₽ в {o.name} ({o.interest_rate:.0%}), "
                    f"сокращая срок, а не платёж"
                )

        topup = min(surplus, max(target - reserve, 0.0))
        reserve += topup
        surplus -= topup

        i_g = monthly_rate(st.r_bench)
        current = {g.id: g.current_amount for g in goals}
        from_stock = {g.id: 0.0 for g in goals}
        dated = sorted((g for g in goals if g.deadline and not g.funded),
                       key=lambda g: (g.deadline, g.id))
        undated = sorted((g for g in goals if g.deadline is None and not g.funded),
                         key=lambda g: (g.gap, g.id))
        if not any(band(o.interest_rate, st.r_bench) == "expensive" for o in st.open_debts()):
            for g in dated + undated:
                if surplus <= EPS:
                    break
                add = min(surplus, g.target_amount - current[g.id])
                if add <= EPS:
                    continue
                from_stock[g.id] = add
                current[g.id] += add
                surplus -= add

        grey_paid_stock = self._grey_split_stock(st, surplus, actions)
        surplus -= grey_paid_stock
        outflow = st.outflow()
        target = TARGET_MONTHS * outflow
        if reserve > target + EPS and outflow > EPS:
            surplus += reserve - target
            reserve = target
        invest_stock = surplus

        flow_left = max(st.fcf(), 0.0)
        fl_reserve = 0.0
        fl_debt: list[dict] = []
        floor = FLOOR_MONTHS * outflow
        if reserve < floor - EPS and flow_left > EPS:
            fl_reserve = flow_left
            months = (floor - reserve) / flow_left
            actions.append(
                f"Весь свободный поток в резерв до пола {round(floor)} ₽ (~{months:.0f} мес)"
            )
            flow_left = 0.0

        expensive_open = sorted(
            (o for o in st.open_debts() if band(o.interest_rate, st.r_bench) == "expensive"),
            key=lambda d: (-d.interest_rate, d.id),
        )
        if expensive_open and flow_left > EPS:
            o = expensive_open[0]
            fl_debt.append({"id": o.id, "name": o.name, "monthly": round(flow_left, 2)})
            months = st.balances[o.id] / flow_left
            actions.append(
                f"Досрочные платежи {round(flow_left)} ₽/мес в {o.name} ({o.interest_rate:.0%}) "
                f"— закрытие за ~{months:.0f} мес"
            )
            flow_left = 0.0
        elif expensive_open:
            actions.append(
                f"Рефинансировать {expensive_open[0].name} "
                f"({expensive_open[0].interest_rate:.0%}): свободного потока на досрочку нет"
            )

        fl_goals: list[dict] = []
        allocated_monthly = {g.id: 0.0 for g in goals}
        can_fund = reserve >= floor - EPS and not expensive_open
        for g in dated:
            n = max(g.months_left(TODAY), 1)
            req = required_monthly(current[g.id], g.target_amount, n, i_g)
            if can_fund and flow_left > EPS and req > EPS:
                give = min(flow_left, req)
                allocated_monthly[g.id] = give
                flow_left -= give
                fl_goals.append({"id": g.id, "name": g.name, "monthly": round(give, 2)})

        topup2 = 0.0
        if reserve < target - EPS and flow_left > EPS:
            topup2 = flow_left
            flow_left = 0.0

        grey_flow = self._grey_split_flow(st, flow_left, actions)
        if grey_flow:
            flow_left -= grey_flow["monthly"]
        invest_flow = flow_left

        goal_rows = []
        for g in sorted(goals, key=lambda x: x.id):
            n = g.months_left(TODAY)
            cur = current[g.id]
            funded_now = cur >= g.target_amount - EPS
            if funded_now:
                status, req, delay = "funded", 0.0, 0
                instr = "исполнить цель / держать в защитных инструментах до траты"
            elif n is None:
                status, req, delay = "no_deadline", None, None
                instr = RISK_MIX[risk]
            else:
                req = required_monthly(cur, g.target_amount, max(n, 1), i_g)
                alloc = allocated_monthly[g.id]
                if alloc >= req - EPS:
                    status, delay = "on_track", 0
                else:
                    status = "underfunded"
                    reach = months_to_reach(cur, alloc, g.target_amount, i_g)
                    delay = max(1, math.ceil(reach - n)) if reach is not None else None
                    actions.append(
                        f"Цель '{g.name}' к {g.deadline.isoformat()} недофинансирована: нужно "
                        f"{round(req)} ₽/мес, выделено {round(alloc)} — сдвиг "
                        f"~{delay if delay is not None else '∞'} мес"
                    )
                instr = ("накопительный счёт" if n < 12
                         else "депозит/ОФЗ с погашением к сроку" if n <= 36
                         else RISK_MIX[risk])
            if g.funded and g.current_amount - g.target_amount > EPS:
                actions.append(
                    f"Цель '{g.name}' профинансирована, излишек "
                    f"{round(g.current_amount - g.target_amount)} ₽ — высвободить"
                )
            goal_rows.append(self._goal_row(
                g, n, cur=cur, req=req, alloc=allocated_monthly[g.id],
                lump=from_stock[g.id], status=status, delay=delay, instrument=instr,
            ))

        if reserve >= target - EPS and outflow > EPS:
            actions.append(f"Резерв укомплектован: {round(reserve)} ₽ (6 мес оттока)")
        elif topup2 > EPS:
            months = (target - reserve) / topup2
            actions.append(
                f"Доводить резерв до {round(target)} ₽: +{round(topup2)} ₽/мес (~{months:.0f} мес)"
            )

        return (reserve, invest_stock, from_stock, goal_rows,
                fl_reserve + topup2, fl_debt, fl_goals, invest_flow, grey_flow)

    def _grey_split_stock(self, st: _State, residual: float, actions: list[str]) -> float:
        if residual <= EPS:
            return 0.0
        grey = sorted(
            (o for o in st.open_debts() if band(o.interest_rate, st.r_bench) == "grey"),
            key=lambda d: (-d.interest_rate, d.id),
        )
        if not grey:
            return 0.0
        budget = residual * 0.5
        paid = 0.0
        for o in grey:
            if budget <= EPS:
                break
            pay = min(budget, st.balances[o.id])
            st.balances[o.id] -= pay
            st.prepaid[o.id] += pay
            paid += pay
            budget -= pay
            actions.append(
                f"Пограничная ставка {o.name} ({o.interest_rate:.0%}): досрочно {round(pay)} ₽ "
                f"(50/50 с инвестициями)"
            )
        return paid

    def _grey_split_flow(self, st: _State, residual: float, actions: list[str]) -> dict | None:
        if residual <= EPS:
            return None
        grey = sorted(
            (o for o in st.open_debts() if band(o.interest_rate, st.r_bench) == "grey"),
            key=lambda d: (-d.interest_rate, d.id),
        )
        if not grey:
            return None
        o = grey[0]
        pay = min(residual * 0.5, st.balances[o.id])
        if pay <= EPS:
            return None
        actions.append(
            f"Пограничная ставка {o.name} ({o.interest_rate:.0%}): 50% остатка потока "
            f"({round(pay)} ₽/мес) на досрочку, 50% — в инвестиции"
        )
        return {"id": o.id, "name": o.name, "monthly": round(pay, 2)}

    def _goal_row(self, g: Goal, n: int | None, cur: float, req: float | None,
                  alloc: float, lump: float, status: str, delay: int | None,
                  instrument: str) -> dict:
        achievable = None
        if status in ("funded", "on_track"):
            achievable = True
        elif status in ("underfunded", "frozen"):
            achievable = False
        return {
            "id": g.id,
            "name": g.name,
            "deadline": g.deadline.isoformat() if g.deadline else None,
            "months_left": n,
            "target": round(g.target_amount, 2),
            "current_start": round(g.current_amount, 2),
            "lump_allocation": round(lump, 2),
            "required_monthly": round(req, 2) if req is not None else None,
            "allocated_monthly": round(alloc, 2),
            "achievable": achievable,
            "expected_delay_months": delay,
            "status": status,
            "instrument": instrument,
        }

    def _build_debt_plan(self, st: _State, branch: str, pdn0: float | None,
                         fl_debt: list[dict], grey_flow: dict | None, fcf1: float) -> list[dict]:
        monthly_extra = {d["id"]: d["monthly"] for d in fl_debt}
        if grey_flow:
            monthly_extra[grey_flow["id"]] = monthly_extra.get(grey_flow["id"], 0.0) + grey_flow["monthly"]
        plan = []
        for o in sorted(st.debts, key=lambda d: d.id):
            bal = st.balances[o.id]
            pre = st.prepaid[o.id]
            closed = bal <= EPS
            extra = monthly_extra.get(o.id, 0.0)
            if closed:
                action = "close_from_lump"
            elif pre > EPS:
                action = "prepay_lump"
            elif extra > EPS:
                action = "prepay_monthly"
            elif branch == "crisis":
                action = "restructure"
            elif o.non_amortizing:
                action = "restructure"
            elif band(o.interest_rate, st.r_bench) == "expensive":
                action = "refinance"
            elif pdn0 is not None and pdn0 > 0.5:
                action = "refinance"
            else:
                action = "keep_schedule"
            note = ""
            if o.non_amortizing and not closed:
                note = "платёж не покрывает проценты — долг не амортизируется"
            elif band(o.interest_rate, st.r_bench) == "cheap" and not closed:
                note = "ставка ниже бенчмарка — досрочное погашение невыгодно"
            plan.append({
                "id": o.id,
                "name": o.name,
                "rate": o.interest_rate,
                "vs_bench": band(o.interest_rate, st.r_bench),
                "balance_start": round(o.amount, 2),
                "monthly_payment": round(o.monthly_payment, 2),
                "action": action,
                "lump_amount": round(pre, 2),
                "extra_monthly": round(extra, 2),
                "closes": closed,
                "note": note,
            })
        return plan

    def _build_lump_plan(self, st: _State, reserve: float, from_stock: dict,
                         goals: list[Goal], invest_stock: float) -> list[dict]:
        plan = [{"bucket": "reserve", "target": None, "amount": round(reserve, 2),
                 "instrument": RESERVE_INSTRUMENT}]
        for o in sorted(st.debts, key=lambda d: d.id):
            if st.prepaid[o.id] > EPS:
                bucket = "debt_close" if st.balances[o.id] <= EPS else "debt_prepay"
                plan.append({"bucket": bucket, "target": o.name,
                             "amount": round(st.prepaid[o.id], 2), "instrument": None})
        for g in sorted(goals, key=lambda x: x.id):
            if from_stock.get(g.id, 0.0) > EPS:
                plan.append({"bucket": "goal", "target": g.name,
                             "amount": round(from_stock[g.id], 2), "instrument": None})
        if invest_stock > EPS:
            plan.append({"bucket": "invest", "target": None,
                         "amount": round(invest_stock, 2), "instrument": None})
        return plan

    def _build_monthly_plan(self, fl_reserve: float, fl_debt: list[dict],
                            fl_goals: list[dict], grey_flow: dict | None,
                            invest_flow: float, goal_rows: list[dict], risk: int) -> list[dict]:
        instr_by_goal = {r["id"]: r["instrument"] for r in goal_rows}
        plan = []
        if fl_reserve > EPS:
            plan.append({"bucket": "reserve_topup", "target": None,
                         "amount": round(fl_reserve, 2), "instrument": RESERVE_INSTRUMENT})
        for d in fl_debt:
            plan.append({"bucket": "debt_extra", "target": d["name"],
                         "amount": d["monthly"], "instrument": None})
        for gl in fl_goals:
            plan.append({"bucket": "goal", "target": gl["name"], "amount": gl["monthly"],
                         "instrument": instr_by_goal.get(gl["id"])})
        if grey_flow:
            plan.append({"bucket": "debt_extra", "target": grey_flow["name"],
                         "amount": grey_flow["monthly"], "instrument": None})
        if invest_flow > EPS:
            plan.append({"bucket": "invest", "target": None,
                         "amount": round(invest_flow, 2), "instrument": RISK_MIX[risk]})
        return plan

    def _status(self, branch: str, reserve: float, outflow: float, st: _State,
                goal_rows: list[dict], invest_stock: float, invest_flow: float) -> str:
        if branch == "crisis":
            return "crisis"
        floor = FLOOR_MONTHS * outflow
        target = TARGET_MONTHS * outflow
        expensive_open = any(
            band(o.interest_rate, st.r_bench) == "expensive" for o in st.open_debts()
        )
        if (outflow > EPS and reserve < floor - EPS) or expensive_open:
            return "vulnerable"
        if any(r["status"] == "underfunded" for r in goal_rows):
            return "stretched"
        if outflow > EPS and reserve < target - EPS:
            return "on_plan"
        if invest_flow > EPS or invest_stock > EPS:
            return "surplus"
        return "on_plan"

    def _verdict(self, status: str, branch: str, st: _State, reserve: float,
                 outflow: float, cushion1: float | None, goal_rows: list[dict],
                 invest_flow: float, invest_stock: float, risk: int, fcf1: float) -> str:
        if status == "crisis":
            deficit = -st.fcf()
            runway = f"{reserve / deficit:.0f}" if deficit > 0 else "∞"
            return (f"Дефицит {round(deficit)} ₽/мес, резерва на ~{runway} мес: "
                    f"реструктуризация, сокращение расходов, цели заморожены.")
        repaired = "закрытие кредитов из ликвидности восстановило поток; " \
            if branch == "crisis_repaired" else ""
        if status == "vulnerable":
            exp = [o for o in st.open_debts()
                   if band(o.interest_rate, st.r_bench) == "expensive"]
            if exp:
                o = max(exp, key=lambda d: d.interest_rate)
                return (f"{repaired}Поток положительный, но дорогой {o.name} "
                        f"({o.interest_rate:.0%}) в приоритете — лавина, цели ждут.")
            return (f"{repaired}Поток {round(fcf1)} ₽/мес целиком строит резерв "
                    f"до пола {round(FLOOR_MONTHS * outflow)} ₽; цели после.")
        at_risk = sum(1 for r in goal_rows if r["status"] == "underfunded")
        if status == "stretched":
            total = sum(1 for r in goal_rows if r["deadline"])
            return (f"{repaired}База устойчива, но {at_risk} из {total} целей с дедлайнами "
                    f"не успевают — сдвигать срок или наращивать взнос.")
        if status == "surplus":
            return (f"{repaired}Профицит: резерв укомплектован, "
                    f"{round(invest_flow)} ₽/мес в инвестиции ({RISK_MIX[risk]}).")
        cush = f"{cushion1:.1f}" if cushion1 is not None else "∞"
        return (f"{repaired}Устойчив: резерв {cush} мес, цели финансируются по графику, "
                f"долги под контролем.")


def main() -> None:
    uploads = Path("/mnt/user-data/uploads")
    out = Path("/home/claude/out2")
    out.mkdir(exist_ok=True)
    engine = ExpertEngine()
    with open(uploads / "portraits_12000.jsonl") as src, \
            open(out / "recommendations.jsonl", "w", encoding="utf-8") as dst:
        for line in src:
            rec = engine.advise(json.loads(line))
            dst.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("done")


if __name__ == "__main__":
    main()
