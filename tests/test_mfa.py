"""MFA/TOTP — двухфакторная аутентификация (SEC-4.4).

Поток: enroll (генерим секрет) → confirm (подтверждаем кодом, активируем, выдаём
recovery-коды) → при логине вместо сессии выдаётся промежуточный mfa_pending-токен →
verify (TOTP или recovery-код) обменивает его на полную сессию. disable выключает.

Секрет хранится зашифрованно (`EncryptedString`), recovery-коды — хешированными.
Промежуточный mfa_pending-токен (как и любой purpose-токен) НЕ даёт доступа к сессии.
"""
from __future__ import annotations

import pyotp
from fastapi.testclient import TestClient

from app.services.security import token_service


def _register(client: TestClient, email: str, password: str = "password123") -> str:
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()["access_token"]


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _enroll(client: TestClient, token: str) -> str:
    r = client.post("/api/auth/mfa/enroll", headers=_bearer(token))
    assert r.status_code == 200
    return r.json()["secret"]


def _enable_mfa(client: TestClient, token: str) -> tuple[str, list[str]]:
    """Полный enroll+confirm; возвращает (secret, recovery_codes)."""
    secret = _enroll(client, token)
    code = pyotp.TOTP(secret).now()
    r = client.post("/api/auth/mfa/confirm", json={"code": code}, headers=_bearer(token))
    assert r.status_code == 200
    return secret, r.json()["recovery_codes"]


# ── Enroll / confirm ──────────────────────────────────────────────────────

def test_enroll_returns_secret_and_uri(client: TestClient) -> None:
    token = _register(client, "enroll@fp.io")
    r = client.post("/api/auth/mfa/enroll", headers=_bearer(token))
    assert r.status_code == 200
    body = r.json()
    assert len(body["secret"]) >= 16
    assert body["provisioning_uri"].startswith("otpauth://totp/")


def test_confirm_valid_code_enables_and_returns_recovery(client: TestClient) -> None:
    token = _register(client, "confirm@fp.io")
    secret, codes = _enable_mfa(client, token)
    assert len(codes) == 10
    status = client.get("/api/auth/mfa/status", headers=_bearer(token))
    assert status.json()["enabled"] is True


def test_confirm_invalid_code_rejected(client: TestClient) -> None:
    token = _register(client, "badconfirm@fp.io")
    _enroll(client, token)
    r = client.post("/api/auth/mfa/confirm", json={"code": "000000"}, headers=_bearer(token))
    assert r.status_code == 400
    status = client.get("/api/auth/mfa/status", headers=_bearer(token))
    assert status.json()["enabled"] is False


# ── Login с MFA: промежуточный токен вместо сессии ────────────────────────

def test_login_with_mfa_returns_pending_not_session(client: TestClient) -> None:
    token = _register(client, "mfalogin@fp.io")
    _enable_mfa(client, token)
    r = client.post("/api/auth/login",
                    json={"email": "mfalogin@fp.io", "password": "password123"})
    assert r.status_code == 200
    body = r.json()
    assert body["mfa_required"] is True
    assert body["mfa_token"]
    assert not body["access_token"]  # полной сессии ещё нет
    # mfa_token не должен авторизовать как сессия.
    assert client.get("/api/auth/me", headers=_bearer(body["mfa_token"])).status_code == 401


def test_verify_with_totp_issues_session(client: TestClient) -> None:
    token = _register(client, "verify@fp.io")
    secret, _ = _enable_mfa(client, token)
    login = client.post("/api/auth/login",
                        json={"email": "verify@fp.io", "password": "password123"}).json()
    code = pyotp.TOTP(secret).now()
    r = client.post("/api/auth/mfa/verify",
                    json={"mfa_token": login["mfa_token"], "code": code})
    assert r.status_code == 200
    session = r.json()["access_token"]
    assert session
    assert client.get("/api/auth/me", headers=_bearer(session)).status_code == 200


def test_verify_with_recovery_code_is_single_use(client: TestClient) -> None:
    token = _register(client, "recov@fp.io")
    _, codes = _enable_mfa(client, token)
    login = client.post("/api/auth/login",
                        json={"email": "recov@fp.io", "password": "password123"}).json()
    # Первое использование recovery-кода проходит.
    r1 = client.post("/api/auth/mfa/verify",
                     json={"mfa_token": login["mfa_token"], "code": codes[0]})
    assert r1.status_code == 200
    # Повторное использование того же кода — отказ (одноразовый).
    login2 = client.post("/api/auth/login",
                         json={"email": "recov@fp.io", "password": "password123"}).json()
    r2 = client.post("/api/auth/mfa/verify",
                     json={"mfa_token": login2["mfa_token"], "code": codes[0]})
    assert r2.status_code == 401


def test_verify_wrong_code_rejected(client: TestClient) -> None:
    token = _register(client, "wrongverify@fp.io")
    _enable_mfa(client, token)
    login = client.post("/api/auth/login",
                        json={"email": "wrongverify@fp.io", "password": "password123"}).json()
    r = client.post("/api/auth/mfa/verify",
                    json={"mfa_token": login["mfa_token"], "code": "000000"})
    assert r.status_code == 401


# ── Disable ───────────────────────────────────────────────────────────────

def test_disable_mfa_restores_plain_login(client: TestClient) -> None:
    token = _register(client, "disable@fp.io")
    secret, _ = _enable_mfa(client, token)
    code = pyotp.TOTP(secret).now()
    r = client.post("/api/auth/mfa/disable", json={"code": code}, headers=_bearer(token))
    assert r.status_code == 200
    assert client.get("/api/auth/mfa/status",
                      headers=_bearer(token)).json()["enabled"] is False
    # После выключения логин снова сразу выдаёт сессию.
    login = client.post("/api/auth/login",
                        json={"email": "disable@fp.io", "password": "password123"}).json()
    assert login["access_token"]
    assert login["mfa_required"] is False


# ── purpose-токены не дают сессии (закрытие дыры) ─────────────────────────

def test_mfa_pending_token_rejected_as_session(client: TestClient) -> None:
    _register(client, "pending@fp.io")
    payload = token_service.decode(
        client.post("/api/auth/login",
                    json={"email": "pending@fp.io", "password": "password123"}
                    ).json()["access_token"])
    mfa_token = token_service.issue_mfa_pending(payload["sub"], payload["email"])
    assert client.get("/api/auth/me", headers=_bearer(mfa_token)).status_code == 401


def test_password_reset_token_rejected_as_session(client: TestClient) -> None:
    """purpose-токен (reset) не должен авторизовать как сессия."""
    _register(client, "purpose@fp.io")
    payload = token_service.decode(
        client.post("/api/auth/login",
                    json={"email": "purpose@fp.io", "password": "password123"}
                    ).json()["access_token"])
    reset_token = token_service.issue_password_reset(payload["sub"], payload["email"])
    assert client.get("/api/auth/me", headers=_bearer(reset_token)).status_code == 401
