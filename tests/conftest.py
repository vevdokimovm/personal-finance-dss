"""Общие фикстуры pytest: изолированная БД и TestClient.

Схема строится реальными Alembic-миграциями через startup приложения —
это заодно проверяет применимость миграций (INFRA-03).
"""
from __future__ import annotations

import os
import tempfile

import pytest

_TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.name}"

from fastapi.testclient import TestClient

from app.database.db import Base, engine
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
