"""Восстановление пароля (P1.3).

Запрос сброса не раскрывает, существует ли email (защита от энумерации).
Установка нового пароля принимает только токен с назначением password_reset,
заодно снимает блокировку аккаунта. В dev (без SMTP) ссылка возвращается в
ответе, чтобы поток можно было пройти локально.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import settings


def _register(client: TestClient, email: str = "r@pwd.io", password: str = "oldpassword123"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": "R",
            "consent": True,
            "newsletter_opt_in": False,
        },
    )


class TestForgotPassword:
    def test_existing_email_returns_reset_link_in_dev(self, client: TestClient) -> None:
        _register(client, email="exists@pwd.io")
        r = client.post("/api/auth/forgot-password", json={"email": "exists@pwd.io"})
        assert r.status_code == 200
        assert r.json().get("reset_url")

    def test_unknown_email_does_not_reveal(self, client: TestClient) -> None:
        r = client.post("/api/auth/forgot-password", json={"email": "nobody@pwd.io"})
        assert r.status_code == 200
        assert r.json().get("reset_url") is None


class TestResetPassword:
    def _get_token(self, client: TestClient, email: str) -> str:
        forgot = client.post("/api/auth/forgot-password", json={"email": email})
        return forgot.json()["reset_url"].split("token=")[-1]

    def test_reset_changes_password(self, client: TestClient) -> None:
        _register(client, email="change@pwd.io", password="oldpassword123")
        token = self._get_token(client, "change@pwd.io")

        r = client.post(
            "/api/auth/reset-password",
            json={"token": token, "new_password": "brandnewpass456"},
        )
        assert r.status_code == 200

        old = client.post(
            "/api/auth/login", json={"email": "change@pwd.io", "password": "oldpassword123"}
        )
        assert old.status_code == 401
        new = client.post(
            "/api/auth/login", json={"email": "change@pwd.io", "password": "brandnewpass456"}
        )
        assert new.status_code == 200

    def test_invalid_token_rejected(self, client: TestClient) -> None:
        r = client.post(
            "/api/auth/reset-password",
            json={"token": "garbage.token.value", "new_password": "whatever12345"},
        )
        assert r.status_code == 400

    def test_access_token_not_accepted_as_reset(self, client: TestClient) -> None:
        reg = _register(client, email="purpose@pwd.io")
        access = reg.json()["access_token"]
        r = client.post(
            "/api/auth/reset-password",
            json={"token": access, "new_password": "whatever12345"},
        )
        assert r.status_code == 400

    def test_reset_clears_lockout(self, client: TestClient) -> None:
        _register(client, email="locked@pwd.io", password="oldpassword123")
        for _ in range(settings.LOGIN_MAX_ATTEMPTS):
            client.post("/api/auth/login", json={"email": "locked@pwd.io", "password": "wrong"})
        token = self._get_token(client, "locked@pwd.io")
        client.post(
            "/api/auth/reset-password",
            json={"token": token, "new_password": "freshpass789"},
        )
        r = client.post(
            "/api/auth/login", json={"email": "locked@pwd.io", "password": "freshpass789"}
        )
        assert r.status_code == 200
