"""notification_log for email notifications dedup (P2.5)

Revision ID: 0016
Revises: 0015
Create Date: 2026-06-20
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notification_log_user_id", "notification_log", ["user_id"])
    op.create_index("ix_notification_log_dedup_key", "notification_log", ["dedup_key"])
    op.create_index("ix_notification_log_id", "notification_log", ["id"])


def downgrade() -> None:
    op.drop_index("ix_notification_log_id", table_name="notification_log")
    op.drop_index("ix_notification_log_dedup_key", table_name="notification_log")
    op.drop_index("ix_notification_log_user_id", table_name="notification_log")
    op.drop_table("notification_log")
