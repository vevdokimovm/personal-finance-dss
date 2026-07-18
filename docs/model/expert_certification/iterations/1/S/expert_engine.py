"""Independent expert engine: standard personal-finance waterfall.

Produces per-profile allocation of liquid stock (B_liq) and monthly cash flow
across reserve / debt prepayment / goals / investments, plus diagnostics,
feasibility of goals and short action items. Thresholds are anchored in
standard financial-planning practice, not in any client-side methodology.
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


class ExpertEngine:
    """Waterfall: triage -> reserve floor -> expensive debt -> reserve target ->
    goals -> grey-zone debt / investments. Crisis branch repairs cash flow by
    fully closing debts when survival math allows it."""

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
            bliq = self._crisis_repair(st, bliq, actions)
            branch = "crisis_repaired" if st.fcf() >= -EPS else "crisis"

        if branch == "crisis":
            result = self._finalize_crisis(st, bliq, goals, risk, actions, flags)
        else:
            result = self._normal_cascade(st, bliq, goals, risk, actions, flags)

        stock, flow, goal_status, instruments = result

        if branch != "crisis" and pdn0 is not None and pdn0 > 0.5 and st.open_debts():
            actions.append(
                f"Рефинансировать оставшиеся кредиты: ПДН {pdn0:.0%} — красная зона, "
                f"снизить платёж/ставку"
            )
        for o in non_amort:
            if st.balances[o.id] > EPS:
                actions.append(
                    f"Реструктурировать {o.name}: платёж {round(o.monthly_payment)} ₽ не покрывает "
                    f"проценты ({round(o.interest_only)} ₽/мес) — долг не амортизируется"
                )
        if bliq > ASV_LIMIT:
            actions.append("Разложить ликвидность по банкам в пределах 1.4 млн ₽ на банк (лимит АСВ)")

        service1 = st.debt_service()
        outflow1 = st.outflow()
        fcf1 = st.fcf()
        pdn1 = service1 / income if income > 0 else None
        reserve_after = stock["reserve"]
        cushion1 = reserve_after / outflow1 if outflow1 > 0 else None

        return {
            "id": profile["id"],
            "kind": profile["kind"],
            "branch": branch,
            "diagnosis": {
                "fcf": round(fcf0, 2),
                "pdn": round(pdn0, 4) if pdn0 is not None else None,
                "debt_service": round(service0, 2),
                "full_outflow": round(outflow0, 2),
                "cushion_months": round(cushion0, 2) if cushion0 is not None else None,
                "flags": flags,
            },
            "post_allocation": {
                "fcf": round(fcf1, 2),
                "pdn": round(pdn1, 4) if pdn1 is not None else None,
                "full_outflow": round(outflow1, 2),
                "reserve_months": round(cushion1, 2) if cushion1 is not None else None,
            },
            "stock_allocation": stock,
            "flow_allocation": flow,
            "goal_status": goal_status,
            "actions": actions,
            "instruments": instruments,
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
                if bal / o.monthly_payment >= runway:
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
                         actions: list[str], flags: list[str]):
        deficit = -st.fcf()
        runway = bliq / deficit if deficit > 0 else None
        if st.income <= EPS:
            note = f"; резерва хватит на ~{runway:.1f} мес текущего оттока" if runway else ""
            actions.insert(0, "Приоритет — восстановление дохода" + note)
        if st.expenses > EPS:
            actions.append(f"Сократить расходы минимум на {round(deficit)} ₽/мес — выход в ноль")
        if st.open_debts():
            actions.append("Запросить реструктуризацию/кредитные каникулы по оставшимся кредитам")
        if any(not g.funded for g in goals):
            actions.append("Взносы на цели заморозить до восстановления положительного потока")

        i_g = monthly_rate(st.r_bench)
        goal_status = []
        for g in sorted(goals, key=lambda x: x.id):
            n = g.months_left(TODAY)
            status = "funded" if g.funded else "frozen"
            delay = None
            if not g.funded and n is not None:
                reach = months_to_reach(g.current_amount, 0.0, g.target_amount, i_g)
                delay = math.ceil(reach - n) if reach is not None else None
            goal_status.append({
                "id": g.id, "name": g.name,
                "deadline": g.deadline.isoformat() if g.deadline else None,
                "months_left": n,
                "target": round(g.target_amount, 2),
                "current": round(g.current_amount, 2),
                "required_monthly": None,
                "allocated_monthly": 0.0,
                "from_stock": 0.0,
                "status": status,
                "delay_months": delay,
                "instrument": "накопительный счёт" if not g.funded else "исполнить цель",
            })
            if g.funded and g.current_amount - g.target_amount > EPS:
                actions.append(
                    f"Цель '{g.name}' профинансирована, излишек {round(g.current_amount - g.target_amount)} ₽ "
                    f"— высвободить в резерв"
                )

        stock = {
            "reserve": round(bliq, 2),
            "debt_prepay": self._prepay_records(st),
            "goals": [],
            "invest": 0.0,
        }
        flow = {"reserve_topup": 0.0, "debt_extra": [], "goals": [], "invest": 0.0}
        instruments = {
            "reserve": "накопительный счёт / депозит до 3 мес с пополнением и снятием",
            "invest": "не применимо до восстановления потока",
        }
        return stock, flow, goal_status, instruments

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
                (o for o in st.open_debts() if o.interest_rate > st.r_bench + EXPENSIVE_SPREAD),
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
        no_expensive = not any(
            o.interest_rate > st.r_bench + EXPENSIVE_SPREAD for o in st.open_debts()
        )
        if no_expensive:
            for g in dated + undated:
                if surplus <= EPS:
                    break
                add = min(surplus, g.target_amount - current[g.id])
                if add <= EPS:
                    continue
                from_stock[g.id] = add
                current[g.id] += add
                surplus -= add

        grey_paid_stock = self._grey_split(st, surplus, actions)
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
        if reserve < floor - EPS and flow_left > EPS:
            fl_reserve = flow_left
            months = (floor - reserve) / flow_left
            actions.append(
                f"Весь свободный поток в резерв до пола {round(floor)} ₽ (~{months:.0f} мес)"
            )
            flow_left = 0.0

        expensive_open = sorted(
            (o for o in st.open_debts() if o.interest_rate > st.r_bench + EXPENSIVE_SPREAD),
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
                f"Рефинансировать {expensive_open[0].name} ({expensive_open[0].interest_rate:.0%}): "
                f"ставка выше бенчмарка, свободного потока на досрочку нет"
            )

        fl_goals: list[dict] = []
        goal_status = []
        allocated_monthly = {g.id: 0.0 for g in goals}
        can_fund_goals = reserve >= floor - EPS and not expensive_open
        for g in dated:
            n = max(g.months_left(TODAY), 1)
            req = required_monthly(current[g.id], g.target_amount, n, i_g)
            if can_fund_goals and flow_left > EPS and req > EPS:
                give = min(flow_left, req)
                allocated_monthly[g.id] = give
                flow_left -= give
                fl_goals.append({"id": g.id, "monthly": round(give, 2)})

        topup2 = 0.0
        if reserve < target - EPS and flow_left > EPS:
            topup2 = flow_left
            flow_left = 0.0

        grey_paid_flow = self._grey_split(st, flow_left, actions, is_flow=True)
        flow_left -= grey_paid_flow
        invest_flow = flow_left

        for g in sorted(goals, key=lambda x: x.id):
            n = g.months_left(TODAY)
            cur = current[g.id]
            funded_now = cur >= g.target_amount - EPS
            if funded_now:
                status = "funded"
                req = 0.0
                delay = 0
            elif n is None:
                status = "no_deadline"
                req = None
                delay = None
            else:
                req = required_monthly(cur, g.target_amount, max(n, 1), i_g)
                alloc = allocated_monthly[g.id]
                if alloc >= req - EPS:
                    status = "on_track"
                    delay = 0
                else:
                    status = "underfunded"
                    reach = months_to_reach(cur, alloc, g.target_amount, i_g)
                    delay = max(1, math.ceil(reach - n)) if reach is not None else None
                    actions.append(
                        f"Цель '{g.name}' к {g.deadline.isoformat()} недофинансирована: нужно "
                        f"{round(req)} ₽/мес, выделено {round(alloc)} — сдвиг ~{delay if delay is not None else '∞'} мес"
                    )
            if g.funded and g.current_amount - g.target_amount > EPS:
                actions.append(
                    f"Цель '{g.name}' профинансирована, излишек "
                    f"{round(g.current_amount - g.target_amount)} ₽ — высвободить"
                )
            if n is not None and not funded_now:
                instr = ("накопительный счёт" if n < 12
                         else "депозит/ОФЗ с погашением к сроку" if n <= 36
                         else RISK_MIX[risk])
            elif funded_now:
                instr = "исполнить цель / держать в защитных инструментах до траты"
            else:
                instr = RISK_MIX[risk]
            goal_status.append({
                "id": g.id, "name": g.name,
                "deadline": g.deadline.isoformat() if g.deadline else None,
                "months_left": n,
                "target": round(g.target_amount, 2),
                "current": round(cur, 2),
                "required_monthly": round(req, 2) if req is not None else None,
                "allocated_monthly": round(allocated_monthly[g.id], 2),
                "from_stock": round(from_stock[g.id], 2),
                "status": status,
                "delay_months": delay,
                "instrument": instr,
            })

        if reserve >= target - EPS and outflow > EPS:
            actions.append(f"Резерв укомплектован: {round(reserve)} ₽ (6 мес оттока)")
        elif topup2 > EPS:
            months = (target - reserve) / topup2
            actions.append(
                f"Доводить резерв до {round(target)} ₽: +{round(topup2)} ₽/мес (~{months:.0f} мес)"
            )

        stock = {
            "reserve": round(reserve, 2),
            "debt_prepay": self._prepay_records(st),
            "goals": [{"id": g.id, "amount": round(from_stock[g.id], 2)}
                      for g in goals if from_stock[g.id] > EPS],
            "invest": round(invest_stock, 2),
        }
        flow = {
            "reserve_topup": round(fl_reserve + topup2, 2),
            "debt_extra": fl_debt + (
                [{"id": -1, "name": "grey_zone_debts", "monthly": round(grey_paid_flow, 2)}]
                if grey_paid_flow > EPS else []
            ),
            "goals": fl_goals,
            "invest": round(invest_flow, 2),
        }
        instruments = {
            "reserve": "накопительный счёт / депозит до 3 мес с пополнением и снятием",
            "invest": RISK_MIX[risk],
        }
        return stock, flow, goal_status, instruments

    def _grey_split(self, st: _State, residual: float, actions: list[str],
                    is_flow: bool = False) -> float:
        if residual <= EPS:
            return 0.0
        grey = sorted(
            (o for o in st.open_debts()
             if st.r_bench <= o.interest_rate <= st.r_bench + EXPENSIVE_SPREAD),
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
            if is_flow:
                paid += pay
                budget -= pay
                actions.append(
                    f"Пограничная ставка {o.name} ({o.interest_rate:.0%}): 50% остатка потока "
                    f"({round(pay)} ₽/мес) на досрочку, 50% — в инвестиции"
                )
                break
            st.balances[o.id] -= pay
            st.prepaid[o.id] += pay
            paid += pay
            budget -= pay
            actions.append(
                f"Пограничная ставка {o.name} ({o.interest_rate:.0%}): досрочно {round(pay)} ₽ "
                f"(50/50 с инвестициями)"
            )
        return paid

    def _prepay_records(self, st: _State) -> list[dict]:
        recs = []
        for o in st.debts:
            if st.prepaid[o.id] > EPS:
                recs.append({
                    "id": o.id,
                    "name": o.name,
                    "amount": round(st.prepaid[o.id], 2),
                    "closes": st.balances[o.id] <= EPS,
                })
        return recs


def main() -> None:
    uploads = Path("/mnt/user-data/uploads")
    out = Path("/home/claude/out")
    out.mkdir(exist_ok=True)
    engine = ExpertEngine()
    results = []
    with open(uploads / "portraits_12000.jsonl") as f:
        for line in f:
            results.append(engine.advise(json.loads(line)))
    with open(out / "recommendations_12000.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"done: {len(results)} recommendations")


if __name__ == "__main__":
    main()
