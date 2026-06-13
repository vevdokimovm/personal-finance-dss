from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api._guards import ensure_calculable
from app.core.metrics import (
    calculate_expense_total,
    calculate_income_total,
    sum_liquid_assets,
    sum_obligation_payments,
)
from app.core.preprocessing import prepare_data
from app.database.crud import (
    get_goals,
    get_liquid_assets,
    get_obligations,
    get_scenarios,
    get_transactions,
    get_user_prefs,
    save_scenario,
)
from app.dependencies import get_db
from app.services.event_logger import log_event, log_recommendation
from app.services.forecasting import forecast_indicators
from app.services.planning import run_planning


class PlanningRequest(BaseModel):
    risk_tolerance: Optional[int] = Field(None, ge=1, le=5, description="Профиль риска (1–5)")
    l_min: Optional[float] = Field(None, ge=0.0, le=10.0, description="Lmin — мин. допустимая Lt'")
    r_bench: Optional[float] = Field(None, ge=0.0, le=1.0, description="OCR — порог Avalanche")
    income_override: Optional[float] = Field(None, ge=0, description="Сценарий: доход вместо фактического")
    expense_override: Optional[float] = Field(None, ge=0, description="Сценарий: расходы вместо фактических")


class ForecastRequest(BaseModel):
    horizon: int = Field(6, ge=1, le=24)


class ScenarioSave(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parameters: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


router = APIRouter(prefix="/planning", tags=["Планирование"])


def _serialize_obligations(items) -> list[dict[str, Any]]:
    return [
        {
            "id": o.id,
            "name": o.name,
            "amount": o.amount,
            "interest_rate": o.interest_rate,
            "term": o.term,
            "monthly_payment": o.monthly_payment,
        }
        for o in items
    ]


def _serialize_goals(items) -> list[dict[str, Any]]:
    return [
        {
            "id": g.id,
            "name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "deadline": g.deadline,
            "category": g.category,
        }
        for g in items
    ]


def _serialize_assets(items) -> list[dict[str, Any]]:
    return [
        {"id": a.id, "name": a.name, "amount": a.amount,
         "interest_rate": a.interest_rate, "type": a.type}
        for a in items
    ]


@router.post("/calculate", summary="Полный цикл СППР: генерация и ранжирование альтернатив")
def calculate_plan(
    payload: PlanningRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    prefs = get_user_prefs(db)
    risk_tolerance = payload.risk_tolerance if payload.risk_tolerance is not None else prefs.risk_tolerance
    l_min = payload.l_min if payload.l_min is not None else prefs.l_min
    r_bench = payload.r_bench if payload.r_bench is not None else prefs.r_bench

    transactions = get_transactions(db)
    obligations = _serialize_obligations(get_obligations(db))
    goals = _serialize_goals(get_goals(db))
    assets = _serialize_assets(get_liquid_assets(db))

    prepared = prepare_data(
        transactions=transactions,
        obligations=obligations,
        goals=goals,
        liquid_assets=assets,
    )

    income_total = (
        payload.income_override if payload.income_override is not None
        else calculate_income_total(prepared["transactions"])
    )
    expense_total = (
        payload.expense_override if payload.expense_override is not None
        else calculate_expense_total(prepared["transactions"])
    )
    bliq = sum_liquid_assets(prepared["liquid_assets"])

    ensure_calculable(prepared["transactions"], prepared["obligations"])

    # active_goals = только незакрытые цели
    active_goals = prepared["active_goals"]

    result = run_planning(
        income_total=income_total,
        expense_total=expense_total,
        obligations=prepared["obligations"],
        goals=active_goals,
        bliq=bliq,
        r_bench=r_bench,
        risk_tolerance=risk_tolerance,
        l_min=l_min,
    )

    result["input_summary"] = {
        "income": round(income_total, 2),
        "expense": round(expense_total, 2),
        "bliq": round(bliq, 2),
        "transactions_count": len(prepared["transactions"]),
        "obligations_count": len(prepared["obligations"]),
        "goals_count": len(prepared["active_goals"]),
        "liquid_assets_count": len(prepared["liquid_assets"]),
        "r_bench": r_bench,
        "l_min": l_min,
        "risk_tolerance": risk_tolerance,
    }

    log_recommendation(result)
    log_event("recommendation_generated", {
        "risk_profile": result.get("risk_profile"),
        "alternatives_total": result.get("alternatives_total"),
        "admissible_count": result.get("admissible_count"),
        "u_score": (result.get("best") or {}).get("utility"),
    })
    return result


@router.post("/forecast", summary="Прогноз Rt/Lt/Dt на горизонт H (форм. 35 ВКР)")
def get_forecast(payload: ForecastRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    transactions = get_transactions(db)
    obligations = _serialize_obligations(get_obligations(db))
    goals = _serialize_goals(get_goals(db))

    prepared = prepare_data(transactions=transactions, obligations=obligations, goals=goals)

    ensure_calculable(prepared["transactions"], prepared["obligations"])

    income = calculate_income_total(prepared["transactions"])
    expense = calculate_expense_total(prepared["transactions"])
    obl_payments = sum_obligation_payments(prepared["obligations"])
    balance = sum(g.get("current_amount", 0) for g in prepared["active_goals"])
    cash_flow = income - expense
    rt = cash_flow - obl_payments
    lt = rt / (expense + obl_payments) if (expense + obl_payments) > 0 else 0.0
    dt = obl_payments / income if income > 0 else 0.0

    return forecast_indicators(
        balance=balance,
        rt=rt,
        lt=lt,
        dt=dt,
        income_total=income,
        expense_total=expense,
        obligation_payments=obl_payments,
        horizon=payload.horizon,
    )


@router.post("/scenarios", summary="Сохранить сценарий что-если (LOG-06)")
def save_scenario_endpoint(payload: ScenarioSave, db: Session = Depends(get_db)) -> dict[str, Any]:
    scenario = save_scenario(
        db, name=payload.name, parameters=payload.parameters, result=payload.result
    )
    log_event("scenario_saved", {"name": payload.name, "parameters": payload.parameters})
    return {
        "id": scenario.id,
        "name": scenario.name,
        "created_at": scenario.created_at.isoformat(),
    }


@router.get("/scenarios", summary="Список сохранённых сценариев")
def list_scenarios_endpoint(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return [
        {
            "id": s.id,
            "name": s.name,
            "parameters": s.parameters_json,
            "created_at": s.created_at.isoformat(),
        }
        for s in get_scenarios(db)
    ]
