"""
Оркестратор алгоритма СППР — полный pipeline планирования.

Композиция модулей из core/:
  1. preprocessing — нормализация входных данных
  2. metrics       — расчёт Rt, Lt, Dt, BLR, CFt, Bt
  3. goals_priority.preallocate_from_bliq — этап 4.0: разовое закрытие близких целей
  4. alternatives.generate_alternatives — этап 4: генерация 21 альтернативы
  5. alternatives.evaluate_alternative  — этап 4b: пересчёт показателей с Avalanche+Si
  6. filtering.filter_alternatives      — этап 5: фильтрация по B_min, Lcrit, Dmax
  7. ranking.rank_alternatives          — этап 6: ранжирование SAW
  8. recommendation.explain_alternative — формирование объяснения для top-3
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.filtering import B_MIN, DT_MAX, LT_CRIT, filter_alternatives
from app.core.goals_priority import preallocate_from_bliq
from app.core.metrics import (
    calculate_blr,
    calculate_bt,
    calculate_dt,
    calculate_lt,
    calculate_rt,
    classify_blr,
)
from app.core.ranking import RISK_PROFILES, rank_alternatives
from app.core.recommendation import explain_alternative


def run_planning(
    income_total: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    bliq: float = 0.0,
    r_bench: float = 0.14,
    risk_tolerance: int = 3,
    l_min: float = LT_CRIT,
    today: datetime | None = None,
) -> dict[str, Any]:
    """Полный цикл планирования СППР по ВКР (этапы 1–6)."""
    today = today or datetime.utcnow()
    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])

    # ── Этап 4.0: предобработка ликвидной позиции ──────────────────────
    bliq_after, closed_goals, active_goals = preallocate_from_bliq(bliq, goals, today)

    # ── Базовые показатели (для отображения и фильтрации) ──────────────
    cash_flow = income_total - expense_total
    obligation_payments = sum(float(o.get("monthly_payment", 0)) for o in obligations)
    rt = calculate_rt(cash_flow=cash_flow, obligation_payments=obligation_payments)
    lt = calculate_lt(rt=rt, expense_total=expense_total, obligation_payments=obligation_payments)
    dt = calculate_dt(obligation_payments=obligation_payments, income_total=income_total)
    bt = calculate_bt(goals)
    blr = calculate_blr(balance=bt, liquid_assets=bliq_after, expense_total=expense_total)

    # ── Этап 4: генерация альтернатив ──────────────────────────────────
    goals_total = sum(
        max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        for g in active_goals
    )
    alternatives = generate_alternatives(
        rt=max(rt, 0),  # R+_t = max(Rt, 0)
        obligation_payments=obligation_payments,
        goals_total=goals_total,
    )

    # ── Этап 4b: пересчёт показателей под каждую альтернативу ──────────
    for alt in alternatives:
        evaluate_alternative(
            alt,
            income_total=income_total,
            expense_total=expense_total,
            obligations=obligations,
            goals=active_goals,
            r_bench=r_bench,
            today=today,
        )

    # ── Этап 5: фильтрация ─────────────────────────────────────────────
    admissible, rejected = filter_alternatives(
        alternatives, b_min=B_MIN, lt_crit=l_min, dt_max=DT_MAX
    )

    # ── Этап 6: ранжирование ───────────────────────────────────────────
    ranked = rank_alternatives(admissible, risk_tolerance)

    # ── Top-3 с объяснениями ───────────────────────────────────────────
    top3 = []
    for alt in ranked[:3]:
        explanation = explain_alternative(
            alt=alt,
            rt=rt, lt=lt, dt=dt,
            expense_total=expense_total,
            obligation_payments=obligation_payments,
            goals_total=goals_total,
            risk_profile_label=profile["label"],
        )
        top3.append({**alt, "explanation": explanation})

    best = top3[0] if top3 else None

    return {
        "indicators": {
            "It": round(income_total, 2),
            "Et": round(expense_total, 2),
            "SigmaP": round(obligation_payments, 2),
            "CFt": round(cash_flow, 2),
            "Rt": round(rt, 2),
            "Lt": round(lt, 4),
            "Dt": round(dt, 4),
            "Bt": round(bt, 2),
            "Bliq": round(bliq_after, 2),
            "BLR": round(blr, 2),
            "BLR_status": classify_blr(blr),
        },
        "bliq_preallocation": {
            "closed_goals": [
                {
                    "id": g.get("id"),
                    "name": g.get("name", ""),
                    "amount": round(float(g.get("_remaining", 0)), 2),
                }
                for g in closed_goals
            ],
            "bliq_used": round(bliq - bliq_after, 2),
            "bliq_remaining": round(bliq_after, 2),
        },
        "risk_profile": profile["label"],
        "weights": {
            "w_rt": profile["w_rt"],
            "w_lt": profile["w_lt"],
            "w_dt": profile["w_dt"],
            "w_goals": profile["w_goals"],
        },
        "alternatives_total": len(alternatives),
        "admissible_count": len(admissible),
        "rejected_count": len(rejected),
        "top3": top3,
        "ranked": ranked,
        "rejected": rejected,
        "best": best,
    }
