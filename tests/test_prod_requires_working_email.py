"""Прод не поднимается без почты — иначе восстановление доступа молча мертво.

## Что закрывает

`validate_production_security` требует стойкий JWT-секрет, `secure`-cookie, админ-ключ,
ключи шифрования, боевые CORS-origins, доверие прокси и запрет SQLite — и **не требовал
SMTP**. То есть сборка «прод без почты» проходила старт молча.

🔴 **Что в ней ломается.** `EmailService` при выключенной почте — тихий no-op, а
`POST /auth/forgot-password` возвращает «на него отправлена ссылка для сброса пароля»
и `reset_url: null` (v9.6.0 правильно перестал отдавать ссылку наружу). Получается
утверждение о факте, которого не было, на **единственном** пути восстановления доступа:
человек, забывший пароль, теряет аккаунт навсегда и не понимает почему. Подтверждение
адреса ломается там же.

Это тот же fail-loud, что у остальных пунктов гарда: лучше не подняться с внятным
списком, чем подняться и врать пользователю.

## Допущение, принятое явно

Прежде «первый деплой без SMTP» считался рабочей конфигурацией. Теперь это ошибка
старта. Цена ошибки несимметрична: не поднявшийся прод чинится одной строкой в `.env`
и заметен сразу, а потерянный доступ к аккаунту не чинится вовсе и заметен не владельцу,
а пользователю. Если почта осознанно не нужна, снимается тем же способом, что остальные
пункты гарда, — настройкой окружения, а не молчанием.
"""
from __future__ import annotations

from app.config import Settings, validate_production_security
from tests.conftest import valid_production_settings


def _prod_settings(**overrides):
    """Настройки боевого стенда — из общей фабрики, а не своей копии.

    🔴 Своя копия перечня и была тем дефектом, который здесь же и разбирается:
    четыре файла держали четыре списка, и каждое расширение гарда роняло их
    по очереди. Источник один — `tests/conftest.py`.
    """
    return valid_production_settings(**overrides)


class TestEmailIsRequiredOnProduction:
    """Без почты боевой запуск не проходит."""

    def test_full_config_passes(self) -> None:
        """Опора: полная конфигурация чиста — иначе тест ниже зелен по чужой причине."""
        assert validate_production_security(_prod_settings()) == []

    def test_missing_smtp_host_is_reported(self) -> None:
        """🔴 Мутация «убрать проверку почты» роняет тест здесь."""
        problems = validate_production_security(_prod_settings(SMTP_HOST=""))
        assert any("SMTP" in p or "почт" in p.lower() for p in problems), problems

    def test_missing_credentials_are_reported(self) -> None:
        """Хоста мало: без логина и пароля отправка так же не работает."""
        assert validate_production_security(_prod_settings(SMTP_USER=""))
        assert validate_production_security(_prod_settings(SMTP_PASSWORD=""))

    def test_message_says_what_breaks(self) -> None:
        """Сообщение называет следствие, а не только отсутствующую переменную.

        «SMTP_HOST не задан» оператор прочитает как необязательное; «сброс пароля
        не работает» — как блокирующее.
        """
        problems = validate_production_security(_prod_settings(SMTP_HOST=""))
        text = " ".join(problems).lower()
        assert "парол" in text or "восстанов" in text, problems


class TestDevelopmentIsUntouched:
    """В development почта по-прежнему необязательна."""

    def test_dev_without_smtp_is_clean(self) -> None:
        assert validate_production_security(Settings(ENVIRONMENT="development")) == []
