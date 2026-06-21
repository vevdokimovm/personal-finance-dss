"""Общие фикстуры pytest: изолированная БД и TestClient.

Схема строится реальными Alembic-миграциями через startup приложения —
это заодно проверяет применимость миграций (INFRA-03).
"""
from __future__ import annotations

import os
import tempfile

import pytest

# По умолчанию — изолированный SQLite-файл. Но если DATABASE_URL задан извне
# (например, PostgreSQL в CI/локальной верификации) — уважаем его, чтобы прогнать
# тот же набор тестов на боевой СУБД.
if not os.environ.get("DATABASE_URL"):
    _TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.name}"

from fastapi.testclient import TestClient

from app.database.db import Base, SessionLocal, engine
from app.main import app


def _reset_db() -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    _reset_db()
    with TestClient(app) as test_client:  # startup → init_db → run_migrations
        yield test_client
    _reset_db()


@pytest.fixture
def db_session():
    """Сессия БД для юнит-тестов. Схема строится теми же миграциями (через startup)."""
    _reset_db()
    with TestClient(app):  # поднимает схему (миграции)
        pass
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        _reset_db()


@pytest.fixture(autouse=True)
def _clear_recommendation_cache():
    """Кэш рекомендаций — модульный (живёт в процессе); чистим перед каждым тестом,
    чтобы результаты не протекали между тестами."""
    try:
        from app.api.routes_recommendation import _recommendation_cache
        _recommendation_cache.clear()
    except Exception:
        pass
    yield
