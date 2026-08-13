"""plan advice events — телеметрия принятия совета (волна 0, п. 0.6)

Revision ID: 0032
Revises: 0031
Create Date: 2026-08-13

Зачем. docs/model/telemetry_spec.md: раунд сертификации на живых данных (волна 2)
меняет эталон с консенсуса экспертов на фактическое решение пользователя —
без записи «что советовала модель / что сделал человек» у такого раунда есть
вход, но нет эталона. Таблица — чистая инфраструктура, ДОРМАНТНАЯ до явного
включения флага `TELEMETRY_COLLECTION_ENABLED` (default False, app/config.py):
правовой контур обезличивания для использования этих данных в сертификации
(152-ФЗ, ROADMAP §8.2а) — отдельная задача юриста, не закрыта миграцией.

Две фазы события: `shown_at` пишется сразу (план показан), `outcome`/
`modified_to`/`decided_at` — nullable, заполняются позже отдельным вызовом
(человек решает не сразу и не всегда).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plan_advice_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("app_version", sa.String(length=32), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("advice", sa.JSON(), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=True),
        sa.Column("modified_to", sa.JSON(), nullable=True),
        sa.Column("shown_at", sa.DateTime(), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_plan_advice_events_plan_id", "plan_advice_events", ["plan_id"])
    op.create_index("ix_plan_advice_events_user_id", "plan_advice_events", ["user_id"])
    op.create_index("ix_plan_advice_events_is_deleted", "plan_advice_events", ["is_deleted"])


def downgrade() -> None:
    op.drop_index("ix_plan_advice_events_is_deleted", table_name="plan_advice_events")
    op.drop_index("ix_plan_advice_events_user_id", table_name="plan_advice_events")
    op.drop_index("ix_plan_advice_events_plan_id", table_name="plan_advice_events")
    op.drop_table("plan_advice_events")
