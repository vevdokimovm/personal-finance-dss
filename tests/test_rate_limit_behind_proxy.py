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

import time

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.requests import Request
from starlette.routing import Route
from starlette.testclient import TestClient

from app.middleware import RateLimitMiddleware

LIMIT = 3
PROTECTED = ("/api/auth/login",)


async def _ok(request):
    return PlainTextResponse("ok")


def _app(trust_proxy: bool) -> TestClient:
    """Отдельное мини-приложение: тест про middleware, а не про эндпоинты продукта."""

    app = Starlette(routes=[Route("/api/auth/login", _ok, methods=["POST"])])
    app.add_middleware(
        RateLimitMiddleware,
        limit=LIMIT,
        window_seconds=60,
        protected_prefixes=PROTECTED,
        trust_proxy_headers=trust_proxy,
    )
    return TestClient(app)


def _post(client: TestClient, client_ip: str | None = None):
    """🔴 Шлём `X-Real-IP`, а не `X-Forwarded-For`.

    Второй за нашим nginx **дополняется**, а не перезаписывается
    (`$proxy_add_x_forwarded_for`), поэтому его левый элемент подделывается клиентом.
    `X-Real-IP` прокси ставит из `$remote_addr` целиком — найдено `/code-review`.
    """
    headers = {"X-Real-IP": client_ip} if client_ip else {}
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

    def test_forwarded_for_is_ignored_entirely(self) -> None:
        """🔴 `X-Forwarded-For` не участвует в счёте вовсе.

        За нашим nginx он дополняется, а не перезаписывается, значит его левый элемент —
        строка от клиента. Пока `X-Real-IP` на месте, подделка цепочки ничего не меняет.
        """
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert client.post(
                "/api/auth/login",
                headers={"X-Real-IP": "203.0.113.40", "X-Forwarded-For": "1.1.1.1"},
            ).status_code == 200
        assert client.post(
            "/api/auth/login",
            headers={"X-Real-IP": "203.0.113.40", "X-Forwarded-For": "9.9.9.9"},
        ).status_code == 429, "смена подделанной цепочки обнулила счётчик"

    def test_missing_header_falls_back_to_socket_address(self) -> None:
        """Заголовка нет — работаем как раньше, а не пускаем без счёта.

        Такой запрос приходит мимо прокси (внутренняя сеть, health-check) и всё равно
        обязан считаться: `unknown`-ключ без лимита стал бы дырой в обход заголовка.
        """
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert _post(client).status_code == 200
        assert _post(client).status_code == 429


