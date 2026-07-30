"""Согласие на финданные существующим пользователям (юрблок L1, гейт)

Revision ID: 0031
Revises: 0030
Create Date: 2026-07-30

Зачем миграция. В 0030 единый флаг `users.consent_at` был развёрнут в
раздельные согласия, но у существующих пользователей появилось только
`personal_data`. Одновременно вводится гейт: обработка финансового портрета
требует отдельного согласия `financial_data`. Без этой миграции гейт закрыл бы
доступ ВСЕМ действующим пользователям — они не давали согласия, которого в
момент их регистрации не существовало как отдельной сущности.

Правовое основание переноса. До разделения действовало ОДНО общее согласие, и
его текст покрывал обработку финансовых данных: продукт без них не работает,
и пользователь соглашался именно на такую обработку. Разделение — уточнение
формы, а не появление нового основания. Поэтому корректно зафиксировать
согласие с тем же моментом времени и пометить редакцию как `1.0-legacy`:
видно, что оно выведено из прежнего режима, а не получено отдельным действием.

Обратная миграция удаляет только записи с этой редакцией — согласия, данные
пользователями явно после разделения, не трогаются.
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None

LEGACY_VERSION = "1.0-legacy"


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(sa.text(
        "SELECT user_id, granted_at FROM user_consents "
        "WHERE consent_type = 'personal_data' AND withdrawn_at IS NULL"
    )).fetchall()
    if not rows:
        return

    existing = {
        row[0] for row in bind.execute(sa.text(
            "SELECT user_id FROM user_consents "
            "WHERE consent_type = 'financial_data'"
        )).fetchall()
    }
    payload = [
        {"id": str(uuid.uuid4()), "user_id": user_id,
         "consent_type": "financial_data", "doc_version": LEGACY_VERSION,
         "granted_at": granted_at}
        for user_id, granted_at in rows if user_id not in existing
    ]
    if payload:
        bind.execute(sa.text(
            "INSERT INTO user_consents "
            "(id, user_id, consent_type, doc_version, granted_at) "
            "VALUES (:id, :user_id, :consent_type, :doc_version, :granted_at)"
        ), payload)


def downgrade() -> None:
    op.get_bind().execute(sa.text(
        "DELETE FROM user_consents WHERE consent_type = 'financial_data' "
        "AND doc_version = :version"
    ), {"version": LEGACY_VERSION})
