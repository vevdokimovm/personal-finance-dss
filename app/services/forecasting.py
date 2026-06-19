"""
Оркестратор прогнозирования — собирает SES + Monte Carlo из core/forecast
с накоплением баланса месяц к месяцу.
"""
from __future__ import annotations

from typing import Optional

from app.core.forecast import (
    MC_SIMULATIONS,
    build_history_from_current,
    detect_trend,
    monte_carlo_intervals,
    ses_forecast,
)


def forecast_indicators(
    balance: float,
    rt: float,
    lt: float,
    dt: float,
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    horizon: int = 6,
    income_history: Optional[list] = None,
    expense_history: Optional[list] = None,
    obligation_history: Optional[list] = None,
    recurring_income: float = 0.0,
    recurring_expense: float = 0.0,
) -> dict:
    """
    Прогноз вектора состояния {Rt+h, Lt+h, Dt+h} на горизонт H.
    Bt+h накапливается: Bt+h = Bt+h-1 + (CF̂ − ΣP̂).

    recurring_income/expense — суммы по регулярным операциям (is_recurring). На SES
    они не влияют (математика модели неизменна), а отдаются как «стабильная база»:
    доля предсказуемого денежного потока показывает надёжность прогноза.
    """
    if income_history is None or len(income_history) < 2:
        income_history = build_history_from_current(income_total, seed=1)
    if expense_history is None or len(expense_history) < 2:
        expense_history = build_history_from_current(expense_total, seed=2)
    if obligation_history is None or len(obligation_history) < 2:
        obligation_history = build_history_from_current(obligation_payments, seed=3)

    income_forecast = ses_forecast(income_history, horizon=horizon)
    expense_forecast = ses_forecast(expense_history, horizon=horizon)
    obl_forecast = ses_forecast(obligation_history, horizon=horizon)

    forecast = []
    bt_running = balance
    for h in range(horizon):
        i_h, e_h, p_h = income_forecast[h], expense_forecast[h], obl_forecast[h]
        cf_h = i_h - e_h
        bt_running = bt_running + (cf_h - p_h)  # форм. 35: накопление баланса
        rt_h = bt_running + cf_h - p_h
        lt_h = bt_running / e_h if e_h > 0 else 0.0
        dt_h = p_h / i_h if i_h > 0 else 0.0
        forecast.append({
            "period": h + 1,
            "Bt": round(bt_running, 2),
            "income": round(i_h, 2),
            "expense": round(e_h, 2),
            "obligations": round(p_h, 2),
            "cash_flow": round(cf_h, 2),
            "Rt": round(rt_h, 2),
            "Lt": round(lt_h, 4),
            "Dt": round(dt_h, 4),
        })

    point_rt = [f["Rt"] for f in forecast]
    intervals = monte_carlo_intervals(point_rt, horizon=horizon)
    for i, ci in enumerate(intervals):
        forecast[i]["Rt_p10"] = ci["p10"]
        forecast[i]["Rt_p50"] = ci["p50"]
        forecast[i]["Rt_p90"] = ci["p90"]

    trend = detect_trend(rt, point_rt)

    # Стабильная регулярная база (is_recurring) — доля предсказуемого потока.
    # На SES/Monte-Carlo не влияет, только характеризует надёжность прогноза.
    recurring_cf = recurring_income - recurring_expense
    stable_baseline = {
        "recurring_income": round(recurring_income, 2),
        "recurring_expense": round(recurring_expense, 2),
        "recurring_cash_flow": round(recurring_cf, 2),
        "income_share": round(recurring_income / income_total, 3) if income_total > 0 else 0.0,
        "expense_share": round(recurring_expense / expense_total, 3) if expense_total > 0 else 0.0,
    }

    # FR-08: первый месяц прогнозного дефицита (Rt < 0).
    # Сначала ищем дефицит в основном прогнозе, иначе — в пессимистичном сценарии (p10).
    deficit_alert = None
    for f in forecast:
        if f["Rt"] < 0:
            deficit_alert = {"period": f["period"], "gap": round(abs(f["Rt"]), 2), "pessimistic": False}
            break
    if deficit_alert is None:
        for f in forecast:
            if f.get("Rt_p10", 0) < 0:
                deficit_alert = {"period": f["period"], "gap": round(abs(f["Rt_p10"]), 2), "pessimistic": True}
                break

    return {
        "current": {"Bt": balance, "Rt": rt, "Lt": lt, "Dt": dt},
        "horizon": horizon,
        "forecast": forecast,
        "deficit_alert": deficit_alert,
        "trend": trend,
        "stable_baseline": stable_baseline,
        "method": {
            "point": "экспоненциальное сглаживание истории с накоплением баланса",
            "interval": f"{MC_SIMULATIONS} случайных сценариев, диапазон 80%",
        },
    }
