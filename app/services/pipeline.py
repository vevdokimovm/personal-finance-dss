from __future__ import annotations

from typing import Any

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


Item = dict[str, Any] | Any


def _build_recommendation(
    rt: float,
    lt: float,
    dt: float,
    has_active_goals: bool,
) -> str:
    if dt > 0.4:
        return "Рекомендуется снизить долговую нагрузку и пересмотреть обязательные платежи."
    if lt < 1:
        return "Рекомендуется повысить ликвидность и увеличить резерв доступных средств."
    if rt > 0 and has_active_goals:
        return "Рекомендуется направить часть доступного ресурса в накопления по активным целям."
    if rt > 0:
        return "Рекомендуется распределить доступные средства между текущими приоритетами."
    return "Финансовое состояние стабильно."


def _build_explanation(
    rt: float,
    lt: float,
    dt: float,
    has_active_goals: bool,
) -> str:
    if dt > 0.4:
        return f"Высокая долговая нагрузка (Dt={dt:.2f}) превышает допустимый уровень."
    if lt < 1:
        return f"Низкая ликвидность (Lt={lt:.2f}) показывает недостаточный запас для покрытия расходов."
    if rt > 0 and has_active_goals:
        return f"Положительный доступный ресурс (Rt={rt:.2f}) позволяет направить часть средств в накопления по активным целям."
    if rt > 0:
        return f"Положительный доступный ресурс (Rt={rt:.2f}) позволяет распределить свободные средства между текущими приоритетами."
    return "Текущие показатели находятся в допустимом диапазоне и не требуют срочного вмешательства."


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
    )
    explanation = _build_explanation(
        rt=rt,
        lt=lt,
        dt=dt,
        has_active_goals=bool(active_goals),
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
