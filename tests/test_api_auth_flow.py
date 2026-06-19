"""Функциональные тесты аутентификации (полный флоу через API)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, password: str = "password123") -> dict:
    return client.post("/api/auth/register", json={
        "email": email, "password": password, "consent": True}).json()


def test_register_returns_token(client: TestClient) -> None:
    resp = client.post("/api/auth/register", json={
        "email": "reg1@fp.io", "password": "password123", "consent": True})
    assert resp.status_code == 201
    assert resp.json()["access_token"]


def test_register_weak_password_rejected(client: TestClient) -> None:
    resp = client.post("/api/auth/register", json={
        "email": "weak@fp.io", "password": "123", "consent": True})
    assert resp.status_code == 422


def test_register_duplicate_email_rejected(client: TestClient) -> None:
    client.post("/api/auth/register", json={
        "email": "dup@fp.io", "password": "password123", "consent": True})
    second = client.post("/api/auth/register", json={
        "email": "dup@fp.io", "password": "password123", "consent": True})
    assert second.status_code in (400, 409)


def test_login_correct_and_wrong(client: TestClient) -> None:
    _register(client, "login@fp.io")
    ok = client.post("/api/auth/login", json={"email": "login@fp.io", "password": "password123"})
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    wrong = client.post("/api/auth/login", json={"email": "login@fp.io", "password": "wrongpass"})
    assert wrong.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    token = _register(client, "me@fp.io")["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "me@fp.io"


def test_logout(client: TestClient) -> None:
    token = _register(client, "logout@fp.io")["access_token"]
    resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_resend_verification(client: TestClient) -> None:
    _register(client, "resend@fp.io")
    resp = client.post("/api/auth/resend-verification", json={"email": "resend@fp.io"})
    assert resp.status_code == 200


def test_change_password(client: TestClient) -> None:
    token = _register(client, "chpwd@fp.io")["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    ok = client.post("/api/auth/change-password", headers=h, json={
        "current_password": "password123", "new_password": "newpassword456"})
    assert ok.status_code == 200

    # старый пароль больше не работает, новый — работает
    assert client.post("/api/auth/login", json={
        "email": "chpwd@fp.io", "password": "password123"}).status_code == 401
    assert client.post("/api/auth/login", json={
        "email": "chpwd@fp.io", "password": "newpassword456"}).status_code == 200


def test_change_password_wrong_current(client: TestClient) -> None:
    token = _register(client, "chpwd2@fp.io")["access_token"]
    resp = client.post("/api/auth/change-password",
                       headers={"Authorization": f"Bearer {token}"},
                       json={"current_password": "wrongcurrent", "new_password": "newpassword456"})
    assert resp.status_code in (400, 401)
