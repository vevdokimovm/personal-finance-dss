"""soft-delete транзакций: is_deleted + deleted_at (BUG-03)

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-05

Колонки добавляются через batch_alter_table: на SQLite это безопасный путь
добавить NOT NULL колонку со server_default на непустой таблице.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch:
        batch.add_column(sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()
        ))
        batch.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch.create_index("ix_transactions_is_deleted", ["is_deleted"])


def downgrade() -> None:
    with op.batch_alter_table("transactions") as batch:
        batch.drop_index("ix_transactions_is_deleted")
        batch.drop_column("deleted_at")
        batch.drop_column("is_deleted")