class TestForgedForwardedFor:
    """🔴 Нашёл `/code-review`: `X-Forwarded-For` подделывается даже за нашим nginx.

    Докстрока middleware утверждала, что nginx «выставляет заголовок сам и затирает
    клиентский». **Это неверно:** `nginx/templates/finpilot.conf.template` использует
    `$proxy_add_x_forwarded_for` — а это **append**, `$http_x_forwarded_for, $remote_addr`.
    Левый элемент цепочки целиком контролируется тем, кто стучится.

    Цена: на проде (`TRUST_PROXY_HEADERS` там обязателен) перебор пароля со случайным
    `X-Forwarded-For` на каждом запросе получал бы свежий счётчик и **не упирался
    в лимит никогда**. То есть защита от перебора не работала бы ровно там, ради чего
    заводилась. Плюс произвольная строка от клиента уезжала в журнал событий.

    Починка: читаем `X-Real-IP`, который nginx ставит из `$remote_addr` (строка 132
    шаблона) и который клиент подменить не может — прокси перезаписывает его целиком.
    """

    def test_forged_forwarded_for_does_not_reset_the_counter(self) -> None:
        """Подделанная цепочка не даёт нового счётчика.

        `X-Real-IP` один и тот же (его ставит прокси), меняется только подделанный
        `X-Forwarded-For` — счёт обязан идти по первому.
        """
        client = _app(trust_proxy=True)
        for index in range(LIMIT):
            assert client.post(
                "/api/auth/login",
                headers={"X-Real-IP": "203.0.113.5", "X-Forwarded-For": f"1.2.3.{index}"},
            ).status_code == 200
        assert client.post(
            "/api/auth/login",
            headers={"X-Real-IP": "203.0.113.5", "X-Forwarded-For": "9.9.9.9"},
        ).status_code == 429, (
            "смена X-Forwarded-For обнулила счётчик — на проде перебор пароля "
            "не упрётся в лимит никогда"
        )

    def test_real_ip_header_identifies_the_client(self) -> None:
        """🔴 Счёт идёт по `X-Real-IP` — его ставит nginx, клиент подменить не может."""
        middleware = RateLimitMiddleware(
            app=None, limit=LIMIT, window_seconds=60,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        request = Request({
            "type": "http", "method": "POST", "path": "/api/auth/login",
            "query_string": b"",
            "headers": [
                (b"x-real-ip", b"203.0.113.7"),
                # Подделка в цепочке игнорируется: nginx её только дополняет.
                (b"x-forwarded-for", b"1.2.3.4, 203.0.113.7"),
            ],
            "client": ("10.0.0.2", 1),
        })
        assert middleware._client_ip(request) == "203.0.113.7"

    def test_different_real_ips_are_counted_apart(self) -> None:
        """Разные клиенты по-прежнему не делят лимит — ради этого всё и затевалось."""
        client = _app(trust_proxy=True)
        for _ in range(LIMIT):
            assert client.post(
                "/api/auth/login", headers={"X-Real-IP": "203.0.113.10"}
            ).status_code == 200
        assert client.post(
            "/api/auth/login", headers={"X-Real-IP": "203.0.113.10"}
        ).status_code == 429
        assert client.post(
            "/api/auth/login", headers={"X-Real-IP": "198.51.100.20"}
        ).status_code == 200


class TestCounterDoesNotLeak:
    """🔴 Нашёл `/code-review`: словарь счётчиков рос без границы.

    `defaultdict(deque)` заводил запись на КАЖДЫЙ уникальный ключ `адрес:путь`
    и не удалял опустевшие. На проде это утечка памяти на каждого посетителя,
    а в связке с подделкой заголовка (закрыта выше) — прямой канал исчерпания:
    новый адрес на каждый запрос давал новую запись.

    Чистка делается по ходу, а не по таймеру: отдельный сборщик пришлось бы
    заводить, останавливать и тестировать, а «убери за собой, когда проходишь
    мимо» не требует ни того, ни другого.
    """

    def test_counter_map_stays_bounded(self) -> None:
        """🔴 Прямая проверка размера: 200 разных адресов не оставляют 200 записей.

        Проверяется `_sweep` напрямую, а не через HTTP: уборка идёт не чаще раза
        в окно (иначе обход словаря платился бы на каждом запросе), и тест, гоняющий
        запросы в одну миллисекунду, до неё просто не доживает — что и показала
        первая редакция, зелёная при сломанной чистке.
        """
        middleware = RateLimitMiddleware(
            app=_ok, limit=LIMIT, window_seconds=1,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        now = time.monotonic()
        for index in range(200):
            middleware._hits[f"203.0.113.{index}:/api/auth/login"].append(now - 10)

        assert len(middleware._hits) == 200, "подготовка не удалась"
        middleware._sweep(now)
        assert len(middleware._hits) == 0, (
            f"после уборки осталось {len(middleware._hits)} протухших записей — "
            "на проде это утечка на каждого посетителя"
        )

    def test_live_counters_survive_the_sweep(self) -> None:
        """Уборка не трогает живые счётчики.

        Без этой пары `_sweep` мог бы «починить» утечку, стирая всё подряд — и лимит
        перестал бы работать вовсе, потому что каждый запрос начинал бы счёт заново.
        """
        middleware = RateLimitMiddleware(
            app=_ok, limit=LIMIT, window_seconds=60,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        now = time.monotonic()
        middleware._hits["203.0.113.1:/api/auth/login"].append(now)      # свежая
        middleware._hits["203.0.113.2:/api/auth/login"].append(now - 90)  # протухшая

        middleware._sweep(now)
        assert "203.0.113.1:/api/auth/login" in middleware._hits
        assert "203.0.113.2:/api/auth/login" not in middleware._hits


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

    @pytest.mark.parametrize("header", ["", "   "])
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
        headers = [(b"x-real-ip", header.encode())] if header else []
        request = Request({
            "type": "http", "method": "POST", "path": "/api/auth/login",
            "query_string": b"", "headers": headers, "client": ("1.2.3.4", 1),
        })
        assert middleware._client_ip(request) == "1.2.3.4"

    def test_real_ip_wins_over_socket(self) -> None:
        """Осмысленный заголовок побеждает адрес сокета.

        Без этой пары предыдущий тест выполнялся бы функцией, всегда возвращающей
        адрес сокета, — то есть починкой, которая ничего не чинит.
        """
        middleware = RateLimitMiddleware(
            app=None, limit=LIMIT, window_seconds=60,
            protected_prefixes=PROTECTED, trust_proxy_headers=True,
        )
        request = Request({
            "type": "http", "method": "POST", "path": "/api/auth/login",
            "query_string": b"", "headers": [(b"x-real-ip", b"203.0.113.7")],
            "client": ("1.2.3.4", 1),
        })
        assert middleware._client_ip(request) == "203.0.113.7"


class TestMfaVerifyIsRateLimited:
    """🔴 Нашёл `/code-review`: перебор второго фактора не ограничен.

    `RATE_LIMITED_PREFIXES` знает `/api/auth/login` и `/api/auth/register`, но
    `/api/auth/mfa/verify` не подходит ни под один префикс. Свой счётчик неудач у роута
    тоже отсутствует — он лишь пишет событие и повторно бросает ошибку.

    Сценарий: атакующий, уже знающий пароль, получает `mfa_pending`-токен на пять минут
    и бросает в шестизначный TOTP сколько угодно догадок за это окно. 10⁶ вариантов
    и никакого предела — второй фактор перестаёт быть фактором.

    Проверяется список префиксов, а не живой перебор: гонять сотню запросов ради
    утверждения «путь под лимитом» дорого и хрупко, а состав списка — это ровно то,
    что забыли.
    """

    def test_mfa_verify_is_covered_by_prefixes(self) -> None:
        from app.main import RATE_LIMITED_PREFIXES

        path = "/api/auth/mfa/verify"
        assert any(path.startswith(prefix) for prefix in RATE_LIMITED_PREFIXES), (
            "перебор TOTP не ограничен ничем: пятиминутный mfa_pending-токен "
            "и 10^6 вариантов — второй фактор перестаёт быть фактором"
        )

    def test_login_and_register_stay_covered(self) -> None:
        """Проверка, что правка не подменила список, а дополнила его."""
        from app.main import RATE_LIMITED_PREFIXES

        for path in ("/api/auth/login", "/api/auth/register"):
            assert any(path.startswith(prefix) for prefix in RATE_LIMITED_PREFIXES), path
