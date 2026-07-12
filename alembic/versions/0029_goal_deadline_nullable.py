"""goals.deadline nullable — бессрочные цели (ROADMAP §6.3)

Канон допускает цель без срока (`deadline: null`): копим фоном, срочность
нейтральная (u_s = 1.0). Колонка была NOT NULL — бессрочная цель обходилась
костылём «дедлайн через 10 лет».

batch_alter_table обязателен: SQLite не умеет ALTER COLUMN и пересоздаёт таблицу.
Индекс `ix_goals_deadline` batch пересобирает вместе с таблицей.

downgrade: NULL нельзя оставить под NOT NULL — бессрочные цели получают
дальний горизонт (сегодня + 10 лет), то есть ровно тот костыль, от которого ушли.

Revision ID: 0029
Revises: 0028
Create Date: 2026-07-12
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("goals") as batch:
        batch.alter_column(
            "deadline",
            existing_type=sa.DateTime(),
            nullable=True,
        )


def downgrade() -> None:
    op.execute(
        "UPDATE goals SET deadline = "
        + (
            "NOW() + INTERVAL '10 years'"
            if op.get_bind().dialect.name == "postgresql"
            else "datetime('now', '+10 years')"
        )
        + " WHERE deadline IS NULL"
    )
    with op.batch_alter_table("goals") as batch:
        batch.alter_column(
            "deadline",
            existing_type=sa.DateTime(),
            nullable=False,
        )
