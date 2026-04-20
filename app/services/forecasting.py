"""
Модуль прогнозирования денежных потоков СППР.

Реализует этап 3 алгоритма из ВКР (раздел 6.2):
  Rt+h = Bt + sum(î_k,t+h) − sum(ê_j,t+h) − sum(P̂_l,t+h)  (форм. 35)

Допущение: при отсутствии явных прогнозных значений доходы,
расходы и обязательные платежи считаются постоянными на всём
горизонте планирования H (наивный прогноз, baseline).
"""
from __future__ import annotations

from typing import Any


def forecast_cashflow(
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    horizon: int = 6,
) -> list[dict[str, Any]]:
    """
    Строит прогноз на h = 1..horizon периодов (месяцев).

    Возвращает список записей:
      { "period": h, "income": î, "expense": ê, "obligations": P̂,
        "cash_flow": CFt+h, "Rt": Rt+h }
    """
    results = []
    for h in range(1, horizon + 1):
        cf = income_total - expense_total
        rt_h = cf - obligation_payments
        results.append({
            "period": h,
            "income": round(income_total, 2),
            "expense": round(expense_total, 2),
            "obligations": round(obligation_payments, 2),
            "cash_flow": round(cf, 2),
            "Rt": round(rt_h, 2),
        })
    return results


def forecast_indicators(
    rt: float,
    lt: float,
    dt: float,
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    horizon: int = 6,
) -> dict[str, Any]:
    """
    Прогноз вектора состояния Zt+h = {Rt+h, Lt+h, Dt+h} на горизонт H.

    При досрочном погашении обязательств Rt растёт — здесь моделируется
    сценарий «без досрочного погашения» (baseline). Используется для
    отображения динамики на странице планирования.
    """
    periods = forecast_cashflow(
        income_total=income_total,
        expense_total=expense_total,
        obligation_payments=obligation_payments,
        horizon=horizon,
    )

    total_load = expense_total + obligation_payments
    forecast = []
    for p in periods:
        lt_h = p["Rt"] / total_load if total_load > 0 else 0.0
        dt_h = obligation_payments / income_total if income_total > 0 else 0.0
        forecast.append({
            "period": p["period"],
            "Rt": p["Rt"],
            "Lt": round(lt_h, 4),
            "Dt": round(dt_h, 4),
            "cash_flow": p["cash_flow"],
        })

    trend = _detect_trend(rt, [f["Rt"] for f in forecast])

    return {
        "current": {"Rt": rt, "Lt": lt, "Dt": dt},
        "horizon": horizon,
        "forecast": forecast,
        "trend": trend,
    }


def _detect_trend(current_rt: float, future_rt: list[float]) -> str:
    """Определяет тренд Rt: стабильный / улучшение / ухудшение."""
    if not future_rt:
        return "stable"
    last = future_rt[-1]
    delta = last - current_rt
    if abs(delta) < abs(current_rt) * 0.05:
        return "stable"
    return "improving" if delta > 0 else "deteriorating"
