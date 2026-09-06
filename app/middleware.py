"""Middleware приложения: базовый rate limiting (INFRA-12).

Скользящее окно по IP для чувствительных эндпоинтов — защита от перебора
и злоупотреблений. In-memory: достаточно для single-instance деплоя FINPILOT.
"""
from __future__ import annotations

import time
import uuid
import logging
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.services.event_logger import log_event

_request_logger = logging.getLogger("finpilot.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Структурное логирование каждого HTTP-запроса (P1.5).

    Пишет request_id, метод, путь, статус и латентность; проставляет X-Request-ID
    в ответ для сквозной трассировки между логами и Sentry.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _request_logger.exception(
                "request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": latency_ms,
                },
            )
            raise
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        _request_logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Ограничение частоты запросов на чувствительных путях (NFR-04).

    🔴 **За прокси считается РЕАЛЬНЫЙ клиент, а не nginx (v8.57.0).** До этого ключом
    был `request.client.host`, а в прод-схеме перед приложением стоит nginx — значит
    один и тот же адрес для всего интернета. Лимит тратился всеми вместе, и, исчерпав
    его, продукт отвечал 429 **всем сразу**, включая пришедших впервые. Защита от
    перебора превращалась в способ положить вход всему сервису; локально этого не видно
    вовсе — прокси нет, адрес настоящий.

    Заголовок доверяется только при `TRUST_PROXY_HEADERS`: его ставит клиент, и с
    доверием «всегда» атакующий шлёт новый адрес на каждый запрос.

    🔴 **Читается `X-Real-IP`, а НЕ `X-Forwarded-For` (найдено `/code-review`).** Здесь
    стоял левый элемент цепочки `X-Forwarded-For` с обоснованием «nginx выставляет
    заголовок сам и затирает клиентский». Обоснование неверно: шаблон использует
    `$proxy_add_x_forwarded_for`, а это **append** — `$http_x_forwarded_for, $remote_addr`.
    Левый элемент целиком контролируется тем, кто стучится, и на проде
    (`TRUST_PROXY_HEADERS` там обязателен) перебор пароля со случайным заголовком
    получал бы свежий счётчик и **не упирался в лимит никогда**.

    `X-Real-IP` nginx ставит из `$remote_addr` и перезаписывает целиком — подменить
    его клиент не может. Появится второй прокси или CDN — менять надо будет здесь,
    и тогда `X-Real-IP` перестанет быть адресом клиента.

    **Счётчик в памяти инстанса** — на мультиинстансном проде каждый считает своё, то есть
    лимит мягче в N раз. Общий стор (Redis) требует нового сервиса в compose и решения
    по хостингу — записан долгом вехи 9. Разница в цене: здесь «мягче», у дефекта
    выше было «вход не работает ни у кого».
    """

    def __init__(
        self,
        app,
        limit: int,
        window_seconds: int,
        protected_prefixes: tuple[str, ...],
        trust_proxy_headers: bool = False,
    ) -> None:
        super().__init__(app)
        self._limit = limit
        self._window = window_seconds
        self._protected = protected_prefixes
        self._trust_proxy = trust_proxy_headers
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        # Момент следующей уборки протухших счётчиков (см. `_sweep`).
        self._next_sweep = 0.0

    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self._protected)

    def _client_ip(self, request: Request) -> str:
        """Адрес, по которому ведётся счёт.

        Пустой заголовок откатывается к адресу сокета: пустая строка как ключ склеила бы
        всех отправителей мусора в один счётчик, и такой отправитель гасил бы лимит
        остальным.
        """
        if self._trust_proxy:
            real_ip = request.headers.get("x-real-ip", "").strip()
            if real_ip:
                return real_ip
        return request.client.host if request.client else "unknown"

    def _key(self, request: Request) -> str:
        """Ключ счёта: клиент и путь. Разные пути не делят лимит между собой.

        🔴 Функция была объявлена и НЕ вызывалась: `dispatch` собирал ту же строку
        руками (нашёл `/code-review ultra`). Два источника одного формата ключа —
        и `_sweep` чистит то, что пишет `dispatch`, а не то, что вернёт `_key`.
        Правка формата в одном месте (скажем, добавить метод HTTP) прошла бы все
        тесты и не сделала бы ничего — либо развела бы чистку и запись по разным
        пространствам ключей, вернув утечку счётчиков, ради которой `_sweep` и писался.
        """
        return f"{self._client_ip(request)}:{request.url.path}"

    def _sweep(self, now: float) -> None:
        """Выбросить счётчики, чьи окна целиком протухли.

        🔴 Найдено `/code-review`: `defaultdict` заводил запись на каждый уникальный
        `адрес:путь` и не удалял НИКОГДА. На проде — утечка на каждого посетителя;
        в связке с подделкой заголовка (закрыта выше) — прямой канал исчерпания памяти:
        новый адрес на каждый запрос давал новую запись.

        Чистится не текущий ключ, а всё протухшее: удалять только свою запись мало —
        память съедают как раз чужие, которых больше никто не тронет. Проход идёт
        не чаще раза в окно (`_next_sweep`), чтобы не платить обходом словаря
        на каждом запросе.
        """
        if now < self._next_sweep:
            return
        window_start = now - self._window
        stale = [key for key, hits in self._hits.items() if not hits or hits[-1] < window_start]
        for key in stale:
            del self._hits[key]
        # Следующая уборка — через окно: за это время накопится ровно один «слой»
        # протухших записей, и обход амортизируется по всем запросам окна.
        self._next_sweep = now + max(self._window, 1)

    async def dispatch(self, request: Request, call_next):
        if not self._is_protected(request.url.path):
            return await call_next(request)

        now = time.monotonic()
        self._sweep(now)

        client_ip = self._client_ip(request)
        key = self._key(request)
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
        # 🔴 `script-src` БЕЗ `'unsafe-inline'` (v8.56.0). Пункт вехи 4.4 был отложен
        # до переезда фронта на React; веха 8 закрыта, Jinja снесена, и собранный SPA
        # inline-скриптов не содержит вовсе (`frontend/dist/index.html` — единственный
        # `<script>` внешний). `'unsafe-inline'` здесь снимал главную защиту CSP от XSS:
        # любой внедрённый в разметку скрипт выполнялся бы.
        #
        # У СТИЛЕЙ он остаётся сознательно: Radix (диалоги, тултипы, тосты) и
        # `react-remove-scroll` ставят стили в рантайме — `style`-атрибутами и
        # инжектируемыми `<style>`. Nonce для рантайм-инжекции требует прокидывания
        # через каждую библиотеку. CSS-инъекция искажает вид, JS-инъекция крадёт токен;
        # снимаем то, что снимается, и называем, что не снимается.
        #
        # Набор директив тот же, что в `nginx/templates/finpilot.conf.template`: раньше
        # middleware был беднее, и ответ приложения защищался слабее того же ответа
        # через прокси — одна страница получала разную политику в зависимости от пути.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        if self._hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """Защита от CSRF на изменяющих запросах (NFR-04).

    Origin сверяется со списком доверенных. Запросы по `Bearer`-токену или API-ключу
    пропускаются: браузер сам такой заголовок не приложит, значит подделать запрос
    с чужого сайта нельзя (B2B `/v1`, Plaid, мобильные и серверные клиенты).

    🔴 **Исправлено в v8.56.0.** Здесь стояло «отсутствие Origin не несёт CSRF-риска —
    атака требует амбиентных cookies в браузере». Рассуждение верное, вывод из него —
    нет: наличие амбиентной cookie проверяется по самой cookie, а не по наличию Origin.
    Запрос **с auth-cookie и без Origin** — ровно тот случай, который докстрока
    объявляла невозможным, и он проходил молча.

    Современный браузер шлёт `Origin` на каждый POST/PUT/PATCH/DELETE, поэтому такой
    запрос либо от клиента, которому cookie не нужна (пусть шлёт `Bearer`), либо
    подделан. На проде он отвергается.

    **Почему не double-submit токен.** Он требует правок фронта (чтение куки, заголовок
    на каждый мутирующий запрос, обновление после логина) и даёт браузерным клиентам
    ту же гарантию, что уже даёт Origin. Разница проявляется только там, где `Origin`
    отсутствует, — а этот случай мы и запрещаем.

    **Только в production.** В development cookie-запрос без Origin — это `TestClient`
    и `curl`; запрет там сломал бы десятки тестов ради угрозы, которой нет: ни чужого
    сайта, ни жертвы. Та же развилка и то же решение, что у гостевой записи в v8.53.0.

    Первым рубежом остаётся `SameSite=lax` на auth-cookie (`routes_auth._set_auth_cookie`):
    браузер не приложит её к cross-site POST. Он живёт на стороне браузера — старого,
    нестандартного или обёрнутого прокси; серверная проверка от клиента не зависит.
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
                # Амбиентная cookie без Origin: см. разбор в докстроке класса.
                if origin is None and settings.AUTH_COOKIE_NAME in request.cookies:
                    if settings.is_production:
                        log_event("csrf_blocked", {"path": request.url.path, "origin": None})
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": "Запрос без указания источника отклонён. "
                                "Обновите страницу и попробуйте ещё раз."
                            },
                        )
        return await call_next(request)
