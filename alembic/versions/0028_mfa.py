"""mfa: поля mfa_secret/mfa_enabled на users + таблица mfa_recovery_codes

Revision ID: 0028
Revises: 0027
Create Date: 2026-06-30

Раздел 4.4 (кибербез-харденинг). MFA/TOTP: секрет TOTP (зашифрован EncryptedString
→ Text) и флаг включённости на users; одноразовые recovery-коды (хеш) — отдельной
таблицей с каскадным удалением по пользователю.

Аддитивно. boolean `mfa_enabled` получает server_default=false для существующих строк
(грабли PostgreSQL: без server_default ALTER на NOT NULL колонке падает).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("mfa_secret", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "mfa_recovery_codes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_mfa_recovery_codes_user_id", "mfa_recovery_codes", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_mfa_recovery_codes_user_id", table_name="mfa_recovery_codes")
    op.drop_table("mfa_recovery_codes")
    op.drop_column("users", "mfa_enabled")
    op.drop_column("users", "mfa_secret")
