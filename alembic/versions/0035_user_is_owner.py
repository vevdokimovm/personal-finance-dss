"""владелец продукта видит аналитику по входу, а не по ADMIN_API_KEY (v8.48.0)

Решение владельца 04.09.2026. Альтернативой был ключ в браузере — его пришлось бы
хранить в localStorage, то есть держать секрет за пределами `.env`, доступный любому
скрипту на странице. Признак в базе не заводит нового секрета и переиспользуется
(поддержка, будущие роли).

🔴 `server_default=false()` обязателен: без него существующие строки на PostgreSQL
получают NULL в NOT NULL-колонке и миграция падает на непустой базе (тот же приём,
что 0018 и 0034). На SQLite это прошло бы незамеченным — таблица пересоздаётся.

Revision ID: 0035
Revises: 0034
Create Date: 2026-09-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column("is_owner", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("is_owner")
