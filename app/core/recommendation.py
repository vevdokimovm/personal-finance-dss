"""
Формирование текстовой рекомендации и пояснения по выбранной альтернативе.

Метод — template-based NLG (Reiter & Dale, 2000): шаблоны + правила на
показателях. Принцип FR-01/UX-02: на экран попадает только человеческий
язык — без формульной нотации (Rt, Lt, U(a), «форм. N», «п.п.»).
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
    Базовая текстовая рекомендация по финансовому состоянию —
    обычным языком, без формул и сокращений.
    """
    parts = []

    if dt > 0.4:
        parts.append(
            f"Тревожный сигнал: на платежи по кредитам уходит {dt*100:.0f}% дохода — "
            f"это больше безопасной границы в 40%. Стоит снизить нагрузку: "
            f"рефинансировать дорогие кредиты или уменьшить ежемесячный платёж, "
            f"растянув срок (сейчас на кредиты уходит {obligation_payments:,.0f} ₽ в месяц)."
        )
    elif dt > 0.2:
        parts.append(
            f"На кредиты уходит {dt*100:.0f}% дохода — пока в пределах нормы, но уже "
            f"близко к границе. Новые кредиты сейчас брать не стоит."
        )

    if lt < 0:
        parts.append(
            "Денег не хватает: расходы вместе с платежами по кредитам больше, чем "
            "доход. Нужно либо сократить необязательные траты, либо увеличить доход."
        )
    elif lt < 0.1:
        parts.append(
            "Почти весь доход съедают обязательные траты — свободным остаётся меньше "
            "десятой части. Финансовая подушка набирается очень медленно."
        )

    if rt > 0:
        if has_active_goals:
            parts.append(
                f"После всех обязательных трат у вас остаётся {rt:,.0f} ₽ свободных денег. "
                f"У вас есть цели для накопления — как поделить эти деньги между досрочным "
                f"погашением кредитов, подушкой безопасности и целями, система подбирает "
                f"под ваш подход к риску."
            )
        else:
            parts.append(
                f"После всех обязательных трат у вас остаётся {rt:,.0f} ₽ свободных денег. "
                f"Хороший момент завести подушку безопасности — запас на 3–6 месяцев жизни "
                f"(примерно {expense_total * 3:,.0f}–{expense_total * 6:,.0f} ₽ при ваших расходах)."
            )
    elif rt < 0:
        parts.append(
            f"Бюджет в минусе: обязательные траты превышают доход на {abs(rt):,.0f} ₽ в месяц. "
            f"Свободных денег для распределения нет — нужно пересмотреть расходы и кредиты."
        )

    if not parts:
        parts.append("Финансовое состояние стабильное — все показатели в норме.")

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
    Объяснение «почему именно этот план» обычным языком:
        gains   — что улучшается,
        costs   — чем приходится жертвовать,
        insight — главный вывод.
    Формат возврата стабилен (его читают фронтенд и снимок рекомендации).
    """
    delta_rt = alt.get("Rt_new", rt) - rt
    delta_lt = alt.get("Lt_new", lt) - lt
    delta_dt = alt.get("Dt_new", dt) - dt

    x_obl = float(alt.get("x_obligations", 0))
    x_res = float(alt.get("x_reserve", 0))
    x_obl_eff = float(alt.get("x_obl_effective", x_obl))
    x_obl_unused = float(alt.get("x_obl_unused", 0))

    gains: list[str] = []
    costs: list[str] = []
    insight: list[str] = []

    # ── Досрочное погашение кредитов ──────────────────────────────────
    if x_obl_eff > 0:
        obl_lines = []
        for o in alt.get("obligation_allocation", []):
            if float(o.get("new_payment", 0)) < obligation_payments:
                obl_lines.append(
                    f"«{o.get('name', 'кредит')}» (ставка {float(o.get('interest_rate', 0))*100:.0f}%)"
                )
        which = ", ".join(obl_lines) if obl_lines else "самый дорогой кредит"
        dt_now = dt * 100
        dt_new = alt.get("Dt_new", dt) * 100
        drop = abs(delta_dt) * 100
        gains.append(
            f"Досрочно гасим {x_obl_eff:,.0f} ₽ — в первую очередь {which}, "
            f"потому что чем дороже кредит, тем выгоднее его закрывать раньше. "
            f"Доля дохода, уходящая на кредиты, снижается с {dt_now:.0f}% до {dt_new:.0f}%."
            if drop >= 0.5 else
            f"Досрочно гасим {x_obl_eff:,.0f} ₽ — в первую очередь {which}, "
            f"потому что дорогие кредиты выгоднее закрывать раньше."
        )

    if x_obl_unused > 0:
        costs.append(
            f"{x_obl_unused:,.0f} ₽ не пошли на досрочное погашение: оставшиеся кредиты "
            f"дешёвые, и держать эти деньги на накопительном счёте выгоднее, чем гасить их "
            f"раньше срока. Поэтому сумма перенаправлена в ваши цели."
        )

    # ── Подушка безопасности (резерв) ─────────────────────────────────
    if x_res > 0:
        months_cover = x_res / expense_total if expense_total > 0 else 0
        gains.append(
            f"В подушку безопасности откладываем {x_res:,.0f} ₽ — это примерно "
            f"{months_cover:.1f} мес. ваших расходов в запасе на случай потери дохода."
        )

    # ── Цели ──────────────────────────────────────────────────────────
    goal_alloc = alt.get("goal_allocation", {}) or {}
    if goal_alloc and goals_total > 0:
        total_to_goals = sum(float(v) for v in goal_alloc.values())
        if total_to_goals > 0:
            gains.append(
                f"На ваши цели направляем {total_to_goals:,.0f} ₽ — деньги поделены между "
                f"целями по их важности и тому, насколько близок срок."
            )

    # ── Изменение свободных денег ─────────────────────────────────────
    if delta_rt > 0:
        gains.append(
            f"Свободных денег со временем станет больше: с {rt:,.0f} до "
            f"{alt.get('Rt_new', rt):,.0f} ₽ в месяц — потому что платежи по кредитам "
            f"уменьшатся."
        )

    # ── Главный вывод ─────────────────────────────────────────────────
    if alt.get("is_recommended"):
        insight.append(
            f"Это лучший вариант для вашего подхода к деньгам — «{risk_profile_label}». "
            f"Он точнее всего балансирует свободные деньги, запас прочности, "
            f"снижение долга и продвижение к целям именно так, как важно для этого профиля."
        )

    if not gains:
        gains.append("Все деньги остаются у вас в распоряжении на следующий месяц.")

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
