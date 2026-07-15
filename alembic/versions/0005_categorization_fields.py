"""категоризация: mcc + is_recurring у транзакций (FR-13)

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch:
        batch.add_column(sa.Column("mcc", sa.String(length=8), nullable=True))
        batch.add_column(sa.Column(
            "is_recurring", sa.Boolean(), nullable=False, server_default=sa.false()
        ))


def downgrade() -> None:
    with op.batch_alter_table("transactions") as batch:
        batch.drop_column("is_recurring")
        batch.drop_column("mcc")
