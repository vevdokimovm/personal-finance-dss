"""Монетизация: каркас тарифов и feature-gating (подготовка к платным функциям).

Продукт на старте бесплатный, но структура заложена, чтобы подключить платно быстро:
тариф пользователя (free/premium) со сроком действия + механизм проверки «доступна ли
фича на тарифе». Платёжной интеграции здесь нет — только структура и логика.

Ключевые свойства:
1. Эффективный тариф учитывает срок: premium с истёкшим plan_expires_at = free.
2. Feature-gating: фича из реестра с тарифом PREMIUM недоступна free-пользователю;
   фича не из реестра доступна всем (по умолчанию бесплатна).
3. grant_premium_days продлевает накопительно (от текущего срока, если он активен) —
   под будущую привязку к реферальным наградам и платежам.

Конкретный список premium-фич — каркасный placeholder (реальное разделение определится
при запуске монетизации); тесты проверяют сам механизм, не продуктовый набор фич.
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.database import crud
from app.database.db import SessionLocal
from app.database.models import User
from app.services.subscription import (
    PlanTier,
    available_features,
    effective_tier,
    has_feature,
    is_premium,
)
from app.utils.time import utcnow


# ─────────────────────────── helpers ───────────────────────────

def _user(db, email: str, tier: str = "free", expires=None) -> User:
    u = crud.create_user(db, email=email, password_hash="x")
    if tier != "free" or expires is not None:
        u.plan_tier = tier
        u.plan_expires_at = expires
        db.commit()
        db.refresh(u)
    return u


def _premium_feature() -> str:
    """Любая фича, помеченная в реестре как PREMIUM (для проверки механизма)."""
    from app.services.subscription import FEATURES
    for key, tier in FEATURES.items():
        if tier == PlanTier.PREMIUM:
            return key
    pytest.skip("в реестре нет premium-фич")


# ─────────────────────── эффективный тариф ───────────────────────

class TestEffectiveTier:
    def test_new_user_is_free(self, db_session) -> None:
        u = _user(db_session, "sub_new@test.io")
        assert effective_tier(u) == PlanTier.FREE
        assert is_premium(u) is False

    def test_premium_no_expiry(self, db_session) -> None:
        u = _user(db_session, "sub_prem@test.io", tier="premium", expires=None)
        assert effective_tier(u) == PlanTier.PREMIUM
        assert is_premium(u) is True

    def test_premium_future_expiry(self, db_session) -> None:
        u = _user(db_session, "sub_future@test.io", tier="premium",
                  expires=utcnow() + timedelta(days=10))
        assert is_premium(u) is True

    def test_premium_expired_is_free(self, db_session) -> None:
        # Premium с истёкшим сроком деградирует до free.
        u = _user(db_session, "sub_expired@test.io", tier="premium",
                  expires=utcnow() - timedelta(days=1))
        assert effective_tier(u) == PlanTier.FREE
        assert is_premium(u) is False


# ─────────────────────── feature-gating ───────────────────────

class TestFeatures:
    def test_premium_feature_blocked_for_free(self, db_session) -> None:
        u = _user(db_session, "feat_free@test.io")
        assert has_feature(u, _premium_feature()) is False

    def test_premium_feature_allowed_for_premium(self, db_session) -> None:
        u = _user(db_session, "feat_prem@test.io", tier="premium")
        assert has_feature(u, _premium_feature()) is True

    def test_unknown_feature_allowed_for_all(self, db_session) -> None:
        # Фича не из реестра считается бесплатной — доступна всем.
        u = _user(db_session, "feat_unknown@test.io")
        assert has_feature(u, "nonexistent_feature_xyz") is True

    def test_available_features_premium_superset(self, db_session) -> None:
        free_u = _user(db_session, "feat_av_free@test.io")
        prem_u = _user(db_session, "feat_av_prem@test.io", tier="premium")
        free_set = set(available_features(free_u))
        prem_set = set(available_features(prem_u))
        assert free_set.issubset(prem_set)


# ─────────────────────── CRUD тарифа ───────────────────────

class TestSetPlan:
    def test_set_plan(self, db_session) -> None:
        db = db_session
        u = _user(db, "setplan@test.io")
        crud.set_plan(db, u.id, "premium", expires_at=utcnow() + timedelta(days=30))
        db.refresh(u)
        assert u.plan_tier == "premium"
        assert is_premium(u) is True

    def test_grant_premium_days_from_free(self, db_session) -> None:
        db = db_session
        u = _user(db, "grant_free@test.io")
        crud.grant_premium_days(db, u.id, 30)
        db.refresh(u)
        assert is_premium(u) is True
        assert u.plan_expires_at > utcnow() + timedelta(days=29)

    def test_grant_premium_days_accumulates(self, db_session) -> None:
        # Повторное продление активного premium считается от текущего срока, не от now.
        db = db_session
        u = _user(db, "grant_acc@test.io", tier="premium",
                  expires=utcnow() + timedelta(days=10))
        crud.grant_premium_days(db, u.id, 30)
        db.refresh(u)
        # Было ~10 дней, добавили 30 → около 40, не 30.
        assert u.plan_expires_at > utcnow() + timedelta(days=35)


# ─────────────────────── require_premium dependency ───────────────────────

class TestRequirePremium:
    def test_blocks_free_user(self, db_session) -> None:
        from app.dependencies import require_premium

        u = _user(db_session, "req_free@test.io")
        with pytest.raises(HTTPException) as exc:
            require_premium(user=u)
        assert exc.value.status_code == 403

    def test_allows_premium_user(self, db_session) -> None:
        from app.dependencies import require_premium

        u = _user(db_session, "req_prem@test.io", tier="premium")
        assert require_premium(user=u) is u


# ─────────────────────── эндпоинт /subscription/me ───────────────────────

class TestSubscriptionEndpoint:
    def _register(self, client, email: str) -> str:
        r = client.post("/api/auth/register",
                        json={"email": email, "password": "password123", "consent": True})
        assert r.status_code == 201, r.text
        return r.json()["access_token"]

    def _uid(self, email: str) -> str:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first().id
        finally:
            db.close()

    def test_me_free_by_default(self, client) -> None:
        token = self._register(client, "sub_me_free@test.io")
        r = client.get("/api/subscription/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["tier"] == "free"
        assert data["is_premium"] is False
        assert "features" in data

    def test_me_reflects_premium(self, client) -> None:
        token = self._register(client, "sub_me_prem@test.io")
        uid = self._uid("sub_me_prem@test.io")
        db = SessionLocal()
        try:
            crud.set_plan(db, uid, "premium", expires_at=utcnow() + timedelta(days=30))
        finally:
            db.close()
        r = client.get("/api/subscription/me", headers={"Authorization": f"Bearer {token}"})
        data = r.json()
        assert data["tier"] == "premium"
        assert data["is_premium"] is True

    def test_me_requires_auth(self, client) -> None:
        assert client.get("/api/subscription/me").status_code == 401
