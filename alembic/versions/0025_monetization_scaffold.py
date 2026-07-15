"""monetization scaffold — тариф и срок действия на users (каркас)

Revision ID: 0025
Revises: 0024
Create Date: 2026-06-29

Добавляет plan_tier (default 'free') и nullable plan_expires_at на users — каркас под
платные функции. Платёжной интеграции нет; это структура для feature-gating. add_column
на SQLite — через batch_alter_table. Аддитивно, данные не затрагиваются (существующие
пользователи получают plan_tier='free').
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column("plan_tier", sa.String(length=20), nullable=False, server_default="free")
        )
        batch.add_column(sa.Column("plan_expires_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("plan_expires_at")
        batch.drop_column("plan_tier")
