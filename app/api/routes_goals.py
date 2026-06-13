from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.crud import create_goal, delete_goal, get_goals
from app.dependencies import get_db
from app.schemas.goal import GoalCreate, GoalResponse


router = APIRouter(tags=["Цели"])


@router.get(
    "/goals",
    response_model=list[GoalResponse],
    summary="Получить список целей",
)
def get_goals_endpoint(
    db: Session = Depends(get_db),
) -> list[GoalResponse]:
    return get_goals(db)


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать цель",
)
def create_goal_endpoint(
    payload: GoalCreate,
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = create_goal(
        db=db,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        comment=payload.comment,
    )
    return goal


@router.delete(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Удалить цель",
)
def delete_goal_endpoint(
    goal_id: int,
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = delete_goal(db=db, goal_id=goal_id)
    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена.",
        )
    return goal
