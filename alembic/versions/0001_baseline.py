"""baseline — схема FINPILOT до внедрения Alembic (v2.0.x)

Revision ID: 0001
Revises:
Create Date: 2026-06-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False, index=True),
        sa.Column("type", sa.String(length=20), nullable=False, index=True),
        sa.Column("date", sa.DateTime(), nullable=False, index=True),
        sa.Column("is_synced", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "obligations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False, server_default="Обязательство"),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("term", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("monthly_payment", sa.Float(), nullable=False),
        sa.Column("payment_day", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("comment", sa.Text(), nullable=True),
    )
    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deadline", sa.DateTime(), nullable=False, index=True),
        sa.Column("category", sa.String(length=32), nullable=False, server_default="material", index=True),
        sa.Column("comment", sa.Text(), nullable=True),
    )
    op.create_table(
        "liquid_assets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False, server_default="Депозит"),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("interest_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("type", sa.String(length=32), nullable=False, server_default="deposit"),
        sa.Column("comment", sa.Text(), nullable=True),
    )
    op.create_table(
        "user_prefs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("l_min", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_tolerance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("horizon", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("r_bench", sa.Float(), nullable=False, server_default="0.14"),
    )


def downgrade() -> None:
    op.drop_table("user_prefs")
    op.drop_table("liquid_assets")
    op.drop_table("goals")
    op.drop_table("obligations")
    op.drop_table("transactions")
