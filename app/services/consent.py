"""Согласия пользователя: выдача, отзыв, текущее состояние (юрблок L1, L3, L4).

Ключевое правило подсистемы: **запись согласия неизменяема по смыслу**. Отзыв
проставляет `withdrawn_at`, но не удаляет строку и не меняет тип или версию —
доказательство обязано пережить отзыв, иначе нечем подтвердить, что в такой-то
период обработка велась на законном основании. Повторная выдача создаёт новую
строку, а не воскрешает старую.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.legal import (
    CONSENT_TYPES,
    UNWITHDRAWABLE,
    current_version,
    is_known,
)
from app.database.models import UserConsent, utcnow


class ConsentWithdrawalNotAllowed(Exception):
    """Отзыв согласия, которое является основанием обработки.

    Отозвать согласие на обработку ПДн, сохранив аккаунт, нельзя: это оставило
    бы данные без правового основания. Путь пользователя — удаление аккаунта,
    которое уносит и данные, и согласия.
    """


def _require_known(consent_type: str) -> None:
    if not is_known(consent_type):
        raise ValueError(f"неизвестный тип согласия: {consent_type}")


def _active(db: Session, user_id: str,
            consent_type: str) -> Optional[UserConsent]:
    """Последнее действующее согласие данного типа, если есть."""
    return (db.query(UserConsent)
            .filter(UserConsent.user_id == user_id,
                    UserConsent.consent_type == consent_type,
                    UserConsent.withdrawn_at.is_(None))
            .order_by(UserConsent.granted_at.desc())
            .first())


def grant_consent(db: Session, user_id: str, consent_type: str, *,
                  source_ip: Optional[str] = None,
                  user_agent: Optional[str] = None) -> UserConsent:
    """Выдать согласие. Если действующее уже есть — возвращается оно же."""
    _require_known(consent_type)
    existing = _active(db, user_id, consent_type)
    if existing is not None:
        return existing
    record = UserConsent(
        user_id=user_id,
        consent_type=consent_type,
        doc_version=current_version(consent_type),
        granted_at=utcnow(),
        source_ip=source_ip,
        user_agent=user_agent,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def withdraw_consent(db: Session, user_id: str, consent_type: str) -> bool:
    """Отозвать согласие. Строка сохраняется, проставляется `withdrawn_at`."""
    _require_known(consent_type)
    if consent_type in UNWITHDRAWABLE:
        raise ConsentWithdrawalNotAllowed(consent_type)
    record = _active(db, user_id, consent_type)
    if record is None:
        return False
    record.withdrawn_at = utcnow()
    db.commit()
    return True


def has_consent(db: Session, user_id: str, consent_type: str) -> bool:
    _require_known(consent_type)
    return _active(db, user_id, consent_type) is not None


def active_consents(db: Session, user_id: str) -> dict[str, UserConsent]:
    """Действующие согласия пользователя по типам (отозванные не попадают)."""
    rows = (db.query(UserConsent)
            .filter(UserConsent.user_id == user_id,
                    UserConsent.withdrawn_at.is_(None))
            .order_by(UserConsent.granted_at.desc())
            .all())
    state: dict[str, UserConsent] = {}
    for row in rows:
        state.setdefault(row.consent_type, row)
    return state


def consent_state(db: Session, user_id: str) -> dict[str, dict]:
    """Состояние по ВСЕМ известным типам — форма ответа API.

    Возвращаются все типы, включая невыданные: фронту нужно знать не только что
    выдано, но и что предстоит спросить.
    """
    active = active_consents(db, user_id)
    state: dict[str, dict] = {}
    for consent_type in CONSENT_TYPES:
        record = active.get(consent_type)
        state[consent_type] = {
            "granted": record is not None,
            "version": record.doc_version if record else current_version(consent_type),
            "granted_at": record.granted_at.isoformat() if record else None,
            "withdrawable": consent_type not in UNWITHDRAWABLE,
        }
    return state


def purge_consents(db: Session, user_id: str) -> None:
    """Удалить согласия при удалении аккаунта (152-ФЗ, право на удаление).

    Здесь право на удаление перевешивает интерес хранить доказательство: данных,
    для которых нужно основание, больше нет.
    """
    db.execute(delete(UserConsent).where(UserConsent.user_id == user_id))
