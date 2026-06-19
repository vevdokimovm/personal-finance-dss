"""
Совместимостный pipeline для эндпоинта /api/recommendation:
короткий путь — расчёт показателей + быстрая текстовая рекомендация,
без полного цикла планирования (для дашборда).
"""
from __future__ import annotations

from typing import Any, Union

from app.core.envelopes import apply_envelopes
from app.core.metrics import (
    calculate_blr,
    calculate_bt,
    calculate_cft,
    calculate_dt,
    calculate_expense_total,
    calculate_income_total,
    calculate_lt,
    calculate_rt,
    classify_blr,
    sum_liquid_assets,
    sum_obligation_payments,
)
from app.core.preprocessing import prepare_data
from app.core.recommendation import build_recommendation_text

Item = Union[dict[str, Any], Any]


def run_pipeline(
    transactions: list[Item],
    obligations: list[Item],
    goals: list[Item],
    liquid_assets: list[Item] | None = None,
) -> dict[str, Any]:
    # Конверты: цели берут накопление из привязанных активов, привязанные активы
    # исключаются из Bliq (подушки) — без двойного учёта на дашборде.
    goals, liquid_assets = apply_envelopes(goals, liquid_assets or [])
    prepared = prepare_data(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=liquid_assets,
    )

    income_total = calculate_income_total(prepared["transactions"])
    expense_total = calculate_expense_total(prepared["transactions"])
    cash_flow = calculate_cft(prepared["transactions"])
    obligation_payments = sum_obligation_payments(prepared["obligations"])
    bliq = sum_liquid_assets(prepared["liquid_assets"])
    bt = calculate_bt(prepared["active_goals"])

    rt = calculate_rt(cash_flow=cash_flow, obligation_payments=obligation_payments)
    lt = calculate_lt(rt=rt, expense_total=expense_total, obligation_payments=obligation_payments)
    dt = calculate_dt(obligation_payments=obligation_payments, income_total=income_total)
    blr = calculate_blr(balance=bt, liquid_assets=bliq, expense_total=expense_total)

    recommendation = build_recommendation_text(
        rt=rt,
        lt=lt,
        dt=dt,
        has_active_goals=bool(prepared["active_goals"]),
        expense_total=expense_total,
        obligation_payments=obligation_payments,
        liquid_savings=bliq,
        goals_accumulated=bt,
    )

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
            "Bliq": round(bliq, 2),
            "BLR": round(blr, 2),
            "BLR_status": classify_blr(blr),
        },
        "recommendation": recommendation,
        "input_summary": {
            "transactions_count": len(prepared["transactions"]),
            "obligations_count": len(prepared["obligations"]),
            "goals_count": len(prepared["goals"]),
            "active_goals_count": len(prepared["active_goals"]),
            "liquid_assets_count": len(prepared["liquid_assets"]),
        },
    }
