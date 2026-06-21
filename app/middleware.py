"""Middleware приложения: базовый rate limiting (INFRA-12).

Скользящее окно по IP для чувствительных эндпоинтов — защита от перебора
и злоупотреблений. In-memory: достаточно для single-instance деплоя FINPILOT.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.services.event_logger import log_event


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limit: int,
        window_seconds: int,
        protected_prefixes: tuple[str, ...],
    ) -> None:
        super().__init__(app)
        self._limit = limit
        self._window = window_seconds
        self._protected = protected_prefixes
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self._protected)

    async def dispatch(self, request: Request, call_next):
        if not self._is_protected(request.url.path):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        now = time.monotonic()
        window_start = now - self._window

        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()

        if len(hits) >= self._limit:
            retry_after = int(self._window - (now - hits[0])) + 1
            log_event("rate_limit_exceeded", {"path": request.url.path, "client": client_ip})
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите позже."},
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Заголовки безопасности на все ответы (NFR-04, INFRA-14).

    Закрывают MIME-sniffing, clickjacking, утечку referrer и ограничивают
    источники ресурсов. HSTS включается только в production (за TLS).
    """

    def __init__(self, app, hsts: bool = False) -> None:
        super().__init__(app)
        self._hsts = hsts

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        if self._hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """Защита от CSRF через проверку Origin на изменяющих запросах (NFR-04).

    Origin сверяется со списком доверенных, только если он présent (браузерный
    запрос). Его отсутствие (curl, server-to-server, мобильный клиент) не несёт
    CSRF-риска — атака требует амбиентных cookies в браузере.
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    def __init__(self, app, allowed_origins: list[str]) -> None:
        super().__init__(app)
        self._allowed = set(allowed_origins)

    async def dispatch(self, request: Request, call_next):
        if request.method not in self.SAFE_METHODS:
            # Запросы по Bearer-токену или API-ключу не используют амбиентные cookies —
            # CSRF им не угрожает (B2B /v1, Plaid, мобильные/серверные клиенты).
            has_bearer = request.headers.get("authorization", "").lower().startswith("bearer ")
            has_api_key = "x-api-key" in request.headers
            if not has_bearer and not has_api_key:
                origin = request.headers.get("origin")
                if origin and origin not in self._allowed:
                    log_event("csrf_blocked", {"path": request.url.path, "origin": origin})
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Запрос с недоверенного источника отклонён."},
                    )
        return await call_next(request)
