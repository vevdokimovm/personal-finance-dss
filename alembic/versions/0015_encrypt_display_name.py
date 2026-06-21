"""display_name to Text for encryption at rest (P1.6)

Revision ID: 0015
Revises: 0014
Create Date: 2026-06-20

display_name шифруется (EncryptedString) — Fernet-шифротекст длиннее 255 символов,
поэтому тип колонки расширяется со String(255) до Text. Поля comment уже Text.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column(
            "display_name",
            type_=sa.Text(),
            existing_type=sa.String(length=255),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column(
            "display_name",
            type_=sa.String(length=255),
            existing_type=sa.Text(),
            existing_nullable=True,
        )
