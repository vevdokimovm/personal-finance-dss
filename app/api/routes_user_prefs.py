from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.crud import get_user_prefs, update_user_prefs
from app.dependencies import get_current_user_id, get_db
from app.schemas.user_prefs import UserPrefsResponse, UserPrefsUpdate

router = APIRouter(prefix="/user-prefs", tags=["Параметры пользователя"])


@router.get("", response_model=UserPrefsResponse,
            summary="Параметры пользователя U (Lmin, R, H, r_bench, валюта)")
def read_prefs(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> UserPrefsResponse:
    return get_user_prefs(db, user_id=user_id)


@router.patch("", response_model=UserPrefsResponse, summary="Обновить параметры пользователя")
def patch_prefs(
    payload: UserPrefsUpdate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> UserPrefsResponse:
    return update_user_prefs(
        db,
        l_min=payload.l_min,
        risk_tolerance=payload.risk_tolerance,
        horizon=payload.horizon,
        r_bench=payload.r_bench,
        base_currency=payload.base_currency,
        user_id=user_id,
    )
