from typing import Optional

import secrets
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import get_user_by_id, get_user_household_ids
from app.database.db import get_db
from app.database.models import User
from app.database.revocation import is_token_revoked, tokens_invalidated_for
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
    # Только полный сессионный токен аутентифицирует. Purpose-токены (mfa_pending,
    # email_verify, password_reset, telegram_link) имеют claim `purpose` и сессией
    # не являются — иначе промежуточный/одноразовый токен давал бы полный доступ.
    if payload.get("purpose"):
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    # Рубеж A — точечный отзыв токена по jti (logout текущей сессии).
    if is_token_revoked(db, payload.get("jti")):
        return None
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    # Рубеж B — массовый отзыв: токен выпущен до отсечки tokens_valid_since
    # (logout-all, смена пароля). Легаси-токены без iat сюда не попадают.
    if tokens_invalidated_for(user, payload.get("iat")):
        return None
    return user


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    """Жёсткая защита: 401, если пользователь не аутентифицирован."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

# Пути демо-песочницы, доступные гостю на проде.
#
# `/api/demo/analyze` — POST, который ничего не пишет: считает произвольный портрет
# в памяти и в БД не заглядывает.
#
# 🔴 `/api/demo/load` и `/api/demo/clear` добавлены 08.09.2026. Они ПИШУТ, и пишут
# в ОБЩИЙ анонимный пул — один на всех гостей сервера, как и всё остальное
# с `user_id IS NULL`.
#
# 🔴 **Поправка к первой редакции этого комментария.** Я написал «пишут исключительно
# в демо-пул того же гостя» — это НЕВЕРНО и опровергается кодом двадцатью строками
# ниже, в докстроке самого гейта: `_clear_all(user_id=None)` бьёт по всему пулу,
# и вставка идёт туда же. Разделения по гостям не существует. Найдено восьмым
# проходом независимого аудита.
#
# **Решение оставлено в силе, но обоснование теперь честное.** Что реально стоит
# на двух чашах:
#   — запрет: демо-песочница на проде недостижима ВСЕМ (гость 401 отсюда, вошедший
#     403 от самих ручек), то есть у продукта нет входа без аккаунта вовсе;
#   — разрешение: два одновременных посетителя витрины затирают демо друг другу —
#     гость A выбрал «Анну», гость B нажал «Павла», у A на экране Павел.
# В пуле при этом только СИНТЕТИКА: гостевая запись финансовых данных на проде
# запрещена всем остальным периметром, так что ПДн там взяться неоткуда, а цена
# столкновения — повторный клик. Полное решение — сессионный пул с `session_id`
# (задача вехи 9+), и оно снимает вопрос целиком.
#
# Без исключения демо-песочница на проде была недостижима ВСЕМ СРАЗУ:
# гость получал 401 отсюда, а вошедший — 403 от самих ручек («демо доступны только
# в гостевом режиме», правило старше и написано под другую эпоху). Два верных
# по отдельности условия сомкнулись, и единственный вход в продукт без аккаунта —
# он же витрина из README — переставал работать на проде, оставаясь рабочим локально.
#
# Найдено шестым проходом независимого аудита. Гейт периметра увидеть этого не мог:
# он проверяет, ЗАКРЫТА ли ручка, а не может ли её кто-нибудь пройти.
READ_ONLY_WRITE_PATHS = frozenset({
    "/api/demo/analyze",
    "/api/demo/load",
    "/api/demo/clear",
})


def require_account_for_writes(
    request: Request,
    user: Optional[User] = Depends(get_current_user),
) -> Optional[User]:
    """🔴 На проде запись финансовых данных требует аккаунта (v8.53.0).

    **Что закрывает.** `get_current_user_id` отдаёт гостю `None`, а
    `_owner_filter(query, model, None)` фильтрует по `user_id IS NULL` — то есть
    гостевой пул **один глобальный на всех посетителей сервера**, без привязки
    к сессии. Посетитель Б видит операции, цели и кредиты посетителя А;
    `/demo/load` зовёт `_clear_all(user_id=None)` и стирает данные всех гостей
    разом. Найдено аудитом independent-expert 05.09.2026.

    **Почему запрет, а не сессионный пул.** Правильная починка — свой `session_id`
    каждому гостю с колонкой во всех финансовых таблицах и фильтрацией по ней:
    изменение схемы и правка каждого запроса. Утечка чужих финансов столько
    не ждёт. Цена ошибки в обе стороны несимметрична: запрет обратим одной
    строкой конфига, утечка персональных данных — нет.

    **Почему на роутере, а не на каждой ручке.** Тот же довод, что у `_FIN`
    (`app/api/router.py`): пропуск одной ручки означал бы дыру, которую нечем
    заметить. Метод проверяется здесь, поэтому чтение остаётся открытым само
    собой, а новая мутирующая ручка получает защиту, не вспомнив о ней.

    **Только в production.** В development гостевая запись — рабочий инструмент,
    и общего пула там не существует: сервер один и человек за ним один.

    Returns:
        Пользователя, если он есть; `None` для гостя, когда запрет не применяется.

    Raises:
        HTTPException: 401, если гость мутирует данные на проде. Именно 401,
            а не 403: человек не «не имеет права», он не представился.
    """
    if user is not None:
        return user
    # Через `is_production`, а не прямым сравнением: property нормализует регистр
    # и пробелы, и "Production" в .env не должно молча снимать защиту.
    if not settings.is_production:
        return None
    if request.method in SAFE_METHODS:
        return None
    # Точное совпадение, а не `endswith` (найдено `/code-review`): суффиксное сравнение
    # молча освободило бы от гейта любой будущий роут, чей путь оканчивается так же.
    if request.url.path in READ_ONLY_WRITE_PATHS:
        return None
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Чтобы вносить свои финансовые данные, нужен аккаунт. "
            "Демо-портреты доступны для просмотра без регистрации."
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_premium(user: User = Depends(require_user)) -> User:
    """Защита платных эндпоинтов (каркас монетизации): 403, если тариф не premium.

    Эффективный тариф учитывает срок — premium с истёкшим plan_expires_at = free."""
    from app.services.subscription import is_premium

    if not is_premium(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Функция доступна на тарифе Premium.",
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


def require_admin(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    current_user: Optional[User] = Depends(get_current_user),
) -> None:
    """Защита админ-эндпоинтов (аналитика, A/B-эксперименты, cron-триггеры).

    Два независимых способа пройти, и оба нужны:

    1. **Владелец продукта по входу** (`user.is_owner`) — чтобы смотреть аналитику
       в интерфейсе, а не через `curl`. Решение владельца 04.09.2026; альтернативой
       был ключ в браузере, но его пришлось бы хранить в `localStorage` — секрет
       за пределами `.env`, доступный любому скрипту страницы.
    2. **`X-Admin-Key`** — для скриптов и cron: у них нет аккаунта, и заменить ключ
       признаком владельца значило бы сломать автоматизацию.

    В production ADMIN_API_KEY обязателен (старт упадёт при отсутствии — fail-loud).
    В development при пустом ключе доступ открыт — чтобы не мешать локальной разработке
    и тестам. 🔴 Из-за этой ветки тесты разграничения обязаны задавать ключ явно, иначе
    они зелены по причине, не имеющей отношения к утверждению
    (`tests/test_owner_access.py`).
    """
    # Владелец первым: у него может не быть ключа вовсе, и это нормальный путь.
    if current_user is not None and getattr(current_user, "is_owner", False):
        return

    expected = settings.ADMIN_API_KEY
    if not expected:
        if settings.is_production:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Админ-доступ не сконфигурирован (ADMIN_API_KEY).",
            )
        return
    # 🔴 Сравниваем БАЙТЫ (найдено `/code-review`). `secrets.compare_digest` на строке
    # с не-ASCII бросает `TypeError`: `curl -H "X-Admin-Key: пароль"` давал 500 вместо
    # 403 — необработанное исключение вместо отказа, плюс шум в Sentry от любого сканера.
    # Кодирование в UTF-8 сохраняет постоянство времени сравнения.
    if not x_admin_key or not secrets.compare_digest(
        x_admin_key.encode("utf-8"), expected.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недействительный админ-ключ."
        )
