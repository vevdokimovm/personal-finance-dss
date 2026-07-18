from __future__ import annotations

import json
import math
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

TODAY = date(2026, 7, 5)
TOXIC_SPREAD = 0.05
DSTI_ELEVATED = 0.30
DSTI_HIGH = 0.50
DSTI_CRITICAL = 0.80
STARTER_MONTHS = 1.0
SAFE_RUNWAY_AFTER_PAYOFF = 6.0
DEFICIT_FIX_KEEP_MONTHS = 3.0
CUSHION_MONTHS = {1: 6.0, 2: 5.25, 3: 4.5, 4: 3.75, 5: 3.0}
INVEST_SPLIT = {
    1: {"deposits": 0.70, "bonds": 0.30, "equity": 0.00, "alt": 0.00},
    2: {"deposits": 0.50, "bonds": 0.40, "equity": 0.10, "alt": 0.00},
    3: {"deposits": 0.30, "bonds": 0.40, "equity": 0.30, "alt": 0.00},
    4: {"deposits": 0.15, "bonds": 0.35, "equity": 0.45, "alt": 0.05},
    5: {"deposits": 0.10, "bonds": 0.20, "equity": 0.60, "alt": 0.10},
}


def fmt(x: float) -> str:
    return f"{x:,.0f}".replace(",", "\u202f") + "\u202f₽"


def months_between(start: date, end: date) -> int:
    return max(1, round((end - start).days / 30.4375))


@dataclass
class Debt:
    id: int
    name: str
    balance: float
    rate: float
    payment: float


@dataclass
class Goal:
    id: int
    name: str
    target: float
    current: float
    deadline: date | None

    @property
    def gap(self) -> float:
        return max(0.0, self.target - self.current)

    @property
    def achieved(self) -> bool:
        return self.current >= self.target

    @property
    def months_left(self) -> int | None:
        if self.deadline is None:
            return None
        return months_between(TODAY, self.deadline)

    @property
    def required_monthly(self) -> float | None:
        ml = self.months_left
        if ml is None:
            return None
        return self.gap / ml


@dataclass
class Portrait:
    id: str
    kind: str
    income: float
    expenses: float
    bliq: float
    r_bench: float
    risk: int
    l_min: float
    debts: list[Debt]
    goals: list[Goal]

    @classmethod
    def from_record(cls, rec: dict) -> "Portrait":
        e = rec["engine"]
        debts = [
            Debt(o["id"], o["name"], o["amount"], o["interest_rate"], o["monthly_payment"])
            for o in e["obligations"]
        ]
        goals = [
            Goal(
                g["id"],
                g["name"],
                g["target_amount"],
                g["current_amount"],
                date.fromisoformat(g["deadline"]) if g["deadline"] else None,
            )
            for g in e["goals"]
        ]
        return cls(
            id=rec["id"],
            kind=rec["kind"],
            income=e["income_total"],
            expenses=e["expense_total"],
            bliq=e["bliq"],
            r_bench=e["r_bench"],
            risk=e["risk_tolerance"],
            l_min=e["l_min"],
            debts=debts,
            goals=goals,
        )


