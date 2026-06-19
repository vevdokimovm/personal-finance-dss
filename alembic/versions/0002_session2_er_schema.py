"""session2 — целевая ER-схема: категории, история, жизненный цикл (DATA-04/06/09)

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-04

ALTER существующих таблиц идёт через batch_alter_table: на SQLite это
пересоздаёт таблицу через CREATE (где DEFAULT CURRENT_TIMESTAMP разрешён) и
копирует данные — иначе ADD COLUMN с CURRENT_TIMESTAMP падает на непустой БД.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SYSTEM_CATEGORIES = [
    ("Зарплата", "income"), ("Аванс", "income"), ("Премия", "income"),
    ("Фриланс", "income"), ("Проценты и дивиденды", "income"),
    ("Возврат", "income"), ("Подарок", "income"),
    ("Продукты", "expense"), ("Кафе и рестораны", "expense"), ("Транспорт", "expense"),
    ("ЖКХ", "expense"), ("Связь и интернет", "expense"), ("Развлечения", "expense"),
    ("Одежда и обувь", "expense"), ("Здоровье", "expense"), ("Образование", "expense"),
    ("Дом и ремонт", "expense"), ("Путешествия", "expense"), ("Переводы", "expense"),
    ("Подписки", "expense"), ("Прочее", "expense"),
]


def upgrade() -> None:
    # ── DATA-04: справочник категорий ─────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("type", sa.String(length=20), nullable=False, server_default="expense"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )

    # ── DATA-06: история платежей и пополнений (новые таблицы) ─────────────
    op.create_table(
        "obligation_payments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("obligation_id", sa.Integer(), sa.ForeignKey("obligations.id"), nullable=False, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), index=True),
        sa.Column("is_early", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("remaining_after", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_table(
        "goal_contributions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("goals.id"), nullable=False, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("contribution_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), index=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="manual"),
    )

    # ── DATA-04: поля транзакции ──────────────────────────────────────────
    with op.batch_alter_table("transactions") as batch:
        batch.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch.add_column(sa.Column("external_id", sa.String(length=128), nullable=True))
        batch.add_column(sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch.create_index("ix_transactions_category_id", ["category_id"])
        batch.create_index("ix_transactions_external_id", ["external_id"])

    # ── DATA-06/09: жизненный цикл обязательств ───────────────────────────
    with op.batch_alter_table("obligations") as batch:
        batch.add_column(sa.Column("bank", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("type", sa.String(length=32), nullable=False, server_default="other"))
        batch.add_column(sa.Column("start_date", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")))
        batch.add_column(sa.Column("closed_at", sa.DateTime(), nullable=True))
        batch.create_index("ix_obligations_is_active", ["is_active"])

    # ── DATA-06: жизненный цикл целей ─────────────────────────────────────
    with op.batch_alter_table("goals") as batch:
        batch.add_column(sa.Column("priority", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")))
        batch.add_column(sa.Column("achieved_at", sa.DateTime(), nullable=True))
        batch.create_index("ix_goals_is_active", ["is_active"])

    # ── DATA-09: аудит профиля ────────────────────────────────────────────
    with op.batch_alter_table("user_prefs") as batch:
        batch.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))

    # ── Сидинг системных категорий ────────────────────────────────────────
    categories_table = sa.table(
        "categories",
        sa.column("name", sa.String),
        sa.column("type", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    op.bulk_insert(
        categories_table,
        [{"name": name, "type": ctype, "is_system": True} for name, ctype in SYSTEM_CATEGORIES],
    )


def downgrade() -> None:
    with op.batch_alter_table("user_prefs") as batch:
        batch.drop_column("updated_at")

    with op.batch_alter_table("goals") as batch:
        batch.drop_index("ix_goals_is_active")
        batch.drop_column("achieved_at")
        batch.drop_column("is_active")
        batch.drop_column("priority")

    with op.batch_alter_table("obligations") as batch:
        batch.drop_index("ix_obligations_is_active")
        batch.drop_column("closed_at")
        batch.drop_column("is_active")
        batch.drop_column("start_date")
        batch.drop_column("type")
        batch.drop_column("bank")

    with op.batch_alter_table("transactions") as batch:
        batch.drop_index("ix_transactions_external_id")
        batch.drop_index("ix_transactions_category_id")
        batch.drop_column("created_at")
        batch.drop_column("external_id")
        batch.drop_column("description")
        batch.drop_column("category_id")

    op.drop_table("goal_contributions")
    op.drop_table("obligation_payments")
    op.drop_table("categories")
