"""категорийные бюджеты: таблица budgets (FR-22)

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("limit_amount", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_budgets_id", "budgets", ["id"])
    op.create_index("ix_budgets_category", "budgets", ["category"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_budgets_category", table_name="budgets")
    op.drop_index("ix_budgets_id", table_name="budgets")
    op.drop_table("budgets")
