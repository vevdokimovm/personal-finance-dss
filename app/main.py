from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
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
# Сборка React (веха 8). Может отсутствовать: `dist/` в `.gitignore`, на чистом клоне
# его нет до `npm run build`. Приложение обязано подниматься и без него — иначе
# отсутствие фронта ломает и API, и миграции, и health-check.
SPA_DIR = FRONTEND_DIR / "dist"
SPA_INDEX = SPA_DIR / "index.html"

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


# 🔴 Страницы вехи 8 отдаёт React (catch-all в конце файла). Jinja-дубли `/`,
# `/dashboard`, `/planning`, `/transactions`, `/obligations`, `/goals`, `/banks`
# и `/legal/*` сняты в v8.45.0: пока они существовали, они выигрывали у SPA —
# объявлены раньше и точнее, — и сервер отдавал СТАРЫЙ интерфейс. Именно поэтому
# сорок с лишним версий фронта работали только в dev через Vite.

@app.get("/validation", response_class=HTMLResponse, summary="Валидация алгоритма на портретах")
async def read_validation(ctx: dict = Depends(page_context)):
    # Раздел валидации — часть гостевой песочницы; вошедшим он не нужен.
    if ctx["current_user"] is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=ctx["request"], name="validation.html", context=ctx)


@app.get("/contacts", response_class=HTMLResponse, summary="Контакты и реквизиты оператора")
async def read_contacts(ctx: dict = Depends(page_context)) -> HTMLResponse:
    return templates.TemplateResponse(request=ctx["request"], name="contacts.html", context=ctx)


# ── Отдача React-приложения (веха 8) ───────────────────────────────────
# 🔴 Ставится ПОСЛЕДНИМ и только здесь. Catch-all перехватывает всё, что не разобрали
# роутеры выше, поэтому любой маршрут, объявленный ниже, был бы мёртв. По той же причине
# `/api` и `/v1` подключены раньше: иначе фронт получал бы `index.html` там, где ждёт
# JSON, — запросы «проходили» бы с кодом 200, и ломалось бы всё сразу и непонятно.
if SPA_INDEX.is_file():
    # Ассеты Vite: имена с хешем содержимого, поэтому кешируются агрессивно самим
    # браузером — отдельная политика не нужна, достаточно отдать их по своим адресам.
    app.mount("/assets", StaticFiles(directory=str(SPA_DIR / "assets")), name="spa-assets")

    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_spa(full_path: str) -> HTMLResponse:
        """`index.html` на любой не-API адрес: маршрутизация клиентская.

        Сервер о `/legal/privacy` и `/transactions` ничего не знает и знать не должен —
        роутер разберётся сам. Без этого прямой заход по ссылке, закладка и обычный F5
        на любом экране дают 404, при том что переходы ВНУТРИ приложения работают:
        дефект невидим в разработке и появляется только у живого пользователя.

        Файлы из корня сборки (`favicon`, шрифты, `robots.txt`) отдаются как файлы —
        иначе браузер получил бы HTML вместо шрифта и молча нарисовал системным.
        """
        # 🔴 Адреса API остаются за API, даже когда такого эндпоинта нет. Иначе опечатка
        # в пути запроса возвращает страницу с кодом 200, и «работает, но неправильно»
        # приходится разбирать по телу ответа вместо кода. Пойман собственным гейтом.
        if full_path.startswith(("api/", "v1/")):
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = (SPA_DIR / full_path).resolve()
        # `resolve()` + проверка принадлежности каталогу: без неё `../../.env` уехал бы
        # с диска по публичному адресу. Проверяется ПОСЛЕ разрешения символических
        # ссылок, иначе ссылка наружу обошла бы запрет.
        if full_path and candidate.is_file() and SPA_DIR.resolve() in candidate.parents:
            return FileResponse(candidate)  # type: ignore[return-value]
        return HTMLResponse(SPA_INDEX.read_text(encoding="utf-8"))
