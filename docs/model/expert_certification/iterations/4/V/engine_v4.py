"""Independent expert engine, round 4.

Implements the methodology fixed in expert_methodology_v4.md before any
data processing. Deterministic, full-dataset, positional contract.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import re
from dataclasses import dataclass, field, replace
from datetime import date, datetime

CUTOFF = date(2026, 7, 18)
DAYS_PER_MONTH = 30.4375

TOP_KEYS = (
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
)
OB_KEYS = ("name", "amount", "interest_rate", "monthly_payment")
GOAL_KEYS = ("name", "target_amount", "current_amount")

ID_RE = re.compile(r'"id"\s*:\s*"(SP4-\d+)"')


@dataclass(frozen=True)
class Constants:
    """All expert constants, fixed before processing (sensitivity-ready)."""

    reserve_months: dict = field(
        default_factory=lambda: {1: 6.0, 2: 5.0, 3: 4.0, 4: 3.0, 5: 3.0})
    starter_months: float = 1.0
    exp_spread: float = 0.02
    toxic_rate: float = 0.45
    pdn_deleverage: float = 0.50
    pdn_elevated: float = 0.30
    debt_share: float = 0.70
    res_share_thin: float = 0.50
    res_share_thin_toxic: float = 0.20
    split_perp: float = 0.50
    min_lump: float = 10_000.0
    lump_floor_toxic_months: float = 1.0
    goal_close_horizon_m: float = 12.0
    excess_place_buffer_m: float = 1.0
    replan_months: float = 12.0


BASE = Constants()

EQUITY_SHARE = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8}


def _is_num(x: object) -> bool:
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))


def _parse_iso(s: str) -> date | None:
    if not isinstance(s, str) or len(s) != 10:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


class Validator:
    """Strict record validation per methodology section 3."""

    def check(self, rec: object) -> str | None:
        """Return defect description or None if the record is valid."""
        if not isinstance(rec, dict):
            return "record is not an object"
        for key in TOP_KEYS:
            if key not in rec:
                return f"missing key '{key}'"
        if not isinstance(rec["id"], str):
            return "id is not a string"
        for key in ("income_total", "expense_total", "bliq"):
            if not _is_num(rec[key]):
                return f"'{key}' is not a finite number"
            if rec[key] < 0:
                return f"'{key}' is negative"
        if not _is_num(rec["r_bench"]) or not 0 <= rec["r_bench"] < 1:
            return "'r_bench' is not a number in [0, 1)"
        rt = rec["risk_tolerance"]
        if not _is_num(rt) or rt != int(rt) or not 1 <= int(rt) <= 5:
            return "'risk_tolerance' is not an integer in 1..5"
        defect = self._check_obligations(rec["obligations"])
        if defect:
            return defect
        return self._check_goals(rec["goals"])

    def _check_obligations(self, obs: object) -> str | None:
        if not isinstance(obs, list):
            return "'obligations' is not a list"
        for i, ob in enumerate(obs):
            if not isinstance(ob, dict):
                return f"obligation #{i + 1} is not an object"
            for key in OB_KEYS:
                if key not in ob:
                    return f"obligation #{i + 1}: missing '{key}'"
            if not isinstance(ob["name"], str):
                return f"obligation #{i + 1}: 'name' is not a string"
            for key in ("amount", "monthly_payment"):
                if not _is_num(ob[key]) or ob[key] < 0:
                    return (f"obligation #{i + 1}: '{key}' is not a "
                            f"non-negative number")
            rate = ob["interest_rate"]
            if not _is_num(rate) or rate < 0:
                return (f"obligation #{i + 1}: 'interest_rate' is not a "
                        f"non-negative number")
            if rate > 3.0:
                return (f"obligation #{i + 1}: rate {rate:.4f} above 300%/yr "
                        f"(garbage per brief rule 2.2)")
        return None

    def _check_goals(self, goals: object) -> str | None:
        if not isinstance(goals, list):
            return "'goals' is not a list"
        for i, g in enumerate(goals):
            if not isinstance(g, dict):
                return f"goal #{i + 1} is not an object"
            for key in GOAL_KEYS:
                if key not in g:
                    return f"goal #{i + 1}: missing '{key}'"
            if "deadline" not in g:
                return f"goal #{i + 1}: 'deadline' key absent (rule 2.3)"
            if not isinstance(g["name"], str):
                return f"goal #{i + 1}: 'name' is not a string"
            for key in ("target_amount", "current_amount"):
                if not _is_num(g[key]) or g[key] < 0:
                    return (f"goal #{i + 1}: '{key}' is not a non-negative "
                            f"number")
            dl = g["deadline"]
            if dl is not None and _parse_iso(dl) is None:
                return f"goal #{i + 1}: 'deadline' is not a real ISO date"
        return None


class ExpertEngine:
    """Deterministic per-portrait decision engine."""

    def __init__(self, consts: Constants = BASE) -> None:
        self.c = consts
        self.validator = Validator()

    def process_line(self, raw: str) -> dict:
        try:
            rec = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            m = ID_RE.search(raw)
            return self._invalid(m.group(1) if m else "", "unparseable JSON")
        defect = self.validator.check(rec)
        if defect:
            rid = rec.get("id") if isinstance(rec, dict) else None
            rid = rid if isinstance(rid, str) else (
                ID_RE.search(raw).group(1) if ID_RE.search(raw) else "")
            return self._invalid(rid, defect)
        return self._decide(rec)

    @staticmethod
    def _invalid(rid: str, reason: str) -> dict:
        return {
            "id": rid, "status": "invalid", "dom": "none",
            "res": 0, "debt": 0, "goal": 0, "inv": 0, "lump": 0,
            "confidence": 5, "flags": ["invalid"], "invalid_reason": reason,
            "diagnostics": {}, "debt_plan": [], "lump_sum_plan": [],
            "monthly_plan": [], "goal_plan": [], "totals": {},
            "verdict": ("Запись дефектна и не читается как валидные "
                        f"финансовые данные ({reason}) — совет не выдаётся."),
        }

    # ------------------------------------------------------------------ core
    def _decide(self, rec: dict) -> dict:
        c = self.c
        income = float(rec["income_total"])
        expense = float(rec["expense_total"])
        obs = [dict(o) for o in rec["obligations"]]
        goals = [dict(g) for g in rec["goals"]]
        bliq = float(rec["bliq"])
        r_bench = float(rec["r_bench"])
        risk = int(rec["risk_tolerance"])

        payments = sum(o["monthly_payment"] for o in obs)
        fcf = income - expense - payments
        burn = expense + payments
        pdn = payments / income if income > 0 else (
            math.inf if payments > 0 else 0.0)
        liq_m = bliq / burn if burn > 0 else math.inf
        res_target_m = c.reserve_months[risk]
        res_target = res_target_m * burn

        flags: list[str] = []
        if income == 0:
            flags.append("zero_income")
        if expense == 0:
            flags.append("zero_expenses")
        if fcf < 0:
            flags.append("deficit")
        if fcf == 0:
            flags.append("zero_flow")
        if not obs:
            flags.append("no_debts")
        if not goals:
            flags.append("no_goals")
        if math.isinf(pdn):
            flags.append("pdn_undefined")
        elif pdn > c.pdn_deleverage:
            flags.append("pdn_critical")
        elif pdn > c.pdn_elevated:
            flags.append("pdn_elevated")
        if burn > 0 and liq_m < c.starter_months:
            flags.append("thin_liquidity")

        debt_plan = self._classify_debts(obs, r_bench)
        if any(d["class"] == "toxic" for d in debt_plan):
            flags.append("toxic_debt")
        if any(d["class"] == "expensive" for d in debt_plan):
            flags.append("expensive_debt")
        if obs and all(d["class"] == "cheap" for d in debt_plan):
            flags.append("cheap_debt_only")
        if any(d["interest_only"] for d in debt_plan):
            flags.append("interest_only")

        goal_states = self._goal_states(goals)
        if any(g["state"] == "overfunded" for g in goal_states):
            flags.append("overfunded_goal")
        if any(g["state"] == "funded" for g in goal_states):
            flags.append("goal_funded")
        if any(g["replan"] for g in goal_states):
            flags.append("replan_overdue_goal")

        lump_moves, bliq_after, ob_left = self._lump_plan(
            debt_plan, goal_states, bliq, burn, res_target, risk)
        lump_total = sum(m["amount"] for m in lump_moves)
        if any(m["kind"] == "place_excess" for m in lump_moves):
            flags.append("excess_liquidity")

        buckets, monthly_plan, goal_plan = self._monthly_plan(
            fcf, burn, bliq_after, res_target, ob_left, goal_states,
            pdn, risk)

        status = "ok" if fcf >= 0 else "deficit"
        dom = self._dominant(buckets)
        confidence = self._confidence(
            fcf, income, pdn, liq_m, res_target_m, debt_plan, goal_states,
            buckets, r_bench)
        verdict = self._verdict(status, flags, dom, debt_plan, goal_states,
                                liq_m, res_target_m, risk)

        diagnostics = {
            "fcf": round(fcf, 2), "pdn": None if math.isinf(pdn)
            else round(pdn, 4),
            "monthly_burn": round(burn, 2), "bliq": round(bliq, 2),
            "liquidity_months": None if math.isinf(liq_m)
            else round(liq_m, 2),
            "reserve_target_months": res_target_m,
            "reserve_target": round(res_target, 2),
            "r_bench": r_bench, "risk_tolerance": risk,
            "n_debts": len(obs), "debt_total": round(
                sum(o["amount"] for o in obs), 2),
            "n_goals": len(goals),
        }
        totals = {
            "monthly_allocated": sum(buckets.values()),
            "lump_total": int(lump_total),
            "bliq_after_lump": round(bliq_after, 2),
        }
        return {
            "id": rec["id"], "status": status, "dom": dom,
            "res": buckets["res"], "debt": buckets["debt"],
            "goal": buckets["goal"], "inv": buckets["inv"],
            "lump": int(lump_total), "confidence": confidence,
            "flags": flags, "diagnostics": diagnostics,
            "debt_plan": debt_plan, "lump_sum_plan": lump_moves,
            "monthly_plan": monthly_plan, "goal_plan": goal_plan,
            "totals": totals, "verdict": verdict,
        }

    # ------------------------------------------------------------- sub-plans
    def _classify_debts(self, obs: list[dict], r_bench: float) -> list[dict]:
        plan = []
        for ob in obs:
            rate = float(ob["interest_rate"])
            if rate >= self.c.toxic_rate:
                cls = "toxic"
            elif rate > r_bench + self.c.exp_spread:
                cls = "expensive"
            else:
                cls = "cheap"
            interest_only = (ob["monthly_payment"]
                             <= ob["amount"] * rate / 12 + 1e-9
                             and ob["amount"] > 0)
            action = {"toxic": "погасить в приоритете (лавина)",
                      "expensive": "гасить досрочно после подушки",
                      "cheap": "минимальные платежи, не гасить досрочно"}[cls]
            plan.append({
                "name": ob["name"], "amount": round(float(ob["amount"]), 2),
                "rate": rate, "monthly_payment": round(
                    float(ob["monthly_payment"]), 2),
                "class": cls, "interest_only": interest_only,
                "action": action,
            })
        return plan

    def _goal_states(self, goals: list[dict]) -> list[dict]:
        states = []
        for g in goals:
            target = float(g["target_amount"])
            current = float(g["current_amount"])
            dl = g["deadline"]
            dl_date = _parse_iso(dl) if dl else None
            remaining = target - current
            replan = False
            if remaining <= 0:
                state = "funded" if remaining == 0 else "overfunded"
                months = None
            elif dl_date is None:
                state, months = "perpetual", None
            else:
                days = (dl_date - CUTOFF).days
                if days <= 0:
                    state, months, replan = ("replan",
                                             self.c.replan_months, True)
                else:
                    state = "on_deadline"
                    months = max(1.0, math.ceil(days / DAYS_PER_MONTH))
            states.append({
                "name": g["name"], "target": round(target, 2),
                "current": round(current, 2),
                "remaining": round(max(0.0, remaining), 2),
                "surplus": round(max(0.0, -remaining), 2),
                "deadline": dl, "state": state, "months_left": months,
                "replan": replan,
            })
        return states

    def _lump_plan(self, debt_plan: list[dict], goal_states: list[dict],
                   bliq: float, burn: float, res_target: float,
                   risk: int) -> tuple[list[dict], float, list[dict]]:
        c = self.c
        moves: list[dict] = []
        bliq_rem = bliq
        ob_left = [dict(d) for d in debt_plan]

        floor_toxic = c.lump_floor_toxic_months * burn
        for ob in sorted((o for o in ob_left if o["class"] == "toxic"),
                         key=lambda o: -o["rate"]):
            avail = bliq_rem - floor_toxic
            pay = min(avail, ob["amount"])
            if pay >= c.min_lump and pay > 0:
                moves.append({"kind": "repay_debt", "target": ob["name"],
                              "rate": ob["rate"], "amount": int(pay),
                              "full": pay >= ob["amount"] - 0.005})
                bliq_rem -= pay
                ob["amount"] = round(ob["amount"] - pay, 2)

        for ob in sorted((o for o in ob_left
                          if o["class"] == "expensive" and o["amount"] > 0),
                         key=lambda o: -o["rate"]):
            avail = bliq_rem - res_target
            pay = min(avail, ob["amount"])
            if pay >= c.min_lump and pay > 0:
                moves.append({"kind": "repay_debt", "target": ob["name"],
                              "rate": ob["rate"], "amount": int(pay),
                              "full": pay >= ob["amount"] - 0.005})
                bliq_rem -= pay
                ob["amount"] = round(ob["amount"] - pay, 2)

        closable = [g for g in goal_states
                    if g["state"] in ("on_deadline", "replan")
                    and g["remaining"] > 0
                    and (g["months_left"] or 0) <= c.goal_close_horizon_m]
        for g in sorted(closable, key=lambda g: g["deadline"] or ""):
            avail = bliq_rem - res_target
            if g["remaining"] <= avail and g["remaining"] >= c.min_lump:
                moves.append({"kind": "close_goal", "target": g["name"],
                              "amount": int(g["remaining"]), "full": True})
                bliq_rem -= g["remaining"]
                g["closed_by_lump"] = True

        debts_alive = any(o["class"] in ("toxic", "expensive")
                          and o["amount"] > 0 for o in ob_left)
        excess = bliq_rem - (res_target + c.excess_place_buffer_m * burn)
        if not debts_alive and excess >= c.min_lump:
            moves.append({"kind": "place_excess", "target":
                          f"инвестиции (риск {risk})",
                          "amount": int(excess), "full": False})
            bliq_rem -= int(excess)

        return moves, bliq_rem, ob_left

    def _monthly_plan(self, fcf: float, burn: float, bliq_after: float,
                      res_target: float, ob_left: list[dict],
                      goal_states: list[dict], pdn: float, risk: int,
                      ) -> tuple[dict, list[dict], list[dict]]:
        c = self.c
        buckets = {"res": 0, "debt": 0, "goal": 0, "inv": 0}
        plan: list[dict] = []
        goal_plan = self._base_goal_plan(goal_states)
        if fcf <= 0:
            return buckets, plan, goal_plan

        budget = float(fcf)
        toxic_alive = any(o["class"] == "toxic" and o["amount"] > 0
                          for o in ob_left)
        exp_alive = any(o["class"] == "expensive" and o["amount"] > 0
                        for o in ob_left)
        any_debt_alive = any(o["amount"] > 0 for o in ob_left)
        liq_after_m = bliq_after / burn if burn > 0 else math.inf

        fres = fdebt = fgoal = finv = 0.0

        if liq_after_m < c.starter_months:
            share = (c.res_share_thin_toxic if toxic_alive
                     else c.res_share_thin)
            take = min(budget * share, max(0.0, res_target - bliq_after))
            fres += take
            budget -= take
            plan.append({"step": "starter_reserve", "amount": take})

        if toxic_alive:
            fdebt += budget
            plan.append({"step": "toxic_avalanche", "amount": budget})
            budget = 0.0
        elif exp_alive or (pdn > c.pdn_deleverage and any_debt_alive):
            take = budget * c.debt_share
            fdebt += take
            budget -= take
            step = ("expensive_avalanche" if exp_alive
                    else "pdn_deleverage")
            plan.append({"step": step, "amount": take})

        dl_goals = sorted(
            (g for g in goal_states
             if g["state"] in ("on_deadline", "replan")
             and g["remaining"] > 0 and not g.get("closed_by_lump")),
            key=lambda g: g["deadline"] or "")
        for g in dl_goals:
            if budget <= 0:
                break
            req = g["remaining"] / g["months_left"]
            take = min(req, budget)
            fgoal += take
            budget -= take
            g["monthly_alloc"] = take

        if budget > 0 and bliq_after + fres < res_target:
            fres += budget
            plan.append({"step": "reserve_topup", "amount": budget})
            budget = 0.0

        if budget > 0:
            perp = [g for g in goal_states if g["state"] == "perpetual"]
            if perp:
                gshare = budget * c.split_perp
                fgoal += gshare
                per_goal = gshare / len(perp)
                for g in perp:
                    g["monthly_alloc"] = per_goal
                finv += budget - gshare
                plan.append({"step": "perpetual_goals", "amount": gshare})
                plan.append({"step": "invest", "amount": budget - gshare})
            else:
                finv += budget
                plan.append({"step": "invest", "amount": budget})
            budget = 0.0

        buckets = self._round_buckets(fcf, fres, fdebt, fgoal, finv)
        goal_plan = self._base_goal_plan(goal_states)
        return buckets, plan, goal_plan

    @staticmethod
    def _round_buckets(fcf: float, fres: float, fdebt: float,
                       fgoal: float, finv: float) -> dict:
        cap = math.floor(max(0.0, fcf))
        b = {"res": math.floor(fres), "debt": math.floor(fdebt),
             "goal": math.floor(fgoal), "inv": math.floor(finv)}
        leftover = cap - sum(b.values())
        if leftover > 0 and sum(b.values()) > 0:
            top = max(b, key=lambda k: b[k])
            b[top] += leftover
        return b

    def _base_goal_plan(self, goal_states: list[dict]) -> list[dict]:
        plan = []
        for g in goal_states:
            alloc = g.get("monthly_alloc", 0.0)
            if g["state"] in ("funded", "overfunded"):
                achievable, note = True, (
                    "цель закрыта" + ("; излишек можно высвободить"
                                      if g["state"] == "overfunded" else ""))
            elif g.get("closed_by_lump"):
                achievable, note = True, "закрыта разовым ходом из накоплений"
            elif g["state"] == "perpetual":
                achievable, note = True, "бессрочная — пополняется из хвоста"
            else:
                months = g["months_left"]
                achievable = alloc * months + 1e-6 >= g["remaining"]
                note = ("укладывается в срок" if achievable else
                        "к дедлайну не успевает при текущем потоке — "
                        "сдвинуть срок или уменьшить сумму")
                if g["replan"]:
                    note = "дедлайн просрочен — перепланирована на 12 мес; " \
                           + note
            plan.append({
                "name": g["name"], "state": g["state"],
                "remaining": g["remaining"],
                "monthly_alloc": int(alloc),
                "months_left": g["months_left"],
                "achievable": achievable, "note": note,
            })
        return plan

    @staticmethod
    def _dominant(b: dict) -> str:
        goals_plus = b["goal"] + b["inv"]
        triples = [("debt", b["debt"]), ("reserve", b["res"]),
                   ("goals+", goals_plus)]
        best = max(triples, key=lambda t: t[1])
        return "none" if best[1] <= 0 else best[0]

    def _confidence(self, fcf: float, income: float, pdn: float,
                    liq_m: float, res_target_m: float,
                    debt_plan: list[dict], goal_states: list[dict],
                    buckets: dict, r_bench: float) -> int:
        c = self.c
        score = 5
        if abs(fcf) < 0.02 * max(income, 1.0):
            score -= 1
        if debt_plan and min(abs(d["rate"] - (r_bench + c.exp_spread))
                             for d in debt_plan) < 0.02:
            score -= 1
        if any(abs(d["rate"] - c.toxic_rate) < 0.05 for d in debt_plan):
            score -= 1
        if not math.isinf(liq_m) and abs(liq_m - res_target_m) < 0.5:
            score -= 1
        if not math.isinf(pdn) and abs(pdn - c.pdn_deleverage) < 0.03:
            score -= 1
        vals = sorted([buckets["debt"], buckets["res"],
                       buckets["goal"] + buckets["inv"]], reverse=True)
        if fcf > 0 and vals[0] > 0 and (vals[0] - vals[1]) < 0.10 * fcf:
            score -= 1
        near_dl = False
        for g in goal_states:
            if g["state"] == "replan":
                near_dl = True
            elif g["state"] == "on_deadline" and g["deadline"]:
                days = (_parse_iso(g["deadline"]) - CUTOFF).days
                if 0 <= days <= 60:
                    near_dl = True
        if near_dl:
            score -= 1
        return max(1, min(5, score))

    @staticmethod
    def _verdict(status: str, flags: list, dom: str, debt_plan: list,
                 goal_states: list, liq_m: float, res_target_m: float,
                 risk: int) -> str:
        if status == "deficit":
            base = ("Поток отрицательный — сначала резать расходы/"
                    "реструктурировать долги")
            if "toxic_debt" in flags:
                base += "; токсичный долг гасим из подушки немедленно"
            return base + "."
        parts = []
        if "toxic_debt" in flags:
            parts.append("приоритет — добить токсичный долг")
        elif "expensive_debt" in flags:
            parts.append("досрочно гасим дорогие кредиты лавиной")
        elif "pdn_critical" in flags:
            parts.append("ПДН критический — разгружаем долг")
        if not math.isinf(liq_m) and liq_m < res_target_m:
            parts.append(f"докапливаем подушку до {res_target_m:g} мес")
        if "excess_liquidity" in flags:
            parts.append("излишек подушки размещаем")
        if any(g["state"] in ("on_deadline", "replan") for g in goal_states):
            parts.append("цели ведём по дедлайнам")
        if not parts:
            parts.append(f"база здорова — копим и инвестируем по риску {risk}")
        return "Статус ок: " + ", ".join(parts) + "."


# ---------------------------------------------------------------------- runs
def read_lines(paths: list[str]) -> list[str]:
    lines = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.rstrip("\n")
                if i == 0 and '"__meta__"' in line:
                    continue
                if line.strip():
                    lines.append(line)
    return lines


def run(paths: list[str], consts: Constants = BASE) -> list[dict]:
    engine = ExpertEngine(consts)
    results = [engine.process_line(line) for line in read_lines(paths)]
    counts: dict[str, int] = {}
    for r in results:
        counts[r["id"]] = counts.get(r["id"], 0) + 1
    for r in results:
        if r["id"] and counts[r["id"]] > 1:
            r["flags"].append("dup_id")
    return results


def write_outputs(results: list[dict], out_dir: str) -> None:
    with open(f"{out_dir}/expert_allocations_v4.csv", "w",
              newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "status", "dom", "res", "debt", "goal", "inv",
                    "lump", "confidence"])
        for r in results:
            w.writerow([r["id"], r["status"], r["dom"], r["res"], r["debt"],
                        r["goal"], r["inv"], r["lump"], r["confidence"]])

    with open(f"{out_dir}/summary_v4.csv", "w", newline="\n",
              encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "status", "dom", "flags", "fcf", "pdn",
                    "monthly_burn", "bliq", "liquidity_months",
                    "reserve_target", "n_debts", "debt_total", "n_goals",
                    "res", "debt", "goal", "inv", "lump"])
        for r in results:
            d = r["diagnostics"]
            fmt = lambda v: ("" if v is None else f"{v:.2f}")  # noqa: E731
            w.writerow([
                r["id"], r["status"], r["dom"], ";".join(r["flags"]),
                fmt(d.get("fcf")), "" if d.get("pdn") is None
                else f"{d['pdn']:.4f}",
                fmt(d.get("monthly_burn")), fmt(d.get("bliq")),
                fmt(d.get("liquidity_months")), fmt(d.get("reserve_target")),
                d.get("n_debts", ""), fmt(d.get("debt_total")),
                d.get("n_goals", ""), r["res"], r["debt"], r["goal"],
                r["inv"], r["lump"]])

    with gzip.open(f"{out_dir}/recommendations_v4.jsonl.gz", "wt",
                   encoding="utf-8") as fh:
        for r in results:
            rec = {k: r[k] for k in (
                "id", "status", "dom", "flags", "diagnostics", "debt_plan",
                "lump_sum_plan", "monthly_plan", "goal_plan", "totals",
                "verdict")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def sensitivity_variants() -> dict[str, Constants]:
    v: dict[str, Constants] = {}
    v["exp_spread-20"] = replace(BASE, exp_spread=0.016)
    v["exp_spread+20"] = replace(BASE, exp_spread=0.024)
    v["toxic_rate-20"] = replace(BASE, toxic_rate=0.36)
    v["toxic_rate+20"] = replace(BASE, toxic_rate=0.54)
    v["reserve-20"] = replace(BASE, reserve_months={
        k: round(m * 0.8, 2) for k, m in BASE.reserve_months.items()})
    v["reserve+20"] = replace(BASE, reserve_months={
        k: round(m * 1.2, 2) for k, m in BASE.reserve_months.items()})
    v["min_lump-20"] = replace(BASE, min_lump=8_000.0)
    v["min_lump+20"] = replace(BASE, min_lump=12_000.0)
    v["pdn-20"] = replace(BASE, pdn_deleverage=0.40)
    v["pdn+20"] = replace(BASE, pdn_deleverage=0.60)
    return v


if __name__ == "__main__":
    import sys
    parts = [f"part{i}.jsonl.gz" for i in (1, 2, 3, 4)]
    res = run(parts)
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    write_outputs(res, out)
    n_inv = sum(r["status"] == "invalid" for r in res)
    n_def = sum(r["status"] == "deficit" for r in res)
    print(f"rows={len(res)} invalid={n_inv} deficit={n_def} "
          f"ok={len(res) - n_inv - n_def}")
