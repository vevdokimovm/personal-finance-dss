"""Реферальная программа (P3.2) + награды/вехи (P3.4)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.crud import count_referrals, ensure_referral_code
from app.database.models import User
from app.dependencies import get_db, require_user
from app.services.referral import next_milestone, referral_milestones

router = APIRouter(prefix="/referral", tags=["Рефералы"])


@router.get("/me", summary="Мой реферальный код, ссылка-приглашение, статистика и вехи")
def my_referral(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    code = ensure_referral_code(db, user)
    invited = count_referrals(db, code)
    invite_url = str(request.base_url).rstrip("/") + f"/register?ref={code}"
    return {
        "referral_code": code,
        "invite_url": invite_url,
        "invited_count": invited,
        "referred_by": user.referred_by_code,
        "milestones": referral_milestones(invited),
        "next_milestone": next_milestone(invited),
    }
