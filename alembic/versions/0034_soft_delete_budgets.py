"""soft-delete for budgets — симметрия с obligations/goals/liquid_assets (P1.7)

Revision ID: 0034
Revises: 0033
Create Date: 2026-08-14
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("budgets") as batch:
        # server_default=false() — чтобы существующие строки получили False на PostgreSQL
        # (Alembic boolean default), тот же приём, что 0018.
        batch.add_column(
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index("ix_budgets_is_deleted", "budgets", ["is_deleted"])


def downgrade() -> None:
    op.drop_index("ix_budgets_is_deleted", table_name="budgets")
    with op.batch_alter_table("budgets") as batch:
        batch.drop_column("deleted_at")
        batch.drop_column("is_deleted")
