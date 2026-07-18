"""Independent expert engine: deterministic personal-finance evaluation.

Implements the methodology fixed in methodology.md (as of 2026-07-08)
for the FINPILOT synthetic test set. One pass, no manual edits.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from datetime import date


AS_OF = date(2026, 7, 8)
MONTH_DAYS = 30.4375


class Methodology:
    DSTI_COMFORT = 0.30
    DSTI_ELEVATED = 0.50
    DSTI_CRITICAL = 0.80
    CUSHION_MONTHS = {1: 6.0, 2: 5.0, 3: 4.0, 4: 3.0, 5: 3.0}
    MIN_CUSHION_MONTHS = 1.0
    EXPENSIVE_SPREAD = 0.015
    EQUITY_SHARE = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8}
    ERP = 0.04
    H_SHORT = 12
    H_MID = 36
    H_LONG = 84
    SPLIT_DEBT_BUILDING = (0.70, 0.30)
    SPLIT_DEBT_FUNDED = (0.80, 0.20)
    SPLIT_CUSHION_GOALS = (0.60, 0.40)
    ON_TRACK_TOLERANCE = 0.99


@dataclass
class Loan:
    loan_id: object
    name: str
    amount: float
    rate: float
    payment: float
    classification: str = "neutral"
    interest_only: bool = False
    lump_extra: float = 0.0
    monthly_extra: float = 0.0


@dataclass
class Goal:
    goal_id: object
    name: str
    target: float
    current: float
    deadline: date | None
    overdue: bool = False
    months_left: int | None = None
    lump_allocated: float = 0.0
    monthly_allocated: float = 0.0
    required_monthly: float = 0.0
    status: str = ""
    instrument: str = ""
    note: str = ""


@dataclass
class Portrait:
    pid: str
    kind: str
    income: float = 0.0
    expense: float = 0.0
    bliq: float = 0.0
    r_bench: float = 0.0
    risk: int = 3
    l_min: float = 0.0
    loans: list = field(default_factory=list)
    goals: list = field(default_factory=list)
    valid: bool = True
    flags: list = field(default_factory=list)


def r2(x: float) -> float:
    return round(x + 0.0, 2)


def is_money(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


class PortraitParser:
    ENGINE_KEYS = {"income_total", "expense_total", "bliq", "r_bench",
                   "risk_tolerance", "l_min", "obligations", "goals"}

    def __init__(self) -> None:
        self.seen_ids: set = set()

    def parse(self, raw: dict) -> Portrait:
        pid = str(raw.get("id", ""))
        p = Portrait(pid=pid, kind=str(raw.get("kind", "unknown")))
        eng = raw.get("engine")
        if not pid or not isinstance(eng, dict):
            return self._reject(p, "missing_required_fields")
        if pid in self.seen_ids:
            return self._reject(p, "duplicate_id")
        self.seen_ids.add(pid)
        if set(eng.keys()) - self.ENGINE_KEYS:
            p.flags.append("extra_fields")
        for key in ("income_total", "expense_total", "bliq", "l_min", "r_bench"):
            v = eng.get(key)
            if not is_money(v) or v < 0:
                return self._reject(p, f"bad_field:{key}")
        risk = eng.get("risk_tolerance")
        if not isinstance(risk, int) or isinstance(risk, bool) or not 1 <= risk <= 5:
            return self._reject(p, "bad_field:risk_tolerance")
        p.income, p.expense = eng["income_total"], eng["expense_total"]
        p.bliq, p.r_bench = eng["bliq"], eng["r_bench"]
        p.l_min, p.risk = eng["l_min"], risk
        if not self._parse_loans(p, eng) or not self._parse_goals(p, eng):
            return p
        return p

    def _reject(self, p: Portrait, reason: str) -> Portrait:
        p.valid = False
        p.flags.append(reason)
        return p

    def _parse_loans(self, p: Portrait, eng: dict) -> bool:
        obs = eng.get("obligations")
        if obs is None:
            p.flags.append("missing_array:obligations")
            obs = []
        if not isinstance(obs, list):
            self._reject(p, "bad_field:obligations")
            return False
        for o in obs:
            if not isinstance(o, dict):
                self._reject(p, "bad_loan_record")
                return False
            a, ir, mp = o.get("amount"), o.get("interest_rate"), o.get("monthly_payment")
            if not (is_money(a) and is_money(ir) and is_money(mp)) or min(a, ir, mp) < 0:
                self._reject(p, "bad_loan_values")
                return False
            if a == 0:
                p.flags.append("zero_amount_debt")
                continue
            p.loans.append(Loan(o.get("id"), str(o.get("name", "")), a, ir, mp))
        return True

    def _parse_goals(self, p: Portrait, eng: dict) -> bool:
        goals = eng.get("goals")
        if goals is None:
            p.flags.append("missing_array:goals")
            goals = []
        if not isinstance(goals, list):
            self._reject(p, "bad_field:goals")
            return False
        for g in goals:
            if not isinstance(g, dict):
                self._reject(p, "bad_goal_record")
                return False
            t, c, d = g.get("target_amount"), g.get("current_amount"), g.get("deadline")
            if not (is_money(t) and is_money(c)) or min(t, c) < 0:
                self._reject(p, "bad_goal_values")
                return False
            deadline = None
            if d is not None:
                try:
                    deadline = date.fromisoformat(str(d))
                except ValueError:
                    self._reject(p, "bad_goal_deadline")
                    return False
            p.goals.append(Goal(g.get("id"), str(g.get("name", "")), t, c, deadline))
        return True


class ExpertAdvisor:
    def __init__(self) -> None:
        self.m = Methodology()

    def advise(self, p: Portrait) -> dict:
        if not p.valid:
            return self._invalid(p)
        d = self._diagnostics(p)
        self._classify_loans(p)
        lump_plan = self._lump_plan(p, d)
        monthly = self._monthly_plan(p, d)
        goal_plan = self._goal_plan(p, d)
        status = self._profile_status(p, d)
        verdict = self._verdict(p, d, status)
        return {
            "id": p.pid, "kind": p.kind, "status": status,
            "flags": sorted(set(p.flags)),
            "diagnostics": {k: (r2(v) if isinstance(v, float) else v)
                            for k, v in d.items()},
            "debt_plan": self._debt_plan(p),
            "lump_sum_plan": lump_plan,
            "monthly_plan": monthly,
            "goal_plan": goal_plan,
            "verdict": verdict,
        }

    def _invalid(self, p: Portrait) -> dict:
        return {"id": p.pid, "kind": p.kind, "status": "INVALID",
                "flags": sorted(set(p.flags)), "diagnostics": {},
                "debt_plan": [], "lump_sum_plan": [], "monthly_plan": [],
                "goal_plan": [],
                "verdict": ("Запись отклонена: некорректные входные "
                            "данные, рекомендации не выдаются.")}

    def _diagnostics(self, p: Portrait) -> dict:
        payments = sum(ln.payment for ln in p.loans)
        outflow = p.expense + payments
        fcf = r2(p.income - outflow)
        if p.income > 0:
            dsti = payments / p.income
        elif payments > 0:
            dsti = None
            p.flags.append("dsti_undefined")
        else:
            dsti = 0.0
        if p.income == 0:
            p.flags.append("no_income")
        liq_months = p.bliq / outflow if outflow > 0 else None
        if outflow == 0:
            p.flags.append("no_outflow")
        target_months = max(p.l_min, self.m.CUSHION_MONTHS[p.risk])
        target_cushion = r2(target_months * outflow)
        deployable = r2(max(0.0, p.bliq - target_cushion))
        runway = r2(p.bliq / -fcf) if fcf < 0 else None
        if fcf < 0:
            p.flags.append("deficit_cf")
        if not p.loans:
            p.flags.append("no_debts")
        if not p.goals:
            p.flags.append("no_goals")
        return {"income": p.income, "expense": p.expense,
                "debt_payments": r2(payments), "outflow": r2(outflow),
                "fcf": fcf, "dsti": None if dsti is None else round(dsti, 4),
                "liq_months": None if liq_months is None else round(liq_months, 2),
                "target_cushion_months": target_months,
                "target_cushion_rub": target_cushion,
                "deployable_lump": deployable, "runway_months": runway,
                "n_debts": len(p.loans), "n_goals": len(p.goals)}

    def _classify_loans(self, p: Portrait) -> None:
        for loan in p.loans:
            if loan.rate > p.r_bench + self.m.EXPENSIVE_SPREAD:
                loan.classification = "expensive"
            elif loan.rate <= p.r_bench:
                loan.classification = "cheap"
            if loan.payment <= loan.amount * loan.rate / 12 + 1e-9:
                loan.interest_only = True
                p.flags.append("interest_only_debt")

    def _expensive(self, p: Portrait) -> list:
        return sorted((ln for ln in p.loans if ln.classification == "expensive"),
                      key=lambda ln: (-ln.rate, str(ln.loan_id)))

    def _lump_allowed(self, d: dict) -> bool:
        return d["fcf"] > 0 and d["dsti"] is not None and d["dsti"] < self.m.DSTI_ELEVATED

    def _lump_plan(self, p: Portrait, d: dict) -> list:
        deployable = d["deployable_lump"]
        if deployable <= 0:
            return []
        if not self._lump_allowed(d):
            p.flags.append("lump_frozen")
            return []
        plan, rem = [], deployable
        for loan in self._expensive(p):
            if rem <= 0:
                break
            pay = r2(min(rem, loan.amount))
            if pay <= 0:
                continue
            loan.lump_extra = pay
            rem = r2(rem - pay)
            plan.append({"action": f"prepay_debt:{loan.loan_id}", "amount": pay,
                         "instrument": "досрочное погашение тела",
                         "note": f"{loan.name}, ставка {loan.rate:.2%}"})
        for goal in self._goals_deadline_sorted(p):
            if rem <= 0:
                break
            need = r2(max(0.0, goal.target - goal.current))
            pay = r2(min(rem, need))
            if pay <= 0:
                continue
            goal.lump_allocated = pay
            rem = r2(rem - pay)
            plan.append({"action": f"fund_goal:{goal.goal_id}", "amount": pay,
                         "instrument": self._instrument(self._goal_months(goal), p.risk),
                         "note": goal.name})
        if rem > 0:
            plan.append({"action": "invest", "amount": rem,
                         "instrument": self._portfolio_label(p.risk, None),
                         "note": "инвестиции сверх подушки и целей"})
        return plan

    def _goals_deadline_sorted(self, p: Portrait) -> list:
        dated = [g for g in p.goals if g.deadline is not None]
        return sorted(dated, key=lambda g: (g.deadline, str(g.goal_id)))

    def _goal_months(self, goal: Goal) -> int | None:
        if goal.deadline is None:
            return None
        days = (goal.deadline - AS_OF).days
        if days < 0:
            goal.overdue = True
            return 0
        return max(1, int(days // MONTH_DAYS)) if days > 0 else 0

    def _eq_share(self, months: int | None, risk: int) -> float:
        base = self.m.EQUITY_SHARE[risk]
        if months is None or months > self.m.H_LONG:
            return base
        if months < self.m.H_MID:
            return 0.0
        return min(base, 0.5)

    def _exp_rate_monthly(self, months: int | None, risk: int, r_bench: float) -> float:
        annual = r_bench + self._eq_share(months, risk) * self.m.ERP
        return (1.0 + annual) ** (1.0 / 12.0) - 1.0

    def _instrument(self, months: int | None, risk: int) -> str:
        if months is not None and months < self.m.H_SHORT:
            return "депозит / фонд денежного рынка"
        if months is not None and months < self.m.H_MID:
            return "ОФЗ и облигации 1–3 лет + депозит"
        return self._portfolio_label(risk, months)

    def _portfolio_label(self, risk: int, months: int | None) -> str:
        eq = int(round(self._eq_share(months, risk) * 100))
        return f"портфель {eq}% акций / {100 - eq}% облигаций"

    def _required_monthly(self, goal: Goal, months: int, i: float) -> float:
        need_fv = goal.target - (goal.current + goal.lump_allocated) * (1.0 + i) ** months
        if need_fv <= 0:
            return 0.0
        if i <= 0:
            return need_fv / months
        return need_fv * i / ((1.0 + i) ** months - 1.0)

    def _monthly_plan(self, p: Portrait, d: dict) -> list:
        total = r2(max(0.0, d["fcf"]))
        if total <= 0:
            return []
        cushion_raw, debt_raw, goals_raw = self._split_fcf(p, d, total)
        allocations = []
        if cushion_raw > 0:
            allocations.append(("cushion", None, cushion_raw,
                                "накопительный счёт / фонд денежного рынка", "пополнение подушки"))
        debt_left = debt_raw
        for loan in self._expensive(p):
            if debt_left <= 0:
                break
            cap = max(0.0, loan.amount - loan.lump_extra)
            take = min(debt_left, cap)
            if take <= 0:
                continue
            loan.monthly_extra = take
            debt_left -= take
            allocations.append((f"debt_prepay:{loan.loan_id}", loan, take,
                                "досрочное погашение тела", f"avalanche, ставка {loan.rate:.2%}"))
        goals_raw += debt_left
        allocations.extend(self._allocate_goals(p, goals_raw, d["fcf"]))
        return self._round_plan(allocations, total, p)

    def _split_fcf(self, p: Portrait, d: dict, total: float) -> tuple:
        below_min = d["liq_months"] is not None and d["liq_months"] < self.m.MIN_CUSHION_MONTHS
        below_target = p.bliq < d["target_cushion_rub"]
        has_expensive = any(ln.classification == "expensive" for ln in p.loans)
        if below_min:
            return total, 0.0, 0.0
        if has_expensive:
            debt_share, rest = (self.m.SPLIT_DEBT_BUILDING if below_target
                                else self.m.SPLIT_DEBT_FUNDED)
            if below_target:
                return rest * total, debt_share * total, 0.0
            return 0.0, debt_share * total, rest * total
        if below_target:
            cushion_share, goal_share = self.m.SPLIT_CUSHION_GOALS
            return cushion_share * total, 0.0, goal_share * total
        return 0.0, 0.0, total

    def _allocate_goals(self, p: Portrait, pool: float, fcf: float) -> list:
        out, rem = [], pool
        if rem <= 0:
            return out
        dated = []
        for goal in self._goals_deadline_sorted(p):
            months = self._goal_months(goal)
            if months == 0:
                req = max(0.0, goal.target - goal.current - goal.lump_allocated)
            else:
                i = self._exp_rate_monthly(months, p.risk, p.r_bench)
                req = self._required_monthly(goal, months, i)
            goal.required_monthly = req
            dated.append((goal, months, req))
        reachable = [(g, m, r) for g, m, r in dated if 0 < r <= max(0.0, fcf) and m > 0]
        stranded = [(g, m, r) for g, m, r in dated
                    if r > 0 and (r > max(0.0, fcf) or m == 0)]
        for goal, months, req in reachable + stranded:
            take = min(rem, req)
            if take > 0:
                goal.monthly_allocated = take
                rem -= take
                out.append((f"goal:{goal.goal_id}", goal, take,
                            self._instrument(months, p.risk), goal.name))
        open_goals = [g for g in p.goals if g.deadline is None
                      and g.target - g.current - g.lump_allocated > 0]
        total_need = sum(g.target - g.current - g.lump_allocated for g in open_goals)
        if rem > 0 and total_need > 0:
            pool_nd = rem
            for goal in open_goals:
                need = goal.target - goal.current - goal.lump_allocated
                take = min(need, pool_nd * need / total_need)
                goal.monthly_allocated = take
                rem -= take
                out.append((f"goal:{goal.goal_id}", goal, take,
                            self._instrument(None, p.risk), goal.name))
        if rem > 1e-9:
            out.append(("invest_surplus", None, rem,
                        self._portfolio_label(p.risk, None), "инвестиции сверх целей"))
        return out

    def _round_plan(self, allocations: list, total: float, p: Portrait) -> list:
        rounded = [[key, obj, r2(amt), instr, note]
                   for key, obj, amt, instr, note in allocations if r2(amt) > 0]
        if not rounded:
            return []
        diff = r2(total - sum(a[2] for a in rounded))
        if diff != 0:
            target = max(rounded, key=lambda a: a[2])
            target[2] = r2(target[2] + diff)
        plan = []
        for key, obj, amt, instr, note in rounded:
            if isinstance(obj, Goal):
                obj.monthly_allocated = amt
            if isinstance(obj, Loan):
                obj.monthly_extra = amt
            plan.append({"bucket": key, "amount": amt,
                         "instrument": instr, "note": note})
        return plan

    def _goal_plan(self, p: Portrait, d: dict) -> list:
        out = []
        for goal in p.goals:
            months = self._goal_months(goal)
            i_long = self._exp_rate_monthly(None, p.risk, p.r_bench)
            self._set_goal_status(goal, months, p, d)
            entry = {"id": goal.goal_id, "name": goal.name,
                     "target": r2(goal.target), "current": r2(goal.current),
                     "months_left": months if goal.deadline else None,
                     "required_monthly": r2(goal.required_monthly),
                     "allocated_monthly": r2(goal.monthly_allocated),
                     "lump_allocated": r2(goal.lump_allocated),
                     "status": goal.status,
                     "instrument": goal.instrument, "note": goal.note}
            if goal.status in ("no_deadline", "overdue") and goal.monthly_allocated > 0:
                eta = self._months_to_target(goal, i_long)
                entry["months_to_target_at_plan"] = eta
            out.append(entry)
        return out

    def _set_goal_status(self, goal: Goal, months: int | None,
                         p: Portrait, d: dict) -> None:
        funded = goal.current + goal.lump_allocated
        goal.instrument = self._instrument(months, p.risk)
        if abs(funded - goal.target) < 0.005:
            goal.status, goal.note = "achieved", "цель закрыта"
            return
        if funded > goal.target:
            goal.status = "overfunded"
            goal.note = (f"перефинансирована: высвободить излишек "
                         f"{r2(funded - goal.target):,.2f} ₽ на другие цели")
            return
        if goal.deadline is None:
            goal.status, goal.note = "no_deadline", "финансируется по остаточному принципу"
            return
        if goal.overdue:
            goal.status = "overdue"
            goal.note = "дедлайн просрочен: требуется разовое пополнение либо перенос срока"
            return
        if months == 0:
            goal.status = "deadline_today"
            goal.note = "дедлайн наступил: закрытие возможно только разовым платежом"
            p.flags.append("deadline_today")
            return
        if goal.required_monthly <= 0:
            goal.status, goal.note = "on_track", "закрывается органическим ростом накоплений"
            return
        if goal.monthly_allocated >= goal.required_monthly * self.m.ON_TRACK_TOLERANCE:
            goal.status, goal.note = "on_track", "график взносов выдерживается"
            return
        if goal.required_monthly > max(0.0, d["fcf"]):
            goal.status = "unreachable"
            goal.note = (f"недостижима к сроку: требуемый взнос "
                         f"{r2(goal.required_monthly):,.2f} ₽/мес превышает весь свободный поток")
            return
        gap = r2(goal.required_monthly - goal.monthly_allocated)
        goal.status = "underfunded"
        goal.note = f"недофинансирование {gap:,.2f} ₽/мес: пересмотреть приоритеты или срок"

    def _months_to_target(self, goal: Goal, i: float) -> int | None:
        cur = goal.current + goal.lump_allocated
        pmt = goal.monthly_allocated
        if cur >= goal.target:
            return 0
        if pmt <= 0:
            if i > 0 and cur > 0:
                return math.ceil(math.log(goal.target / cur) / math.log(1.0 + i))
            return None
        if i <= 0:
            return math.ceil((goal.target - cur) / pmt)
        x = (goal.target + pmt / i) / (cur + pmt / i)
        return math.ceil(math.log(x) / math.log(1.0 + i))

    def _debt_plan(self, p: Portrait) -> list:
        out = []
        avalanche = {l.loan_id: k + 1 for k, l in enumerate(self._expensive(p))}
        for loan in p.loans:
            action, note = "keep_schedule", "платить по графику"
            if loan.classification == "expensive":
                action = "prepay_avalanche"
                note = f"приоритет досрочного погашения #{avalanche[loan.loan_id]}"
            elif loan.classification == "cheap":
                note = "ставка ниже бенчмарка: досрочное погашение невыгодно"
            payoff = self._months_to_payoff(loan)
            if loan.interest_only:
                action = ("restructure" if loan.classification != "expensive"
                          else "prepay_avalanche")
                note += "; платёж не покрывает амортизацию тела — реструктуризация обязательна"
            out.append({"id": loan.loan_id, "name": loan.name,
                        "amount": r2(loan.amount), "rate": loan.rate,
                        "monthly_payment": r2(loan.payment),
                        "classification": loan.classification,
                        "interest_only": loan.interest_only,
                        "months_to_payoff_schedule": payoff,
                        "monthly_extra": r2(loan.monthly_extra),
                        "lump_extra": r2(loan.lump_extra),
                        "action": action, "note": note})
        return out

    def _months_to_payoff(self, loan: Loan) -> int | None:
        i = loan.rate / 12.0
        if i <= 0:
            return math.ceil(loan.amount / loan.payment) if loan.payment > 0 else None
        if loan.payment <= loan.amount * i:
            return None
        return math.ceil(-math.log(1.0 - i * loan.amount / loan.payment)
                         / math.log(1.0 + i))

    def _profile_status(self, p: Portrait, d: dict) -> str:
        dsti = d["dsti"]
        if d["fcf"] < 0 or (dsti is None and d["debt_payments"] > 0) \
                or (dsti is not None and dsti >= self.m.DSTI_CRITICAL):
            return "CRISIS"
        if (dsti is not None and dsti >= self.m.DSTI_ELEVATED) \
                or (d["liq_months"] is not None
                    and d["liq_months"] < self.m.MIN_CUSHION_MONTHS):
            return "STRAINED"
        if any(ln.classification == "expensive" for ln in p.loans) \
                or p.bliq < d["target_cushion_rub"]:
            return "STABILIZING"
        goals_ok = all(g.status in ("on_track", "achieved", "overfunded")
                       for g in p.goals)
        if d["deployable_lump"] > 0 and goals_ok:
            return "SURPLUS"
        return "STEADY"

    def _verdict(self, p: Portrait, d: dict, status: str) -> str:
        fcf, liq = d["fcf"], d["liq_months"]
        dsti_txt = "не определён" if d["dsti"] is None else f"{d['dsti']:.0%}"
        if status == "CRISIS":
            if fcf < 0:
                run = d["runway_months"]
                run_txt = f"{run:,.1f}" if run is not None else "0"
                return (f"Кризис: дефицит {abs(fcf):,.0f} ₽/мес (ПДН {dsti_txt}), подушки хватит "
                        f"на {run_txt} мес — срочно резать расходы и реструктурировать долги.")
            return (f"Кризис долговой нагрузки: ПДН {dsti_txt} при потоке {fcf:,.0f} ₽/мес — "
                    f"реструктуризация и запрет новых кредитов.")
        if status == "STRAINED":
            liq_txt = "∞" if liq is None else f"{liq:.1f}"
            return (f"Напряжённо: ПДН {dsti_txt}, ликвидность {liq_txt} мес — весь поток "
                    f"{fcf:,.0f} ₽/мес в подушку и снижение нагрузки.")
        if status == "STABILIZING":
            n_exp = sum(1 for ln in p.loans if ln.classification == "expensive")
            if n_exp:
                word = ("дорогой кредит" if n_exp % 10 == 1 and n_exp % 100 != 11
                        else "дорогих кредита" if n_exp % 10 in (2, 3, 4)
                        and n_exp % 100 not in (12, 13, 14) else "дорогих кредитов")
                return (f"Стабилизация: {n_exp} {word} гасим avalanche, "
                        f"поток {fcf:,.0f} ₽/мес, подушка {0 if liq is None else round(liq, 1)}"
                        f"/{d['target_cushion_months']:.0f} мес.")
            return (f"Стабилизация: доращиваем подушку до {d['target_cushion_months']:.0f} мес "
                    f"({d['target_cushion_rub']:,.0f} ₽), поток {fcf:,.0f} ₽/мес.")
        if status == "SURPLUS":
            return (f"Профицит: излишек {d['deployable_lump']:,.0f} ₽ разворачиваем в рынок, "
                    f"поток {fcf:,.0f} ₽/мес работает на цели.")
        return (f"Устойчиво: подушка обеспечена, дорогих долгов нет, поток {fcf:,.0f} ₽/мес "
                f"распределён по целям.")


class Runner:
    SUMMARY_COLS = ["id", "kind", "status", "income", "expense", "debt_payments",
                    "outflow", "fcf", "dsti", "bliq", "liq_months",
                    "target_cushion_rub", "deployable_lump", "n_debts",
                    "n_expensive", "n_goals", "m_cushion", "m_debt", "m_goals",
                    "m_invest", "lump_debt", "lump_goals", "lump_invest", "flags"]

    def __init__(self, src: str, out_dir: str) -> None:
        self.src, self.out_dir = src, out_dir
        self.parser, self.advisor = PortraitParser(), ExpertAdvisor()
        self.monthly_violations = 0
        self.lump_violations = 0
        self.status_counts: dict = {}
        self.kind_status: dict = {}

    def run(self) -> dict:
        rec_path = f"{self.out_dir}/recommendations.jsonl"
        csv_path = f"{self.out_dir}/summary.csv"
        with open(self.src) as fin, open(rec_path, "w") as frec, \
                open(csv_path, "w", newline="") as fcsv:
            writer = csv.DictWriter(fcsv, fieldnames=self.SUMMARY_COLS)
            writer.writeheader()
            for line in fin:
                raw = json.loads(line)
                portrait = self.parser.parse(raw)
                rec = self.advisor.advise(portrait)
                self._control(portrait, rec)
                self._count(rec)
                frec.write(json.dumps(rec, ensure_ascii=False) + "\n")
                writer.writerow(self._summary_row(portrait, rec))
        return {"monthly_violations": self.monthly_violations,
                "lump_violations": self.lump_violations,
                "status_counts": self.status_counts,
                "kind_status": self.kind_status}

    def _control(self, p: Portrait, rec: dict) -> None:
        d = rec["diagnostics"]
        if not d:
            return
        total = round(max(0.0, d["fcf"]), 2)
        got = round(sum(x["amount"] for x in rec["monthly_plan"]), 2)
        if abs(got - total) > 0.005:
            self.monthly_violations += 1
        lump = round(sum(x["amount"] for x in rec["lump_sum_plan"]), 2)
        if lump - d["deployable_lump"] > 0.005:
            self.lump_violations += 1

    def _count(self, rec: dict) -> None:
        s, k = rec["status"], rec["kind"]
        self.status_counts[s] = self.status_counts.get(s, 0) + 1
        self.kind_status.setdefault(k, {})[s] = self.kind_status.get(k, {}).get(s, 0) + 1

    def _summary_row(self, p: Portrait, rec: dict) -> dict:
        d = rec["diagnostics"]
        buckets = {"m_cushion": 0.0, "m_debt": 0.0, "m_goals": 0.0, "m_invest": 0.0}
        for x in rec["monthly_plan"]:
            key = x["bucket"]
            if key == "cushion":
                buckets["m_cushion"] += x["amount"]
            elif key.startswith("debt_prepay"):
                buckets["m_debt"] += x["amount"]
            elif key.startswith("goal:"):
                buckets["m_goals"] += x["amount"]
            else:
                buckets["m_invest"] += x["amount"]
        lump = {"lump_debt": 0.0, "lump_goals": 0.0, "lump_invest": 0.0}
        for x in rec["lump_sum_plan"]:
            if x["action"].startswith("prepay_debt"):
                lump["lump_debt"] += x["amount"]
            elif x["action"].startswith("fund_goal"):
                lump["lump_goals"] += x["amount"]
            else:
                lump["lump_invest"] += x["amount"]
        n_exp = sum(1 for ln in rec["debt_plan"] if ln["classification"] == "expensive")
        return {"id": rec["id"], "kind": rec["kind"], "status": rec["status"],
                "income": d.get("income"), "expense": d.get("expense"),
                "debt_payments": d.get("debt_payments"), "outflow": d.get("outflow"),
                "fcf": d.get("fcf"), "dsti": d.get("dsti"), "bliq": r2(p.bliq),
                "liq_months": d.get("liq_months"),
                "target_cushion_rub": d.get("target_cushion_rub"),
                "deployable_lump": d.get("deployable_lump"),
                "n_debts": d.get("n_debts"), "n_expensive": n_exp,
                "n_goals": d.get("n_goals"),
                **{k: r2(v) for k, v in buckets.items()},
                **{k: r2(v) for k, v in lump.items()},
                "flags": ";".join(rec["flags"])}


def main() -> None:
    runner = Runner("/mnt/user-data/uploads/portraits_12000.jsonl",
                    "/home/claude/finpilot_eval")
    controls = runner.run()
    with open("/home/claude/finpilot_eval/controls.json", "w") as f:
        json.dump(controls, f, ensure_ascii=False, indent=2)
    print(json.dumps(controls, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
