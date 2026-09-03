"""Реферальная программа (P3.2) + награды/вехи (P3.4)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.crud import count_referrals, ensure_referral_code
from app.database.models import User
from app.dependencies import get_db, require_user
from app.services.referral import next_milestone, referral_milestones

router = APIRouter(prefix="/referral", tags=["Рефералы"])


class ReferralMilestone(BaseModel):
    """Веха реферальной программы. `reward` зарезервирован под механику наград и
    пока всегда `None` — сознательно не выдумываем начисление до монетизации."""

    threshold: int
    title: str
    reward: str | None = None
    reached: bool


class ReferralNextMilestone(BaseModel):
    """Ближайшая недостигнутая веха и сколько приглашений до неё."""

    threshold: int
    title: str
    remaining: int


class ReferralMe(BaseModel):
    """Ответ `/referral/me`.

    Схема заведена ДО фронта (v8.37.0): раньше эндпоинт был размечен `-> dict`, то есть
    в OpenAPI попадал как `{[key: string]: unknown}`. Фронту оставалось бы писать
    рукописный тип и каст — ровно так родился дефект v8.31.1, когда рукописный тип
    пообещал поля, которых схема не требует, и экран упал в error boundary.

    `referred_by` и `next_milestone` необязательны честно: первый пуст у того, кто
    пришёл сам, второй — `None`, когда все вехи достигнуты.
    """

    referral_code: str
    invite_url: str
    invited_count: int
    referred_by: str | None = None
    milestones: list[ReferralMilestone]
    next_milestone: ReferralNextMilestone | None = None


@router.get("/me", summary="Мой реферальный код, ссылка-приглашение, статистика и вехи")
def my_referral(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> ReferralMe:
    code = ensure_referral_code(db, user)
    invited = count_referrals(db, code)
    invite_url = str(request.base_url).rstrip("/") + f"/register?ref={code}"
    upcoming = next_milestone(invited)
    return ReferralMe(
        referral_code=code,
        invite_url=invite_url,
        invited_count=invited,
        referred_by=user.referred_by_code,
        milestones=[ReferralMilestone(**m) for m in referral_milestones(invited)],
        next_milestone=ReferralNextMilestone(**upcoming) if upcoming else None,
    )
