"""Хранилище состояния MFA (раздел 4.4).

Операции над секретом TOTP и recovery-кодами в БД. Крипто — в `services/mfa.py`,
здесь — только доступ к данным (как `revocation.py` для отзыва токенов).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.models import MfaPendingAttempt, MfaRecoveryCode, User
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


# Порог неудачных кодов на ОДИН `mfa_pending`-токен. Пять — компромисс между
# опечаткой и перебором: человек, читающий шестизначный код с телефона, ошибается
# один-два раза; пять неверных подряд означают либо чужой телефон, либо машину.
MAX_MFA_ATTEMPTS = 5


def register_mfa_failure(db: Session, jti: str, user_id: str, expires_at: datetime) -> int:
    """Учесть неудачный код и вернуть общее число неудач по этому токену.

    🔴 **Считается токен, а не пользователь** (v9.2.0). Счётчик на пользователе выглядит
    строже и слабее на деле: атакующий, знающий пароль, повторным входом получает новый
    токен и обнуляет счёт. Привязка к токену делает партию догадок дороже ровно на один
    полный вход — то есть переносит стоимость туда, где уже стоят и лимит, и учёт
    неудачных входов.

    Строка заводится при ПЕРВОЙ неудаче, а не при выдаче токена: у подавляющего
    большинства входов неудач нет вовсе, и таблица не должна расти по числу входов.

    Args:
        jti: Идентификатор выдачи из `mfa_pending`-токена.
        user_id: Владелец токена — для каскадного удаления вместе с аккаунтом.
        expires_at: Срок годности самого токена; строка живёт не дольше него.

    Returns:
        Сколько неудач накопилось по этому токену, включая текущую.
    """
    purge_expired_mfa_attempts(db)
    row = db.get(MfaPendingAttempt, jti)
    if row is None:
        row = MfaPendingAttempt(
            jti=jti, user_id=user_id, failures=1, expires_at=expires_at
        )
        db.add(row)
    else:
        row.failures += 1
    db.commit()
    return row.failures


def mfa_token_is_burned(db: Session, jti: str) -> bool:
    """Исчерпан ли лимит попыток по этому токену.

    🔴 Проверяется ДО сверки кода — иначе верный код, угаданный на шестой попытке,
    прошёл бы, и весь счётчик оказался бы украшением.
    """
    row = db.get(MfaPendingAttempt, jti)
    return row is not None and row.failures >= MAX_MFA_ATTEMPTS


def clear_mfa_attempts(db: Session, jti: str) -> None:
    """Убрать счётчик после успешного входа — токен отработал, следить больше не за чем."""
    db.execute(delete(MfaPendingAttempt).where(MfaPendingAttempt.jti == jti))
    db.commit()


def purge_expired_mfa_attempts(db: Session) -> None:
    """Выбросить счётчики токенов, которые всё равно уже недействительны.

    Зовётся из `register_mfa_failure`, то есть по неудаче, а не по расписанию:
    отдельный планировщик ради таблицы, растущей только от неудачных входов, —
    механизм дороже задачи. Диапазон закрыт индексом по `expires_at`.
    """
    db.execute(delete(MfaPendingAttempt).where(MfaPendingAttempt.expires_at < utcnow()))
    db.commit()
