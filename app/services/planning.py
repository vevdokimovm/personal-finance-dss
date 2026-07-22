"""
Оркестратор алгоритма СППР — полный pipeline планирования.

Композиция модулей из core/:
  1. preprocessing — нормализация входных данных
  2. metrics       — расчёт Rt, Lt, Dt, BLR, CFt, Bt
  3. goals_priority.preallocate_from_bliq — этап 4.0: разовое закрытие близких целей
  4. alternatives.generate_alternatives — этап 4: генерация 66 альтернатив (шаг 10%)
  5. alternatives.evaluate_alternative  — этап 4b: пересчёт показателей с Avalanche+Si
  6. filtering.filter_alternatives      — этап 5: фильтрация по Rt>=0 и ПДН<=0.40
  7. ranking.rank_alternatives          — этап 6: ранжирование SAW
  8. recommendation.explain_alternative — формирование объяснения для top-3
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.money import FLOW_EPS, money
from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.crisis import build_crisis_plan
from app.core.filtering import B_MIN, DT_MAX, L_MIN, filter_alternatives
from app.core.goals_priority import preallocate_from_bliq
from app.core.investment import annotate_investment_tranche
from app.core.surplus import build_surplus_plan
from app.core.metrics import (
    calculate_blr,
    calculate_bt,
    calculate_dt,
    calculate_lt,
    calculate_rt,
    classify_blr,
)
from app.core.ranking import (
    RISK_PROFILES,
    effective_floor_months,
    rank_alternatives,
)
from app.core.recommendation import explain_alternative
from app.utils.time import utcnow


def run_planning(
    income_total: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    bliq: float = 0.0,
    r_bench: float = 0.14,
    risk_tolerance: int = 3,
    l_min: float = L_MIN,
    today: datetime | None = None,
    step: float = 0.10,
    toxic_floor: bool = True,
) -> dict[str, Any]:
    """Полный цикл планирования СППР по ВКР (этапы 1–6)."""
    today = today or utcnow()
    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])

    # ── Базовые показатели (для отображения и фильтрации) ──────────────
    cash_flow = income_total - expense_total
    obligation_payments = sum(float(o.get("monthly_payment", 0)) for o in obligations)
    rt = calculate_rt(cash_flow=cash_flow, obligation_payments=obligation_payments)

    # ── Этап 4.0: предобработка ликвидной позиции ──────────────────────
    # Только при неотрицательном потоке (v3.1.0): в дефиците цели заморожены,
    # и подушка не тратится на разовое закрытие близких целей — она нужна
    # как запас хода и ресурс балансового хода кризисного модуля.
    is_deficit = rt < -FLOW_EPS  # R3-F1: полкопейки не делают кризис
    if not is_deficit:
        bliq_after, closed_goals, active_goals = preallocate_from_bliq(bliq, goals, today)
    else:
        bliq_after, closed_goals, active_goals = bliq, [], list(goals)

    lt = calculate_lt(liquid_reserve=bliq_after, expense_total=expense_total)
    dt = calculate_dt(obligation_payments=obligation_payments, income_total=income_total)
    bt = calculate_bt(goals)
    blr = calculate_blr(balance=bt, liquid_assets=bliq_after, expense_total=expense_total)

    # ── Кризисный модуль (v3.1.0, G2): план действий при Rt < 0 ────────
    crisis_plan = build_crisis_plan(
        income_total=income_total,
        expense_total=expense_total,
        obligations=obligations,
        goals=goals,
        bliq=bliq,
        today=today,
    ) if is_deficit else None

    # ── Слой запаса (v3.2.0, G4): разовые ходы из излишка сверх подушки ──
    # Только при неотрицательном потоке: в дефиците запасом распоряжается
    # кризисный модуль. Считается ПОСЛЕ этапа 4.0 (на остатке bliq_after).
    surplus_plan = build_surplus_plan(
        bliq=bliq_after,
        expense_total=expense_total,
        obligations=obligations,
        goals=active_goals,
        r_bench=r_bench,
        risk_tolerance=risk_tolerance,
        lt_target=float(profile["lt_target"]),
        today=today,
    ) if rt >= 0 else None

    # ── Этап 4: генерация альтернатив ──────────────────────────────────
    goals_total = sum(
        max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        for g in active_goals
    )
    alternatives = generate_alternatives(
        rt=max(rt, 0),  # R+_t = max(Rt, 0)
        obligation_payments=obligation_payments,
        goals_total=goals_total,
        step=step,  # §6.3: knob сетки (0.10 → 66; 0.05 → 231) для стенд-замера
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
            bliq=bliq_after,
            today=today,
        )

    # ── Этап 5: фильтрация ─────────────────────────────────────────────
    # dt_current (G3, v3.1.0): гейт «план не увеличивает ПДН» — пользователь
    # с перегруженным ПДН всё равно получает план, а не пустой экран.
    admissible, rejected = filter_alternatives(
        alternatives, b_min=B_MIN, l_min=l_min, dt_max=DT_MAX, dt_current=dt
    )

    # ── Ранжирование ───────────────────────────────────────────────────
    # G8 (стенд р.4): при токсичном долге стартовый запас ликвидности
    # сокращается — лавина по ставке 40-290% дороже страховки от сбоя дохода.
    floor_months = (effective_floor_months(obligations, r_bench)
                    if toxic_floor else None)
    ranked = rank_alternatives(admissible, risk_tolerance,
                               floor_months=floor_months)

    # ── Инвестиционный транш (v3.1.0, G5): терминальный сток резерва ────
    # Резервный поток сверх целевой подушки Lt* размечается как инвестиции
    # с инструментальной полкой по профилю (депозит / облигации / акции).
    for alt in ranked:
        annotate_investment_tranche(
            alt,
            bliq=bliq_after,
            expense_total=expense_total,
            lt_target=float(profile["lt_target"]),
            risk_tolerance=risk_tolerance,
        )

    # Дедупликация по ФАКТИЧЕСКОМУ распределению: если досрочка перенаправлена
    # в цели (кредиты дешевле бенчмарка), варианты, отличающиеся только долей
    # досрочки, дают одинаковый эффект. Оставляем по одному представителю на
    # уникальный эффективный сплит — чтобы топ-3 были реально разными планами.
    def _effective_signature(alt: dict) -> tuple[int, int, int]:
        x_obl_eff = round(float(alt.get("x_obl_effective", alt.get("x_obligations", 0))))
        # Эффективный резерв (номинальный + переток остатка целей, ADR-009): два
        # варианта с насыщенными целями, отличающиеся только номинальным сплитом
        # резерв/цели, дают одинаковый фактический план — дедупим по истинному эффекту.
        x_res = round(float(alt.get("x_reserve_effective", alt.get("x_reserve", 0))))
        goals_sum = round(sum(float(v) for v in (alt.get("goal_allocation", {}) or {}).values()))
        return (x_obl_eff, x_res, goals_sum)

    seen_signatures: set[tuple[int, int, int]] = set()
    distinct_ranked: list[dict] = []
    for alt in ranked:
        sig = _effective_signature(alt)
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        distinct_ranked.append(alt)

    # ── Top-3 с объяснениями ───────────────────────────────────────────
    top3 = []
    for alt in distinct_ranked[:3]:
        explanation = explain_alternative(
            alt=alt,
            rt=rt, lt=lt, dt=dt,
            expense_total=expense_total,
            obligation_payments=obligation_payments,
            goals_total=goals_total,
            risk_profile_label=profile["label"],
            alternatives_count=len(alternatives),
        )
        top3.append({**alt, "explanation": explanation})

    best = top3[0] if top3 else None

    return {
        "indicators": {
            "It": money(income_total),
            "Et": money(expense_total),
            "SigmaP": money(obligation_payments),
            "CFt": money(cash_flow),
            "Rt": money(rt),
            "Lt": round(lt, 4),
            "Dt": round(dt, 4),
            "Bt": money(bt),
            "Bliq": money(bliq_after),
            "BLR": money(blr),
            "BLR_status": classify_blr(blr),
            # Флаг перегруженного ПДН (v3.1.0): план выдаётся, но пользователю
            # показывается предупреждение + рекомендация рефинансирования.
            "Dt_alert": dt > DT_MAX,
        },
        "bliq_preallocation": {
            "closed_goals": [
                {
                    "id": g.get("id"),
                    "name": g.get("name", ""),
                    "amount": money(g.get("_remaining", 0)),
                }
                for g in closed_goals
            ],
            "bliq_used": money(bliq - bliq_after),
            "bliq_remaining": money(bliq_after),
        },
        "risk_profile": profile["label"],
        "weights": {
            "w_rt": profile["w_rt"],
            "w_lt": profile["w_lt"],
            "w_dt": profile["w_dt"],
            "w_goals": profile["w_goals"],
            "lt_target": profile["lt_target"],
        },
        "crisis_plan": crisis_plan,
        "surplus_plan": surplus_plan,
        "alternatives_total": len(alternatives),
        "admissible_count": len(admissible),
        "rejected_count": len(rejected),
        "top3": top3,
        "ranked": ranked,
        "rejected": rejected,
        "best": best,
    }
