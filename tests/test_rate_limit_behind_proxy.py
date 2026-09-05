"""Rate-limit считает реального клиента, а не nginx (v8.57.0).

## 🔴 Дефект, который включился бы в первый день на проде

`RateLimitMiddleware` берёт `request.client.host`. В прод-схеме перед приложением стоит
nginx (`nginx/templates/finpilot.conf.template`), и до FastAPI доезжает **адрес прокси**,
один и тот же для всего интернета. Значит:

- лимит `RATE_LIMIT_REQUESTS` тратится **всеми пользователями вместе**;
- исчерпав его, продукт отвечает 429 **всем сразу**, включая тех, кто зашёл впервые;
- ограничение при этом **не работает по назначению**: атакующий тратит общий счётчик,
  и жертвами становятся не он, а обычные люди.

То есть защита от перебора превращается в готовый способ положить вход всему сервису.
На локальной машине этого не видно вовсе — прокси нет, `client.host` настоящий.

## Почему нельзя просто доверять `X-Forwarded-For`

Заголовок ставит клиент, и подделать его тривиально: с фальшивым `X-Forwarded-For`
на каждый запрос счётчик не наберётся никогда. Доверять ему можно **только** там,
где перед приложением действительно стоит наш прокси, — то есть по явному признаку
в конфигурации, а не по наличию заголовка.

Отсюда `TRUST_PROXY_HEADERS`: выключен по умолчанию (dev, прямой доступ), включается
в прод-окружении, где nginx выставляет `X-Forwarded-For` сам и затирает клиентский.

## Почему берётся ЛЕВЫЙ адрес, а не правый

`X-Forwarded-For` — цепочка `клиент, прокси1, прокси2`. Правый конец ближе к нам,
но у нас ровно один доверенный хоп, и его адрес нам не нужен: нужен исходный клиент,
то есть **левый** элемент. При нескольких прокси это потребовало бы отсчёта от конца
на число доверенных хопов — оговорено в докстроке middleware, чтобы не выяснять
это заново при появлении CDN.

## Redis остаётся долгом вехи 9, и это осознанно

Счётчик по-прежнему в памяти инстанса: на мультиинстансном проде каждый инстанс считает
своё. Это делает лимит мягче (в N раз при N инстансах), но **не ломает продукт**, в отличие
от дефекта выше. Общий стор требует нового сервиса в compose и решения владельца
по хостингу — веха 9. Разница в цене ошибки: здесь «лимит мягче», там «вход не работает
ни у кого».
"""
from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.requests import Request
from starlette.routing import Route
from starlette.testclient import TestClient

from app.middleware import RateLimitMiddleware

LIMIT = 3
PROTECTED = ("/api/auth/login",)


def _app(trust_proxy: bool) -> TestClient:
    """Отдельное мини-приложение: тест про middleware, а не про эндпоинты продукта."""

    async def endpoint(request):
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route("/api/auth/login", endpoint, methods=["POST"])])
    app.add_middleware(
        RateLimitMiddleware,
        limit=LIMIT,
        window_seconds=60,
        protected_prefixes=PROTECTED,
        trust_proxy_headers=trust_proxy,
    )
    return TestClient(app)


def _post(client: TestClient, forwarded_for: str | None = None):
    headers = {"X-Forwarded-For": forwarded_for} if forwarded_for else {}
    return client.post("/api/auth/login", headers=headers)


