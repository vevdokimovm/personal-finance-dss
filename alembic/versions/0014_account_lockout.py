"""account lockout fields for users (P1.2)

Revision ID: 0014
Revises: 0013
Create Date: 2026-06-20

Добавляет users.failed_login_attempts (INTEGER NOT NULL DEFAULT 0) и
users.locked_until (DATETIME NULL) — защита логина от перебора пароля.
server_default гарантирует корректное значение для уже существующих строк
(и совместим с PostgreSQL, и с SQLite).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column(
                "failed_login_attempts",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch.add_column(sa.Column("locked_until", sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("locked_until")
        batch.drop_column("failed_login_attempts")
