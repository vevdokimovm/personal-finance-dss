from sqlalchemy import inspect, text

from app.database.db import Base, engine
from app.database.models import Goal, Obligation, Transaction


def _add_missing_sqlite_columns() -> None:
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
        },
    }

    inspector = inspect(engine)

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            existing_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            for column_name, statement in columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(statement))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _add_missing_sqlite_columns()
