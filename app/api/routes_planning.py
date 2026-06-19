from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Response
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
from app.dependencies import get_current_user_id, get_db
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
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    result = _compute_plan(payload, db, user_id)
    log_recommendation(result)
    log_event("recommendation_generated", {
        "risk_profile": result.get("risk_profile"),
        "alternatives_total": result.get("alternatives_total"),
        "admissible_count": result.get("admissible_count"),
        "u_score": (result.get("best") or {}).get("utility"),
    })
    return result


def _compute_plan(
    payload: PlanningRequest,
    db: Session,
    user_id: str | None,
) -> dict[str, Any]:
    prefs = get_user_prefs(db, user_id=user_id)
    risk_tolerance = payload.risk_tolerance if payload.risk_tolerance is not None else prefs.risk_tolerance
    l_min = payload.l_min if payload.l_min is not None else prefs.l_min

    transactions = get_transactions(db, user_id=user_id)
    obligations = _serialize_obligations(get_obligations(db, user_id=user_id))
    goals = _serialize_goals(get_goals(db, user_id=user_id))
    assets = _serialize_assets(get_liquid_assets(db, user_id=user_id))

    # r_bench (OCR): явный из запроса → лучшая ставка ликвидных активов → дефолт prefs.
    # Экономический смысл: альтернативная доходность рубля = ваша реальная ставка по накоплениям.
    if payload.r_bench is not None:
        r_bench = payload.r_bench
        r_bench_source = "request"
    else:
        best_asset_rate = max((float(a.get("interest_rate") or 0.0) for a in assets), default=0.0)
        if best_asset_rate > 0:
            r_bench = best_asset_rate
            r_bench_source = "best_asset_rate"
        else:
            r_bench = prefs.r_bench
            r_bench_source = "prefs_default"

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
        "r_bench_source": r_bench_source,
        "l_min": l_min,
        "risk_tolerance": risk_tolerance,
    }
    return result


def _plan_to_csv(result: dict[str, Any]) -> str:
    """Формирует CSV-таблицу плана распределения (разделитель ; для Excel-RU)."""
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    ind = result.get("indicators", {})
    top3 = result.get("top3", [])
    best = top3[0] if top3 else {}

    writer.writerow(["FINPILOT — план распределения", ""])
    writer.writerow(["Профиль риска", result.get("risk_profile", "")])
    writer.writerow([])
    writer.writerow(["ПОКАЗАТЕЛЬ", "ЗНАЧЕНИЕ"])
    writer.writerow(["Свободные деньги (Rt), ₽", ind.get("Rt", "")])
    writer.writerow(["Ликвидность (Lt)", ind.get("Lt", "")])
    writer.writerow(["Долговая нагрузка (Dt), %", round(ind.get("Dt", 0) * 100, 1)])
    writer.writerow(["Подушка (BLR), мес", round(ind.get("BLR", 0), 2)])
    writer.writerow([])
    writer.writerow(["РЕКОМЕНДОВАННОЕ РАСПРЕДЕЛЕНИЕ", best.get("name", "")])
    writer.writerow(["На досрочное погашение, ₽", best.get("x_obligations", 0)])
    writer.writerow(["В подушку безопасности, ₽", best.get("x_reserve", 0)])
    writer.writerow(["На цели, ₽", best.get("x_goals", 0)])
    writer.writerow(["Оценка полезности U", best.get("utility", "")])
    writer.writerow([])
    writer.writerow(["ВСЕ ВАРИАНТЫ (топ-3)", ""])
    writer.writerow(["#", "Название", "Долг", "Резерв", "Цели", "Оценка"])
    for i, alt in enumerate(top3, start=1):
        writer.writerow([
            i, alt.get("name", ""), alt.get("x_obligations", 0),
            alt.get("x_reserve", 0), alt.get("x_goals", 0), alt.get("utility", ""),
        ])
    return buf.getvalue()


@router.get("/export.csv", summary="Экспорт плана распределения в CSV (скачивание файла)")
def export_plan_csv(
    risk_tolerance: int | None = None,
    l_min: float | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    payload = PlanningRequest(risk_tolerance=risk_tolerance, l_min=l_min)
    result = _compute_plan(payload, db, user_id)
    filename = f"finpilot-plan-{datetime.utcnow():%Y-%m-%d}.csv"
    return Response(
        content="\ufeff" + _plan_to_csv(result),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/forecast", summary="Прогноз Rt/Lt/Dt на горизонт H (форм. 35 ВКР)")
def get_forecast(
    payload: ForecastRequest,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    transactions = get_transactions(db, user_id=user_id)
    obligations = _serialize_obligations(get_obligations(db, user_id=user_id))
    goals = _serialize_goals(get_goals(db, user_id=user_id))

    # Регулярные операции (is_recurring) — стабильная база прогноза (FR-13).
    recurring_income = sum(
        t.amount for t in transactions
        if getattr(t, "is_recurring", False) and t.type == "income"
    )
    recurring_expense = sum(
        t.amount for t in transactions
        if getattr(t, "is_recurring", False) and t.type == "expense"
    )

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
        recurring_income=recurring_income,
        recurring_expense=recurring_expense,
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
