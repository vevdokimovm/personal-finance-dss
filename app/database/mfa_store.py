"""Хранилище состояния MFA (раздел 4.4).

Операции над секретом TOTP и recovery-кодами в БД. Крипто — в `services/mfa.py`,
здесь — только доступ к данным (как `revocation.py` для отзыва токенов).
"""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.models import MfaRecoveryCode, User
from app.services import mfa as mfa_service
from app.utils.time import utcnow


def set_pending_secret(db: Session, user: User, secret: str) -> None:
    """Завести секрет в состоянии «pending» (ещё не подтверждён кодом)."""
    user.mfa_secret = secret
    user.mfa_enabled = False
    db.commit()


def activate_mfa(db: Session, user: User, recovery_hashes: list[str]) -> None:
    """Активировать MFA и заменить набор recovery-кодов (хеши)."""
    user.mfa_enabled = True
    db.execute(delete(MfaRecoveryCode).where(MfaRecoveryCode.user_id == user.id))
    for code_hash in recovery_hashes:
        db.add(MfaRecoveryCode(user_id=user.id, code_hash=code_hash))
    db.commit()


def disable_mfa(db: Session, user: User) -> None:
    """Полностью выключить MFA: убрать секрет, флаг и все recovery-коды."""
    user.mfa_secret = None
    user.mfa_enabled = False
    db.execute(delete(MfaRecoveryCode).where(MfaRecoveryCode.user_id == user.id))
    db.commit()


def consume_recovery_code(db: Session, user: User, code: str) -> bool:
    """Сверить код с неиспользованными recovery-кодами; при совпадении пометить
    использованным (одноразовость) и вернуть True."""
    rows = db.execute(
        select(MfaRecoveryCode).where(
            MfaRecoveryCode.user_id == user.id,
            MfaRecoveryCode.used_at.is_(None),
        )
    ).scalars().all()
    for row in rows:
        if mfa_service.verify_recovery_code(code, row.code_hash):
            row.used_at = utcnow()
            db.commit()
            return True
    return False