class TestBehindProxy:
    """🔴 За прокси счёт идёт по реальному клиенту."""

    def test_different_clients_do_not_share_the_limit(self) -> None:
        """Главное утверждение: сосед не тратит мой лимит.

        Без этого один активный (или злонамеренный) посетитель гасит вход всем.
        """
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert _post(client, "203.0.113.10").status_code == 200
        assert _post(client, "203.0.113.10").status_code == 429, "свой лимит не сработал"

        assert _post(client, "198.51.100.20").status_code == 200, (
            "другой пользователь получил 429 из-за чужих запросов — на проде это "
            "означает отказ входа всем, кто пришёл после активного посетителя"
        )

    def test_same_client_is_still_limited(self) -> None:
        """Проверка, что починка не отключила лимит вовсе."""
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert _post(client, "203.0.113.30").status_code == 200
        assert _post(client, "203.0.113.30").status_code == 429

    def test_leftmost_address_wins(self) -> None:
        """Из цепочки берётся исходный клиент, а не последний прокси.

        `X-Forwarded-For: клиент, прокси` — правый конец ближе к нам и одинаков
        у всех, то есть по нему счёт снова стал бы общим.
        """
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            _post(client, "203.0.113.40, 10.0.0.2")
        assert _post(client, "203.0.113.40, 10.0.0.9").status_code == 429, (
            "смена ПОСЛЕДНЕГО хопа обнулила счётчик — значит ключом был прокси"
        )

    def test_missing_header_falls_back_to_socket_address(self) -> None:
        """Заголовка нет — работаем как раньше, а не пускаем без счёта.

        Такой запрос приходит мимо прокси (внутренняя сеть, health-check) и всё равно
        обязан считаться: `unknown`-ключ без лимита стал бы дырой в обход заголовка.
        """
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert _post(client).status_code == 200
        assert _post(client).status_code == 429


class TestWithoutProxy:
    """Без доверия к заголовку он игнорируется — иначе лимит подделывается одной строкой."""

    def test_forged_header_does_not_reset_the_counter(self) -> None:
        """🔴 Главная причина, почему заголовок не доверяется по умолчанию.

        С доверием «всегда» атакующий шлёт новый `X-Forwarded-For` на каждый запрос,
        и счётчик не наберётся никогда — лимита фактически нет.
        """
        client = _app(trust_proxy=False)
        for index in range(LIMIT):
            assert _post(client, f"203.0.113.{index}").status_code == 200
        assert _post(client, "203.0.113.99").status_code == 429, (
            "подделанный X-Forwarded-For обнулил счётчик — лимит обходится одной строкой"
        )


class TestConfigDefaults:
    """Умолчание безопасное, включение — осознанное."""

    def test_trust_is_off_by_default(self) -> None:
        """Локальная разработка идёт без прокси, и доверие там — чистый риск."""
        from app.config import Settings

        assert Settings().TRUST_PROXY_HEADERS is False

    @pytest.mark.parametrize("header", ["", "   ", ",", " , "])
    def test_blank_header_resolves_to_socket_address(self, header: str) -> None:
        """🔴 Пустой или мусорный заголовок даёт адрес сокета, а НЕ пустую строку.

        Тест смотрит на `_client_ip` напрямую, и это не педантизм. Две предыдущие
        редакции ходили через HTTP и обе были зелёными при мутации «пустая строка идёт
        ключом»: мутация склеивает в один счётчик ВСЕХ, включая запросы без заголовка,
        поэтому любая проверка, построенная на «склеились ли счётчики», подтверждает
        и правильное поведение, и сломанное.

        Различает их только сам ключ: `1.2.3.4` против `''`. Пустая строка как ключ —
        общий счётчик для всех отправителей мусора, и такой отправитель гасит лимит
        остальным.
        """
        middleware = RateLimitMiddleware(
            app=None, limit=LIMIT, window_seconds=60,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        headers = [(b"x-forwarded-for", header.encode())] if header else []
        request = Request({
            "type": "http", "method": "POST", "path": "/api/auth/login",
            "query_string": b"", "headers": headers, "client": ("1.2.3.4", 1),
        })
        assert middleware._client_ip(request) == "1.2.3.4"

    def test_forwarded_address_wins_over_socket(self) -> None:
        """Обратная сторона: осмысленный заголовок побеждает адрес сокета.

        Без этой пары предыдущий тест выполнялся бы функцией, всегда возвращающей
        адрес сокета, — то есть починкой, которая ничего не чинит.
        """
        middleware = RateLimitMiddleware(
            app=None, limit=LIMIT, window_seconds=60,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        request = Request({
            "type": "http", "method": "POST", "path": "/api/auth/login",
            "query_string": b"", "headers": [(b"x-forwarded-for", b"203.0.113.7, 10.0.0.2")],
            "client": ("1.2.3.4", 1),
        })
        assert middleware._client_ip(request) == "203.0.113.7"
