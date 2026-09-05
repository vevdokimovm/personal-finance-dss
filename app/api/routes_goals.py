from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    add_goal_contribution,
    can_write_household,
    create_goal,
    delete_goal,
    get_goal_by_id,
    get_goals,
    restore_goal,
    update_goal,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas.goal import GoalContributionCreate, GoalCreate, GoalResponse, GoalUpdate
from app.services.event_logger import log_event

router = APIRouter(prefix="/goals", tags=["Цели"])


@router.get("", response_model=list[GoalResponse], summary="Список целей")
def list_goals(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[GoalResponse]:
    return get_goals(db, user_id=user_id)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать цель",
)
def create_goal_endpoint(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> GoalResponse:
    if payload.household_id is not None and not can_write_household(
        db, payload.household_id, user_id
    ):
        raise HTTPException(
            status_code=403, detail="Нет прав на запись в этот household"
        )
    goal = create_goal(
        db,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        category=payload.category.value,
        comment=payload.comment,
        priority=payload.priority,
        savings_rate=payload.savings_rate,
        linked_asset_id=payload.linked_asset_id,
        currency=payload.currency,
        user_id=user_id,
        household_id=payload.household_id,
    )
    # 🔴 `user_id` обязателен: без него событие не попадает в воронку (H7, v8.51.0).
    log_event("goal_created", {
        "category": payload.category.value,
        "target_amount": payload.target_amount,
        "shared": payload.household_id is not None,
    }, user_id=user_id)
    return goal


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Изменить цель (частично; current_amount — отдельным действием)",
)
def update_goal_endpoint(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> GoalResponse:
    fields = payload.model_dump(exclude_unset=True)
    if "category" in fields and fields["category"] is not None:
        fields["category"] = fields["category"].value
    goal = update_goal(db, goal_id, user_id=user_id, **fields)
    if goal is None:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    log_event("goal_updated", {"goal_id": goal_id}, user_id=user_id)
    return goal


@router.post(
    "/{goal_id}/contributions",
    response_model=GoalResponse,
    summary="Внести прогресс в цель (прибавляет к current_amount, не перезаписывает)",
)
def add_goal_contribution_endpoint(
    goal_id: int,
    payload: GoalContributionCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> GoalResponse:
    goal = get_goal_by_id(db, goal_id, user_id=user_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    if goal.linked_asset_id is not None:
        raise HTTPException(
            status_code=409,
            detail="Прогресс цели с привязанным активом выводится из баланса актива "
            "автоматически — вносить его вручную нельзя.",
        )
    updated = add_goal_contribution(db, goal_id, payload.amount, user_id=user_id)
    log_event(
        "goal_contribution_added",
        {"goal_id": goal_id, "amount": payload.amount},
        user_id=user_id,
    )
    return updated


@router.delete(
    "/{goal_id}",
    summary="Удалить цель",
)
def delete_goal_endpoint(
    goal_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
):
    if delete_goal(db, goal_id, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{goal_id}/restore",
    response_model=GoalResponse,
    summary="Восстановить удалённую цель (undo)",
)
def restore_goal_endpoint(
    goal_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> GoalResponse:
    goal = restore_goal(db, goal_id, user_id=user_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Удалённая цель не найдена")
    log_event("goal_restored", {"goal_id": goal_id}, user_id=user_id)
    return goal
