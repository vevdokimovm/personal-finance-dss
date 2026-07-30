"""Раздельные согласия с версией текста и моментом отзыва (юрблок L1, L4)

Юридический пакет обещает пользователю ТРИ раздельных согласия — на обработку
ПДн, на обработку финансовых данных и на рекламную рассылку, — каждое с датой,
временем и редакцией текста. В схеме было одно поле `users.consent_at` и флаг
`users.newsletter_opt_in`: доказать, на что и в какой редакции согласился
конкретный человек, невозможно, а обязательное согласие оказывалось склеено с
необязательной рассылкой.

Миграция обратно совместима и не теряет данных:
  * старые колонки НЕ удаляются — на них ещё смотрит существующий код и они
    остаются вторым свидетелем на время перехода;
  * каждому пользователю с непустым `consent_at` заводится согласие типа
    `personal_data` версии 1.0 с тем же моментом;
  * каждому с `newsletter_opt_in = true` — согласие типа `marketing`.

downgrade просто сносит таблицу: исходные колонки на месте, данные не теряются.

Revision ID: 0030
Revises: 0029
Create Date: 2026-07-29
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None

CONSENT_VERSION = "1.0"


def upgrade() -> None:
    op.create_table(
        "user_consents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("consent_type", sa.String(length=32), nullable=False),
        sa.Column("doc_version", sa.String(length=16), nullable=False),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(), nullable=True),
        sa.Column("source_ip", sa.String(length=255), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_consents_user_id", "user_consents", ["user_id"])
    op.create_index("ix_user_consents_user_type", "user_consents",
                    ["user_id", "consent_type"])

    bind = op.get_bind()
    users = bind.execute(sa.text(
        "SELECT id, consent_at, newsletter_opt_in FROM users"
    )).fetchall()
    rows = []
    for user_id, consent_at, newsletter in users:
        if consent_at is not None:
            rows.append({"id": str(uuid.uuid4()), "user_id": user_id,
                         "consent_type": "personal_data",
                         "doc_version": CONSENT_VERSION,
                         "granted_at": consent_at, "withdrawn_at": None,
                         "source_ip": None, "user_agent": None})
        if newsletter:
            rows.append({"id": str(uuid.uuid4()), "user_id": user_id,
                         "consent_type": "marketing",
                         "doc_version": CONSENT_VERSION,
                         "granted_at": consent_at or sa.func.now(),
                         "withdrawn_at": None,
                         "source_ip": None, "user_agent": None})
    if rows:
        bind.execute(sa.text(
            "INSERT INTO user_consents "
            "(id, user_id, consent_type, doc_version, granted_at, withdrawn_at,"
            " source_ip, user_agent) VALUES "
            "(:id, :user_id, :consent_type, :doc_version, :granted_at,"
            " :withdrawn_at, :source_ip, :user_agent)"
        ), rows)


def downgrade() -> None:
    op.drop_index("ix_user_consents_user_type", table_name="user_consents")
    op.drop_index("ix_user_consents_user_id", table_name="user_consents")
    op.drop_table("user_consents")
