from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.crud import (
    apply_category_rule,
    category_id_for,
    create_transaction,
    delete_category_rule,
    delete_transaction,
    get_category_rules,
    get_transactions,
    restore_transaction,
    set_transaction_category,
    upsert_category_rule,
)
from app.core.categorization import MIN_MATCH_TOKEN_LEN, normalize_match_key
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
        currency=payload.currency,
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
    user_id: str | None = Depends(get_current_user_id),
) -> TransactionResponse:
    transaction = delete_transaction(db=db, transaction_id=transaction_id, user_id=user_id)
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


# ── P2.7: обучение категоризации на правках пользователя ──────────────────
class CategoryAssignRequest(BaseModel):
    """Переназначение категории операции. По умолчанию запоминает правило и применяет его
    к существующим совпадающим операциям (это и есть «обучение»). `match_token` можно сузить
    вручную; если не задан — берётся описание операции."""

    category: str = Field(min_length=1, max_length=255)
    match_token: str | None = Field(default=None, max_length=255)
    apply_to_matching: bool = True
    learn: bool = True


class CategoryRuleResponse(BaseModel):
    id: int
    match_token: str
    category: str
    type: str

    model_config = {"from_attributes": True}


class CategoryAssignResponse(BaseModel):
    transaction: TransactionResponse
    rule: CategoryRuleResponse | None = None
    updated_count: int = 0


@router.post(
    "/transactions/{transaction_id}/category",
    response_model=CategoryAssignResponse,
    summary="Переназначить категорию операции (+обучение правилом)",
)
def set_transaction_category_endpoint(
    transaction_id: int,
    payload: CategoryAssignRequest,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict:
    transaction = set_transaction_category(
        db, transaction_id, payload.category, user_id=user_id
    )
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Транзакция не найдена."
        )

    rule = None
    updated_count = 0
    if payload.learn:
        token = payload.match_token or transaction.description or payload.category
        if len(normalize_match_key(token)) >= MIN_MATCH_TOKEN_LEN:
            category_id = category_id_for(db, payload.category, transaction.type)
            rule = upsert_category_rule(
                db, user_id, token, payload.category, transaction.type, category_id=category_id
            )
            if payload.apply_to_matching:
                updated_count = apply_category_rule(
                    db,
                    user_id,
                    rule.match_token,
                    payload.category,
                    transaction.type,
                    exclude_id=transaction.id,
                )

    log_event("transaction_recategorized", {
        "transaction_id": transaction_id,
        "category": payload.category,
        "learned": rule is not None,
        "updated_count": updated_count,
    })
    return {"transaction": transaction, "rule": rule, "updated_count": updated_count}


@router.get(
    "/category-rules",
    response_model=list[CategoryRuleResponse],
    summary="Список выученных правил категоризации",
)
def get_category_rules_endpoint(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[CategoryRuleResponse]:
    return get_category_rules(db, user_id)


@router.delete(
    "/category-rules/{rule_id}",
    summary="Удалить правило категоризации",
)
def delete_category_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    if not delete_category_rule(db, rule_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Правило не найдено."
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
