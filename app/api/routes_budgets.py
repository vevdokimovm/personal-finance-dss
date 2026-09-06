from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_budget,
    delete_budget,
    get_budget_status,
    get_budgets,
    restore_budget,
)
from app.api._guards import ensure_can_share, ensure_scope_unchanged
from app.dependencies import get_current_user_id, get_db
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetStatus
from app.services.event_logger import log_event

router = APIRouter(prefix="/budgets", tags=["Бюджеты"])


@router.get("", response_model=list[BudgetResponse], summary="Список бюджетов")
def list_budgets(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[BudgetResponse]:
    return get_budgets(db, user_id=user_id)


@router.get(
    "/status",
    response_model=list[BudgetStatus],
    summary="План-факт по категорийным бюджетам (FR-22)",
)
def budget_status(
    days: int = 30,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[BudgetStatus]:
    return [BudgetStatus(**row) for row in get_budget_status(db, days=days, user_id=user_id)]


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
    # Общий котёл требует права на него — одна проверка на все сущности
    # (`_guards.ensure_can_share`), четыре копии разошлись бы при первой правке.
    ensure_can_share(db, payload.household_id, user_id)
    # POST здесь upsert: у существующей строки владение не меняется, а запрос
    # на смену отклоняется явно, а не выполняется наполовину.
    ensure_scope_unchanged(db, payload.category, payload.household_id, user_id)
    budget = create_budget(
        db,
        category=payload.category,
        limit_amount=payload.limit_amount,
        user_id=user_id,
        household_id=payload.household_id,
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


@router.post(
    "/{budget_id}/restore",
    response_model=BudgetResponse,
    summary="Восстановить удалённый бюджет (undo)",
)
def restore_budget_endpoint(
    budget_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> BudgetResponse:
    budget = restore_budget(db, budget_id, user_id=user_id)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Удалённый бюджет не найден."
        )
    log_event("budget_restored", {"budget_id": budget_id})
    return budget
