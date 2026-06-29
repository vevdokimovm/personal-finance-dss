from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api._guards import ensure_calculable
from app.core.envelopes import apply_envelopes
from app.core.metrics import (
    calculate_expense_total,
    calculate_income_total,
    sum_liquid_assets,
    sum_obligation_payments,
)
from app.core.preprocessing import prepare_data
from app.database.crud import (
    create_plan_snapshot,
    get_goals,
    get_liquid_assets,
    get_obligations,
    get_plan_snapshot,
    get_plan_snapshots,
    get_scenarios,
    get_transactions,
    get_user_prefs,
    resolve_household_id,
    save_scenario,
    soft_delete_plan_snapshot,
)
from app.dependencies import get_current_user_id, get_db
from app.services.cbr_rate import get_opportunity_cost_rate
from app.services.cache import TTLCache
from app.services.event_logger import log_event, log_recommendation
from app.services.forecasting import forecast_indicators
from app.services.currency import to_base_currency
from app.services.plan_export import plan_to_pdf, plan_to_xlsx
from app.services.planning import run_planning


# ── Кэш расчёта плана (P1.2) ──────────────────────────────────────────────
# Бутылочное горло /calculate — Monte Carlo внутри run_planning (нагрузочный P0.4).
# Кэшируем по отпечатку РЕАЛЬНЫХ входов run_planning (после резолва prefs и r_bench),
# а не по сырому payload: один набор данных с разным профилем риска обязан считаться
# отдельно. Логирование событий остаётся в роуте и срабатывает на каждый вызов.
_planning_cache = TTLCache(ttl_seconds=180, max_size=256)


def _round_floats(obj: Any, ndigits: int = 4) -> Any:
    if isinstance(obj, float):
        return round(obj, ndigits)
    if isinstance(obj, dict):
        return {k: _round_floats(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, ndigits) for v in obj]
    return obj


def _stable_items(items: list[dict[str, Any]]) -> list[str]:
    # Порядконезависимый отпечаток списка записей: каждая запись → канонический JSON,
    # список строк сортируется (порядок строк из БД не должен влиять на ключ).
    return sorted(
        json.dumps(_round_floats(it), sort_keys=True, default=str, ensure_ascii=False)
        for it in items
    )


def _plan_fingerprint(
    *,
    income_total: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    bliq: float,
    r_bench: float,
    risk_tolerance: int,
    l_min: float,
) -> str:
    payload = {
        "income": round(float(income_total), 2),
        "expense": round(float(expense_total), 2),
        "bliq": round(float(bliq), 2),
        "r_bench": round(float(r_bench), 6),
        "risk": int(risk_tolerance),
        "l_min": round(float(l_min), 4),
        "obligations": _stable_items(obligations),
        "goals": _stable_items(goals),
    }
    blob = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class PlanningRequest(BaseModel):
    risk_tolerance: Optional[int] = Field(None, ge=1, le=5, description="Профиль риска (1–5)")
    l_min: Optional[float] = Field(None, ge=0.0, le=10.0, description="Lmin — мин. допустимая Lt'")
    r_bench: Optional[float] = Field(None, ge=0.0, le=1.0, description="OCR — порог Avalanche")
    income_override: Optional[float] = Field(
        None, ge=0, description="Сценарий: доход вместо фактического")
    expense_override: Optional[float] = Field(
        None, ge=0, description="Сценарий: расходы вместо фактических")


class ForecastRequest(BaseModel):
    horizon: int = Field(6, ge=1, le=24)


