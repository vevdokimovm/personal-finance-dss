"""jwt revocation — блок-лист revoked_tokens + users.tokens_valid_since

Revision ID: 0027
Revises: 0026
Create Date: 2026-06-30

Раздел 4.4 (кибербез-харденинг): отзыв JWT.
  - Таблица revoked_tokens (PK jti) — точечный отзыв конкретного токена при выходе.
  - Колонка users.tokens_valid_since — глобальная отсечка для logout-all: все токены,
    выпущенные раньше неё, недействительны.

Аддитивно: новая таблица + nullable-колонка, существующие данные не затрагиваются.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "revoked_tokens",
        sa.Column("jti", sa.String(length=36), primary_key=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_revoked_tokens_expires_at", "revoked_tokens", ["expires_at"], unique=False
    )
    op.add_column("users", sa.Column("tokens_valid_since", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "tokens_valid_since")
    op.drop_index("ix_revoked_tokens_expires_at", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")
