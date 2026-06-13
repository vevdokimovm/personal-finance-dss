"""Маршруты аутентификации (INFRA-06, NFR-05, DATA-03).

Регистрация/логин выдают JWT, который кладётся в httpOnly-cookie (защита от XSS)
и параллельно возвращается в теле (для не-браузерных клиентов). Первый
зарегистрированный пользователь усыновляет данные анонимного режима
(single→multi-миграция без потери данных).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import (
    adopt_orphan_rows,
    count_users,
    create_user,
    get_user_by_email,
)
from app.database.models import User
from app.dependencies import get_db, require_user
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.event_logger import log_event
from app.services.security import password_hasher, token_service

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        max_age=settings.JWT_TTL_HOURS * 3600,
        path="/",
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже зарегистрирован.",
        )

    is_first_user = count_users(db) == 0
    user = create_user(
        db=db,
        email=payload.email,
        password_hash=password_hasher.hash(payload.password),
        display_name=payload.display_name,
    )

    # Первый пользователь усыновляет данные анонимного режима (single→multi).
    if is_first_user:
        adopted = adopt_orphan_rows(db, user.id)
        log_event("orphan_rows_adopted", {"count": adopted}, user_id=user.id)

    token = token_service.issue(user.id, user.email)
    _set_auth_cookie(response, token)
    log_event("user_registered", {"first_user": is_first_user}, user_id=user.id)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthResponse, summary="Вход")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = get_user_by_email(db, payload.email)
    if user is None or not password_hasher.verify(payload.password, user.password_hash):
        log_event("login_failed", {"email_domain": payload.email.split("@")[-1]})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учётная запись отключена."
        )

    token = token_service.issue(user.id, user.email)
    _set_auth_cookie(response, token)
    log_event("login_success", user_id=user.id)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/logout", summary="Выход")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME, path="/")
    return {"detail": "Сессия завершена."}


@router.get("/me", response_model=UserResponse, summary="Текущий пользователь")
def me(user: User = Depends(require_user)) -> UserResponse:
    return UserResponse.model_validate(user)
