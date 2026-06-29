"""Маршруты мультивалюты: курсы и конвертация (FR-19, DATA-08)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies import require_admin
from app.database.models import FxRate
from app.services.currency import CurrencyConverter
from app.utils.time import utcnow

router = APIRouter(prefix="/fx", tags=["Валюты"])


class FxRateResponse(BaseModel):
    currency: str
    rate_to_usd: float
    updated_at: datetime


class FxRateUpsert(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    rate_to_usd: float = Field(gt=0)


class ConvertRequest(BaseModel):
    amount: float
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)


@router.get("/rates", response_model=list[FxRateResponse], summary="Список курсов к USD")
def list_rates(db: Session = Depends(get_db)) -> list[FxRateResponse]:
    rows = db.query(FxRate).order_by(FxRate.currency.asc()).all()
    return [
        FxRateResponse(
            currency=r.currency, rate_to_usd=float(r.rate_to_usd), updated_at=r.updated_at
        )
        for r in rows
    ]


@router.put("/rates", response_model=FxRateResponse, summary="Обновить/добавить курс")
def upsert_rate(payload: FxRateUpsert, db: Session = Depends(get_db)) -> FxRateResponse:
    code = payload.currency.upper()
    row = db.query(FxRate).filter(FxRate.currency == code).first()
    if row is None:
        row = FxRate(currency=code, rate_to_usd=Decimal(str(payload.rate_to_usd)))
        db.add(row)
    else:
        row.rate_to_usd = Decimal(str(payload.rate_to_usd))
        row.updated_at = utcnow()
    db.commit()
    db.refresh(row)
    return FxRateResponse(
        currency=row.currency, rate_to_usd=float(row.rate_to_usd), updated_at=row.updated_at
    )


@router.post("/convert", summary="Конвертировать сумму между валютами")
def convert(payload: ConvertRequest, db: Session = Depends(get_db)) -> dict:
    converter = CurrencyConverter.from_db(db)
    if not converter.supports(payload.from_currency) or not converter.supports(payload.to_currency):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неизвестная валюта — добавьте курс через PUT /api/fx/rates.",
        )
    result = converter.convert(payload.amount, payload.from_currency, payload.to_currency)
    return {
        "amount": payload.amount,
        "from": payload.from_currency.upper(),
        "to": payload.to_currency.upper(),
        "result": float(result),
    }


@router.post("/refresh", summary="Обновить курсы валют с ЦБ РФ (живой источник)",
             dependencies=[Depends(require_admin)])
def refresh_rates(db: Session = Depends(get_db)) -> dict:
    """Тянет актуальные курсы с cbr.ru и обновляет таблицу. При недоступности источника
    текущие курсы сохраняются (source=fallback). Защищено суточным кэшем от частых запросов."""
    from app.services.cbr_fx import update_fx_rates

    return update_fx_rates(db)
