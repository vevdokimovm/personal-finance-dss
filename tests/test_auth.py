"""Тесты v3.0.0: аутентификация и изоляция данных по пользователю (INFRA-06, DATA-03)."""
from __future__ import annotations


def _register(client, email: str, password: str = "strongpass1"):
    """Регистрация с явным согласием на обработку ПДн.

    Поле `consent` обязательное и без значения по умолчанию (юрблок L2):
    предотмеченная галочка читается надзором как навязанное согласие,
    поэтому контракт требует его называть явно в каждом вызове.
    """
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "consent": True},
    )


def _auth_header(client, email: str, password: str = "passwordX1") -> dict[str, str]:
    """Готовый к работе пользователь: зарегистрирован И дал согласие на финданные.

    Согласие выдаётся здесь, а не в самих тестах, потому что моделирует
    реальный путь: обработка финансового портрета требует ОТДЕЛЬНОГО основания
    (юрблок L1), и без него роутеры обязаны отвечать 403. Тесты про изоляцию
    данных проверяют изоляцию, а не гейт — гейт проверяется отдельно
    в `tests/test_consent_gate.py`.
    """
    r = _register(client, email, password)
    assert r.status_code == 201
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    client.post("/api/consents/financial_data", headers=headers)
    return headers


def test_register_returns_token_and_user(client):
    r = _register(client, "u1@fp.io", "strongpass1")
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == "u1@fp.io"


def test_register_duplicate_email_conflict(client):
    _register(client, "dup@fp.io", "strongpass1")
    r = _register(client, "dup@fp.io", "other12345")
    assert r.status_code == 409


def test_register_weak_password_rejected(client):
    r = _register(client, "weak@fp.io", "short")
    assert r.status_code == 422


def test_login_success_and_wrong_password(client):
    _register(client, "log@fp.io", "strongpass1")
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

    _register(client, "hash@fp.io", "strongpass1")
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
        json={"amount": 50000, "type": "income", "date": "2026-06-01T00:00:00", "category": "Guest"},  # noqa: E501
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
        json={"amount": 100000, "type": "income", "date": "2026-06-02T00:00:00", "category": "A-income"},  # noqa: E501
        headers=header_a,
    )
    client.post(
        "/api/transactions",
        json={"amount": 77000, "type": "income", "date": "2026-06-03T00:00:00", "category": "B-income"},  # noqa: E501
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
        json={"amount": 100000, "type": "income", "date": "2026-06-02T00:00:00", "category": "Secret"},  # noqa: E501
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
    client.patch("/api/user-prefs", json={"risk_tolerance": 5, "base_currency": "USD"}, headers=header_a)  # noqa: E501
    client.patch("/api/user-prefs", json={"risk_tolerance": 1, "base_currency": "EUR"}, headers=header_b)  # noqa: E501
    pa = client.get("/api/user-prefs", headers=header_a).json()
    pb = client.get("/api/user-prefs", headers=header_b).json()
    assert pa["risk_tolerance"] == 5 and pa["base_currency"] == "USD"
    assert pb["risk_tolerance"] == 1 and pb["base_currency"] == "EUR"
