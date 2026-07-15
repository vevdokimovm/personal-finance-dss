"""снимок сценариев что-если: таблица scenarios (LOG-06)

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parent_recommendation_id", sa.Integer(),
                  sa.ForeignKey("recommendations.id"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_scenarios_id", "scenarios", ["id"])
    op.create_index("ix_scenarios_parent_recommendation_id", "scenarios",
                    ["parent_recommendation_id"])


def downgrade() -> None:
    op.drop_index("ix_scenarios_parent_recommendation_id", table_name="scenarios")
    op.drop_index("ix_scenarios_id", table_name="scenarios")
    op.drop_table("scenarios")
