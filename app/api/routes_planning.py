from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.database.crud import get_transactions, get_obligations, get_goals
from app.services.planning import run_planning
from app.services.forecasting import forecast_indicators
from app.core.metrics import (
    calculate_income_total, calculate_expense_total,
    calculate_cft, sum_obligation_payments,
    calculate_rt, calculate_lt, calculate_dt,
)
from app.core.preprocessing import prepare_data


class PlanningRequest(BaseModel):
    risk_tolerance: int = Field(3, ge=1, le=5, description="Профиль риска (1–5)")
    l_min: float = Field(0.0, ge=0.0, le=1.0, description="Мин. допустимый уровень Lt' (L_min из ВКР)")


class ForecastRequest(BaseModel):
    horizon: int = Field(6, ge=1, le=24, description="Горизонт прогноза (месяцев)")


router = APIRouter(prefix="/planning", tags=["Планирование"])


@router.post("/calculate", summary="Генерация и ранжирование альтернатив СППР")
def calculate_plan(
    payload: PlanningRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Полный цикл планирования по алгоритму ВКР:
    1. Расчёт текущих показателей (Rt, Lt, Dt)
    2. Генерация альтернатив распределения Rt
    3. Оценка (пересчёт Rt', Lt', Dt')
    4. Фильтрация по ограничениям
    5. Ранжирование через U(a)
    """
    transactions = get_transactions(db)
    obligations = get_obligations(db)
    goals = get_goals(db)

    prepared = prepare_data(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
    )

    income = calculate_income_total(prepared["transactions"])
    expense = calculate_expense_total(prepared["transactions"])
    cash_flow = calculate_cft(prepared["transactions"])
    obl_payments = sum_obligation_payments(prepared["obligations"])
    rt = calculate_rt(cash_flow=cash_flow, obligation_payments=obl_payments)
    # Lt = Rt / (Расходы + Обязательства) — формула ВКР, соответствует табл. 17
    lt = calculate_lt(available_resource=rt, total_expense_load=expense + obl_payments)
    dt = calculate_dt(obligation_payments=obl_payments, total_income=income)

    # Суммарная потребность по целям
    goals_total = sum(
        float(g.get("target_amount", 0) if isinstance(g, dict) else getattr(g, "target_amount", 0))
        - float(g.get("current_amount", 0) if isinstance(g, dict) else getattr(g, "current_amount", 0))
        for g in prepared["active_goals"]
    )

    result = run_planning(
        rt=rt,
        lt=lt,
        dt=dt,
        income_total=income,
        expense_total=expense,
        obligation_payments=obl_payments,
        goals_total=max(goals_total, 0),
        risk_tolerance=payload.risk_tolerance,
        l_min=payload.l_min,
    )

    result["input_summary"] = {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "obligations": round(obl_payments, 2),
        "cash_flow": round(cash_flow, 2),
        "goals_total": round(max(goals_total, 0), 2),
        "transactions_count": len(prepared["transactions"]),
        "obligations_count": len(prepared["obligations"]),
        "goals_count": len(prepared["active_goals"]),
    }

    return result


@router.post("/forecast", summary="Прогноз показателей Rt/Lt/Dt на горизонт H (ВКР, форм. 35)")
def get_forecast(
    payload: ForecastRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Этап 3 алгоритма ВКР: прогнозирование денежных потоков.
    Rt+h = CFt+h − sum(P̂_l,t+h)  при постоянных доходах/расходах (baseline).
    """
    transactions = get_transactions(db)
    obligations = get_obligations(db)

    prepared = prepare_data(transactions=transactions, obligations=obligations, goals=[])

    income = calculate_income_total(prepared["transactions"])
    expense = calculate_expense_total(prepared["transactions"])
    cash_flow = calculate_cft(prepared["transactions"])
    obl_payments = sum_obligation_payments(prepared["obligations"])
    rt = calculate_rt(cash_flow=cash_flow, obligation_payments=obl_payments)
    lt = calculate_lt(available_resource=rt, total_expense_load=expense + obl_payments)
    dt = calculate_dt(obligation_payments=obl_payments, total_income=income)

    return forecast_indicators(
        rt=rt,
        lt=lt,
        dt=dt,
        income_total=income,
        expense_total=expense,
        obligation_payments=obl_payments,
        horizon=payload.horizon,
    )
