"""Регрессия обратимости цепочки миграций на PostgreSQL (BUG-027).

`downgrade base` падал на миграции 0009 (обратный каст `user_id` varchar→integer
без `USING`). На SQLite баг непроявим (динамическая типизация молчит про тип
колонки), поэтому тест осмыслен только на боевой СУБД и на SQLite скипается.

Запуск под PG:
    DATABASE_URL=postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot_test \\
        pytest tests/test_migration_reversibility.py
"""
from __future__ import annotations

import pytest
from sqlalchemy import inspect

from alembic import command
from app.database.db import engine
from app.database.init_db import _alembic_config

_IS_PG = engine.url.get_backend_name() == "postgresql"

pytestmark = pytest.mark.skipif(
    not _IS_PG,
    reason="обратимость миграций проверяется на PostgreSQL (SQLite не типизирует строго)",
)


def test_full_chain_downgrade_then_upgrade() -> None:
    """Полный цикл head → base → head на чистой PG: вся цепочка обратима."""
    cfg = _alembic_config()
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")  # без фикса 0009 — DatatypeMismatch на PG
    command.upgrade(cfg, "head")
    assert inspect(engine).has_table("alembic_version")
