"""Маршруты аутентификации (INFRA-06, NFR-05, DATA-03).

Регистрация/логин выдают JWT, который кладётся в httpOnly-cookie (защита от XSS)
и параллельно возвращается в теле (для не-браузерных клиентов). Первый
зарегистрированный пользователь усыновляет данные анонимного режима
(single→multi-миграция без потери данных).
"""
from __future__ import annotations

from functools import partial

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import (
    count_users,
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_referral_code,
    mark_email_verified,
    register_failed_login,
    reset_failed_logins,
    update_user_password,
    update_user_profile,
)
from app.database.models import User
from app.dependencies import get_db, require_user
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    UserResponse,
)
from app.services.email_dispatch import dispatch_email
from app.services.email_service import email_service
from app.services.event_logger import log_event
from app.services.security import password_hasher, token_service
from app.utils.time import utcnow

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

    if not payload.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо согласие на обработку персональных данных.",
        )

    is_first_user = count_users(db) == 0
    # Реферальный код учитываем только если он реально существует.
    referred_by = None
    if payload.referral_code:
        inviter = get_user_by_referral_code(db, payload.referral_code.strip().upper())
        if inviter:
            referred_by = inviter.referral_code
    user = create_user(
        db=db,
        email=payload.email,
        password_hash=password_hasher.hash(payload.password),
        display_name=payload.display_name,
        newsletter_opt_in=payload.newsletter_opt_in,
        referred_by_code=referred_by,
    )

    # Ссылка подтверждения email (токен на 48 ч).
    verify_token = token_service.issue_verification(user.id, user.email)
    verify_url = str(request.base_url).rstrip("/") + f"/api/auth/verify?token={verify_token}"
    # Письмо с подтверждением — фоном, чтобы ответ не ждал SMTP и не падал при сбое.
    # Результат отправки фиксируется событием (email_sent/skipped/failed) — наблюдаемость.
    background_tasks.add_task(
        dispatch_email,
        partial(email_service.send_verification, user.email, verify_url, user.display_name),
        event_kind="verification",
        to_email=user.email,
        user_id=user.id,
    )

    # Гостевой режим постоянный: новый пользователь начинает с чистого аккаунта,
    # гостевые/демо-данные остаются в анонимном пуле (user_id IS NULL) и видны
    # только в гостевом режиме.

    token = token_service.issue(user.id, user.email)
    _set_auth_cookie(response, token)
    log_event("user_registered", {"first_user": is_first_user}, user_id=user.id)

    # В dev (без SMTP) отдаём ссылку прямо в ответе — чтобы можно было подтвердить локально.
    # без SMTP отдаём ссылку (self-hosted)
    dev_link = verify_url if not settings.email_enabled else None
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
        verification_url=dev_link,
    )


@router.post("/login", response_model=AuthResponse, summary="Вход")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = get_user_by_email(db, payload.email)

    # Блокировка действует даже при верном пароле, пока не истечёт срок.
    if user is not None and user.locked_until and user.locked_until > utcnow():
        retry_min = max(1, int((user.locked_until - utcnow()).total_seconds() // 60) + 1)
        log_event("login_locked", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Слишком много неудачных попыток. Повторите через {retry_min} мин.",
        )

    if user is None or not password_hasher.verify(payload.password, user.password_hash):
        if user is not None:
            register_failed_login(
                db, user, settings.LOGIN_MAX_ATTEMPTS, settings.LOGIN_LOCKOUT_MINUTES
            )
        log_event("login_failed", {"email_domain": payload.email.split("@")[-1]})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Учётная запись отключена."
        )

    reset_failed_logins(db, user)
    token = token_service.issue(user.id, user.email)
    _set_auth_cookie(response, token)
    log_event("login_success", user_id=user.id)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/logout", summary="Выход")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME, path="/")
    return {"detail": "Сессия завершена."}


@router.post("/forgot-password", summary="Запрос сброса пароля")
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    user = get_user_by_email(db, payload.email)

    # Энумерация закрыта: ответ одинаков независимо от того, есть ли такой email.
    reset_url: str | None = None
    if user is not None:
        token = token_service.issue_password_reset(
            user.id, user.email, settings.PASSWORD_RESET_TTL_HOURS
        )
        reset_url = str(request.base_url).rstrip("/") + f"/reset-password?token={token}"
        background_tasks.add_task(
            dispatch_email,
            partial(email_service.send_password_reset, user.email, reset_url, user.display_name),
            event_kind="password_reset",
            to_email=user.email,
            user_id=user.id,
        )
        log_event("password_reset_requested", user_id=user.id)

    # В dev (без SMTP) отдаём ссылку прямо в ответе — чтобы можно было сбросить локально.
    dev_link = reset_url if (user is not None and not settings.email_enabled) else None
    return {
        "detail": "Если аккаунт с таким email существует, "
                  "на него отправлена ссылка для сброса пароля.",
        "reset_url": dev_link,
    }


@router.post("/reset-password", summary="Установка нового пароля по токену")
def reset_password(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    user_id = token_service.decode_password_reset(payload.token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ссылка для сброса недействительна или истекла.",
        )

    user = update_user_password(db, user_id, password_hasher.hash(payload.new_password))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ссылка для сброса недействительна или истекла.",
        )

    # Сброс пароля снимает блокировку аккаунта — пользователь восстановил доступ.
    reset_failed_logins(db, user)
    log_event("password_reset_completed", user_id=user.id)
    return {"detail": "Пароль обновлён. Теперь вы можете войти с новым паролем."}


@router.get("/me", response_model=UserResponse, summary="Текущий пользователь")
def me(user: User = Depends(require_user)) -> UserResponse:
    log_event("pii_access", {"resource": "profile", "action": "read"}, user_id=user.id)
    return UserResponse.model_validate(user)


@router.get("/verify", summary="Подтверждение email по ссылке из письма")
def verify_email(
    token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    user_id = token_service.decode_verification(token)
    user = mark_email_verified(db, user_id) if user_id else None
    if user:
        log_event("email_verified", {}, user_id=user.id)
        # Приветственное письмо — после подтверждения адреса, фоном.
        background_tasks.add_task(
            dispatch_email,
            partial(email_service.send_welcome, user.email, user.display_name),
            event_kind="welcome",
            to_email=user.email,
            user_id=user.id,
        )
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
        dispatch_email,
        partial(email_service.send_verification, user.email, verify_url, user.display_name),
        event_kind="verification",
        to_email=user.email,
        user_id=user.id,
    )
    # без SMTP отдаём ссылку (self-hosted)
    dev_link = verify_url if not settings.email_enabled else None
    return {"detail": "Письмо отправлено.", "verification_url": dev_link}


@router.patch("/me", response_model=UserResponse, summary="Обновить профиль")
def update_profile(
    payload: UpdateProfileRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    updated = update_user_profile(db, user_id=user.id, display_name=payload.display_name)
    log_event("pii_access", {"resource": "profile", "action": "update"}, user_id=user.id)
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
    update_user_password(db, user_id=user.id,
                         password_hash=password_hasher.hash(payload.new_password))
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
