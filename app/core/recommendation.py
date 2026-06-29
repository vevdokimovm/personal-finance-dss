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
    liquid_savings: float = 0.0,
    goals_accumulated: float = 0.0,
) -> str:
    """
    Базовая текстовая рекомендация по финансовому состоянию —
    обычным языком, без формул и сокращений.

    lt здесь = месяцы автономии (stock-based ликвидность).
    """
    parts = []
    autonomy = lt  # месяцы жизни на ликвидной подушке без дохода

    # ── Долговая нагрузка ──────────────────────────────────────────────
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

    # ── Подушка безопасности (по месяцам автономии) ────────────────────
    if rt >= 0 and autonomy < 2.5:
        parts.append(
            f"Финансовая подушка пока тонкая — её хватит примерно на {autonomy:.1f} мес. "
            f"жизни без дохода. Безопасный минимум — 3 месяца расходов "
            f"(около {expense_total * 3:,.0f} ₽), поэтому в первую очередь стоит пополнять резерв."
        )

    # ── Свободный поток ────────────────────────────────────────────────
    if rt > 0:
        if has_active_goals:
            parts.append(
                f"После всех обязательных трат у вас остаётся {rt:,.0f} ₽ свободных денег. "
                f"У вас есть цели для накопления — как поделить эти деньги между досрочным "
                f"погашением кредитов, подушкой безопасности и целями, система подбирает "
                f"под ваш подход к риску."
            )
        elif autonomy >= 2.5:
            parts.append(
                f"После всех обязательных трат у вас остаётся {rt:,.0f} ₽ свободных денег, "
                f"а подушка уже на комфортном уровне. Можно направить свободные средства "
                f"на досрочное погашение дорогих кредитов или поставить цель для накопления."
            )
    elif rt < 0:
        deficit = abs(rt)
        savings = max(0.0, liquid_savings) + max(0.0, goals_accumulated)
        msg = (
            f"Бюджет в минусе: обязательные траты превышают доход на {deficit:,.0f} ₽ в месяц. "
        )
        if savings > 0 and deficit > 0:
            runway = int(savings // deficit)
            if runway >= 1:
                msg += (
                    f"Покрыть дефицит можно из накоплений — у вас {savings:,.0f} ₽ "
                    f"(подушка и ликвидные средства), этого хватит примерно на {runway} мес. "
                    f"Но это временный буфер: за это время нужно сократить расходы, "
                    f"увеличить доход или снизить нагрузку по кредитам, "
                    f"иначе накопления закончатся."
                )
            else:
                msg += (
                    f"Накоплений ({savings:,.0f} ₽) не хватит даже на месяц такого дефицита — "
                    f"ситуация требует срочного пересмотра расходов или рефинансирования кредитов."
                )
        else:
            msg += (
                "Свободных денег и накоплений для покрытия нет — нужно срочно пересмотреть "
                "расходы и кредиты."
            )
        parts.append(msg)

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
    alternatives_count: int = 0,
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
                rate_pct = float(o.get('interest_rate', 0)) * 100
                obl_lines.append(
                    f"«{o.get('name', 'кредит')}» (ставка {rate_pct:.0f}%)"
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

    # ── Главный вывод: конкретное распределение простым языком ────────
    # Ведём с фактическим (эффективным) сплитом в % и ₽ — так карточки
    # становятся понятными и отличаются друг от друга.
    goals_sum = sum(float(v) for v in (alt.get("goal_allocation", {}) or {}).values())
    eff_total = x_obl_eff + x_res + goals_sum

    def _pct(part: float) -> int:
        return round(part / eff_total * 100) if eff_total > 0 else 0

    split_parts: list[str] = []
    if x_obl_eff > 0:
        split_parts.append(f"{_pct(x_obl_eff)}% на досрочку кредитов ({x_obl_eff:,.0f} ₽)")
    if x_res > 0:
        split_parts.append(f"{_pct(x_res)}% в подушку безопасности ({x_res:,.0f} ₽)")
    if goals_sum > 0:
        split_parts.append(f"{_pct(goals_sum)}% на цели ({goals_sum:,.0f} ₽)")
    split_str = ", ".join(
        split_parts) if split_parts else "вся сумма остаётся свободной на следующий месяц"

    if alt.get("is_recommended"):
        compared = (
            f"система сравнила {alternatives_count} вариантов распределения "
            f"и этот набрал наивысшую оценку."
            if alternatives_count
            else "система сравнила все варианты распределения и этот набрал наивысшую оценку."
        )
        insight.append(
            f"Рекомендуем направить {split_str}. "
            f"Это оптимальный баланс для профиля «{risk_profile_label}»: {compared}"
        )
    else:
        insight.append(
            f"Здесь деньги идут так: {split_str}. "
            f"Это рабочий план, но его оценка ниже лучшего — для профиля "
            f"«{risk_profile_label}» такой перекос чуть менее выгоден."
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
