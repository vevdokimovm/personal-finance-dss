"""cbr key rate cache — durable last-known-good ключевой ставки ЦБ

Revision ID: 0026
Revises: 0025
Create Date: 2026-06-29

Одна новая таблица cbr_key_rate_cache — устойчивость источника ключевой ставки.
cbr.ru недоступен с датацентровых IP (403) и бывает нестабилен; кэшируем каждое
успешно полученное значение, чтобы при недоступности отдавать последнее реальное,
а не мёртвый статический дефолт. Уникальность по effective_date (дата вступления
ставки в силу) — одна строка на изменение ставки, заодно аудит-след.

Аддитивно: только создание таблицы, существующие данные не затрагиваются.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cbr_key_rate_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_cbr_key_rate_cache_effective_date",
        "cbr_key_rate_cache",
        ["effective_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_cbr_key_rate_cache_effective_date", table_name="cbr_key_rate_cache")
    op.drop_table("cbr_key_rate_cache")