class ExpertAdvisor:
    """Independent expert allocation engine: crisis triage -> lump
    deployment of excess liquidity -> monthly cash-flow waterfall."""

    def analyze(self, p: Portrait) -> dict:
        flags: list[str] = []
        debts = deepcopy(p.debts)
        goals = deepcopy(p.goals)
        bliq = p.bliq

        m_total = sum(d.payment for d in debts)
        fcf = p.income - p.expenses - m_total
        dsti = (m_total / p.income) if p.income > 0 else None
        burn = p.expenses + m_total

        if p.expenses == 0:
            flags.append("DATA_ANOMALY_ZERO_EXPENSES")
        for g in goals:
            if g.achieved:
                flags.append(f"GOAL_ACHIEVED:{g.name}")
        cheap = [d for d in debts if d.rate <= p.r_bench]
        if cheap:
            flags.append("CHEAP_DEBT_KEEP:" + ",".join(d.name for d in cheap))

        if p.income == 0:
            result = self._crisis_no_income(p, debts, goals, bliq, burn, flags)
        elif fcf < 0:
            result = self._crisis_deficit(p, debts, goals, bliq, fcf, dsti, burn, flags)
        else:
            result = self._regular(p, debts, goals, bliq, dsti, flags)

        result["id"] = p.id
        result["kind"] = p.kind
        return result

    # ------------------------------------------------------------------ crisis

    def _crisis_no_income(self, p, debts, goals, bliq, burn, flags):
        flags.append("NO_INCOME")
        payoffs = self._survival_payoffs(debts, bliq, burn, income=0.0)
        for d, _ in payoffs:
            bliq -= d.balance
            debts.remove(d)
        burn = p.expenses + sum(d.payment for d in debts)
        runway = bliq / burn if burn > 0 else None
        if runway is not None and runway < 3:
            flags.append("RUNWAY_CRITICAL")
        if goals and any(not g.achieved for g in goals):
            flags.append("GOALS_FROZEN")
        advice = self._verdict_no_income(p, debts, payoffs, bliq, burn, runway)
        return self._pack(
            status="crisis_no_income",
            metrics=self._metrics(p, debts, bliq, fcf=-burn, dsti=None, burn=burn, runway=runway,
                                  cushion_target=None),
            lump={"debt_payoff": [self._payoff_row(d, r) for d, r in payoffs],
                  "goal_topups": [], "invest": 0.0},
            monthly={"to_cushion": 0.0, "debt_prepay": [], "goal_contributions": [],
                     "invest_total": 0.0, "invest_split": {}},
            goals=self._goal_rows(goals, funded={}),
            flags=flags,
            advice=advice,
        )

    def _crisis_deficit(self, p, debts, goals, bliq, fcf, dsti, burn, flags):
        flags.append("DEFICIT_CASHFLOW")
        payoffs = self._survival_payoffs(debts, bliq, burn, income=p.income)
        for d, _ in payoffs:
            bliq -= d.balance
            debts.remove(d)
        m_total = sum(d.payment for d in debts)
        fcf = p.income - p.expenses - m_total
        burn = p.expenses + m_total
        dsti = m_total / p.income if p.income > 0 else None
        fixed = fcf >= 0
        if fixed:
            flags.append("CASHFLOW_FIXED_BY_PAYOFF")
            res = self._regular(p, debts, goals, bliq, dsti, flags)
            payoff_rows = [self._payoff_row(d, r) for d, r in payoffs]
            res["lump_plan"]["debt_payoff"] = payoff_rows + res["lump_plan"]["debt_payoff"]
            total = sum(r["amount"] for r in payoff_rows)
            names = ", ".join(d.name for d, _ in payoffs)
            prefix = (f"Исходный поток отрицательный: платежи по кредитам не помещаются в доход. "
                      f"Резерв позволяет закрыть {names} ({fmt(total)}) — после этого бюджет "
                      f"выходит в плюс ({fmt(fcf)}/мес) и применяется стандартное распределение.")
            res["advice"] = prefix + " " + res["advice"]
            return res
        gap = max(0.0, -fcf)
        runway = (bliq / gap) if gap > 0 else None
        if dsti is not None and dsti >= DSTI_HIGH:
            flags.append("DSTI_HIGH")
            flags.append("RESTRUCTURING_ADVISED")
        if goals and any(not g.achieved for g in goals):
            flags.append("GOALS_FROZEN")
        advice = self._verdict_deficit(p, debts, payoffs, bliq, fcf, gap, runway, dsti, fixed)
        return self._pack(
            status="crisis_deficit",
            metrics=self._metrics(p, debts, bliq, fcf=fcf, dsti=dsti, burn=burn, runway=runway,
                                  cushion_target=None),
            lump={"debt_payoff": [self._payoff_row(d, r) for d, r in payoffs],
                  "goal_topups": [], "invest": 0.0},
            monthly={"to_cushion": 0.0, "debt_prepay": [], "goal_contributions": [],
                     "invest_total": 0.0, "invest_split": {}},
            goals=self._goal_rows(goals, funded={}),
            flags=flags,
            advice=advice,
        )

    def _survival_payoffs(self, debts, bliq, burn, income):
        chosen: list[tuple[Debt, str]] = []
        b, cur_burn = bliq, burn
        pool = sorted(
            [d for d in debts if d.balance > 0],
            key=lambda d: d.payment / d.balance, reverse=True,
        )
        if income == 0:
            for d in pool:
                if d.balance > b:
                    continue
                b_after = b - d.balance
                burn_after = cur_burn - d.payment
                runway_now = b / cur_burn if cur_burn > 0 else math.inf
                runway_after = b_after / burn_after if burn_after > 0 else math.inf
                if runway_after > runway_now and runway_after >= SAFE_RUNWAY_AFTER_PAYOFF:
                    chosen.append((d, "runway_extension"))
                    b, cur_burn = b_after, burn_after
            return chosen
        fcf = income - cur_burn
        for d in pool:
            if fcf >= 0:
                break
            if d.balance > b:
                continue
            b_after = b - d.balance
            burn_after = cur_burn - d.payment
            if b_after >= DEFICIT_FIX_KEEP_MONTHS * burn_after:
                chosen.append((d, "cashflow_fix"))
                b, cur_burn = b_after, burn_after
                fcf = income - cur_burn
        if fcf < 0:
            return []
        return chosen

    # ----------------------------------------------------------------- regular

    def _regular(self, p, debts, goals, bliq, dsti, flags):
        has_expensive = any(d.rate > p.r_bench for d in debts)
        aggressive = dsti is not None and dsti >= DSTI_HIGH and has_expensive
        if dsti is not None:
            if dsti >= DSTI_CRITICAL:
                flags.append("DSTI_CRITICAL")
                flags.append("RESTRUCTURING_ADVISED")
            elif dsti >= DSTI_HIGH:
                flags.append("DSTI_HIGH")
            elif dsti >= DSTI_ELEVATED:
                flags.append("DSTI_ELEVATED")

        lump_payoff, lump_topups, lump_invest, bliq = self._deploy_lump(
            p, debts, goals, bliq, aggressive, flags
        )

        m_total = sum(d.payment for d in debts)
        fcf = p.income - p.expenses - m_total
        burn = p.expenses + m_total
        cushion_target = max(p.l_min, CUSHION_MONTHS[p.risk] * burn)
        runway = bliq / burn if burn > 0 else None

        monthly, funded = self._monthly_waterfall(
            p, debts, goals, bliq, fcf, burn, cushion_target, aggressive, flags
        )

        status = "overleveraged" if aggressive else "stable"
        if not aggressive and fcf > 0 and burn > 0 and fcf / max(p.income, 1) >= 0.4:
            status = "strong_surplus"

        advice = self._verdict_regular(
            p, debts, goals, bliq, fcf, dsti, burn, cushion_target,
            lump_payoff, lump_topups, lump_invest, monthly, funded, aggressive
        )
        return self._pack(
            status=status,
            metrics=self._metrics(p, debts, bliq, fcf=fcf, dsti=dsti, burn=burn, runway=runway,
                                  cushion_target=cushion_target),
            lump={"debt_payoff": lump_payoff, "goal_topups": lump_topups, "invest": lump_invest},
            monthly=monthly,
            goals=self._goal_rows(goals, funded),
            flags=flags,
            advice=advice,
        )

    def _deploy_lump(self, p, debts, goals, bliq, aggressive, flags):
        payoff_rows: list[dict] = []
        topup_rows: list[dict] = []
        invest_lump = 0.0
        for _ in range(6):
            burn = p.expenses + sum(d.payment for d in debts)
            target = max(p.l_min, CUSHION_MONTHS[p.risk] * burn)
            surplus = bliq - target
            if surplus <= 1.0:
                break
            expensive = sorted(
                [d for d in debts if d.rate > p.r_bench and d.balance > 0],
                key=lambda d: d.rate, reverse=True,
            )
            moved = False
            for d in expensive:
                if surplus <= 1.0:
                    break
                amount = min(surplus, d.balance)
                full = amount >= d.balance - 0.01
                payoff_rows.append(self._payoff_row(d, "full" if full else "partial", amount))
                d.balance -= amount
                bliq -= amount
                surplus -= amount
                moved = True
                if full:
                    debts.remove(d)
            if not moved:
                break
        burn = p.expenses + sum(d.payment for d in debts)
        target = max(p.l_min, CUSHION_MONTHS[p.risk] * burn)
        surplus = bliq - target
        if surplus > 1.0 and not aggressive:
            deadline_goals = sorted(
                [g for g in goals if g.deadline and not g.achieved],
                key=lambda g: g.deadline,
            )
            m_total = sum(d.payment for d in debts)
            capacity = max(0.0, p.income - p.expenses - m_total)
            for g in deadline_goals:
                req = g.required_monthly or 0.0
                if req <= capacity:
                    capacity -= req
                    continue
                need_lump = min(g.gap, surplus,
                                max(0.0, (req - capacity) * (g.months_left or 1)))
                if need_lump > 1.0:
                    topup_rows.append({"goal": g.name, "amount": round(need_lump, 2)})
                    g.current += need_lump
                    bliq -= need_lump
                    surplus -= need_lump
                capacity = max(0.0, capacity - (g.required_monthly or 0.0))
                if surplus <= 1.0:
                    break
        if surplus > 1.0:
            invest_lump = surplus
            bliq -= surplus
            flags.append("LIQUIDITY_SURPLUS_DEPLOYED")
        if bliq < max(p.l_min, STARTER_MONTHS * (p.expenses + sum(d.payment for d in debts))):
            flags.append("CUSHION_BELOW_STARTER")
        return payoff_rows, topup_rows, round(invest_lump, 2), bliq

    def _monthly_waterfall(self, p, debts, goals, bliq, fcf, burn, cushion_target,
                           aggressive, flags):
        remaining = max(0.0, fcf)
        to_cushion = 0.0
        prepay_rows: list[dict] = []
        goal_rows: list[dict] = []
        funded: dict[int, float] = {}

        starter = STARTER_MONTHS * burn
        if bliq < starter and remaining > 0:
            to_cushion += remaining
            remaining = 0.0

        toxic = sorted([d for d in debts if d.rate >= p.r_bench + TOXIC_SPREAD],
                       key=lambda d: d.rate, reverse=True)
        if toxic:
            flags.append("TOXIC_DEBT")
        if remaining > 0 and toxic:
            top = toxic[0]
            amt = min(remaining, top.balance)
            prepay_rows.append({"loan": top.name, "amount": round(amt, 2),
                                "rate": top.rate, "mode": "avalanche_toxic"})
            remaining -= amt

        if remaining > 0 and bliq < cushion_target and not aggressive:
            add = min(remaining, cushion_target - bliq)
            to_cushion += add
            remaining -= add

        moderate = sorted(
            [d for d in debts if p.r_bench < d.rate < p.r_bench + TOXIC_SPREAD],
            key=lambda d: d.rate, reverse=True,
        )
        if aggressive and remaining > 0:
            pool = toxic[1:] + moderate if toxic else moderate
            for d in pool:
                if remaining <= 0:
                    break
                amt = min(remaining, d.balance)
                prepay_rows.append({"loan": d.name, "amount": round(amt, 2),
                                    "rate": d.rate, "mode": "dsti_reduction"})
                remaining -= amt

        if not aggressive:
            deadline_goals = sorted(
                [g for g in goals if g.deadline and not g.achieved],
                key=lambda g: g.deadline,
            )
            for g in deadline_goals:
                req = g.required_monthly or 0.0
                if req <= 0:
                    continue
                alloc = min(req, remaining)
                if alloc > 0:
                    goal_rows.append({"goal": g.name, "amount": round(alloc, 2),
                                      "required": round(req, 2),
                                      "deadline": g.deadline.isoformat()})
                    funded[g.id] = alloc
                    remaining -= alloc
                if alloc + 1.0 < req:
                    flags.append(f"GOAL_AT_RISK:{g.name}")

            if remaining > 0 and moderate:
                top = moderate[0]
                amt = min(remaining, top.balance)
                prepay_rows.append({"loan": top.name, "amount": round(amt, 2),
                                    "rate": top.rate, "mode": "avalanche_expensive"})
                remaining -= amt

        invest_total = remaining
        nd_goals = [g for g in goals if g.deadline is None and not g.achieved]
        earmark = [g.name for g in nd_goals] if invest_total > 0 and nd_goals else []
        split = {k: round(invest_total * v, 2)
                 for k, v in INVEST_SPLIT[p.risk].items() if v > 0}
        monthly = {
            "to_cushion": round(to_cushion, 2),
            "debt_prepay": prepay_rows,
            "goal_contributions": goal_rows,
            "invest_total": round(invest_total, 2),
            "invest_split": split,
            "invest_earmarked_goals": earmark,
        }
        return monthly, funded

    # ------------------------------------------------------------------ output

    def _metrics(self, p, debts, bliq, fcf, dsti, burn, runway, cushion_target):
        return {
            "income": round(p.income, 2),
            "expenses": round(p.expenses, 2),
            "debt_service": round(sum(d.payment for d in debts), 2),
            "fcf": round(fcf, 2),
            "dsti": round(dsti, 4) if dsti is not None else None,
            "burn": round(burn, 2),
            "bliq_after_lump": round(bliq, 2),
            "runway_months": round(runway, 1) if runway is not None else None,
            "cushion_target": round(cushion_target, 2) if cushion_target else None,
            "r_bench": p.r_bench,
            "risk": p.risk,
        }

    def _payoff_row(self, d: Debt, reason: str, amount: float | None = None) -> dict:
        return {"loan": d.name, "amount": round(amount if amount is not None else d.balance, 2),
                "rate": d.rate, "reason": reason}

    def _goal_rows(self, goals, funded):
        rows = []
        for g in goals:
            req = g.required_monthly
            rows.append({
                "name": g.name,
                "target": round(g.target, 2),
                "current": round(g.current, 2),
                "gap": round(g.gap, 2),
                "deadline": g.deadline.isoformat() if g.deadline else None,
                "months_left": g.months_left,
                "required_monthly": round(req, 2) if req is not None else None,
                "planned_monthly": round(funded.get(g.id, 0.0), 2),
                "achieved": g.achieved,
            })
        return rows

    def _pack(self, status, metrics, lump, monthly, goals, flags, advice):
        return {"status": status, "metrics": metrics, "lump_plan": lump,
                "monthly_plan": monthly, "goals": goals,
                "flags": sorted(set(flags)), "advice": advice}

    # ----------------------------------------------------------------- verdicts

    def _verdict_no_income(self, p, debts, payoffs, bliq, burn, runway):
        parts = ["Доход отсутствует — режим сохранения ликвидности."]
        if runway is not None:
            parts.append(f"Резерва {fmt(bliq)} хватит примерно на {runway:.0f} мес. текущих трат ({fmt(burn)}/мес).")
        if payoffs:
            names = ", ".join(d.name for d, _ in payoffs)
            parts.append(f"Рекомендуется закрыть из резерва {names}: это снижает ежемесячную нагрузку и удлиняет запас прочности.")
        if debts:
            parts.append("По остальным кредитам — только минимальные платежи; при риске просрочки заранее запросить у банка реструктуризацию или кредитные каникулы.")
        parts.append("Инвестиции и досрочные погашения дорогих целей исключены; пополнение целей заморозить. Приоритет — восстановление дохода и сокращение необязательных расходов на 20–30%.")
        return " ".join(x.strip() for x in parts if x.strip())

    def _verdict_deficit(self, p, debts, payoffs, bliq, fcf, gap, runway, dsti, fixed):
        parts = ["Денежный поток отрицательный."]
        parts.append(f"Дефицит {fmt(gap)}/мес; резерв покрывает его ~{runway:.0f} мес." if runway else f"Дефицит {fmt(gap)}/мес.")
        if dsti is not None and dsti >= 1.0:
            parts.append(f"Платежи по кредитам ({dsti:.0%} дохода) физически не помещаются в бюджет — первоочередная мера: реструктуризация или рефинансирование под посильный платёж, до договорённости с банком не допускать хаотичных просрочек.")
            if debts:
                top = max(debts, key=lambda d: d.rate)
                parts.append(f"Приоритет пересмотра условий — {top.name} (ставка {top.rate:.0%}, платёж {fmt(top.payment)}/мес).")
            parts.append("Параллельно сократить прочие расходы, чтобы уменьшить скорость проедания резерва.")
        else:
            parts.append(f"Первоочередная задача — сократить расходы минимум на {fmt(gap)} в месяц до выхода в ноль.")
            if dsti is not None and dsti >= DSTI_HIGH:
                parts.append(f"Долговая нагрузка {dsti:.0%} — показана реструктуризация или рефинансирование под меньший платёж.")
        parts.append("Пополнение целей и инвестиции заморозить до стабилизации потока.")
        return " ".join(x.strip() for x in parts if x.strip())

    def _verdict_regular(self, p, debts, goals, bliq, fcf, dsti, burn, cushion_target,
                         lump_payoff, lump_topups, lump_invest, monthly, funded, aggressive):
        parts = []
        if aggressive:
            parts.append(f"Долговая нагрузка {dsti:.0%} от дохода — критический уровень: весь свободный поток направляется на снижение долга, пополнение целей приостановлено, показано рефинансирование под меньший платёж.")
        elif dsti is not None and dsti >= DSTI_HIGH:
            parts.append(f"Долговая нагрузка {dsti:.0%} — высокая, но все ставки не выше бенчмарка {p.r_bench:.0%}: платежи держать строго по графику, без досрочных погашений; при возможности — рефинансирование под меньший платёж.")
        achieved = [g.name for g in goals if g.achieved]
        if achieved:
            parts.append("Цели " + ", ".join(achieved) + " уже профинансированы — излишек накоплений перенаправить на остальные цели или в инвестиционный портфель.")
        if lump_payoff:
            total = sum(r["amount"] for r in lump_payoff)
            full = [r["loan"] for r in lump_payoff if r["reason"] == "full"]
            s = f"Избыточная ликвидность позволяет направить {fmt(total)} на досрочное погашение дорогих кредитов"
            s += f" (полностью закрыть: {', '.join(full)})." if full else " (частичное погашение с сокращением срока)."
            parts.append(s)
        if monthly["to_cushion"] > 0:
            parts.append(f"Подушку довести до целевых {fmt(cushion_target)} ({CUSHION_MONTHS[p.risk]:.2g} мес. расходов) — на это ежемесячно {fmt(monthly['to_cushion'])}.")
        toxic_rows = [r for r in monthly["debt_prepay"] if r["mode"] == "avalanche_toxic"]
        if toxic_rows:
            r = toxic_rows[0]
            parts.append(f"Дорогой кредит {r['loan']} ({r['rate']:.0%}) гасить досрочно по {fmt(r['amount'])}/мес — гарантированная доходность выше рынка ({p.r_bench:.0%}).")
        cheap = [d for d in debts if d.rate <= p.r_bench]
        if cheap:
            parts.append(f"Кредиты со ставкой не выше бенчмарка ({', '.join(d.name for d in cheap)}) досрочно не гасить — выгоднее размещать деньги под {p.r_bench:.0%}.")
        if monthly["goal_contributions"]:
            total_g = sum(r["amount"] for r in monthly["goal_contributions"])
            parts.append(f"На цели с дедлайнами — {fmt(total_g)}/мес по требуемым взносам.")
        if lump_topups:
            parts.append("Часть избытка резерва направить разовыми пополнениями в цели с ближайшими сроками: " + ", ".join(f"{t['goal']} +{fmt(t['amount'])}" for t in lump_topups) + ".")
        if monthly["invest_total"] > 0:
            split = ", ".join(f"{k} {v/monthly['invest_total']:.0%}" for k, v in monthly["invest_split"].items())
            tail = f" Свободный остаток {fmt(monthly['invest_total'])}/мес инвестировать (профиль риска {p.risk}/5): {split}."
            if monthly["invest_earmarked_goals"]:
                tail += " Целевое назначение — накопления по целям без срока: " + ", ".join(monthly["invest_earmarked_goals"]) + "."
            parts.append(tail)
        if lump_invest > 0:
            parts.append(f"Разовый инвестиционный транш из избытка ликвидности — {fmt(lump_invest)} по тому же распределению.")
        if not parts:
            parts.append("Свободный поток отсутствует; поддерживать текущие платежи и резерв.")
        return " ".join(x.strip() for x in parts if x.strip())


