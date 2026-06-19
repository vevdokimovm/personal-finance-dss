"""goal linked_asset_id (конверты)

Revision ID: 0013
Revises: 0012
Create Date: 2026-06-16

Добавляет goals.linked_asset_id (INTEGER FK liquid_assets.id, NULL) — связь
цели с ликвидным активом, где физически копятся деньги (вариант B «конвертов»).
NULL = цель не привязана (старое поведение, обратная совместимость).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("goals") as batch:
        batch.add_column(sa.Column("linked_asset_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_goals_linked_asset",
            "liquid_assets",
            ["linked_asset_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("goals") as batch:
        batch.drop_constraint("fk_goals_linked_asset", type_="foreignkey")
        batch.drop_column("linked_asset_id")
