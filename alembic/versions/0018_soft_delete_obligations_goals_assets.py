"""soft-delete for obligations, goals, liquid_assets (P1.7)

Revision ID: 0018
Revises: 0017
Create Date: 2026-06-24
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None

_TABLES = ("obligations", "goals", "liquid_assets")


def upgrade() -> None:
    for table in _TABLES:
        with op.batch_alter_table(table) as batch:
            # server_default=false() — чтобы существующие строки получили False на
            # PostgreSQL (Alembic boolean default).
            batch.add_column(
                sa.Column(
                    "is_deleted",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )
            batch.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        op.create_index(f"ix_{table}_is_deleted", table, ["is_deleted"])


def downgrade() -> None:
    for table in _TABLES:
        op.drop_index(f"ix_{table}_is_deleted", table_name=table)
        with op.batch_alter_table(table) as batch:
            batch.drop_column("deleted_at")
            batch.drop_column("is_deleted")
