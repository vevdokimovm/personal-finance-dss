"""Инвалидация сессий при смене/сбросе пароля (SEC-4.4, банковская планка).

Финпродукт: смена креденшелов обязана гасить старые сессии. Option A —
симметрично на обоих флоу, бэкенд-only (без координации с фронтом):

  * `/auth/change-password` (пользователь залогинен) — рубеж `tokens_valid_since`
    валит все его сессии, текущий токен дополнительно гасится точечно по jti
    (закрывает sub-секундное окно округления рубежа), auth-cookie чистится →
    клиент уходит в logged-out начисто и переавторизуется.
  * `/auth/reset-password` (пользователь НЕ залогинен, пришёл по reset-токену) —
    рубеж валит все старые сессии с других устройств; вход новым паролем проходит
    сразу (рубеж секундной гранулярности не задевает свежий токен).

Токены «устройств» форжатся с `iat` в прошлом — так рубеж их детерминированно
валит, без зависимости от той же секунды (тот же приём, что в test_jwt_revocation).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.database.crud import get_user_by_email
from app.database.db import SessionLocal
from app.services.security import token_service
from app.utils.time import utcnow


def _register(client: TestClient, email: str, password: str = "password123") -> str:
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()["access_token"]


def _forge(sub: str, email: str, minutes_ago: int) -> str:
    """Токен, как выдал бы более ранний логин: валидный jti, iat в прошлом."""
    issued = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return jwt.encode(
        {
            "sub": sub,
            "email": email,
            "jti": uuid.uuid4().hex,
            "iat": issued,
            "exp": issued + timedelta(hours=12),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _reset_token_for(email: str) -> str:
    db = SessionLocal()
    try:
        user = get_user_by_email(db, email)
        assert user is not None
        return token_service.issue_password_reset(user.id, user.email)
    finally:
        db.close()


def _sub_email(token: str) -> tuple[str, str]:
    payload = token_service.decode(token)
    assert payload is not None
    return payload["sub"], payload["email"]


# ── reset-password: гасит все старые сессии ───────────────────────────────

def test_reset_password_revokes_all_sessions(client: TestClient) -> None:
    token = _register(client, "reset_rev@fp.io")
    sub, email = _sub_email(token)
    device = _forge(sub, email, minutes_ago=5)
    assert client.get("/api/auth/me", headers=_bearer(device)).status_code == 200

    r = client.post(
        "/api/auth/reset-password",
        json={"token": _reset_token_for(email), "new_password": "brandnewpass1"},
    )
    assert r.status_code == 200
    # Рубеж сдвинут — старая сессия мертва.
    assert client.get("/api/auth/me", headers=_bearer(device)).status_code == 401


def test_reset_password_old_password_rejected_new_works(client: TestClient) -> None:
    _register(client, "reset_pw@fp.io")
    client.post(
        "/api/auth/reset-password",
        json={"token": _reset_token_for("reset_pw@fp.io"), "new_password": "brandnewpass1"},
    )
    # Старый пароль больше не подходит, новый — логинит и даёт рабочую сессию.
    assert client.post(
        "/api/auth/login", json={"email": "reset_pw@fp.io", "password": "password123"}
    ).status_code == 401
    fresh = client.post(
        "/api/auth/login", json={"email": "reset_pw@fp.io", "password": "brandnewpass1"}
    )
    assert fresh.status_code == 200
    token = fresh.json()["access_token"]
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 200


# ── change-password: гасит все сессии (включая текущую) + чистит cookie ────

def test_change_password_revokes_all_sessions_including_current(client: TestClient) -> None:
    token = _register(client, "chg_rev@fp.io")
    sub, email = _sub_email(token)
    current = _forge(sub, email, minutes_ago=5)   # устройство-инициатор
    other = _forge(sub, email, minutes_ago=10)    # другое устройство
    assert client.get("/api/auth/me", headers=_bearer(current)).status_code == 200
    assert client.get("/api/auth/me", headers=_bearer(other)).status_code == 200

    r = client.post(
        "/api/auth/change-password",
        json={"current_password": "password123", "new_password": "brandnewpass1"},
        headers=_bearer(current),
    )
    assert r.status_code == 200
    # Обе сессии мертвы: инициатор — точечно по jti, другое устройство — по рубежу.
    assert client.get("/api/auth/me", headers=_bearer(current)).status_code == 401
    assert client.get("/api/auth/me", headers=_bearer(other)).status_code == 401


def test_change_password_clears_auth_cookie(client: TestClient) -> None:
    token = _register(client, "chg_cookie@fp.io")
    sub, email = _sub_email(token)
    current = _forge(sub, email, minutes_ago=5)
    r = client.post(
        "/api/auth/change-password",
        json={"current_password": "password123", "new_password": "brandnewpass1"},
        headers=_bearer(current),
    )
    assert r.status_code == 200
    set_cookie = r.headers.get("set-cookie", "")
    assert settings.AUTH_COOKIE_NAME in set_cookie
    assert ('Max-Age=0' in set_cookie) or ('expires=' in set_cookie.lower())


def test_change_password_new_password_logs_in(client: TestClient) -> None:
    token = _register(client, "chg_pw@fp.io")
    sub, email = _sub_email(token)
    current = _forge(sub, email, minutes_ago=5)
    client.post(
        "/api/auth/change-password",
        json={"current_password": "password123", "new_password": "brandnewpass1"},
        headers=_bearer(current),
    )
    assert client.post(
        "/api/auth/login", json={"email": "chg_pw@fp.io", "password": "password123"}
    ).status_code == 401
    assert client.post(
        "/api/auth/login", json={"email": "chg_pw@fp.io", "password": "brandnewpass1"}
    ).status_code == 200


def test_change_password_wrong_current_keeps_sessions(client: TestClient) -> None:
    """Инвалидация привязана к УСПЕХУ: неверный текущий пароль → 400 и сессия жива
    (рубеж не сдвинут, jti не отозван)."""
    token = _register(client, "chg_wrong@fp.io")
    sub, email = _sub_email(token)
    current = _forge(sub, email, minutes_ago=5)
    assert client.get("/api/auth/me", headers=_bearer(current)).status_code == 200

    r = client.post(
        "/api/auth/change-password",
        json={"current_password": "WRONGpass999", "new_password": "brandnewpass1"},
        headers=_bearer(current),
    )
    assert r.status_code == 400
    # Сессия не тронута.
    assert client.get("/api/auth/me", headers=_bearer(current)).status_code == 200
    db = SessionLocal()
    try:
        user = get_user_by_email(db, "chg_wrong@fp.io")
        assert user.tokens_valid_since is None
    finally:
        db.close()


def test_reset_does_not_affect_other_users(client: TestClient) -> None:
    """Сброс пароля одного пользователя не трогает сессии другого."""
    token_a = _register(client, "iso_a@fp.io")
    _register(client, "iso_b@fp.io")
    sub_b, email_b = _sub_email(_register(client, "iso_b2@fp.io"))
    device_b = _forge(sub_b, email_b, minutes_ago=5)
    assert client.get("/api/auth/me", headers=_bearer(device_b)).status_code == 200

    client.post(
        "/api/auth/reset-password",
        json={"token": _reset_token_for("iso_a@fp.io"), "new_password": "brandnewpass1"},
    )
    # Сессия другого пользователя жива.
    assert client.get("/api/auth/me", headers=_bearer(device_b)).status_code == 200
    # А инициатора — уже невалидна была бы (проверяется в основном тесте); здесь — изоляция.
    _ = token_a
