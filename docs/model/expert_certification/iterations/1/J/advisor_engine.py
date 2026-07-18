"""Expert financial advisory engine for 12,000 client portraits.

Methodology (classic personal-finance triage, adapted to the schema):
  1. Diagnostics: free cash flow, debt-service ratio, liquidity runway.
  2. Debt strategy: each loan rate vs personal benchmark r_bench (avalanche).
  3. Lump-sum plan: deploy excess liquidity above the buffer target.
  4. Monthly waterfall: buffer -> expensive debt -> deadline goals -> portfolio.
  5. Survival mode for zero-income / negative-cash-flow profiles.
"""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

REF_DATE = date(2026, 7, 7)
SPREAD = 0.02                      # prepay only if rate > r_bench + spread
BUFFER_MONTHS = {1: 6.0, 2: 6.0, 3: 4.0, 4: 3.0, 5: 3.0}
EQUITY_SHARE = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8}
DSR_HIGH = 0.5
DSR_CRITICAL = 0.8
URGENT_HORIZON_M = 12.0
MID_HORIZON_M = 36.0


@dataclass
class Obligation:
    id: int
    name: str
    amount: float
    interest_rate: float
    monthly_payment: float
    category: str = ""             # expensive | neutral | cheap


@dataclass
class Goal:
    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[date]
    months_left: Optional[float] = None
    gap: float = 0.0
    required_monthly: Optional[float] = None
    overdue: bool = False


@dataclass
class Portrait:
    pid: str
    kind: str
    income: float
    expenses: float
    bliq: float
    r_bench: float
    risk: int
    l_min: float
    obligations: list[Obligation]
    goals: list[Goal]


@dataclass
class Advice:
    portrait: Portrait
    status: str = ""
    flags: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    debt_plan: list[dict[str, Any]] = field(default_factory=list)
    lump_plan: list[dict[str, Any]] = field(default_factory=list)
    monthly_plan: list[dict[str, Any]] = field(default_factory=list)
    goal_plan: list[dict[str, Any]] = field(default_factory=list)
    verdict: str = ""


