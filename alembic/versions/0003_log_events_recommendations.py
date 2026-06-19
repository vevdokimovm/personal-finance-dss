"""log — продуктовая аналитика: events + recommendations (LOG-01, LOG-02)

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-05

Две новые таблицы создаются «с нуля» (CREATE TABLE), batch_alter_table не нужен —
ALTER существующих таблиц здесь нет.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── LOG-01: единая событийная модель ──────────────────────────────────
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("session_id", sa.String(length=64), nullable=True, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("event_payload", sa.JSON(), nullable=True),
        sa.Column("app_version", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, index=True),
    )

    # ── LOG-02: снимок каждой рекомендации ────────────────────────────────
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("income_total", sa.Float(), nullable=False),
        sa.Column("expense_total", sa.Float(), nullable=False),
        sa.Column("obligation_payments_total", sa.Float(), nullable=False),
        sa.Column("balance_bt", sa.Float(), nullable=False),
        sa.Column("bliq", sa.Float(), nullable=False),
        sa.Column("rt", sa.Float(), nullable=False),
        sa.Column("lt", sa.Float(), nullable=False),
        sa.Column("dt", sa.Float(), nullable=False),
        sa.Column("blr", sa.Float(), nullable=False),
        sa.Column("optimal_x_obl", sa.Float(), nullable=False),
        sa.Column("optimal_x_res", sa.Float(), nullable=False),
        sa.Column("optimal_x_goals", sa.Float(), nullable=False),
        sa.Column("u_score", sa.Float(), nullable=False),
        sa.Column("alternatives_total", sa.Integer(), nullable=False),
        sa.Column("alternatives_accepted", sa.Integer(), nullable=False),
        sa.Column("reasoning_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("recommendations")
    op.drop_table("events")
