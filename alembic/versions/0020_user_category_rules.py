"""user category rules — обучение категоризации на правках (P2.7)

Revision ID: 0020
Revises: 0019
Create Date: 2026-06-27
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_category_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("match_token", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False, server_default="expense"),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "match_token", "type", name="uq_user_category_rule"),
    )
    op.create_index(
        "ix_user_category_rules_user_id", "user_category_rules", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_user_category_rules_user_id", table_name="user_category_rules")
    op.drop_table("user_category_rules")
