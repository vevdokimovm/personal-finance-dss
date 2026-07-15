"""referral codes for users (P3.2)

Revision ID: 0017
Revises: 0016
Create Date: 2026-06-21
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("referral_code", sa.String(length=12), nullable=True))
        batch.add_column(sa.Column("referred_by_code", sa.String(length=12), nullable=True))
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)
    op.create_index("ix_users_referred_by_code", "users", ["referred_by_code"])


def downgrade() -> None:
    op.drop_index("ix_users_referred_by_code", table_name="users")
    op.drop_index("ix_users_referral_code", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("referred_by_code")
        batch.drop_column("referral_code")
