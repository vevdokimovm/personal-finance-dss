"""Инициализация БД: применение Alembic-миграций + гарантия user_prefs (INFRA-03)."""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from alembic import command
from app.database.db import engine
from app.database.models import UserPrefs

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _alembic_config() -> Config:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    return cfg


def run_migrations() -> None:
    """Приводит схему к head. Существующую дореляembic-БД сначала штампует baseline."""
    cfg = _alembic_config()
    inspector = inspect(engine)
    if inspector.has_table("transactions") and not inspector.has_table("alembic_version"):
        command.stamp(cfg, "0001")
    command.upgrade(cfg, "head")


def _ensure_user_prefs() -> None:
    with Session(engine) as session:
        if session.get(UserPrefs, 1) is None:
            session.add(UserPrefs(id=1))
            session.commit()


def init_db() -> None:
    run_migrations()
    _ensure_user_prefs()
