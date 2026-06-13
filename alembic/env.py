"""Alembic-окружение FINPILOT (INFRA-03).

URL и engine берутся напрямую из приложения (app.database.db.engine), чтобы
миграции всегда шли в ту же БД, что и рантайм. render_as_batch=True — чтобы
ALTER-операции работали на SQLite (dev), где нативного ALTER почти нет.
"""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context

from app.database.db import Base, engine
import app.database.models  # noqa: F401  — регистрирует таблицы в Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", str(engine.url))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
