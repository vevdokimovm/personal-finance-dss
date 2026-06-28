from typing import Optional

import secrets
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import get_user_by_id, get_user_household_ids
from app.database.db import get_db
from app.database.models import User
from app.services.security import token_service

__all__ = [
    "get_db",
    "get_current_user",
    "require_user",
    "get_current_user_id",
    "get_current_scope",
    "RequestScope",
    "require_admin",
]


def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> None:
    """Защита админ-эндпоинтов (аналитика, cron-триггеры).

    В production ADMIN_API_KEY обязателен (старт упадёт при отсутствии — fail-loud), и эндпоинт
    требует совпадающий заголовок X-Admin-Key. В development при пустом ключе доступ открыт —
    чтобы не мешать локальной разработке и тестам.
    """
    expected = settings.ADMIN_API_KEY
    if not expected:
        if settings.is_production:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Админ-доступ не сконфигурирован (ADMIN_API_KEY).",
            )
        return
    if not x_admin_key or not secrets.compare_digest(x_admin_key, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недействительный админ-ключ."
        )


def _extract_token(request: Request) -> Optional[str]:
    """JWT из заголовка Authorization: Bearer (приоритет) либо из httpOnly-cookie.

    Явный Bearer-токен сильнее амбиентной cookie: API-клиент, передавший токен
    заголовком, всегда работает от своего имени, даже если в запросе затесалась
    чужая/устаревшая cookie.
    """
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    cookie = request.cookies.get(settings.AUTH_COOKIE_NAME)
    if cookie:
        return cookie
    return None


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    """Опциональный текущий пользователь.

    Возвращает None в анонимном режиме (legacy single-user v2.x) — это не ошибка.
    Защищённые роуты используют require_user, остальные деградируют к None.
    """
    token = _extract_token(request)
    if not token:
        return None
    payload = token_service.decode(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return get_user_by_id(db, user_id)


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    """Жёсткая защита: 401, если пользователь не аутентифицирован."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_id(
    user: Optional[User] = Depends(get_current_user),
) -> Optional[str]:
    """Идентификатор владельца для фильтрации данных (None = анонимный режим)."""
    return user.id if user is not None else None


@dataclass(frozen=True)
class RequestScope:
    """Скоуп текущего запроса: персональный владелец + его household-ы (P3.7).

    Удобно для эндпоинтов, которым нужно одновременно знать user_id и состав
    домохозяйств (например, чтобы решить, в чей котёл писать). Чтение доменных
    данных household-скоуп подмешивает само (в crud._owner_filter), поэтому для
    обычных list-эндпоинтов достаточно get_current_user_id.
    """

    user_id: Optional[str]
    household_ids: tuple[int, ...]


def get_current_scope(
    user_id: Optional[str] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RequestScope:
    return RequestScope(
        user_id=user_id,
        household_ids=tuple(get_user_household_ids(db, user_id)),
    )