class ScenarioSave(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parameters: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    household_id: int | None = None  # P3.7: общий для семьи (если член household)


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
            "savings_rate": g.savings_rate,
            "linked_asset_id": g.linked_asset_id,
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
    risk_tolerance = (
        payload.risk_tolerance if payload.risk_tolerance is not None
        else prefs.risk_tolerance
    )
    l_min = payload.l_min if payload.l_min is not None else prefs.l_min

    base_currency = (prefs.base_currency or "RUB").upper()
    transactions = to_base_currency(db, get_transactions(db, user_id=user_id), base_currency)
    obligations = to_base_currency(
        db, _serialize_obligations(get_obligations(db, user_id=user_id)), base_currency
    )
    goals = to_base_currency(db, _serialize_goals(get_goals(db, user_id=user_id)), base_currency)
    all_assets = to_base_currency(
        db, _serialize_assets(get_liquid_assets(db, user_id=user_id)), base_currency
    )

    # Конверты: цели берут накопление/ставку из привязанных активов, а сами
    # привязанные активы исключаются из свободного резерва (Bliq) — без двойного учёта.
    # r_bench при этом учитывает ставку всех активов (привязанный вклад — тоже доходность).
    goals, assets = apply_envelopes(goals, all_assets)

    # r_bench (OCR): явный из запроса → реальная ставка ликвидных активов пользователя
    #             → ключевая ставка ЦБ после НДФЛ → дефолт prefs.
    # Экономический смысл: альтернативная доходность рубля = ваша реальная посленалоговая
    # доходность по накоплениям; если своих активов нет — рыночный ориентир (ключевая ЦБ).
    if payload.r_bench is not None:
        r_bench = payload.r_bench
        r_bench_source = "request"
    else:
        best_asset_rate = max((float(a.get("interest_rate") or 0.0)
                              for a in all_assets), default=0.0)
        if best_asset_rate > 0:
            r_bench = best_asset_rate
            r_bench_source = "best_asset_rate"
        else:
            ocr = get_opportunity_cost_rate(fallback=float(prefs.r_bench))
            r_bench = ocr["r_bench"]
            r_bench_source = ocr["source"]

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

    cache_key = "plan:%s:%s" % (
        user_id or "guest",
        _plan_fingerprint(
            income_total=income_total,
            expense_total=expense_total,
            obligations=prepared["obligations"],
            goals=active_goals,
            bliq=bliq,
            r_bench=r_bench,
            risk_tolerance=risk_tolerance,
            l_min=l_min,
        ),
    )
    cached = _planning_cache.get(cache_key)
    if cached is not None:
        # Копия: вызывающий (и логирование) не должны мутировать объект в кэше.
        return copy.deepcopy(cached)

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
    _planning_cache.set(cache_key, copy.deepcopy(result))
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
    r_bench: float | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    payload = PlanningRequest(risk_tolerance=risk_tolerance, l_min=l_min, r_bench=r_bench)
    result = _compute_plan(payload, db, user_id)
    filename = f"finpilot-plan-{datetime.utcnow():%Y-%m-%d}.csv"
    return Response(
        content="\ufeff" + _plan_to_csv(result),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export.xlsx", summary="Экспорт плана распределения в XLSX (скачивание файла)")
def export_plan_xlsx(
    risk_tolerance: int | None = None,
    l_min: float | None = None,
    r_bench: float | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    payload = PlanningRequest(risk_tolerance=risk_tolerance, l_min=l_min, r_bench=r_bench)
    result = _compute_plan(payload, db, user_id)
    filename = f"finpilot-plan-{datetime.utcnow():%Y-%m-%d}.xlsx"
    return Response(
        content=plan_to_xlsx(result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export.pdf", summary="Экспорт плана распределения в PDF (скачивание файла)")
def export_plan_pdf(
    risk_tolerance: int | None = None,
    l_min: float | None = None,
    r_bench: float | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    payload = PlanningRequest(risk_tolerance=risk_tolerance, l_min=l_min, r_bench=r_bench)
    result = _compute_plan(payload, db, user_id)
    filename = f"finpilot-plan-{datetime.utcnow():%Y-%m-%d}.pdf"
    return Response(
        content=plan_to_pdf(result),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class PlanHistorySave(BaseModel):
    """Параметры расчёта для сохранения снапшота плана в историю (P2.6)."""

    risk_tolerance: int | None = None
    l_min: float | None = None
    r_bench: float | None = None
    note: str | None = Field(default=None, max_length=500)
    household_id: int | None = None  # P3.7: общий для семьи (если член household)


def _snapshot_summary(s: Any) -> dict[str, Any]:
    return {
        "id": s.id,
        "created_at": s.created_at.isoformat(),
        "risk_profile": s.risk_profile,
        "indicators": {"Rt": s.rt, "Lt": s.lt, "Dt": s.dt, "BLR": s.blr},
        "best": {
            "name": s.best_name,
            "x_obligations": s.x_obligations,
            "x_reserve": s.x_reserve,
            "x_goals": s.x_goals,
            "utility": s.utility,
        },
        "note": s.note,
    }


def _snapshot_detail(s: Any) -> dict[str, Any]:
    data = _snapshot_summary(s)
    data["top3"] = s.top3 or []
    return data


@router.post("/history", summary="Сохранить снапшот плана в историю (P2.6)")
def save_plan_history(
    payload: PlanHistorySave,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    req = PlanningRequest(
        risk_tolerance=payload.risk_tolerance, l_min=payload.l_min, r_bench=payload.r_bench
    )
    result = _compute_plan(req, db, user_id)
    hh = resolve_household_id(db, user_id, payload.household_id)
    snap = create_plan_snapshot(db, result, user_id=user_id, note=payload.note, household_id=hh)
    log_event("plan_snapshot_saved", {"id": snap.id, "risk_profile": snap.risk_profile})
    return _snapshot_detail(snap)


@router.get("/history", summary="История сохранённых планов (P2.6)")
def list_plan_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    snaps = get_plan_snapshots(db, user_id=user_id, limit=limit)
    return {"items": [_snapshot_summary(s) for s in snaps], "count": len(snaps)}


@router.get("/history/{snapshot_id}", summary="Снапшот плана по id (P2.6)")
def get_plan_history(
    snapshot_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    snap = get_plan_snapshot(db, snapshot_id, user_id=user_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="Снапшот плана не найден")
    return _snapshot_detail(snap)


@router.delete("/history/{snapshot_id}", summary="Удалить снапшот плана (P2.6)")
def delete_plan_history(
    snapshot_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    if not soft_delete_plan_snapshot(db, snapshot_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Снапшот плана не найден")
    return {"status": "deleted", "id": snapshot_id}


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
def save_scenario_endpoint(
    payload: ScenarioSave,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    hh = resolve_household_id(db, user_id, payload.household_id)
    scenario = save_scenario(
        db, name=payload.name, parameters=payload.parameters, result=payload.result,
        user_id=user_id, household_id=hh,
    )
    log_event("scenario_saved", {"name": payload.name, "parameters": payload.parameters})
    return {
        "id": scenario.id,
        "name": scenario.name,
        "created_at": scenario.created_at.isoformat(),
    }


@router.get("/scenarios", summary="Список сохранённых сценариев")
def list_scenarios_endpoint(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[dict[str, Any]]:
    return [
        {
            "id": s.id,
            "name": s.name,
            "parameters": s.parameters_json,
            "created_at": s.created_at.isoformat(),
        }
        for s in get_scenarios(db, user_id=user_id)
    ]


@router.get("/key-rate", summary="Текущая ключевая ставка ЦБ РФ")
def key_rate_endpoint() -> dict[str, object]:
    """Ключевая ставка Банка России (в долях) — ориентир для ставки накоплений.
    При недоступности cbr.ru возвращает резервное значение из настроек."""
    from app.config import settings
    from app.services.cbr_rate import get_key_rate

    return get_key_rate(fallback=settings.CBR_KEY_RATE_FALLBACK)


@router.get("/spending-advice", summary="Советы по расходам (анализ трат по категориям)")
def spending_advice_endpoint(
    months: int = 6,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Анализ расходов по категориям за окно месяцев: персональная норма (медиана),
    аномалии (robust z-score) и мягкие советы по сокращению (мат-модель v3.0.0)."""
    from app.services.spending import get_spending_advice

    return get_spending_advice(db, user_id=user_id, months=months)
