"""Реферальная программа (P3.2)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.crud import count_referrals, ensure_referral_code
from app.database.models import User
from app.dependencies import get_db, require_user

router = APIRouter(prefix="/referral", tags=["Рефералы"])


@router.get("/me", summary="Мой реферальный код и статистика приглашений")
def my_referral(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    code = ensure_referral_code(db, user)
    return {
        "referral_code": code,
        "invited_count": count_referrals(db, code),
        "referred_by": user.referred_by_code,
    }
