from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_budget,
    delete_budget,
    get_budget_status,
    get_budgets,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.services.event_logger import log_event

router = APIRouter(prefix="/budgets", tags=["Бюджеты"])


@router.get("", response_model=list[BudgetResponse], summary="Список бюджетов")
def list_budgets(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[BudgetResponse]:
    return get_budgets(db, user_id=user_id)


@router.get("/status", summary="План-факт по категорийным бюджетам (FR-22)")
def budget_status(
    days: int = 30,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[dict[str, Any]]:
    return get_budget_status(db, days=days, user_id=user_id)


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать или обновить бюджет",
)
def add_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> BudgetResponse:
    budget = create_budget(
        db, category=payload.category, limit_amount=payload.limit_amount, user_id=user_id
    )
    log_event("budget_set", {"category": payload.category, "limit": payload.limit_amount})
    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить бюджет",
)
def remove_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> None:
    if not delete_budget(db, budget_id, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бюджет не найден.")
    log_event("budget_deleted", {"budget_id": budget_id})
