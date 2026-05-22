from sqlalchemy import inspect, text

from app.database.db import Base, engine
from app.database.models import Goal, LiquidAsset, Obligation, Transaction, UserPrefs


def _add_missing_sqlite_columns() -> None:
    """SQLite-only автомиграция: добавляет недостающие колонки."""
    if engine.dialect.name != "sqlite":
        return

    required_columns = {
        "obligations": {
            "name": "ALTER TABLE obligations ADD COLUMN name VARCHAR(255) NOT NULL DEFAULT 'Обязательство'",
            "payment_day": "ALTER TABLE obligations ADD COLUMN payment_day INTEGER NOT NULL DEFAULT 1",
            "comment": "ALTER TABLE obligations ADD COLUMN comment TEXT",
        },
        "goals": {
            "current_amount": "ALTER TABLE goals ADD COLUMN current_amount FLOAT NOT NULL DEFAULT 0.0",
            "comment": "ALTER TABLE goals ADD COLUMN comment TEXT",
            "category": "ALTER TABLE goals ADD COLUMN category VARCHAR(32) NOT NULL DEFAULT 'material'",
        },
    }

    inspector = inspect(engine)

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            if not inspector.has_table(table_name):
                continue
            existing = {c["name"] for c in inspector.get_columns(table_name)}
            for column_name, stmt in columns.items():
                if column_name not in existing:
                    connection.execute(text(stmt))


def _ensure_user_prefs() -> None:
    """Гарантирует, что в таблице user_prefs всегда есть строка с id=1."""
    from sqlalchemy.orm import Session

    with Session(engine) as session:
        prefs = session.get(UserPrefs, 1)
        if prefs is None:
            session.add(UserPrefs(id=1))
            session.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _add_missing_sqlite_columns()
    _ensure_user_prefs()