class Runner:
    def __init__(self, src: Path, out_dir: Path):
        self.src = src
        self.out_dir = out_dir
        self.advisor = ExpertAdvisor()

    def run(self) -> dict:
        out_path = self.out_dir / "expert_recommendations_12000.jsonl"
        stats: dict = {"status": {}, "kind_status": {}, "sums": {}, "n": 0}
        results_index: dict[str, dict] = {}
        with open(self.src) as fin, open(out_path, "w") as fout:
            for line in fin:
                rec = json.loads(line)
                p = Portrait.from_record(rec)
                res = self.advisor.analyze(p)
                fout.write(json.dumps(res, ensure_ascii=False) + "\n")
                self._accumulate(stats, res)
                if res["id"] in SAMPLE_IDS:
                    results_index[res["id"]] = (rec, res)
        stats_path = self.out_dir / "run_stats.json"
        stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2))
        return results_index

    def _accumulate(self, stats, res):
        stats["n"] += 1
        st = res["status"]
        stats["status"][st] = stats["status"].get(st, 0) + 1
        key = f"{res['kind']}|{st}"
        stats["kind_status"][key] = stats["kind_status"].get(key, 0) + 1
        s = stats["sums"]
        m = res["monthly_plan"]
        s["monthly_invest"] = s.get("monthly_invest", 0) + m["invest_total"]
        s["monthly_cushion"] = s.get("monthly_cushion", 0) + m["to_cushion"]
        s["monthly_prepay"] = s.get("monthly_prepay", 0) + sum(r["amount"] for r in m["debt_prepay"])
        s["monthly_goals"] = s.get("monthly_goals", 0) + sum(r["amount"] for r in m["goal_contributions"])
        lp = res["lump_plan"]
        s["lump_payoff"] = s.get("lump_payoff", 0) + sum(r["amount"] for r in lp["debt_payoff"])
        s["lump_invest"] = s.get("lump_invest", 0) + lp["invest"]
        s["lump_topups"] = s.get("lump_topups", 0) + sum(r["amount"] for r in lp["goal_topups"])


SAMPLE_IDS: set[str] = set()


def main():
    src = Path("/mnt/user-data/uploads/portraits_12000.jsonl")
    out_dir = Path("/home/claude/out")
    out_dir.mkdir(exist_ok=True)

    kinds_seen: dict[str, list[str]] = {}
    with open(src) as f:
        for line in f:
            rec = json.loads(line)
            kinds_seen.setdefault(rec["kind"], []).append(rec["id"])
    for kind, ids in kinds_seen.items():
        SAMPLE_IDS.update(ids[:2])

    runner = Runner(src, out_dir)
    samples = runner.run()
    print("done", len(samples), "samples captured")


if __name__ == "__main__":
    main()
