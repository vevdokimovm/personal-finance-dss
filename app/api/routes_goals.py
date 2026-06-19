from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import create_goal, delete_goal, get_goals
from app.dependencies import get_current_user_id, get_db
from app.schemas.goal import GoalCreate, GoalResponse
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
    goal = create_goal(
        db,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        category=payload.category.value,
        comment=payload.comment,
        priority=payload.priority,
        user_id=user_id,
    )
    log_event("goal_created", {
        "category": payload.category.value,
        "target_amount": payload.target_amount,
    })
    return goal


@router.delete(
    "/{goal_id}",
    summary="Удалить цель",
)
def delete_goal_endpoint(goal_id: int, db: Session = Depends(get_db)):
    if delete_goal(db, goal_id) is None:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
