"""Ссылки подтверждения и сброса пароля не отдаются в HTTP-ответе на проде.

## Что закрывает

Три эндпоинта возвращают готовую ссылку прямо в теле ответа, когда почта не настроена:
регистрация (`verify_url`), сброс пароля (`reset_url`) и повторная отправка письма.
Условие было **`not settings.email_enabled`** — то есть проверялось наличие SMTP,
а не окружение, хотя комментарий рядом говорил «в dev».

🔴 **Прод без SMTP — не гипотетическая конфигурация, а ожидаемая.** Старт-гард
`validate_production_security` проверяет JWT-секрет, cookie, ключ администратора, CORS,
доверие прокси и запрет SQLite — и **не** требует почты, значит приложение штатно
поднимается без неё. Собственный план первого деплоя это прямо предполагает.

**Что это давало.** `POST /api/auth/forgot-password` с чужим адресом возвращал ссылку
сброса, а `POST /api/auth/reset-password` по ней меняет пароль: полный захват аккаунта
по одному известному email, без доступа к почте жертвы. Дополнительно ломалась защита
от перебора аккаунтов, объявленная в том же ответе: текст «если аккаунт существует»
одинаков для всех, но поле `reset_url` не-null **только для существующего** — наличие
поля и есть ответ на вопрос, есть ли такой пользователь.

## Правило

Удобство разработки живёт в dev. На проде ссылка уходит только в письмо; нет почты —
нет ссылки нигде, и это правильный отказ: невозможность сбросить пароль чинится
настройкой SMTP, а не выдачей токена в открытый ответ.
"""
from __future__ import annotations

import pytest

from app.config import settings


@pytest.fixture
def _prod(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
    monkeypatch.setattr(settings, "SMTP_HOST", "", raising=False)
    monkeypatch.setattr(settings, "SMTP_USER", "", raising=False)
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "", raising=False)
    return settings


class TestNoLinkInResponseOnProduction:
    """Ни один из трёх ответов не несёт ссылку, когда окружение — production."""

    def test_forgot_password_does_not_return_reset_url(self, client, _prod) -> None:
        """🔴 Главный случай: захват аккаунта по одному известному адресу."""
        email = "leak-probe@test.io"
        created = client.post(
            "/api/auth/register",
            json={"email": email, "password": "strongpass123", "consent": True},
        )
        # 🔴 Без этой строки тест был бы зелёным и при живом дефекте: несозданный
        # аккаунт даёт `reset_url = None` по причине `user is None`, а не по починке.
        assert created.status_code in (200, 201), created.text
        # 🔴 Атакующий знает только чужой адрес — ни сессии, ни куки у него нет.
        # Кука от регистрации выше сделала бы запрос «своим» и упёрлась бы в CSRF-стража,
        # то есть тест проверял бы совсем другую защиту.
        client.cookies.clear()
        response = client.post("/api/auth/forgot-password", json={"email": email})
        assert response.status_code == 200
        assert response.json().get("reset_url") is None, (
            "ответ несёт ссылку сброса пароля на проде — по ней пароль меняется "
            "без доступа к почте владельца аккаунта"
        )

    def test_forgot_password_answers_the_same_for_unknown_email(self, client, _prod) -> None:
        """Ответ неотличим для существующего и несуществующего адреса.

        Иначе поле `reset_url` работает оракулом перебора: текст один, а наличие
        поля выдаёт, что аккаунт есть.
        """
        known = "enum-probe@test.io"
        client.post(
            "/api/auth/register",
            json={"email": known, "password": "strongpass123", "consent": True},
        )
        client.cookies.clear()
        first = client.post("/api/auth/forgot-password", json={"email": known}).json()
        second = client.post(
            "/api/auth/forgot-password", json={"email": "nobody-here@test.io"}
        ).json()
        assert first == second, (
            "ответы для существующего и несуществующего адреса различаются — "
            "аккаунты перебираются по одному запросу"
        )

    def test_register_does_not_return_verify_url(self, client, _prod) -> None:
        response = client.post(
            "/api/auth/register",
            json={
                "email": "verify-probe@test.io",
                "password": "strongpass123",
                "consent": True,
            },
        )
        assert response.json().get("verify_url") is None, (
            "ответ регистрации несёт ссылку подтверждения на проде"
        )

    def test_resend_verification_does_not_return_verify_url(self, client, _prod) -> None:
        email = "resend-probe@test.io"
        client.post(
            "/api/auth/register",
            json={"email": email, "password": "strongpass123", "consent": True},
        )
        client.cookies.clear()
        response = client.post("/api/auth/resend-verification", json={"email": email})
        assert response.json().get("verify_url") is None, (
            "ответ повторной отправки несёт ссылку подтверждения на проде"
        )


class TestDevKeepsItsConvenience:
    """🔴 В dev ссылка остаётся — иначе починка ломает рабочий инструмент.

    Без почты и без ссылки локально нельзя ни подтвердить адрес, ни сбросить пароль,
    и разработка встанет. Правило про окружение, а не про то, что ссылка вредна сама
    по себе.
    """

    def test_forgot_password_returns_link_in_development(self, client, monkeypatch) -> None:
        monkeypatch.setattr(settings, "ENVIRONMENT", "development", raising=False)
        monkeypatch.setattr(settings, "SMTP_HOST", "", raising=False)
        email = "dev-probe@test.io"
        client.post(
            "/api/auth/register",
            json={"email": email, "password": "strongpass123", "consent": True},
        )
        client.cookies.clear()
        body = client.post("/api/auth/forgot-password", json={"email": email}).json()
        assert body.get("reset_url"), "в dev ссылка сброса пропала — сбросить пароль нечем"
