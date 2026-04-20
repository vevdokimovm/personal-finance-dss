from __future__ import annotations

from typing import Any, Union

from app.core.metrics import (
    calculate_cft,
    calculate_dt,
    calculate_expense_total,
    calculate_income_total,
    calculate_lt,
    calculate_rt,
    sum_obligation_payments,
)
from app.core.preprocessing import prepare_data


Item = Union[dict[str, Any], Any]


def _build_recommendation(
    rt: float,
    lt: float,
    dt: float,
    has_active_goals: bool,
    expense_total: float,
    obligation_payments: float,
) -> str:
    parts = []

    # Критическая зона — долги
    if dt > 0.4:
        parts.append(
            f"⚠ КРИТИЧНО: Долговая нагрузка составляет {dt*100:.1f}% от доходов "
            f"(порог безопасности — 40%). Рекомендуется провести реструктуризацию: "
            f"рефинансировать кредиты с наибольшей ставкой или увеличить срок погашения "
            f"для снижения ежемесячного платежа ({obligation_payments:,.0f} ₽)."
        )
    elif dt > 0.2:
        parts.append(
            f"Долговая нагрузка ({dt*100:.1f}%) в пределах нормы, "
            f"но приближается к пороговому значению (40%). Не рекомендуется "
            f"брать новые кредитные обязательства."
        )

    # Ликвидность (Lt = Rt / (Расходы + Обязательства), диапазон ВКР: 0.09–0.89)
    if lt < 0.1:
        parts.append(
            f"Ликвидность критически низкая (Lt = {lt:.2f}): свободный ресурс покрывает "
            f"менее 10% суммарной нагрузки. Необходимо сократить необязательные расходы "
            f"или найти дополнительные источники дохода."
        )
    elif lt < 0.3:
        parts.append(
            f"Ликвидность низкая (Lt = {lt:.2f}). Рекомендуется увеличить свободный "
            f"ресурс для формирования финансовой подушки безопасности."
        )

    # Свободный ресурс
    if rt > 0:
        if has_active_goals:
            suggested = round(rt * 0.3, 2)
            parts.append(
                f"Доступный ресурс +{rt:,.0f} ₽. У вас есть активные цели накопления — "
                f"рекомендуется направить ~30% ({suggested:,.0f} ₽) на их достижение, "
                f"а оставшуюся часть сохранить как резервный буфер."
            )
        else:
            parts.append(
                f"Доступный ресурс +{rt:,.0f} ₽. Рекомендуется создать финансовую цель "
                f"(например, подушка безопасности на 3‑6 месяцев расходов = "
                f"{expense_total * 3:,.0f}–{expense_total * 6:,.0f} ₽) "
                f"и начать систематические отчисления."
            )
    elif rt < 0:
        parts.append(
            f"Доступный ресурс отрицательный ({rt:,.0f} ₽): ваши расходы и обязательства "
            f"превышают доходы. Необходимо срочно пересмотреть бюджет."
        )

    if not parts:
        parts.append("Финансовое состояние стабильно. Все показатели в норме.")

    return " ".join(parts)


def _build_explanation(
    rt: float,
    lt: float,
    dt: float,
    has_active_goals: bool,
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    cash_flow: float,
) -> str:
    lines = []
    lines.append(f"Общий доход: {income_total:,.0f} ₽. Общие расходы: {expense_total:,.0f} ₽.")
    lines.append(f"Денежный поток (CFt = Доходы − Расходы): {cash_flow:,.0f} ₽.")

    if obligation_payments > 0:
        lines.append(f"Ежемесячные обязательства: {obligation_payments:,.0f} ₽.")

    lines.append(
        f"Rt = CFt − Обязательства = {cash_flow:,.0f} − {obligation_payments:,.0f} = {rt:,.0f} ₽ — "
        f"{'положительный, есть свободные средства' if rt >= 0 else 'отрицательный, дефицит бюджета'}."
    )
    lines.append(
        f"Lt = Rt / (Расходы + Обязательства) = {lt:.2f} — "
        f"{'достаточная' if lt >= 1.5 else 'низкая' if lt < 1 else 'пограничная'} ликвидность."
    )
    lines.append(
        f"Dt = Обязательства / Доходы = {dt*100:.1f}% — "
        f"{'опасный уровень (> 40%)' if dt > 0.4 else 'умеренный уровень (20–40%)' if dt > 0.2 else 'безопасный уровень (< 20%)'}."
    )

    return " ".join(lines)


def run_pipeline(
    transactions: list[Item],
    obligations: list[Item],
    goals: list[Item],
) -> dict[str, Any]:
    prepared_data = prepare_data(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
    )

    prepared_transactions = prepared_data["transactions"]
    prepared_obligations = prepared_data["obligations"]
    prepared_goals = prepared_data["goals"]
    active_goals = prepared_data["active_goals"]

    income_total = calculate_income_total(prepared_transactions)
    expense_total = calculate_expense_total(prepared_transactions)
    cash_flow = calculate_cft(prepared_transactions)
    obligation_payments = sum_obligation_payments(prepared_obligations)

    rt = calculate_rt(
        cash_flow=cash_flow,
        obligation_payments=obligation_payments,
    )
    total_expense_load = expense_total + obligation_payments
    lt = calculate_lt(
        available_resource=rt,
        total_expense_load=total_expense_load,
    )
    dt = calculate_dt(
        obligation_payments=obligation_payments,
        total_income=income_total,
    )

    recommendation = _build_recommendation(
        rt=rt,
        lt=lt,
        dt=dt,
        has_active_goals=bool(active_goals),
        expense_total=expense_total,
        obligation_payments=obligation_payments,
    )
    explanation = _build_explanation(
        rt=rt,
        lt=lt,
        dt=dt,
        has_active_goals=bool(active_goals),
        income_total=income_total,
        expense_total=expense_total,
        obligation_payments=obligation_payments,
        cash_flow=cash_flow,
    )

    return {
        "indicators": {
            "Rt": rt,
            "Lt": lt,
            "Dt": dt,
        },
        "recommendation": recommendation,
        "explanation": explanation,
        "input_summary": {
            "transactions_count": len(prepared_transactions),
            "obligations_count": len(prepared_obligations),
            "goals_count": len(prepared_goals),
            "active_goals_count": len(active_goals),
        },
    }
