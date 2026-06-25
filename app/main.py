from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.api.router import router as api_router
from app.api.routes_b2b import router as b2b_router
from app.config import settings, validate_production_security
from app.database.db import engine
from app.database.init_db import init_db
from app.database.models import User
from app.dependencies import get_current_user
from app.logging_config import setup_logging
from app.middleware import (
    CSRFMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.observability import init_sentry

PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["app_version"] = settings.APP_VERSION

# Наблюдаемость (P1.5): структурное логирование + опциональный Sentry.
setup_logging(level=settings.LOG_LEVEL, json_format=settings.LOG_JSON)
init_sentry(settings.SENTRY_DSN, environment=settings.ENVIRONMENT, release=settings.APP_VERSION)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Трекинг ошибок: Sentry подключаем первым, чтобы ловить и сбои старта.
    # release = версия (ошибки группируются по релизу); no-op без DSN (локально/тесты).
    init_sentry(
        settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.APP_VERSION,
    )
    # Fail-loud: в production не стартуем с дефолтными секретами / незащищённой cookie.
    problems = validate_production_security(settings)
    if problems:
        raise RuntimeError(
            "Небезопасная конфигурация для production:\n  - " + "\n  - ".join(problems)
        )
    init_db()
    # init_db прогоняет миграции через alembic, чей fileConfig сбрасывает logging —
    # восстанавливаем структурный JSON-логгер для рантайма.
    setup_logging(level=settings.LOG_LEVEL, json_format=settings.LOG_JSON)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Эндпоинты под rate-лимитом: чувствительные (auth, импорт, анализ) + дорогие compute-пути
# (planning/calculate и /forecast — Monte Carlo; защита от ресурсного абьюза, P0.4 hardening).
RATE_LIMITED_PREFIXES = (
    "/api/recommendation",
    "/api/banks",
    "/api/analysis",
    "/api/auth/login",
    "/api/auth/register",
    "/api/planning/calculate",
    "/api/planning/forecast",
    "/v1/analyze",
)

# Rate-limit добавляется первым → внутренний слой; CORS — внешний (перехватывает preflight).
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    protected_prefixes=RATE_LIMITED_PREFIXES,
)
app.add_middleware(CSRFMiddleware, allowed_origins=settings.cors_origins_list)
app.add_middleware(SecurityHeadersMiddleware, hsts=settings.is_production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Внешний слой: логирует финальный статус каждого запроса и проставляет X-Request-ID.
app.add_middleware(RequestLoggingMiddleware)


@app.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    """Health-check: liveness + проверка коннекта к БД (для docker/балансировщика/мониторинга)."""
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    healthy = db_status == "ok"
    return JSONResponse(
        {
            "status": "ok" if healthy else "degraded",
            "database": db_status,
            "version": settings.APP_VERSION,
        },
        status_code=200 if healthy else 503,
    )

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(api_router)
app.include_router(b2b_router)  # B2B-контракт /v1/analyze вне /api-префикса (FR-23)


def page_context(
    request: Request, current_user: Optional[User] = Depends(get_current_user)
) -> dict[str, Any]:
    """Контекст для SSR-страниц. current_user управляет видимостью гостевых элементов
    (загрузка демо-портретов и раздел валидации скрыты для вошедших пользователей)."""
    return {
        "request": request,
        "project_name": settings.PROJECT_NAME,
        "current_user": current_user,
        "legal": settings.legal_context,
    }


@app.get("/", response_class=HTMLResponse, summary="Главная страница приложения")
@app.get("/dashboard", response_class=HTMLResponse, summary="Обзорная панель")
async def read_dashboard(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="dashboard.html", context=ctx)


@app.get("/planning", response_class=HTMLResponse, summary="Планирование и рекомендации СППР")
async def read_planning(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="planning.html", context=ctx)


@app.get("/transactions", response_class=HTMLResponse, summary="Журнал операций")
async def read_transactions(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="transactions.html", context=ctx)


@app.get("/obligations", response_class=HTMLResponse, summary="Обязательства")
async def read_obligations(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="obligations.html", context=ctx)


@app.get("/goals", response_class=HTMLResponse, summary="Цели накопления")
async def read_goals(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="goals.html", context=ctx)


@app.get("/banks", response_class=HTMLResponse, summary="Банковская интеграция")
async def read_banks(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="banks.html", context=ctx)


@app.get("/validation", response_class=HTMLResponse, summary="Валидация алгоритма на портретах")
async def read_validation(ctx: dict = Depends(page_context)):
    # Раздел валидации — часть гостевой песочницы; вошедшим он не нужен.
    if ctx["current_user"] is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=ctx["request"], name="validation.html", context=ctx)


@app.get("/profile", response_class=HTMLResponse, summary="Личный профиль и настройки")
async def read_profile(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="profile.html", context=ctx)


# ── Юридический блок (P1.1): публичные документы и контакты ────────────
@app.get("/legal/privacy", response_class=HTMLResponse, summary="Политика обработки ПДн (152-ФЗ)")
async def read_legal_privacy(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=ctx["request"], name="legal/privacy.html", context=ctx
    )


@app.get("/legal/terms", response_class=HTMLResponse, summary="Пользовательское соглашение (оферта)")
async def read_legal_terms(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="legal/terms.html", context=ctx)


@app.get("/legal/consent", response_class=HTMLResponse, summary="Согласие на обработку ПДн")
async def read_legal_consent(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=ctx["request"], name="legal/consent.html", context=ctx
    )


@app.get(
    "/legal/financial-consent",
    response_class=HTMLResponse,
    summary="Согласие на обработку финансовых данных",
)
async def read_legal_financial_consent(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=ctx["request"], name="legal/financial_consent.html", context=ctx
    )


@app.get("/contacts", response_class=HTMLResponse, summary="Контакты и реквизиты оператора")
async def read_contacts(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="contacts.html", context=ctx)


@app.get("/reset-password", response_class=HTMLResponse, summary="Страница установки нового пароля")
async def read_reset_password(
    token: str = "", ctx: dict = Depends(page_context)
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=ctx["request"], name="reset_password.html", context={**ctx, "reset_token": token}
    )


@app.get("/forgot-password", response_class=HTMLResponse, summary="Страница запроса сброса пароля")
async def read_forgot_password(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=ctx["request"], name="forgot_password.html", context=ctx
    )
