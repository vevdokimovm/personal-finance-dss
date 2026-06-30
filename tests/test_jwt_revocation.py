"""JWT-ревокация (SEC-4.4): blacklist по jti + рубеж tokens_valid_since.

Stateless JWT нельзя отозвать по своей природе — он валиден до exp. Два механизма
дают реальный отзыв:
  - blacklist по jti — точечный отзыв одного токена (logout текущей сессии);
  - tokens_valid_since на пользователе — массовый отзыв всех ранее выданных
    токенов (logout-all / смена пароля).

Юнит-слой проверяет модуль `app.database.revocation` напрямую; интеграционный —
реальное поведение через HTTP (logout отзывает, чужие сессии живут, logout-all
валит всё, legacy-токены без jti продолжают работать).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.database.models import RevokedToken, User
from app.database.revocation import (
    bump_tokens_valid_since,
    epoch_to_naive_utc,
    is_token_revoked,
    purge_expired,
    revoke_token,
    tokens_invalidated_for,
)
from app.services.security import token_service
from app.utils.time import utcnow


def _epoch(dt: datetime) -> int:
    """naive-UTC datetime → unix-секунды (так iat/exp приходят из JWT)."""
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def _make_user(db, email: str = "rev@fp.io") -> User:
    user = User(email=email, password_hash="x")
    db.add(user)
    db.commit()
    return user


# --------------------------------------------------------------------------- #
# Юнит: модуль revocation                                                      #
# --------------------------------------------------------------------------- #

def test_is_token_revoked_false_for_unknown(db_session) -> None:
    assert is_token_revoked(db_session, "never-seen-jti") is False


def test_revoke_then_is_revoked(db_session) -> None:
    jti = "jti-abc"
    revoke_token(db_session, jti, utcnow() + timedelta(hours=1))
    assert is_token_revoked(db_session, jti) is True


def test_is_token_revoked_none_jti_is_false(db_session) -> None:
    # Legacy-токен без jti отозвать нельзя — это не ошибка, а обратная совместимость.
    assert is_token_revoked(db_session, None) is False


def test_revoke_token_idempotent(db_session) -> None:
    jti = "jti-dup"
    exp = utcnow() + timedelta(hours=1)
    revoke_token(db_session, jti, exp)
    revoke_token(db_session, jti, exp)  # повтор — не падает, не дублирует
    assert is_token_revoked(db_session, jti) is True
    assert db_session.query(RevokedToken).filter(RevokedToken.jti == jti).count() == 1


def test_purge_expired_removes_only_expired(db_session) -> None:
    revoke_token(db_session, "jti-old", utcnow() - timedelta(hours=1))   # истёк
    revoke_token(db_session, "jti-fresh", utcnow() + timedelta(hours=1))  # живой
    removed = purge_expired(db_session)
    assert removed == 1
    assert is_token_revoked(db_session, "jti-old") is False
    assert is_token_revoked(db_session, "jti-fresh") is True


def test_bump_sets_whole_second_cutoff(db_session) -> None:
    user = _make_user(db_session)
    assert user.tokens_valid_since is None
    before = utcnow()
    bump_tokens_valid_since(db_session, user)
    assert user.tokens_valid_since is not None
    # Рубеж режется до целой секунды (iat в JWT — секундной гранулярности).
    assert user.tokens_valid_since.microsecond == 0
    assert abs((user.tokens_valid_since - before).total_seconds()) < 5


def test_tokens_invalidated_for_no_cutoff(db_session) -> None:
    user = _make_user(db_session, "nc@fp.io")
    assert user.tokens_valid_since is None
    assert tokens_invalidated_for(user, _epoch(utcnow())) is False


def test_tokens_invalidated_for_before_and_after(db_session) -> None:
    user = _make_user(db_session, "ba@fp.io")
    cutoff = utcnow().replace(microsecond=0)
    user.tokens_valid_since = cutoff
    # Токен, выпущенный ДО рубежа, недействителен; выпущенный ПОСЛЕ — годен.
    assert tokens_invalidated_for(user, _epoch(cutoff - timedelta(seconds=30))) is True
    assert tokens_invalidated_for(user, _epoch(cutoff + timedelta(seconds=30))) is False


def test_tokens_invalidated_for_none_iat(db_session) -> None:
    user = _make_user(db_session, "ni@fp.io")
    user.tokens_valid_since = utcnow()
    assert tokens_invalidated_for(user, None) is False


def test_epoch_to_naive_utc_normalizes_inputs() -> None:
    # unix-секунды → naive-UTC; aware-datetime → tzinfo снят (контракт ADR-002).
    aware = datetime(2026, 6, 30, 12, 0, 0, tzinfo=timezone.utc)
    from_epoch = epoch_to_naive_utc(int(aware.timestamp()))
    assert from_epoch.tzinfo is None
    assert from_epoch == aware.replace(tzinfo=None)
    assert epoch_to_naive_utc(aware).tzinfo is None


# --------------------------------------------------------------------------- #
# Интеграция: HTTP-поведение                                                   #
# --------------------------------------------------------------------------- #

def _register(client: TestClient, email: str, password: str = "password123") -> str:
    resp = client.post("/api/auth/register", json={
        "email": email, "password": password, "consent": True})
    assert resp.status_code == 201
    return resp.json()["access_token"]


def _login(client: TestClient, email: str, password: str = "password123") -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_issued_token_carries_jti(client: TestClient) -> None:
    token = _register(client, "jti-present@fp.io")
    payload = token_service.decode(token)
    assert payload is not None
    jti = payload.get("jti")
    assert isinstance(jti, str) and len(jti) == 32  # uuid4().hex


def test_logout_revokes_current_token(client: TestClient) -> None:
    token = _register(client, "revoke-me@fp.io")
    h = {"Authorization": f"Bearer {token}"}
    # До logout токен работает.
    assert client.get("/api/auth/me", headers=h).status_code == 200
    assert client.post("/api/auth/logout", headers=h).status_code == 200
    # После logout тот же токен мёртв.
    assert client.get("/api/auth/me", headers=h).status_code == 401


def test_logout_does_not_kill_other_sessions(client: TestClient) -> None:
    _register(client, "multi@fp.io")
    token_a = _login(client, "multi@fp.io")
    token_b = _login(client, "multi@fp.io")
    # Гасим только сессию A.
    assert client.post("/api/auth/logout",
                       headers={"Authorization": f"Bearer {token_a}"}).status_code == 200
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_a}"}).status_code == 401
    # Сессия B жива.
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_b}"}).status_code == 200


def test_logout_all_kills_every_session(client: TestClient) -> None:
    # Текущая сессия (только что вошли).
    token_current = _register(client, "nuke@fp.io")
    payload = token_service.decode(token_current)
    # «Другое устройство» — сессия, открытая РАНЬШЕ (так это и бывает в реале:
    # два устройства не входят в ту же секунду, что и сам logout-all). Куём токен
    # с iat в прошлом, как выдал бы более ранний логин.
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    token_other = jwt.encode(
        {"sub": payload["sub"], "email": payload["email"], "jti": uuid.uuid4().hex,
         "iat": past, "exp": past + timedelta(hours=12)},
        settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM,
    )
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_other}"}).status_code == 200
    # logout-all валит всё: текущий — по jti, более ранний — по рубежу.
    assert client.post("/api/auth/logout-all",
                       headers={"Authorization": f"Bearer {token_current}"}).status_code == 200
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_current}"}).status_code == 401
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_other}"}).status_code == 401


def test_login_after_logout_all_works(client: TestClient) -> None:
    _register(client, "relogin@fp.io")
    token_old = _login(client, "relogin@fp.io")
    client.post("/api/auth/logout-all", headers={"Authorization": f"Bearer {token_old}"})
    # Свежий логин выдаёт рабочий токен (рубеж режется по секундам — re-login проходит).
    token_new = _login(client, "relogin@fp.io")
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {token_new}"}).status_code == 200


def test_logout_all_requires_auth(client: TestClient) -> None:
    assert client.post("/api/auth/logout-all").status_code == 401


def test_logout_is_safe_without_token(client: TestClient) -> None:
    # Logout без валидной сессии не должен падать — просто чистит cookie.
    assert client.post("/api/auth/logout").status_code == 200


def test_legacy_token_without_jti_still_valid(client: TestClient) -> None:
    # Токены, выпущенные ДО появления jti, обязаны продолжать работать.
    token = _register(client, "legacy@fp.io")
    payload = token_service.decode(token)
    now = datetime.now(timezone.utc)
    legacy = jwt.encode(
        {"sub": payload["sub"], "email": payload["email"],
         "iat": now, "exp": now + timedelta(hours=1)},
        settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM,
    )
    assert "jti" not in jwt.decode(legacy, settings.JWT_SECRET,
                                   algorithms=[settings.JWT_ALGORITHM])
    assert client.get("/api/auth/me",
                      headers={"Authorization": f"Bearer {legacy}"}).status_code == 200