class AdvisorEngine:
    """Turns one Portrait into one Advice via a deterministic expert rule set."""

    def advise(self, p: Portrait) -> Advice:
        a = Advice(portrait=p)
        self._diagnose(p, a)
        self._classify_debts(p, a)
        if a.diagnostics["survival_mode"] and self._deleverage_from_reserves(p, a):
            self._diagnose(p, a)                       # regime may have flipped
        if a.diagnostics["survival_mode"]:
            self._survival_plan(p, a)
        else:
            self._lump_sum_plan(p, a)
            self._monthly_waterfall(p, a)
        self._goal_feasibility(p, a)
        self._verdict(p, a)
        return a

    # -- step 1: diagnostics -------------------------------------------------
    _DIAG_FLAGS = {"zero_expenses_anomaly", "zero_income", "cash_flow_deficit",
                   "dsr_critical", "dsr_high", "buffer_below_1m",
                   "overfunded_goals_release"}

    def _diagnose(self, p: Portrait, a: Advice) -> None:
        a.flags = [f for f in a.flags if f not in self._DIAG_FLAGS]
        payments = sum(o.monthly_payment for o in p.obligations)
        outflow = p.expenses + payments
        fcf = p.income - outflow
        dsr = payments / p.income if p.income > 0 else (None if payments == 0 else float("inf"))
        liq_months = p.bliq / outflow if outflow > 0 else float("inf")
        buffer_target = max(p.l_min, BUFFER_MONTHS[p.risk] * outflow)
        release = sum(max(0.0, g.current_amount - g.target_amount) for g in p.goals)
        survival = p.income <= 0 or fcf < 0

        if p.expenses <= 0:
            a.flags.append("zero_expenses_anomaly")
        if p.income <= 0:
            a.flags.append("zero_income")
        if fcf < 0 and p.income > 0:
            a.flags.append("cash_flow_deficit")
        if dsr is not None and dsr != float("inf"):
            if dsr >= DSR_CRITICAL:
                a.flags.append("dsr_critical")
            elif dsr >= DSR_HIGH:
                a.flags.append("dsr_high")
        if liq_months != float("inf") and liq_months < 1:
            a.flags.append("buffer_below_1m")
        if release > 0:
            a.flags.append("overfunded_goals_release")

        a.diagnostics = {
            "payments": round(payments, 2),
            "outflow": round(outflow, 2),
            "fcf": round(fcf, 2),
            "dsr": None if dsr is None else (round(dsr, 4) if dsr != float("inf") else "inf"),
            "liquidity_months": round(liq_months, 1) if liq_months != float("inf") else "inf",
            "buffer_target_rub": round(buffer_target, 2),
            "buffer_gap": round(max(0.0, buffer_target - p.bliq), 2),
            "goal_overfund_release": round(release, 2),
            "survival_mode": survival,
        }

    # -- step 2: debt classification ------------------------------------------
    def _classify_debts(self, p: Portrait, a: Advice) -> None:
        for o in sorted(p.obligations, key=lambda x: -x.interest_rate):
            if o.interest_rate > p.r_bench + SPREAD:
                o.category = "expensive"
                action = "досрочное гашение (лавина: сначала эта ставка)"
            elif o.interest_rate < p.r_bench:
                o.category = "cheap"
                action = "платить по графику, разницу инвестировать под r_bench (арбитраж ставок)"
            else:
                o.category = "expensive" if p.risk <= 3 else "cheap"
                action = ("гасить досрочно (гарантированная доходность при низком риск-профиле)"
                          if o.category == "expensive"
                          else "платить по графику, свободное — в рынок")
            a.debt_plan.append({
                "loan": o.name, "balance": round(o.amount, 2),
                "rate": o.interest_rate, "vs_r_bench": round(o.interest_rate - p.r_bench, 4),
                "category": o.category, "action": action,
            })

    # -- step 3: lump-sum deployment ------------------------------------------
    def _lump_sum_plan(self, p: Portrait, a: Advice) -> None:
        deployable = max(0.0, p.bliq - a.diagnostics["buffer_target_rub"])
        deployable += a.diagnostics["goal_overfund_release"]
        a.diagnostics["deployable_lump"] = round(deployable, 2)
        if deployable <= 0:
            return
        rest = deployable
        for o in sorted((o for o in p.obligations if o.category == "expensive"),
                        key=lambda x: -x.interest_rate):
            if rest <= 0:
                break
            pay = min(rest, o.amount)
            a.lump_plan.append({"action": "prepay_debt", "target": o.name,
                                "amount": round(pay, 2), "rate": o.interest_rate})
            rest -= pay
        urgent = [g for g in p.goals
                  if g.months_left is not None and g.months_left <= URGENT_HORIZON_M and g.gap > 0]
        for g in sorted(urgent, key=lambda x: x.months_left):
            if rest <= 0:
                break
            put = min(rest, g.gap)
            a.lump_plan.append({"action": "fund_urgent_goal", "target": g.name,
                                "amount": round(put, 2), "deadline": str(g.deadline)})
            g.gap -= put
            rest -= put
        if rest > 0:
            eq = EQUITY_SHARE[p.risk]
            a.lump_plan.append({
                "action": "invest_lump", "amount": round(rest, 2),
                "allocation": {"акции/фонды": round(rest * eq, 2),
                               "облигации/вклады": round(rest * (1 - eq), 2)},
            })

    # -- step 4: monthly waterfall ---------------------------------------------
    def _monthly_waterfall(self, p: Portrait, a: Advice) -> None:
        fcf = max(0.0, a.diagnostics["fcf"])
        a.diagnostics["monthly_free"] = round(fcf, 2)
        if fcf <= 0:
            return
        rest = fcf

        gap = a.diagnostics["buffer_gap"]
        if gap > 0 and rest > 0:
            contrib = rest
            a.monthly_plan.append({
                "bucket": "1_buffer", "amount": round(contrib, 2),
                "instrument": "накопительный счёт",
                "note": f"до цели {a.diagnostics['buffer_target_rub']:.0f} ₽, "
                        f"~{gap / contrib:.1f} мес. заполнения",
            })
            rest = 0.0

        exp_after_lump = self._expensive_balance_after_lump(p, a)
        if exp_after_lump > 0 and rest > 0:
            a.monthly_plan.append({
                "bucket": "2_debt_prepay", "amount": round(rest, 2),
                "instrument": "досрочное гашение (макс. ставка первой)",
                "note": f"остаток дорогого долга после lump: {exp_after_lump:.0f} ₽, "
                        f"~{exp_after_lump / rest:.1f} мес. до закрытия",
            })
            rest = 0.0

        if rest > 0:
            for g in sorted((g for g in p.goals if g.required_monthly and g.gap > 0),
                            key=lambda x: x.months_left):
                if rest <= 0:
                    break
                put = min(rest, g.required_monthly)
                a.monthly_plan.append({
                    "bucket": "3_goal", "goal": g.name, "amount": round(put, 2),
                    "instrument": self._instrument_for_horizon(g.months_left, p.risk),
                    "note": f"дедлайн {g.deadline}, требуется {g.required_monthly:.0f} ₽/мес",
                })
                rest -= put

        if rest > 0:
            eq = EQUITY_SHARE[p.risk]
            a.monthly_plan.append({
                "bucket": "4_invest", "amount": round(rest, 2),
                "instrument": f"портфель: {eq:.0%} акции / {1 - eq:.0%} облигации+вклады",
                "note": "долгосрок и цели без дедлайна",
            })

    def _expensive_balance_after_lump(self, p: Portrait, a: Advice) -> float:
        total = sum(o.amount for o in p.obligations if o.category == "expensive")
        prepaid = sum(x["amount"] for x in a.lump_plan if x["action"] == "prepay_debt")
        return max(0.0, total - prepaid)

    @staticmethod
    def _instrument_for_horizon(months: Optional[float], risk: int) -> str:
        if months is None or months > MID_HORIZON_M:
            eq = EQUITY_SHARE[risk]
            return f"портфель {eq:.0%}/{1 - eq:.0%}"
        if months > URGENT_HORIZON_M:
            return "вклад / ОФЗ до дедлайна"
        return "накопительный счёт (без рыночного риска)"

    # -- crisis deleveraging -------------------------------------------------------
    def _deleverage_from_reserves(self, p: Portrait, a: Advice) -> bool:
        """Close loans from bliq when it repairs the cash flow / extends runway.

        Criterion for zero income: payment/balance > 1/runway (each ruble spent
        extends survival). With income > 0 any affordable closure raises fcf,
        so close by flow relief per ruble until fcf >= 0. Floor: keep 2 months
        of living expenses (or 1 month of outflow when expenses are zero).
        """
        if not p.obligations:
            return False
        floor = 2 * p.expenses if p.expenses > 0 else sum(
            o.monthly_payment for o in p.obligations)
        actions = []
        deficit0 = -(p.income - p.expenses
                     - sum(o.monthly_payment for o in p.obligations))
        excess0 = p.bliq - floor
        if p.income > 0 and 0 < deficit0 and excess0 > 0:
            rem, spend_total, plan = deficit0, 0.0, []
            for o in sorted(p.obligations,
                            key=lambda x: -x.monthly_payment / x.amount):
                ratio = o.monthly_payment / o.amount
                relief = min(o.monthly_payment, rem)
                spend = relief / ratio
                plan.append((o, spend, relief))
                spend_total += spend
                rem -= relief
                if rem <= 1e-6:
                    break
            if rem <= 1e-6 and spend_total <= excess0:      # full repair feasible
                for o, spend, relief in plan:
                    full = spend >= o.amount - 0.01
                    p.bliq -= spend
                    actions.append({
                        "action": ("prepay_close_loan_crisis" if full
                                   else "prepay_partial_crisis"),
                        "target": o.name, "amount": round(spend, 2),
                        "rate": o.interest_rate,
                        "flow_relief_monthly": round(relief, 2),
                        "note": ("кредит закрыт из резерва — поток восстановлен" if full
                                 else "частичное досрочное с пересчётом платежа"),
                    })
                    if full:
                        p.obligations = [x for x in p.obligations if x.id != o.id]
                    else:
                        o.amount -= spend
                        o.monthly_payment -= relief
        while True:
            deficit = -(p.income - p.expenses
                        - sum(o.monthly_payment for o in p.obligations))
            excess = p.bliq - floor
            if deficit <= 0 or excess <= 0:
                break
            runway = p.bliq / deficit
            cands = [o for o in p.obligations
                     if o.amount > 0 and o.monthly_payment / o.amount > 1.0 / runway]
            if not cands:
                break
            o = max(cands, key=lambda x: x.monthly_payment / x.amount)
            ratio = o.monthly_payment / o.amount
            spend_to_fix = deficit / ratio            # exact prepay to reach fcf = 0
            spend = min(excess, o.amount, spend_to_fix)
            relief = spend * ratio
            full = spend >= o.amount - 0.01
            p.bliq -= spend
            actions.append({
                "action": "prepay_close_loan_crisis" if full else "prepay_partial_crisis",
                "target": o.name, "amount": round(spend, 2), "rate": o.interest_rate,
                "flow_relief_monthly": round(relief, 2),
                "note": ("кредит закрыт из резерва — ремонт денежного потока" if full
                         else "частичное досрочное с пересчётом платежа"),
            })
            if full:
                p.obligations = [x for x in p.obligations if x.id != o.id]
            else:
                o.amount -= spend
                o.monthly_payment -= relief
        if not actions:
            return False
        a.lump_plan.extend(actions)
        a.flags.append("deleveraged_from_reserves")
        a.debt_plan = [x for x in a.debt_plan
                       if x["loan"] in {o.name for o in p.obligations}]
        return True

    # -- survival mode -----------------------------------------------------------
    def _survival_plan(self, p: Portrait, a: Advice) -> None:
        d = a.diagnostics
        d["deployable_lump"] = 0.0
        d["monthly_free"] = 0.0
        reserve2 = sum(g.current_amount for g in p.goals)
        runway_base = p.bliq
        runway_full = p.bliq + reserve2
        outflow = d["outflow"]
        d["runway_months"] = round(runway_base / outflow, 1) if outflow > 0 else "inf"
        d["runway_with_goal_funds"] = round(runway_full / outflow, 1) if outflow > 0 else "inf"

        a.monthly_plan.append({
            "bucket": "0_survival", "amount": 0,
            "instrument": "вся ликвидность — накопительный счёт/короткий вклад",
            "note": "никаких рыночных инструментов и досрочных гашений до восстановления дохода",
        })
        if p.income <= 0:
            a.monthly_plan.append({
                "bucket": "0_survival", "amount": 0, "instrument": "-",
                "note": f"восстановить доход; запас хода {d['runway_months']} мес. "
                        f"(с накоплениями целей — {d['runway_with_goal_funds']})",
            })
        else:
            cut = -a.diagnostics["fcf"]
            a.monthly_plan.append({
                "bucket": "0_survival", "amount": round(cut, 2), "instrument": "-",
                "note": f"сократить расходы минимум на {cut:.0f} ₽/мес до безубыточности",
            })
        if any(o.category == "expensive" for o in p.obligations):
            a.monthly_plan.append({
                "bucket": "0_survival", "amount": 0,
                "instrument": "рефинансирование/реструктуризация",
                "note": "дорогие кредиты при отрицательном потоке — приоритет переговоров с банком",
            })
        a.flags.append("survival_mode")

    # -- goal feasibility ---------------------------------------------------------
    def _goal_feasibility(self, p: Portrait, a: Advice) -> None:
        stage3_budget = 0.0 if a.diagnostics["survival_mode"] else max(0.0, a.diagnostics["fcf"])
        required_total = sum(g.required_monthly or 0.0 for g in p.goals if g.gap > 0)
        for g in p.goals:
            entry: dict[str, Any] = {
                "goal": g.name,
                "target": round(g.target_amount, 2),
                "saved": round(g.current_amount, 2),
                "gap": round(max(0.0, g.gap), 2),
                "deadline": str(g.deadline) if g.deadline else None,
            }
            if g.gap <= 0:
                entry["status"] = "funded"
                entry["note"] = "цель закрыта; излишек высвобожден в общий план"
            elif g.overdue:
                entry["status"] = "overdue"
                entry["note"] = "дедлайн прошёл — пересогласовать срок или закрыть из lump"
            elif g.required_monthly is None:
                entry["status"] = "open_ended"
                entry["note"] = "без дедлайна — финансируется из бакета 4_invest"
            else:
                entry["required_monthly"] = round(g.required_monthly, 2)
                feasible = required_total <= stage3_budget + 1e-9
                entry["status"] = "on_track" if feasible else "at_risk"
                if not feasible and stage3_budget > 0:
                    months_needed = g.gap / (stage3_budget * (g.required_monthly / required_total))
                    entry["note"] = (f"совокупно цели требуют {required_total:.0f} ₽/мес при потоке "
                                     f"{stage3_budget:.0f} ₽; реалистичный срок ~{months_needed:.0f} мес")
                elif not feasible:
                    entry["note"] = "нет свободного потока — цель заморожена до стабилизации"
            a.goal_plan.append(entry)
        if any(e["status"] == "at_risk" for e in a.goal_plan):
            a.flags.append("goals_underfunded")

    # -- verdict --------------------------------------------------------------------
    def _verdict(self, p: Portrait, a: Advice) -> None:
        d = a.diagnostics
        runway = d.get("runway_months")
        if d["survival_mode"]:
            r = runway if isinstance(runway, (int, float)) else 999
            a.status = "CRITICAL" if r < 3 else ("ALERT" if r < 12 else "WATCH")
        elif "dsr_critical" in a.flags:
            a.status = "CRITICAL"
        elif "dsr_high" in a.flags or "buffer_below_1m" in a.flags:
            a.status = "ALERT"
        elif d["buffer_gap"] > 0 or any(o.category == "expensive" for o in p.obligations):
            a.status = "BUILDING"
        else:
            a.status = "STRONG"
        a.verdict = self._verdict_text(p, a)

    def _verdict_text(self, p: Portrait, a: Advice) -> str:
        d = a.diagnostics
        if d["survival_mode"]:
            base = ("Доход отсутствует" if p.income <= 0 else
                    f"Дефицит {-d['fcf']:.0f} ₽/мес")
            return (f"{base}; запас хода {d.get('runway_months')} мес. Режим сохранения "
                    f"ликвидности: всё в накопительный счёт, расходы вниз, инвестиции на паузу.")
        parts = []
        if d["buffer_gap"] > 0:
            parts.append(f"добрать подушку {d['buffer_gap']:.0f} ₽")
        exp = [x for x in a.debt_plan if x["category"] == "expensive"]
        if exp:
            parts.append(f"гасить дорогой долг ({len(exp)} шт., до {max(x['rate'] for x in exp):.0%})")
        cheap = [x for x in a.debt_plan if x["category"] == "cheap"]
        if cheap and not exp:
            parts.append("кредиты дешевле бенчмарка — не гасить досрочно, работать на арбитраже")
        if d.get("deployable_lump", 0) > 0:
            parts.append(f"развернуть излишек ликвидности {d['deployable_lump']:.0f} ₽")
        if d.get("monthly_free", 0) > 0:
            parts.append(f"поток {d['monthly_free']:.0f} ₽/мес по waterfall")
        return "; ".join(parts).capitalize() + "." if parts else "Профиль сбалансирован — поддерживать текущую структуру."


