"""
Формирование текстовой рекомендации и пояснения по выбранной альтернативе.
Метод — template-based NLG (Reiter & Dale, 2000): шаблоны + правила на показателях.
"""
from __future__ import annotations

from typing import Any


CATEGORY_LABELS = {
    "income_growth": "рост дохода",
    "safety": "безопасность",
    "material": "материальная цель",
    "emotional": "эмоциональная цель",
}


def build_recommendation_text(
    rt: float,
    lt: float,
    dt: float,
    has_active_goals: bool,
    expense_total: float,
    obligation_payments: float,
) -> str:
    """
    Базовая текстовая рекомендация по показателям финансового состояния.
    Выбирает шаблоны по правилам и подставляет расчётные значения.
    """
    parts = []

    if dt > 0.4:
        parts.append(
            f"Критично: долговая нагрузка {dt*100:.1f}% превышает порог 40%. "
            f"Требуется реструктуризация: рефинансирование дорогих кредитов или "
            f"снижение платежа за счёт увеличения срока (текущие платежи "
            f"{obligation_payments:,.0f} ₽/мес)."
        )
    elif dt > 0.2:
        parts.append(
            f"Долговая нагрузка {dt*100:.1f}% в пределах нормы, но приближается к "
            f"порогу. Новые кредитные обязательства брать не рекомендуется."
        )

    if lt < 0:
        parts.append(
            f"Свободный поток отрицательный (Lt = {lt:.2f}): расходы и обязательства "
            f"превышают доходы. Необходимо сократить переменные расходы или повысить доход."
        )
    elif lt < 0.1:
        parts.append(
            f"Ликвидность критически низкая (Lt = {lt:.2f}). Меньше 10% обязательной "
            f"нагрузки остаётся в свободном потоке."
        )

    if rt > 0:
        if has_active_goals:
            parts.append(
                f"Свободный поток +{rt:,.0f} ₽. Есть активные цели накопления — "
                f"распределение между погашением долга, резервом и целями выбирается "
                f"алгоритмом по профилю риска пользователя."
            )
        else:
            parts.append(
                f"Свободный поток +{rt:,.0f} ₽. Рекомендуется создать финансовую цель "
                f"(например, подушку безопасности на 3–6 месяцев расходов "
                f"= {expense_total * 3:,.0f}–{expense_total * 6:,.0f} ₽)."
            )
    elif rt < 0:
        parts.append(
            f"Дефицитный бюджет (Rt = {rt:,.0f} ₽). Алгоритм отклоняет распределение, "
            f"требуется структурный пересмотр расходов и обязательств."
        )

    if not parts:
        parts.append("Финансовое состояние стабильно. Все показатели в норме.")

    return " ".join(parts)


def explain_alternative(
    alt: dict[str, Any],
    rt: float,
    lt: float,
    dt: float,
    expense_total: float,
    obligation_payments: float,
    goals_total: float,
    risk_profile_label: str,
) -> dict[str, Any]:
    """
    Структурированное объяснение «почему именно эта альтернатива»:
        gains  — что улучшается (с указанием конкретных кредитов и целей)
        costs  — чем жертвуем
        insight — ключевой вывод
    """
    delta_rt = alt.get("Rt_new", rt) - rt
    delta_lt = alt.get("Lt_new", lt) - lt
    delta_dt = alt.get("Dt_new", dt) - dt

    x_obl = float(alt.get("x_obligations", 0))
    x_res = float(alt.get("x_reserve", 0))
    x_goals = float(alt.get("x_goals", 0))
    x_obl_eff = float(alt.get("x_obl_effective", x_obl))
    x_obl_unused = float(alt.get("x_obl_unused", 0))

    gains, costs, insight = [], [], []

    # ── Обязательства ─────────────────────────────────────────────────
    if x_obl_eff > 0:
        obl_lines = []
        for o in alt.get("obligation_allocation", []):
            if float(o.get("new_payment", 0)) < obligation_payments:  # затронут
                obl_lines.append(
                    f"{o.get('name', 'кредит')} (ставка {float(o.get('interest_rate', 0))*100:.1f}%)"
                )
        which = ", ".join(obl_lines) if obl_lines else "наиболее дорогим кредитам"
        gains.append(
            f"Досрочное погашение {x_obl_eff:,.0f} ₽ направлено по правилу Avalanche на "
            f"{which}. Долговая нагрузка: {dt*100:.1f}% → {alt['Dt_new']*100:.1f}% "
            f"({'−' if delta_dt < 0 else '+'}{abs(delta_dt)*100:.1f} п.п.)."
        )
    if x_obl_unused > 0:
        costs.append(
            f"Невозможно эффективно потратить {x_obl_unused:,.0f} ₽ на досрочку: все "
            f"кредиты имеют ставку ниже альтернативной доходности. Эта сумма возвращена в цели."
        )

    # ── Резерв ─────────────────────────────────────────────────────────
    if x_res > 0:
        months_cover = x_res / expense_total if expense_total > 0 else 0
        gains.append(
            f"В резервный фонд направлено {x_res:,.0f} ₽ "
            f"(≈ {months_cover:.1f} мес. расходов)."
        )

    # ── Цели ───────────────────────────────────────────────────────────
    goal_alloc = alt.get("goal_allocation", {}) or {}
    if goal_alloc and goals_total > 0:
        goal_lines = []
        for goal_id, amount in goal_alloc.items():
            if amount > 0:
                goal_lines.append(f"{amount:,.0f} ₽")
        total_to_goals = sum(float(v) for v in goal_alloc.values())
        if total_to_goals > 0:
            gains.append(
                f"На финансовые цели направлено {total_to_goals:,.0f} ₽, распределение "
                f"между целями выполнено пропорционально стратегической ценности и срочности."
            )

    # ── Изменение свободного потока ────────────────────────────────────
    if delta_rt > 0:
        gains.append(
            f"Свободный поток вырастет: {rt:,.0f} → {alt['Rt_new']:,.0f} ₽ "
            f"(+{delta_rt:,.0f} ₽/мес после уменьшения обязательных платежей)."
        )

    # ── Ключевой вывод ────────────────────────────────────────────────
    if alt.get("is_recommended"):
        insight.append(
            f"Наилучшая альтернатива для профиля «{risk_profile_label}»: "
            f"U(a) = {alt.get('utility', 0):.3f}."
        )

    if not gains:
        gains.append("Все средства остаются в распоряжении на следующий период.")

    return {
        "gains": gains,
        "costs": costs,
        "insight": " ".join(insight),
        "delta": {
            "Rt": round(delta_rt, 2),
            "Lt": round(delta_lt, 4),
            "Dt": round(delta_dt, 4),
        },
    }
