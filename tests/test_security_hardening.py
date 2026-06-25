"""Усиление безопасности (P1.2).

Покрывает три рубежа:
A. Fail-loud конфигурация: в production приложение не стартует с дефолтными секретами
   или незащищённой cookie.
B. Account lockout: после серии неудачных входов аккаунт временно блокируется
   (защита от перебора пароля поверх глобального rate-limit).
C. Валидация сумм (BUG-018): отрицательные денежные значения отклоняются на входе.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, settings, validate_production_security


# ── A. Fail-loud конфигурация для production ──────────────────────────

class TestProductionConfigGuard:
    def test_default_secret_in_production_flagged(self) -> None:
        s = Settings(ENVIRONMENT="production")  # JWT_SECRET дефолтный
        problems = validate_production_security(s)
        assert problems
        assert any("JWT_SECRET" in p for p in problems)

    def test_insecure_cookie_in_production_flagged(self) -> None:
        s = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 40, COOKIE_SECURE=False)
        problems = validate_production_security(s)
        assert any("COOKIE_SECURE" in p for p in problems)

    def test_development_not_flagged(self) -> None:
        s = Settings(ENVIRONMENT="development")
        assert validate_production_security(s) == []

    def test_secure_production_passes(self) -> None:
        s = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 40, COOKIE_SECURE=True,
                     ADMIN_API_KEY="y" * 24)
        assert validate_production_security(s) == []


# ── B. Account lockout на /auth/login ─────────────────────────────────

def _register(client: TestClient, email: str = "lock@test.io", password: str = "password123"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": "L",
            "consent": True,
            "newsletter_opt_in": False,
        },
    )


class TestLoginLockout:
    def test_lockout_after_max_attempts(self, client: TestClient) -> None:
        _register(client, email="lock1@test.io")
        for _ in range(settings.LOGIN_MAX_ATTEMPTS):
            r = client.post(
                "/api/auth/login", json={"email": "lock1@test.io", "password": "wrong"}
            )
            assert r.status_code == 401
        # Даже верный пароль не пройдёт, пока действует блокировка.
        r = client.post(
            "/api/auth/login", json={"email": "lock1@test.io", "password": "password123"}
        )
        assert r.status_code == 429

    def test_successful_login_resets_counter(self, client: TestClient) -> None:
        _register(client, email="reset@test.io")
        for _ in range(settings.LOGIN_MAX_ATTEMPTS - 1):
            client.post("/api/auth/login", json={"email": "reset@test.io", "password": "wrong"})
        r = client.post(
            "/api/auth/login", json={"email": "reset@test.io", "password": "password123"}
        )
        assert r.status_code == 200
        # Счётчик сброшен: одна ошибка снова даёт 401, а не мгновенный 429.
        r = client.post("/api/auth/login", json={"email": "reset@test.io", "password": "wrong"})
        assert r.status_code == 401

    def test_correct_password_before_lockout(self, client: TestClient) -> None:
        _register(client, email="ok@test.io")
        r = client.post(
            "/api/auth/login", json={"email": "ok@test.io", "password": "password123"}
        )
        assert r.status_code == 200


# ── C. Валидация сумм (BUG-018) ───────────────────────────────────────

class TestAmountValidation:
    def test_negative_goal_target_rejected(self, client: TestClient) -> None:
        _register(client, email="g@test.io")
        r = client.post(
            "/api/goals",
            json={"name": "G", "target_amount": -1000, "deadline": "2027-01-01T00:00:00"},
        )
        assert r.status_code == 422

    def test_negative_obligation_amount_rejected(self, client: TestClient) -> None:
        _register(client, email="o@test.io")
        r = client.post(
            "/api/obligations",
            json={"name": "O", "amount": -5000, "monthly_payment": 1000},
        )
        assert r.status_code == 422

    def test_valid_goal_accepted(self, client: TestClient) -> None:
        _register(client, email="gv@test.io")
        r = client.post(
            "/api/goals",
            json={"name": "G", "target_amount": 100000, "deadline": "2027-01-01T00:00:00"},
        )
        assert r.status_code in (200, 201)


class TestCalculateRateLimited:
    """calculate/forecast (дорогие Monte Carlo пути) — под rate-лимитом (P0.4 hardening)."""

    def _mw(self):
        from app.main import RATE_LIMITED_PREFIXES
        from app.middleware import RateLimitMiddleware

        return RateLimitMiddleware(
            app=None, limit=30, window_seconds=60, protected_prefixes=RATE_LIMITED_PREFIXES
        )

    def test_calculate_is_protected(self) -> None:
        assert self._mw()._is_protected("/api/planning/calculate")

    def test_forecast_is_protected(self) -> None:
        assert self._mw()._is_protected("/api/planning/forecast")

    def test_light_planning_not_protected(self) -> None:
        mw = self._mw()
        assert not mw._is_protected("/api/planning/key-rate")
        assert not mw._is_protected("/api/planning/scenarios")
