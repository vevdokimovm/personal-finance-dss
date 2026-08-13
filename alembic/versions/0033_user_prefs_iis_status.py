"""user_prefs: iis_type/iis_contributed_this_year (ADR-017)

Revision ID: 0033
Revises: 0032
Create Date: 2026-08-13

Продолжение ADR-014 (нота ИИС) — реальный расчёт вычета типа А требует знать
статус счёта пользователя. Аддитивно: `iis_type` (none/A/B/three, default
'none' — существующие строки не тронуты по смыслу), `iis_contributed_this_year`
(Numeric, default 0). server_default обязателен для NOT NULL на непустой
таблице (грабли PostgreSQL — см. finpilot-alembic-migration).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_prefs",
        sa.Column(
            "iis_type", sa.String(length=8), nullable=False, server_default="none"
        ),
    )
    op.add_column(
        "user_prefs",
        sa.Column(
            "iis_contributed_this_year", sa.Numeric(12, 2), nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("user_prefs", "iis_contributed_this_year")
    op.drop_column("user_prefs", "iis_type")
