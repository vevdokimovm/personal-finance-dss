"""plan snapshots — история рассчитанных планов (P2.6)

Revision ID: 0019
Revises: 0018
Create Date: 2026-06-25
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plan_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("risk_profile", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("rt", sa.Float(), nullable=False, server_default="0"),
        sa.Column("lt", sa.Float(), nullable=False, server_default="0"),
        sa.Column("dt", sa.Float(), nullable=False, server_default="0"),
        sa.Column("blr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("best_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("x_obligations", sa.Float(), nullable=False, server_default="0"),
        sa.Column("x_reserve", sa.Float(), nullable=False, server_default="0"),
        sa.Column("x_goals", sa.Float(), nullable=False, server_default="0"),
        sa.Column("utility", sa.Float(), nullable=False, server_default="0"),
        sa.Column("top3", sa.JSON(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_plan_snapshots_user_id", "plan_snapshots", ["user_id"])
    op.create_index("ix_plan_snapshots_created_at", "plan_snapshots", ["created_at"])
    op.create_index("ix_plan_snapshots_is_deleted", "plan_snapshots", ["is_deleted"])


def downgrade() -> None:
    op.drop_index("ix_plan_snapshots_is_deleted", table_name="plan_snapshots")
    op.drop_index("ix_plan_snapshots_created_at", table_name="plan_snapshots")
    op.drop_index("ix_plan_snapshots_user_id", table_name="plan_snapshots")
    op.drop_table("plan_snapshots")
