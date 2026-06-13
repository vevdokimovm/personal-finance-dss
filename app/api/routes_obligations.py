from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_obligation,
    delete_obligation,
    get_obligations,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas.obligation import ObligationCreate, ObligationResponse
from app.services.event_logger import log_event

router = APIRouter(tags=["Обязательства"])


@router.get(
    "/obligations",
    response_model=list[ObligationResponse],
    summary="Получить список обязательств",
)
def get_obligations_endpoint(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[ObligationResponse]:
    return get_obligations(db, user_id=user_id)


@router.post(
    "/obligations",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать обязательство",
)
def create_obligation_endpoint(
    payload: ObligationCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> ObligationResponse:
    obligation = create_obligation(
        db=db,
        name=payload.name,
        amount=payload.amount,
        interest_rate=payload.interest_rate,
        term=payload.term,
        monthly_payment=payload.monthly_payment,
        payment_day=payload.payment_day,
        comment=payload.comment,
        bank=payload.bank,
        type=payload.type,
        start_date=payload.start_date,
        user_id=user_id,
    )
    log_event("obligation_created", {
        "type": payload.type,
        "bank": payload.bank,
        "amount": payload.amount,
        "interest_rate": payload.interest_rate,
    })
    return obligation


@router.delete(
    "/obligations/{obligation_id}",
    summary="Удалить обязательство",
)
def delete_obligation_endpoint(
    obligation_id: int,
    db: Session = Depends(get_db),
):
    if delete_obligation(db=db, obligation_id=obligation_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обязательство не найдено.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
