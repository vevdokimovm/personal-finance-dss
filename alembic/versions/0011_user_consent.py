"""user consent fields (152-FZ)

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-15

Добавляет users.newsletter_opt_in (BOOLEAN NOT NULL DEFAULT FALSE) и
users.consent_at (TIMESTAMP NULL) — фиксация согласия на обработку ПДн.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("newsletter_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("users", sa.Column("consent_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "consent_at")
    op.drop_column("users", "newsletter_opt_in")
