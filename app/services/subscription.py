"""Монетизация (каркас): тарифы и feature-gating.

Подготовка к платным функциям без платёжной интеграции. Даёт:
- PlanTier — перечисление тарифов;
- effective_tier/is_premium — эффективный тариф пользователя с учётом срока действия
  (premium с истёкшим plan_expires_at трактуется как free);
- FEATURES — реестр фич с требуемым тарифом + has_feature/available_features.

Конкретный набор premium-фич ниже — каркасный placeholder: реальное разделение
free/premium определится при запуске монетизации. Здесь важен рабочий механизм, а не
продуктовый список. Фича, не указанная в реестре, считается бесплатной (доступна всем).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from app.database.models import User


class PlanTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


# Реестр фич → минимальный тариф для доступа. Placeholder-каркас (см. модульный docstring).
FEATURES: dict[str, "PlanTier"] = {
    "advanced_analytics": PlanTier.PREMIUM,
    "priority_support": PlanTier.PREMIUM,
    "unlimited_scenarios": PlanTier.PREMIUM,
}


def effective_tier(user: User) -> PlanTier:
    """Текущий тариф пользователя с учётом срока. Premium с истёкшим сроком = free."""
    if user.plan_tier == PlanTier.PREMIUM.value:
        expires = user.plan_expires_at
        if expires is None or expires > datetime.utcnow():
            return PlanTier.PREMIUM
    return PlanTier.FREE


def is_premium(user: User) -> bool:
    return effective_tier(user) == PlanTier.PREMIUM


def has_feature(user: User, feature_key: str) -> bool:
    """Доступна ли фича пользователю. Фича не из реестра — бесплатна (доступна всем)."""
    required = FEATURES.get(feature_key)
    if required is None or required == PlanTier.FREE:
        return True
    return is_premium(user)


def available_features(user: User) -> list[str]:
    """Ключи фич, доступных пользователю на его тарифе."""
    return [key for key in FEATURES if has_feature(user, key)]
