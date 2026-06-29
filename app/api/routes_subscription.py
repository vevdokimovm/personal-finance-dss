"""Монетизация (каркас): статус тарифа пользователя.

GET /subscription/me — текущий тариф, признак premium, срок действия и доступные фичи.
Управление тарифом (выдача premium) пока идёт через CRUD/будущий платёжный вебхук, не
через публичный эндпоинт.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.dependencies import require_user
from app.services.subscription import available_features, effective_tier, is_premium

router = APIRouter(prefix="/subscription", tags=["Подписка"])


@router.get("/me", summary="Мой тариф и доступные функции")
def subscription_me(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    return {
        "tier": effective_tier(user).value,
        "is_premium": is_premium(user),
        "expires_at": user.plan_expires_at.isoformat() if user.plan_expires_at else None,
        "features": available_features(user),
    }
