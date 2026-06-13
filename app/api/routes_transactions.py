from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_transaction,
    delete_transaction,
    get_transactions,
)
from app.dependencies import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse


router = APIRouter(tags=["Транзакции"])


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Получить список транзакций",
)
def get_transactions_endpoint(
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    return get_transactions(db)


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать транзакцию",
)
def create_transaction_endpoint(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    transaction = create_transaction(
        db=db,
        amount=payload.amount,
        category=payload.category,
        type=payload.type,
        date=payload.date,
    )
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
    return transaction
