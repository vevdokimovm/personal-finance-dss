"""JWT-ревокация (SEC-4.4): blacklist по jti + рубеж tokens_valid_since.

Зачем. Stateless JWT нельзя «отозвать» по своей природе — подпись валидна до exp,
сервер состояния сессии не держит. Это плата за отсутствие похода в БД на каждый
запрос. Но logout и смена пароля обязаны реально гасить доступ, поэтому добавляем
минимальное состояние отзыва:

  - blacklist по jti (таблица revoked_tokens) — точечный отзыв ОДНОГО токена.
    Используется при logout текущей сессии: гасим именно тот токен, что предъявлен,
    не трогая остальные устройства.
  - рубеж tokens_valid_since на пользователе — МАССОВЫЙ отзыв: любой токен с iat
    раньше рубежа считается мёртвым. Используется при logout-all и смене пароля.

Контракт времени — naive-UTC всюду (ADR-002): колонки моделей naive, `utcnow()`
возвращает naive, iat/exp из JWT (unix-секунды) нормализуем в naive-UTC. Сравнения
naive↔naive — риск TypeError исключён.

Гранулярность. iat в JWT — секундной точности (NumericDate). Поэтому рубеж режется
до целой секунды: токен, выпущенный в ту же секунду, что и logout-all, рубеж
переживёт — и это намеренно, чтобы немедленный re-login сразу после logout-all
проходил. Текущий токен при logout-all гасится отдельно и точно — по jti. Краевой
случай: токен ДРУГОГО устройства, выпущенный в ту же секунду, что и logout-all,
рубеж переживёт (sub-секундное окно) — приемлемый остаток, повторный logout-all
его добьёт.

Коммит. Мутаторы (revoke_token / purge_expired / bump_tokens_valid_since) коммитят
сами — как и весь слой crud. Отзыв должен пережить границу запроса: следующий
запрос идёт в новой сессии и обязан видеть уже зафиксированное состояние.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.models import RevokedToken, User
from app.utils.time import utcnow

NumericDate = Union[int, float, datetime]


def epoch_to_naive_utc(value: NumericDate) -> datetime:
    """iat/exp из JWT приходят unix-секундами; приводим к naive-UTC (ADR-002)."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo is not None else value
    return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)


def revoke_token(db: Session, jti: str, expires_at: NumericDate) -> None:
    """Заносит jti в чёрный список до его exp. Идемпотентно: повторный отзыв — no-op."""
    if not jti or db.get(RevokedToken, jti) is not None:
        return
    db.add(RevokedToken(jti=jti, expires_at=epoch_to_naive_utc(expires_at)))
    db.commit()


def is_token_revoked(db: Session, jti: Optional[str]) -> bool:
    """True, если токен с этим jti отозван.

    Токен без jti (legacy, выпущен до SEC-4.4) отозвать точечно нельзя → False;
    это обратная совместимость, а не ошибка.
    """
    if not jti:
        return False
    return db.get(RevokedToken, jti) is not None


def purge_expired(db: Session) -> int:
    """Удаляет из чёрного списка записи с истёкшим exp. Возвращает число удалённых.

    После exp токен и так не пройдёт verify — держать запись смысла нет, чистим,
    чтобы таблица не росла бесконечно.
    """
    result = db.execute(delete(RevokedToken).where(RevokedToken.expires_at <= utcnow()))
    db.commit()
    return result.rowcount or 0


def bump_tokens_valid_since(db: Session, user: User) -> None:
    """Сдвигает рубеж массового отзыва на «сейчас» (до целой секунды).

    Все токены пользователя, выпущенные раньше, перестают проходить проверку.
    """
    user.tokens_valid_since = utcnow().replace(microsecond=0)
    db.commit()


def tokens_invalidated_for(user: User, iat: Optional[NumericDate]) -> bool:
    """True, если токен выпущен ДО рубежа tokens_valid_since пользователя.

    Рубеж не сдвигался (NULL) либо iat отсутствует (legacy) → токен валиден.
    """
    cutoff = user.tokens_valid_since
    if cutoff is None or iat is None:
        return False
    return epoch_to_naive_utc(iat) < cutoff
