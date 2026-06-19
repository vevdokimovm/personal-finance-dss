from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_transaction,
    delete_transaction,
    get_transactions,
    restore_transaction,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.event_logger import log_event

router = APIRouter(tags=["Транзакции"])


@router.get("/transactions/export.csv", summary="Экспорт операций в CSV (скачивание)")
def export_transactions_csv(
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    rows = get_transactions(db, user_id=user_id)
    if date_from:
        rows = [t for t in rows if str(t.date)[:10] >= date_from]
    if date_to:
        rows = [t for t in rows if str(t.date)[:10] <= date_to]

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["Дата", "Тип", "Категория", "Сумма", "Описание", "Источник"])
    for t in rows:
        writer.writerow([
            str(t.date)[:10],
            "Доход" if t.type == "income" else "Расход",
            t.category or "",
            t.amount,
            getattr(t, "description", "") or "",
            "Банк" if getattr(t, "is_synced", False) else "Ручной",
        ])

    filename = f"finpilot-operations-{datetime.utcnow():%Y-%m-%d}.csv"
    return Response(
        content="\ufeff" + buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Получить список транзакций",
)
def get_transactions_endpoint(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[TransactionResponse]:
    return get_transactions(db, user_id=user_id)


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать транзакцию",
)
def create_transaction_endpoint(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> TransactionResponse:
    transaction = create_transaction(
        db=db,
        amount=payload.amount,
        category=payload.category,
        type=payload.type,
        date=payload.date,
        description=payload.description,
        mcc=payload.mcc,
        user_id=user_id,
    )
    log_event("transaction_created", {
        "type": payload.type,
        "category": payload.category,
        "amount": payload.amount,
    })
    return transaction


@router.delete(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Удалить транзакцию",
)
def delete_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    transaction = delete_transaction(db=db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Транзакция не найдена.",
        )
    log_event("transaction_deleted", {"transaction_id": transaction_id})
    return transaction


@router.post(
    "/transactions/{transaction_id}/restore",
    response_model=TransactionResponse,
    summary="Восстановить удалённую транзакцию (undo)",
)
def restore_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    transaction = restore_transaction(db=db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Удалённая транзакция не найдена.",
        )
    log_event("transaction_restored", {"transaction_id": transaction_id})
    return transaction
