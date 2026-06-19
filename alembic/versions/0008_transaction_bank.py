"""transactions.bank — источник-банк импортированной операции

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-06
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("bank", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transactions", "bank")
