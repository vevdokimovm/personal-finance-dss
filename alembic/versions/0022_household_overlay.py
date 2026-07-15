"""household overlay — семейные/многопользовательские бюджеты (P3.7)

Revision ID: 0022
Revises: 0021
Create Date: 2026-06-28

Аддитивная миграция: три новые таблицы (households, household_memberships,
household_invites) + nullable household_id FK на 7 доменных таблицах. Колонка
nullable, без бэкфилла — все существующие строки остаются household_id = NULL,
то есть личными, ровно как до P3.7. Поэтому миграция не меняет поведение для
текущих пользователей.

FK household_id → households.id с ON DELETE SET NULL: при прямом удалении
household строки автоматически возвращаются в личное владение автора (user_id),
не теряясь и не повисая обезличенными (152-ФЗ). add_column идёт через
batch_alter_table — нативного ALTER ADD CONSTRAINT на SQLite нет.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None

_DOMAIN_TABLES = (
    "transactions",
    "obligations",
    "goals",
    "budgets",
    "scenarios",
    "liquid_assets",
    "plan_snapshots",
)


def upgrade() -> None:
    # 1. households — контейнер совместного пространства.
    op.create_table(
        "households",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, server_default="Семья"),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_households_owner_id", "households", ["owner_id"])

    # 2. household_memberships — кто в household и с какой ролью.
    op.create_table(
        "household_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "household_id",
            sa.Integer(),
            sa.ForeignKey("households.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("household_id", "user_id", name="uq_household_member"),
    )
    op.create_index(
        "ix_household_memberships_household_id", "household_memberships", ["household_id"]
    )
    op.create_index("ix_household_memberships_user_id", "household_memberships", ["user_id"])

    # 3. household_invites — приглашения по токену.
    op.create_table(
        "household_invites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "household_id",
            sa.Integer(),
            sa.ForeignKey("households.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_by", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("token", name="uq_household_invite_token"),
    )
    op.create_index(
        "ix_household_invites_household_id", "household_invites", ["household_id"]
    )
    op.create_index("ix_household_invites_status", "household_invites", ["status"])

    # 4. nullable household_id FK на доменных таблицах (через batch для SQLite).
    for table in _DOMAIN_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("household_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(
                f"fk_{table}_household",
                "households",
                ["household_id"],
                ["id"],
                ondelete="SET NULL",
            )
        op.create_index(f"ix_{table}_household_id", table, ["household_id"])


def downgrade() -> None:
    for table in _DOMAIN_TABLES:
        op.drop_index(f"ix_{table}_household_id", table_name=table)
        with op.batch_alter_table(table) as batch:
            batch.drop_constraint(f"fk_{table}_household", type_="foreignkey")
            batch.drop_column("household_id")

    op.drop_index("ix_household_invites_status", table_name="household_invites")
    op.drop_index("ix_household_invites_household_id", table_name="household_invites")
    op.drop_table("household_invites")

    op.drop_index("ix_household_memberships_user_id", table_name="household_memberships")
    op.drop_index("ix_household_memberships_household_id", table_name="household_memberships")
    op.drop_table("household_memberships")

    op.drop_index("ix_households_owner_id", table_name="households")
    op.drop_table("households")
