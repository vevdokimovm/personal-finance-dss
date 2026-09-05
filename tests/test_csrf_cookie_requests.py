"""Запрос по cookie без Origin на проде отвергается (v8.56.0).

## Дыра, которую закрывает батч

`CSRFMiddleware` сверяет `Origin` со списком доверенных **только если он есть**.
Докстрока объясняла это так: «его отсутствие (curl, server-to-server, мобильный клиент)
не несёт CSRF-риска — атака требует амбиентных cookies в браузере».

🔴 **Рассуждение верное, а вывод из него — нет.** Условие «есть амбиентная cookie»
проверяется не по наличию `Origin`, а по наличию самой cookie. Запрос, пришедший
**с auth-cookie и без Origin**, — это ровно тот случай, который докстрока объявляет
невозможным: cookie в нём есть, а проверка пропускает его молча. Современный браузер
шлёт `Origin` на каждый POST/PUT/PATCH/DELETE, поэтому такой запрос либо от клиента,
которому cookie не нужна (тогда пусть шлёт `Bearer`), либо подделан.

## Что уже защищало и почему этого мало

`SameSite=lax` на auth-cookie закрывает классический form-CSRF: браузер не приложит
cookie к cross-site POST. Это первый рубеж, и он остаётся. Но он живёт целиком
на стороне браузера — старого, нестандартного или обёрнутого прокси. Проверка на
сервере не зависит от того, чем к нам пришли.

## Почему не double-submit токен

Роадмап предлагал «рассмотреть double-submit CSRF-токен». Рассмотрен и отвергнут
в пользу строгой проверки Origin: double-submit требует правок фронта (чтение куки,
заголовок на каждый мутирующий запрос, обновление после логина) и даёт **ту же**
гарантию для браузерных клиентов, что уже даёт Origin. Разница проявляется только
там, где `Origin` отсутствует, — а именно этот случай мы и запрещаем.

## Только в production

В development и тестах cookie-запрос без Origin — обычный `TestClient` и `curl`.
Запретить их везде значило бы сломать десятки тестов и локальную работу ради дыры,
которой в dev не существует: там нет ни чужого сайта, ни жертвы. Та же развилка
и то же решение, что у гостевой записи в v8.53.0.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings

TODAY = "2026-09-05T12:00:00+00:00"
PAYLOAD = {"amount": 100.0, "type": "expense", "category": "Еда", "date": TODAY}


@pytest.fixture
def production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")


def _login_with_cookie(client: TestClient, email: str) -> None:
    """Регистрация оставляет auth-cookie в клиенте — дальше он ходит как браузер."""
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert response.status_code in (200, 201), response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    client.post("/api/consents/financial_data", headers=headers, json={})


class TestCookieRequestsNeedOrigin:
    """🔴 Главное утверждение: cookie без Origin на проде не проходит."""

    def test_cookie_request_without_origin_is_refused(
        self, client: TestClient, production
    ) -> None:
        """Мутирующий запрос по cookie обязан назвать источник.

        Мутация «вернуть прежнее условие» роняет ровно этот тест.
        """
        _login_with_cookie(client, "csrf-cookie@test.io")
        response = client.post("/api/transactions", json=PAYLOAD)
        assert response.status_code == 403, (
            f"запрос с амбиентной cookie и без Origin принят ({response.status_code}) — "
            "это ровно тот случай, который докстрока объявляла невозможным"
        )

    def test_cookie_request_with_trusted_origin_passes(
        self, client: TestClient, production
    ) -> None:
        """Свой origin работает — иначе «починка» просто выключила бы продукт."""
        _login_with_cookie(client, "csrf-cookie-ok@test.io")
        origin = next(iter(settings.cors_origins_list))
        response = client.post(
            "/api/transactions", json=PAYLOAD, headers={"Origin": origin}
        )
        assert response.status_code in (200, 201), response.text

    def test_cookie_request_with_foreign_origin_is_refused(
        self, client: TestClient, production
    ) -> None:
        """Чужой origin отвергается и без нового правила — проверка, что не сломали."""
        _login_with_cookie(client, "csrf-cookie-evil@test.io")
        response = client.post(
            "/api/transactions", json=PAYLOAD, headers={"Origin": "https://evil.example"}
        )
        assert response.status_code == 403


class TestNonCookieClientsAreUnaffected:
    """Клиенты без амбиентной cookie CSRF не подвержены и не должны страдать."""

    def test_bearer_client_without_origin_passes(
        self, client: TestClient, production
    ) -> None:
        """🔴 `Bearer` без Origin — мобильный и server-to-server клиент.

        Токен в заголовке браузер сам не приложит, значит подделать запрос
        с чужого сайта нельзя. Запретить их значило бы закрыть B2B и мобильных
        ради угрозы, которой у них нет.
        """
        registered = client.post(
            "/api/auth/register",
            json={"email": "csrf-bearer@test.io", "password": "password123", "consent": True},
        )
        headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
        client.post("/api/consents/financial_data", headers=headers, json={})
        client.cookies.clear()

        response = client.post("/api/transactions", json=PAYLOAD, headers=headers)
        assert response.status_code in (200, 201), response.text

    def test_anonymous_request_without_cookie_is_not_blocked_by_csrf(
        self, client: TestClient
    ) -> None:
        """Гость без cookie на dev проходит: у него нечего подделывать.

        Проверяется в development сознательно — на проде гостевая запись запрещена
        отдельным гейтом (v8.53.0), и он ответил бы 401 раньше CSRF.
        """
        client.cookies.clear()
        response = client.post("/api/transactions", json=PAYLOAD)
        assert response.status_code != 403


class TestDevelopmentUnchanged:
    """В development ничего не менялось — иначе сломались бы все тесты и локальная работа."""

    def test_cookie_request_without_origin_still_works_in_dev(
        self, client: TestClient
    ) -> None:
        _login_with_cookie(client, "csrf-dev@test.io")
        response = client.post("/api/transactions", json=PAYLOAD)
        assert response.status_code in (200, 201), response.text


class TestCookieFlags:
    """`SameSite=lax` — решение, а не умолчание; закрепляем его тестом."""

    def test_auth_cookie_is_httponly_and_samesite_lax(self, client: TestClient) -> None:
        """🔴 Почему `lax`, а не `strict`.

        `strict` не приложит cookie при переходе по внешней ссылке — человек, кликнув
        «Подтвердить почту» из письма, попал бы на сайт неавторизованным и решил бы,
        что ссылка сломана. `lax` закрывает cross-site POST (то есть form-CSRF)
        и сохраняет переход по ссылке. Роадмап требовал «подтвердить Strict/Lax» —
        подтверждено здесь вместе с причиной.
        """
        response = client.post(
            "/api/auth/register",
            json={"email": "csrf-flags@test.io", "password": "password123", "consent": True},
        )
        raw = response.headers.get("set-cookie", "")
        assert "httponly" in raw.lower(), "auth-cookie читается из JS — XSS уносит сессию"
        assert "samesite=lax" in raw.lower().replace(" ", ""), raw
