"""telegram link — привязка Telegram-чата к аккаунту (P3.6)

Revision ID: 0024
Revises: 0023
Create Date: 2026-06-29

Добавляет nullable telegram_chat_id на users + уникальный индекс (один чат — один
аккаунт; NULL не конфликтуют, поэтому множество непривязанных пользователей допустимо).
add_column на SQLite — через batch_alter_table. Аддитивно, данные не затрагиваются.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("telegram_chat_id", sa.String(length=32), nullable=True))
    op.create_index(
        "ix_users_telegram_chat_id", "users", ["telegram_chat_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_users_telegram_chat_id", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("telegram_chat_id")
