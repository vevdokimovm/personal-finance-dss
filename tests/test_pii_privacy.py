"""Приватность ПДн (P1.6): шифрование в покое + аудит доступа.

Шифруются только поля-заметки и имя (не ищутся, не участвуют в расчётах). email,
денежные суммы и индексируемые name остаются открытыми — их защита «в покое» делается
на уровне БД/диска. Доступ к ПДн журналируется (152-ФЗ).
"""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.db import engine
from app.database.types import EncryptedString


def _register(client: TestClient, email="pii@test.io", password="password123", name="Иван Тестов"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": name,
            "consent": True,
            "newsletter_opt_in": False,
        },
    )


class TestEncryptionAtRest:
    def test_display_name_encrypted_in_db(self, client: TestClient) -> None:
        _register(client, email="enc@test.io", name="Секретное Имя")
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT display_name FROM users WHERE email = :e"), {"e": "enc@test.io"}
            ).first()
        assert row is not None and row[0]
        assert "Секретное" not in row[0]  # в БД зашифровано

    def test_display_name_readable_via_orm(self, client: TestClient) -> None:
        _register(client, email="orm@test.io", name="Читаемое Имя")
        me = client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json()["display_name"] == "Читаемое Имя"  # через ORM расшифровано

    def test_goal_comment_encrypted_in_db(self, client: TestClient) -> None:
        _register(client, email="gc@test.io")
        r = client.post(
            "/api/goals",
            json={
                "name": "Цель",
                "target_amount": 100000,
                "deadline": "2027-01-01T00:00:00",
                "comment": "Личная заметка про деньги",
            },
        )
        assert r.status_code in (200, 201)
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT comment FROM goals WHERE comment IS NOT NULL ORDER BY id DESC LIMIT 1")
            ).first()
        assert row is not None and row[0]
        assert "Личная заметка" not in row[0]  # зашифровано

    def test_legacy_plaintext_readable(self) -> None:
        # Старое незашифрованное значение читается как есть (обратная совместимость).
        enc = EncryptedString()
        assert enc.process_result_value("просто старый текст", None) == "просто старый текст"

    def test_roundtrip(self) -> None:
        enc = EncryptedString()
        bound = enc.process_bind_param("конфиденциально", None)
        assert bound != "конфиденциально"  # на запись шифруется
        assert enc.process_result_value(bound, None) == "конфиденциально"  # на чтение возвращается


class TestPiiAccessAudit:
    def test_profile_access_audited(self, client: TestClient) -> None:
        _register(client, email="audit@test.io")
        client.get("/api/auth/me")
        with engine.connect() as conn:
            cnt = conn.execute(
                text("SELECT COUNT(*) FROM events WHERE event_type = 'pii_access'")
            ).scalar()
        assert cnt >= 1
