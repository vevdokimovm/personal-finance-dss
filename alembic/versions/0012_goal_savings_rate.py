"""goal savings_rate

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-16

Добавляет goals.savings_rate (NUMERIC(6,4) NOT NULL DEFAULT 0) — ставка по
инструменту, где копятся деньги цели (вклад/накопительный счёт). 0 = без процентов.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "goals",
        sa.Column("savings_rate", sa.Numeric(6, 4), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("goals", "savings_rate")
