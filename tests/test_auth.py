"""Тесты v3.0.0: аутентификация и изоляция данных по пользователю (INFRA-06, DATA-03)."""
from __future__ import annotations


def _auth_header(client, email: str, password: str = "passwordX1") -> dict[str, str]:
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_register_returns_token_and_user(client):
    r = client.post("/api/auth/register", json={"email": "u1@fp.io", "password": "strongpass1"})
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == "u1@fp.io"


def test_register_duplicate_email_conflict(client):
    client.post("/api/auth/register", json={"email": "dup@fp.io", "password": "strongpass1"})
    r = client.post("/api/auth/register", json={"email": "dup@fp.io", "password": "other12345"})
    assert r.status_code == 409


def test_register_weak_password_rejected(client):
    r = client.post("/api/auth/register", json={"email": "weak@fp.io", "password": "short"})
    assert r.status_code == 422


def test_login_success_and_wrong_password(client):
    client.post("/api/auth/register", json={"email": "log@fp.io", "password": "strongpass1"})
    ok = client.post("/api/auth/login", json={"email": "log@fp.io", "password": "strongpass1"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"email": "log@fp.io", "password": "WRONGPASS"})
    assert bad.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401
    header = _auth_header(client, "me@fp.io")
    r = client.get("/api/auth/me", headers=header)
    assert r.status_code == 200
    assert r.json()["email"] == "me@fp.io"


def test_password_is_hashed_not_plaintext(client):
    from app.database.crud import get_user_by_email
    from app.database.db import SessionLocal

    client.post("/api/auth/register", json={"email": "hash@fp.io", "password": "strongpass1"})
    db = SessionLocal()
    try:
        user = get_user_by_email(db, "hash@fp.io")
        assert user is not None
        assert user.password_hash != "strongpass1"
        assert user.password_hash.startswith("$2")  # bcrypt-префикс
    finally:
        db.close()


def test_new_user_starts_with_clean_account(client):
    # Гость создаёт данные до регистрации
    client.post(
        "/api/transactions",
        json={"amount": 50000, "type": "income", "date": "2026-06-01T00:00:00", "category": "Guest"},
    )
    header = _auth_header(client, "first@fp.io")
    # Новый пользователь не наследует гостевые/демо-данные — аккаунт чистый
    txs = client.get("/api/transactions", headers=header).json()
    assert txs == []


def test_data_isolation_between_users(client):
    header_a = _auth_header(client, "iso_a@fp.io")
    header_b = _auth_header(client, "iso_b@fp.io")

    client.post(
        "/api/transactions",
        json={"amount": 100000, "type": "income", "date": "2026-06-02T00:00:00", "category": "A-income"},
        headers=header_a,
    )
    client.post(
        "/api/transactions",
        json={"amount": 77000, "type": "income", "date": "2026-06-03T00:00:00", "category": "B-income"},
        headers=header_b,
    )

    a_cats = {t["category"] for t in client.get("/api/transactions", headers=header_a).json()}
    b_cats = {t["category"] for t in client.get("/api/transactions", headers=header_b).json()}

    assert "A-income" in a_cats and "B-income" not in a_cats
    assert "B-income" in b_cats and "A-income" not in b_cats


def test_anonymous_cannot_see_user_data(client):
    header = _auth_header(client, "private@fp.io")
    client.post(
        "/api/transactions",
        json={"amount": 100000, "type": "income", "date": "2026-06-02T00:00:00", "category": "Secret"},
        headers=header,
    )
    # Аноним (без токена и без cookie) не видит данные зарегистрированного пользователя.
    # Чистим cookie: TestClient переиспущет cookie логина, в реальном браузере её нет.
    client.cookies.clear()
    anon = client.get("/api/transactions").json()
    assert anon == []


def test_prefs_isolated_per_user(client):
    header_a = _auth_header(client, "pref_a@fp.io")
    header_b = _auth_header(client, "pref_b@fp.io")
    client.patch("/api/user-prefs", json={"risk_tolerance": 5, "base_currency": "USD"}, headers=header_a)
    client.patch("/api/user-prefs", json={"risk_tolerance": 1, "base_currency": "EUR"}, headers=header_b)
    pa = client.get("/api/user-prefs", headers=header_a).json()
    pb = client.get("/api/user-prefs", headers=header_b).json()
    assert pa["risk_tolerance"] == 5 and pa["base_currency"] == "USD"
    assert pb["risk_tolerance"] == 1 and pb["base_currency"] == "EUR"
