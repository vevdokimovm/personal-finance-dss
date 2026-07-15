"""email_verified flag for users

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-14

Добавляет users.email_verified (BOOLEAN NOT NULL DEFAULT FALSE).
Default через sa.false() — диалект-безопасно (PostgreSQL строгий к типу DEFAULT).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "email_verified")
