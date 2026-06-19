"""Маршруты аутентификации (INFRA-06, NFR-05, DATA-03).

Регистрация/логин выдают JWT, который кладётся в httpOnly-cookie (защита от XSS)
и параллельно возвращается в теле (для не-браузерных клиентов). Первый
зарегистрированный пользователь усыновляет данные анонимного режима
(single→multi-миграция без потери данных).
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import (
    adopt_orphan_rows,
    count_users,
    create_user,
    delete_user,
    get_user_by_email,
    mark_email_verified,
    update_user_password,
    update_user_profile,
)
from app.database.models import User
from app.dependencies import get_db, require_user
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)
from app.services.email_service import email_service
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
def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AuthResponse:
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

    # Ссылка подтверждения email (токен на 48 ч).
    verify_token = token_service.issue_verification(user.id, user.email)
    verify_url = str(request.base_url).rstrip("/") + f"/api/auth/verify?token={verify_token}"
    # Письмо с подтверждением — фоном, чтобы ответ не ждал SMTP и не падал при сбое.
    background_tasks.add_task(
        email_service.send_verification, user.email, verify_url, user.display_name
    )

    # Первый пользователь усыновляет данные анонимного режима (single→multi).
    if is_first_user:
        adopted = adopt_orphan_rows(db, user.id)
        log_event("orphan_rows_adopted", {"count": adopted}, user_id=user.id)

    token = token_service.issue(user.id, user.email)
    _set_auth_cookie(response, token)
    log_event("user_registered", {"first_user": is_first_user}, user_id=user.id)

    # В dev (без SMTP) отдаём ссылку прямо в ответе — чтобы можно было подтвердить локально.
    dev_link = verify_url if (not settings.email_enabled and not settings.is_production) else None
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
        verification_url=dev_link,
    )


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


@router.get("/verify", summary="Подтверждение email по ссылке из письма")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    user_id = token_service.decode_verification(token)
    if user_id and mark_email_verified(db, user_id):
        log_event("email_verified", {}, user_id=user_id)
        return RedirectResponse(url="/profile?verified=1", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/profile?verified=0", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/resend-verification", summary="Повторно отправить письмо подтверждения")
def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_user),
) -> dict[str, str | None]:
    if user.email_verified:
        return {"detail": "Email уже подтверждён.", "verification_url": None}
    verify_token = token_service.issue_verification(user.id, user.email)
    verify_url = str(request.base_url).rstrip("/") + f"/api/auth/verify?token={verify_token}"
    background_tasks.add_task(
        email_service.send_verification, user.email, verify_url, user.display_name
    )
    dev_link = verify_url if (not settings.email_enabled and not settings.is_production) else None
    return {"detail": "Письмо отправлено.", "verification_url": dev_link}


@router.patch("/me", response_model=UserResponse, summary="Обновить профиль")
def update_profile(
    payload: UpdateProfileRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    updated = update_user_profile(db, user_id=user.id, display_name=payload.display_name)
    return UserResponse.model_validate(updated)


@router.post("/change-password", summary="Сменить пароль")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if not password_hasher.verify(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текущий пароль неверен.",
        )
    update_user_password(db, user_id=user.id, password_hash=password_hasher.hash(payload.new_password))
    return {"detail": "Пароль обновлён."}


@router.delete("/me", summary="Удалить аккаунт со всеми данными")
def delete_account(
    response: Response,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    delete_user(db, user_id=user.id)
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME, path="/")
    return {"detail": "Аккаунт и все данные удалены."}
