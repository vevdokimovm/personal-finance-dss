"""Инициализация БД: применение Alembic-миграций + гарантия user_prefs (INFRA-03)."""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from alembic import command
from app.database.db import engine
from app.database.models import UserPrefs  # noqa: F401 — используется в _ensure_user_prefs

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
    """Гарантирует одну legacy-строку настроек (user_id=None) для анонимного режима."""
    with Session(engine) as session:
        existing = session.query(UserPrefs).filter(UserPrefs.user_id.is_(None)).first()
        if existing is None:
            session.add(UserPrefs(user_id=None))
            session.commit()


def init_db() -> None:
    run_migrations()
    _ensure_user_prefs()
