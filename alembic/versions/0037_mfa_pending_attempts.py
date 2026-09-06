"""Счётчик неудачных кодов на один `mfa_pending`-токен.

🔴 Вторая половина защиты второго фактора. В v9.1.0 префикс `/api/auth/mfa/` попал
под rate-limit, и это закрыло **частоту** попыток. Общее их число за пять минут жизни
токена осталось неограниченным: атакующий, знающий пароль, получает токен и перебирает
шестизначный TOTP столько раз, сколько успевает в разрешённом темпе.

Таблица привязывает счётчик к КОНКРЕТНОМУ токену (`jti`), а не к пользователю. Счётчик
на пользователе выглядит строже и слабее на деле: повторный вход выдаёт новый токен
и обнуляет счёт. Привязка к токену делает каждую партию догадок дороже ровно на один
полный вход — там уже стоит и лимит, и учёт неудачных входов.

В базе, а не в памяти процесса: за gunicorn с четырьмя воркерами память дала бы четыре
независимых счётчика, то есть порог, тихо умноженный на число воркеров.

`ondelete="CASCADE"` — строки не переживают своего пользователя; удаление аккаунта
не должно спотыкаться о служебный счётчик.

Revision ID: 0037
Revises: 0036
"""
import sqlalchemy as sa
from alembic import op

revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mfa_pending_attempts",
        sa.Column("jti", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE",
            name="fk_mfa_pending_attempts_user",
        ),
    )
    op.create_index(
        "ix_mfa_pending_attempts_user_id", "mfa_pending_attempts", ["user_id"]
    )
    # Индекс по сроку: чистка протухших строк идёт диапазонным условием, и без него
    # она превращается в полный проход по таблице при каждой неудачной попытке.
    op.create_index(
        "ix_mfa_pending_attempts_expires_at", "mfa_pending_attempts", ["expires_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_mfa_pending_attempts_expires_at", table_name="mfa_pending_attempts")
    op.drop_index("ix_mfa_pending_attempts_user_id", table_name="mfa_pending_attempts")
    op.drop_table("mfa_pending_attempts")
