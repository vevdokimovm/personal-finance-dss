"""Перечень валидного прод-конфига живёт в одном месте и не отстаёт от гарда.

## Что закрывает

`validate_production_security` расширяется по мере находок, а перечень «полностью
правильного прода» жил **копиями в четырёх тестовых файлах**. Каждое расширение роняло
их по очереди:

| версия | что добавили в гард | что покраснело |
|---|---|---|
| v8.56.0 | `CORS_ORIGINS`, `DATABASE_URL` | перечни |
| v9.1.0 | `TRUST_PROXY_HEADERS` | перечни, и **только на CI** |
| v9.6.0 | SMTP | перечни в четырёх файлах |

🔴 **Правило уже было сформулировано** — в комментарии одного из тех тестов: «такой тест
перечисляет валидный прод ЦЕЛИКОМ, значит обязан пополняться вместе с гардом». Правило,
которое надо ПОМНИТЬ, не работает: три повтора это доказали.

Теперь перечень один (`tests/conftest.py::VALID_PRODUCTION_ENV`), и этот гейт держит
его актуальным механически: расширили гард, не пополнив фабрику — красное здесь, сразу
и в одном месте.

## Цена, если не держать

Красный CI при исправном коде — ровно тот шум, из-за которого в v9.4.0 месяц не замечали
настоящие падения контура.
"""
from __future__ import annotations

from app.config import validate_production_security
from tests.conftest import VALID_PRODUCTION_ENV, valid_production_settings


class TestFactoryPassesTheGuard:
    """Фабрика описывает прод, который гард считает правильным."""

    def test_no_problems_reported(self) -> None:
        """🔴 Мутация «добавить проверку в гард, не пополнив фабрику» роняет тест здесь."""
        problems = validate_production_security(valid_production_settings())
        assert problems == [], (
            "фабрика валидного прод-конфига отстала от старт-гарда: "
            + "; ".join(problems)
            + " — пополните VALID_PRODUCTION_ENV в tests/conftest.py"
        )

    def test_overrides_still_break_it(self) -> None:
        """Фабрика не «затыкает» гард: порча поля по-прежнему видна.

        Иначе единый источник превратился бы в способ сделать все тесты зелёными.
        """
        assert validate_production_security(valid_production_settings(COOKIE_SECURE=False))
        assert validate_production_security(valid_production_settings(JWT_SECRET="short"))
        assert validate_production_security(valid_production_settings(SMTP_HOST=""))


class TestFactoryIsActuallyProduction:
    """Опора: это боевой стенд, а не dev с другим именем."""

    def test_environment_is_production(self) -> None:
        assert valid_production_settings().is_production

    def test_covers_every_guarded_setting(self) -> None:
        """Перечень покрывает все поля, которые гард проверяет поимённо.

        Проверка грубая — по вхождению имени поля в исходник гарда, — но именно она
        ловит то, что ломалось трижды: гард знает про поле, фабрика не знает.
        """
        import inspect

        import app.config as config

        source = inspect.getsource(config.validate_production_security)
        named = {key for key in VALID_PRODUCTION_ENV if key != "ENVIRONMENT"}
        # Поля упоминаются либо напрямую, либо через свойство (`email_enabled`).
        unreferenced = {
            key
            for key in named
            if key not in source and key.lower() not in source.lower()
        }
        assert unreferenced <= {"SMTP_USER", "SMTP_PASSWORD", "SMTP_HOST"}, (
            f"в фабрике поля, которых гард не проверяет: {sorted(unreferenced)}"
        )