# -- IO -------------------------------------------------------------------------
def load_portraits(path: str) -> list[Portrait]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line)
            e = raw["engine"]
            goals = []
            for g in e["goals"]:
                dl = datetime.strptime(g["deadline"], "%Y-%m-%d").date() if g["deadline"] else None
                goal = Goal(g["id"], g["name"], g["target_amount"], g["current_amount"], dl)
                goal.gap = max(0.0, goal.target_amount - goal.current_amount)
                if dl:
                    m = (dl - REF_DATE).days / 30.4375
                    goal.overdue = m <= 0 and goal.gap > 0
                    goal.months_left = max(1.0, m) if not goal.overdue else 1.0
                    goal.required_monthly = goal.gap / goal.months_left if goal.gap > 0 else None
                goals.append(goal)
            obs = [Obligation(o["id"], o["name"], o["amount"], o["interest_rate"], o["monthly_payment"])
                   for o in e["obligations"]]
            out.append(Portrait(raw["id"], raw["kind"], e["income_total"], e["expense_total"],
                                e["bliq"], e["r_bench"], e["risk_tolerance"], e["l_min"], obs, goals))
    return out


def advice_to_dict(a: Advice) -> dict[str, Any]:
    return {
        "id": a.portrait.pid, "kind": a.portrait.kind, "status": a.status,
        "flags": a.flags, "diagnostics": a.diagnostics, "debt_plan": a.debt_plan,
        "lump_sum_plan": a.lump_plan, "monthly_plan": a.monthly_plan,
        "goal_plan": a.goal_plan, "verdict": a.verdict,
    }


