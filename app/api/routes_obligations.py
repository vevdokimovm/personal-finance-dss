from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_obligation,
    delete_obligation,
    get_obligations,
    restore_obligation,
    update_obligation,
)
from app.api._guards import ensure_can_share
from app.dependencies import get_current_user_id, get_db
from app.schemas.obligation import ObligationCreate, ObligationResponse, ObligationUpdate
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
    # Общий котёл требует права на него — одна проверка на все сущности
    # (`_guards.ensure_can_share`), четыре копии разошлись бы при первой правке.
    ensure_can_share(db, payload.household_id, user_id)
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
        currency=payload.currency,
        user_id=user_id,
        household_id=payload.household_id,
    )
    # 🔴 `user_id` обязателен: `analytics.funnel()` фильтрует `Event.user_id.isnot(None)`,
    # и событие без него не попадает в воронку ВООБЩЕ. Гипотеза H7 independent-expert,
    # подтверждена 05.09.2026: экран метрик показывал ложный обрыв на первом шаге.
    log_event("obligation_created", {
        "type": payload.type,
        "bank": payload.bank,
        "amount": payload.amount,
        "interest_rate": payload.interest_rate,
    }, user_id=user_id)
    return obligation


@router.put(
    "/obligations/{obligation_id}",
    response_model=ObligationResponse,
    summary="Изменить обязательство (частично, только переданные поля)",
)
def update_obligation_endpoint(
    obligation_id: int,
    payload: ObligationUpdate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> ObligationResponse:
    obligation = update_obligation(
        db, obligation_id, user_id=user_id, **payload.model_dump(exclude_unset=True)
    )
    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Обязательство не найдено."
        )
    log_event("obligation_updated", {"obligation_id": obligation_id}, user_id=user_id)
    return obligation


@router.delete(
    "/obligations/{obligation_id}",
    summary="Удалить обязательство",
)
def delete_obligation_endpoint(
    obligation_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
):
    if delete_obligation(db=db, obligation_id=obligation_id, user_id=user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обязательство не найдено.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/obligations/{obligation_id}/restore",
    response_model=ObligationResponse,
    summary="Восстановить удалённое обязательство (undo)",
)
def restore_obligation_endpoint(
    obligation_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> ObligationResponse:
    obligation = restore_obligation(db=db, obligation_id=obligation_id, user_id=user_id)
    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Удалённое обязательство не найдено.",
        )
    log_event("obligation_restored", {"obligation_id": obligation_id}, user_id=user_id)
    return obligation
