"""v3.0.0 International: users + FK, Decimal/numeric, мультивалюта, ingestion-таблицы.

Покрывает: DATA-03 (users + user_id FK), DATA-08/REFACTOR-03 (деньги → numeric(14,2),
ставки → numeric(6,4)), FR-19 (currency / base_currency / fx_rates),
INFRA-17 (plaid_tokens), INFRA-18 (manual_snapshots).

Стратегия апгрейда single→multi: user_id NULLABLE; существующие данные остаются
«осиротевшими» и усыновляются первым зарегистрированным пользователем
(см. app/api/routes_auth.py::_adopt_orphan_rows) — без хардкода учётки в миграции.

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

MONEY = sa.Numeric(14, 2)
RATE = sa.Numeric(6, 4)

# Сид-курсы к USD-пивоту. Плейсхолдеры на дату сборки — правятся через /api/fx.
FX_SEED = (
    ("USD", "1.0"),
    ("EUR", "1.09"),
    ("GBP", "1.27"),
    ("RUB", "0.0107"),
    ("KZT", "0.0021"),
    ("CNY", "0.14"),
    ("TRY", "0.026"),
    ("AED", "0.2723"),
)


def upgrade() -> None:
    # ── Новые таблицы ────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "fx_rates",
        sa.Column("currency", sa.String(3), primary_key=True),
        sa.Column("rate_to_usd", sa.Numeric(18, 8), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "manual_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_ref", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "plaid_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True
        ),
        sa.Column("item_id", sa.String(128), nullable=False, index=True),
        sa.Column("token_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    fx = sa.table(
        "fx_rates",
        sa.column("currency", sa.String),
        sa.column("rate_to_usd", sa.Numeric),
        sa.column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        fx,
        [
            {"currency": c, "rate_to_usd": r, "updated_at": datetime.utcnow()}
            for c, r in FX_SEED
        ],
        multiinsert=False,
    )

    # ── user_id + currency + типы денег на существующих таблицах ────
    with op.batch_alter_table("transactions") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_transactions_user_id"),
                nullable=True,
            )
        )
        b.add_column(sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"))
        b.alter_column("amount", type_=MONEY, existing_type=sa.Float())
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])

    with op.batch_alter_table("obligations") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_obligations_user_id"),
                nullable=True,
            )
        )
        b.add_column(sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"))
        b.alter_column("amount", type_=MONEY, existing_type=sa.Float())
        b.alter_column("monthly_payment", type_=MONEY, existing_type=sa.Float())
        b.alter_column("interest_rate", type_=RATE, existing_type=sa.Float())
    op.create_index("ix_obligations_user_id", "obligations", ["user_id"])

    with op.batch_alter_table("goals") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_goals_user_id"),
                nullable=True,
            )
        )
        b.add_column(sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"))
        b.alter_column("target_amount", type_=MONEY, existing_type=sa.Float())
        b.alter_column("current_amount", type_=MONEY, existing_type=sa.Float())
    op.create_index("ix_goals_user_id", "goals", ["user_id"])

    with op.batch_alter_table("liquid_assets") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_liquid_assets_user_id"),
                nullable=True,
            )
        )
        b.add_column(sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"))
        b.alter_column("amount", type_=MONEY, existing_type=sa.Float())
        b.alter_column("interest_rate", type_=RATE, existing_type=sa.Float())
    op.create_index("ix_liquid_assets_user_id", "liquid_assets", ["user_id"])

    with op.batch_alter_table("budgets") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_budgets_user_id"),
                nullable=True,
            )
        )
        b.alter_column("limit_amount", type_=MONEY, existing_type=sa.Float())
    op.create_index("ix_budgets_user_id", "budgets", ["user_id"])

    with op.batch_alter_table("scenarios") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_scenarios_user_id"),
                nullable=True,
            )
        )
    op.create_index("ix_scenarios_user_id", "scenarios", ["user_id"])

    with op.batch_alter_table("obligation_payments") as b:
        b.alter_column("amount", type_=MONEY, existing_type=sa.Float())
        b.alter_column("remaining_after", type_=MONEY, existing_type=sa.Float())

    with op.batch_alter_table("goal_contributions") as b:
        b.alter_column("amount", type_=MONEY, existing_type=sa.Float())

    with op.batch_alter_table("user_prefs") as b:
        b.add_column(
            sa.Column(
                "user_id",
                sa.String(36),
                sa.ForeignKey("users.id", name="fk_user_prefs_user_id"),
                nullable=True,
            )
        )
        b.add_column(sa.Column("base_currency", sa.String(3), nullable=False, server_default="RUB"))
        b.alter_column("l_min", type_=RATE, existing_type=sa.Float())
        b.alter_column("r_bench", type_=RATE, existing_type=sa.Float())
    op.create_index("ix_user_prefs_user_id", "user_prefs", ["user_id"], unique=True)

    # ── events / recommendations: user_id int → uuid-строка ─────────
    with op.batch_alter_table("events") as b:
        b.alter_column("user_id", type_=sa.String(36), existing_type=sa.Integer())
    with op.batch_alter_table("recommendations") as b:
        b.alter_column("user_id", type_=sa.String(36), existing_type=sa.Integer())


def downgrade() -> None:
    # PostgreSQL не кастует varchar→integer без явного USING (SQLite — динамическая
    # типизация, молчит). На чистой/пустой таблице (типичный сценарий downgrade base
    # в CI/тестах цепочки) каст — no-op и проходит. BUG-027.
    with op.batch_alter_table("recommendations") as b:
        b.alter_column(
            "user_id",
            type_=sa.Integer(),
            existing_type=sa.String(36),
            postgresql_using="user_id::integer",
        )
    with op.batch_alter_table("events") as b:
        b.alter_column(
            "user_id",
            type_=sa.Integer(),
            existing_type=sa.String(36),
            postgresql_using="user_id::integer",
        )

    op.drop_index("ix_user_prefs_user_id", table_name="user_prefs")
    with op.batch_alter_table("user_prefs") as b:
        b.alter_column("r_bench", type_=sa.Float(), existing_type=RATE)
        b.alter_column("l_min", type_=sa.Float(), existing_type=RATE)
        b.drop_column("base_currency")
        b.drop_column("user_id")

    with op.batch_alter_table("goal_contributions") as b:
        b.alter_column("amount", type_=sa.Float(), existing_type=MONEY)
    with op.batch_alter_table("obligation_payments") as b:
        b.alter_column("remaining_after", type_=sa.Float(), existing_type=MONEY)
        b.alter_column("amount", type_=sa.Float(), existing_type=MONEY)

    for table in ("scenarios", "budgets", "liquid_assets", "goals", "obligations", "transactions"):
        op.drop_index(f"ix_{table}_user_id", table_name=table)
    with op.batch_alter_table("scenarios") as b:
        b.drop_column("user_id")
    with op.batch_alter_table("budgets") as b:
        b.alter_column("limit_amount", type_=sa.Float(), existing_type=MONEY)
        b.drop_column("user_id")
    with op.batch_alter_table("liquid_assets") as b:
        b.alter_column("interest_rate", type_=sa.Float(), existing_type=RATE)
        b.alter_column("amount", type_=sa.Float(), existing_type=MONEY)
        b.drop_column("currency")
        b.drop_column("user_id")
    with op.batch_alter_table("goals") as b:
        b.alter_column("current_amount", type_=sa.Float(), existing_type=MONEY)
        b.alter_column("target_amount", type_=sa.Float(), existing_type=MONEY)
        b.drop_column("currency")
        b.drop_column("user_id")
    with op.batch_alter_table("obligations") as b:
        b.alter_column("interest_rate", type_=sa.Float(), existing_type=RATE)
        b.alter_column("monthly_payment", type_=sa.Float(), existing_type=MONEY)
        b.alter_column("amount", type_=sa.Float(), existing_type=MONEY)
        b.drop_column("currency")
        b.drop_column("user_id")
    with op.batch_alter_table("transactions") as b:
        b.alter_column("amount", type_=sa.Float(), existing_type=MONEY)
        b.drop_column("currency")
        b.drop_column("user_id")

    op.drop_table("plaid_tokens")
    op.drop_table("manual_snapshots")
    op.drop_table("fx_rates")
    op.drop_table("users")
