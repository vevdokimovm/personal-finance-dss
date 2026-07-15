"""Реферальная программа (P3.2)."""
from __future__ import annotations

from app.database import crud


def _register(client, email, referral_code=None):
    payload = {"email": email, "password": "password123", "consent": True}
    if referral_code is not None:
        payload["referral_code"] = referral_code
    return client.post("/api/auth/register", json=payload)


class TestReferralCodeGeneration:
    def test_create_user_gets_code(self, db_session) -> None:
        u = crud.create_user(db_session, email="ref1@test.io", password_hash="x")
        assert u.referral_code is not None
        assert len(u.referral_code) == 8

    def test_codes_are_unique(self, db_session) -> None:
        a = crud.create_user(db_session, email="a@test.io", password_hash="x")
        b = crud.create_user(db_session, email="b@test.io", password_hash="x")
        assert a.referral_code != b.referral_code


class TestReferralAttribution:
    def test_valid_referral_recorded(self, db_session) -> None:
        inviter = crud.create_user(db_session, email="inviter@test.io", password_hash="x")
        invited = crud.create_user(
            db_session, email="invited@test.io", password_hash="x",
            referred_by_code=inviter.referral_code,
        )
        assert invited.referred_by_code == inviter.referral_code
        assert crud.count_referrals(db_session, inviter.referral_code) == 1

    def test_count_referrals_multiple(self, db_session) -> None:
        inviter = crud.create_user(db_session, email="boss@test.io", password_hash="x")
        for i in range(3):
            crud.create_user(db_session, email=f"u{i}@test.io", password_hash="x",
                             referred_by_code=inviter.referral_code)
        assert crud.count_referrals(db_session, inviter.referral_code) == 3


class TestRegisterEndpoint:
    def test_register_with_valid_code(self, client, db_session) -> None:
        inviter = crud.create_user(db_session, email="host@test.io", password_hash="x")
        r = _register(client, "newbie@test.io", referral_code=inviter.referral_code)
        assert r.status_code == 201
        assert crud.count_referrals(db_session, inviter.referral_code) == 1

    def test_register_with_invalid_code_ignored(self, client, db_session) -> None:
        r = _register(client, "solo@test.io", referral_code="NOTACODE1")
        assert r.status_code == 201
        user = crud.get_user_by_email(db_session, "solo@test.io")
        assert user.referred_by_code is None

    def test_referral_me_endpoint(self, client, db_session) -> None:
        _register(client, "owner@test.io")
        # логинимся, чтобы получить сессию
        login = client.post("/api/auth/login",
                            json={"email": "owner@test.io", "password": "password123"})
        assert login.status_code == 200
        r = client.get("/api/referral/me")
        assert r.status_code == 200
        body = r.json()
        assert body["referral_code"]
        assert body["invited_count"] == 0