def run(src: str, out_dir: str) -> list[Advice]:
    engine = AdvisorEngine()
    portraits = load_portraits(src)
    advices = [engine.advise(p) for p in portraits]

    with open(f"{out_dir}/recommendations_12000.jsonl", "w", encoding="utf-8") as f:
        for a in advices:
            f.write(json.dumps(advice_to_dict(a), ensure_ascii=False) + "\n")

    with open(f"{out_dir}/recommendations_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "status", "income", "expenses", "debt_payments", "fcf",
                    "dsr", "liq_months", "buffer_target", "buffer_gap", "deployable_lump",
                    "n_expensive_debts", "n_cheap_debts", "monthly_to_buffer",
                    "monthly_to_debt", "monthly_to_goals", "monthly_to_invest", "flags"])
        for a in advices:
            d, p = a.diagnostics, a.portrait
            def bucket(prefix: str) -> float:
                return round(sum(x["amount"] for x in a.monthly_plan
                                 if x["bucket"].startswith(prefix)), 2)
            w.writerow([p.pid, p.kind, a.status, round(p.income, 2), round(p.expenses, 2),
                        d["payments"], d["fcf"], d["dsr"], d["liquidity_months"],
                        d["buffer_target_rub"], d["buffer_gap"], d.get("deployable_lump", 0),
                        sum(1 for o in p.obligations if o.category == "expensive"),
                        sum(1 for o in p.obligations if o.category == "cheap"),
                        bucket("1"), bucket("2"), bucket("3"), bucket("4"),
                        "|".join(a.flags)])
    return advices


if __name__ == "__main__":
    run("/mnt/user-data/uploads/portraits_12000.jsonl", "/mnt/user-data/outputs")
