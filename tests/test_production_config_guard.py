"""Старт-гард ловит конфиги, ломающие прод молча (v8.56.0).

## Почему это веха 9, а не «полировка»

`validate_production_security` проверяет секреты: `JWT_SECRET`, `COOKIE_SECURE`,
`ADMIN_API_KEY`, ключ шифрования. Всё это — про **взлом**. Но деплой ломается
не только взломом: конфиг, оставшийся дефолтным, роняет продукт **тихо и полностью**,
и увидит это первый живой пользователь, а не мы.

Два таких параметра нашлись при разборе CSRF (v8.56.0):

🔴 **`CORS_ORIGINS` с дефолтным `localhost`.** `CSRFMiddleware` отвергает мутирующий
запрос, чей `Origin` не в списке. Браузер шлёт `Origin` на каждый POST/PUT/PATCH/DELETE —
значит с дефолтным списком **любое действие пользователя на проде вернёт 403**: вход,
операция, план. Сайт открывается, читается и ничего не сохраняет. Диагноз по симптому
почти невозможен: 403 выглядит как проблема прав, а не конфига.

🔴 **`DATABASE_URL` со SQLite.** Данные лягут в файл внутри контейнера и исчезнут
при первом же пересоздании. Это не «медленнее» — это потеря финансовых данных
пользователей без следа, причём выглядит как штатная работа.

**Общее у обоих:** дефолт удобен для разработки, губителен в бою и **не даёт ошибки
в момент старта**. Старт-гард превращает тихую катастрофу в громкий отказ до запуска.
"""
from __future__ import annotations

import pytest

from app.config import Settings, validate_production_security
from tests.conftest import VALID_PRODUCTION_ENV

# Значения, при которых секретные проверки молчат: тест про КОНФИГ, а не про секреты,
# и их шум мешал бы увидеть предмет.
# 🔴 Секреты берутся из ОБЩЕЙ фабрики (`tests/conftest.py`), а не своей копии.
# Копий было четыре, и каждое расширение старт-гарда роняло их по очереди:
# v8.56.0 — CORS/DATABASE_URL, v9.1.0 — TRUST_PROXY_HEADERS (только на CI),
# v9.6.0 — SMTP. Разбор и мета-гейт — `test_valid_production_config_is_single_sourced.py`.
# `CORS_ORIGINS` и `DATABASE_URL` исключены намеренно: тесты этого файла их и портят,
# а фабрика подставляет боевые значения — иначе проверка «дефолтный localhost отвергнут»
# проверяла бы фабрику, а не гард.
_VARIED_HERE = {"ENVIRONMENT", "CORS_ORIGINS", "DATABASE_URL"}
SECRETS = {k: v for k, v in VALID_PRODUCTION_ENV.items() if k not in _VARIED_HERE}
PROD_DB = "postgresql+psycopg2://finpilot:pass@db:5432/finpilot"
PROD_ORIGINS = "https://finpilot.ru,https://www.finpilot.ru"
# 🔴 Дефолт задаётся ЯВНО, а не берётся из окружения. Под PG-матрицей
# `DATABASE_URL` стоит в env, `Settings` его подхватывает — и тест про SQLite
# проверял машину, на которой запущен, а не код. Локально зелёный, в матрице
# красный: тот же класс, что PIT-032.
DEV_DB = "sqlite:///./sppr.db"


def _settings(**overrides) -> Settings:
    return Settings(
        ENVIRONMENT="production", **{"DATABASE_URL": DEV_DB, **SECRETS, **overrides}
    )


def _problem_about(settings: Settings, needle: str) -> str | None:
    for problem in validate_production_security(settings):
        if needle.lower() in problem.lower():
            return problem
    return None


class TestCorsOriginsMustBeReal:
    """🔴 Дефолтный localhost на проде = 403 на каждое действие пользователя."""

    def test_default_localhost_origins_are_refused(self) -> None:
        settings = _settings(DATABASE_URL=PROD_DB)
        problem = _problem_about(settings, "CORS_ORIGINS")
        assert problem, (
            "старт с дефолтными localhost-origins разрешён — на проде каждый POST "
            "получит 403 от CSRFMiddleware, и сайт будет открываться, ничего не сохраняя"
        )

    def test_localhost_among_real_origins_is_still_refused(self) -> None:
        """Один забытый localhost в списке — тоже проблема, а не мелочь.

        Он не ломает продукт, но открывает доверие к источнику, который на боевом
        сервере может поднять кто угодно с доступом к машине.
        """
        settings = _settings(
            DATABASE_URL=PROD_DB, CORS_ORIGINS=f"{PROD_ORIGINS},http://localhost:5173"
        )
        assert _problem_about(settings, "CORS_ORIGINS")

    def test_http_origin_is_refused(self) -> None:
        """🔴 `http://` в проде: cookie идёт с флагом `Secure` и по HTTP не долетит.

        Конфигурация внутренне противоречива — `COOKIE_SECURE=true` рядом с `http://`
        origin гарантирует, что сессия не установится. Ловить это на живом сайте дорого.
        """
        settings = _settings(DATABASE_URL=PROD_DB, CORS_ORIGINS="http://finpilot.ru")
        assert _problem_about(settings, "CORS_ORIGINS")

    def test_real_https_origins_pass(self) -> None:
        """Правильный конфиг проходит — иначе гейт запретил бы деплой вообще."""
        settings = _settings(DATABASE_URL=PROD_DB, CORS_ORIGINS=PROD_ORIGINS)
        assert _problem_about(settings, "CORS_ORIGINS") is None


class TestProxyTrustMustBeExplicit:
    """🔴 Нашёл `/code-review`: старт-гард не смотрел на `TRUST_PROXY_HEADERS`.

    Настройка выключена по умолчанию и такой же уезжает в `.env.example`. Деплой
    с шаблоном nginx из этой же репы и дефолтом возвращает ровно тот дефект, что
    закрыт в v9.0.0: `request.client.host` — адрес контейнера прокси, один на весь
    интернет, лимит тратится всеми вместе, и, исчерпав его, продукт отвечает 429
    **всем сразу**.

    Гейт заведён ловить «тихую поломку прода» и проверяет CORS, SQLite и cookie —
    а эту настройку пропускал, хотя цена ошибки та же: продукт работает, пока никто
    не перебирает пароль, и падает для всех, когда кто-то начал.
    """

    def test_default_is_refused_in_production(self) -> None:
        # Явно выключаем: в `SECRETS` доверие включено, потому что это часть
        # ВАЛИДНОГО прод-конфига, а здесь проверяется именно дефолт.
        settings = _settings(
            CORS_ORIGINS=PROD_ORIGINS, DATABASE_URL=PROD_DB, TRUST_PROXY_HEADERS=False
        )
        problem = _problem_about(settings, "TRUST_PROXY_HEADERS")
        assert problem, (
            "старт с выключенным доверием прокси разрешён — за nginx лимит считает "
            "всех пользователей как одного и отвечает 429 всем сразу"
        )

    def test_enabled_passes(self) -> None:
        settings = _settings(
            CORS_ORIGINS=PROD_ORIGINS, DATABASE_URL=PROD_DB, TRUST_PROXY_HEADERS=True
        )
        assert _problem_about(settings, "TRUST_PROXY_HEADERS") is None


class TestDatabaseMustNotBeSqlite:
    """🔴 SQLite в контейнере = потеря данных при первом пересоздании."""

    def test_sqlite_is_refused_in_production(self) -> None:
        settings = _settings(CORS_ORIGINS=PROD_ORIGINS)
        problem = _problem_about(settings, "DATABASE_URL")
        assert problem, (
            "старт на SQLite разрешён — финансовые данные лягут в файл внутри "
            "контейнера и исчезнут при первом пересоздании, без следа и без ошибки"
        )

    def test_postgres_passes(self) -> None:
        settings = _settings(CORS_ORIGINS=PROD_ORIGINS, DATABASE_URL=PROD_DB)
        assert _problem_about(settings, "DATABASE_URL") is None


class TestDevelopmentUnaffected:
    """В development дефолты — норма, и гейт обязан молчать."""

    @pytest.mark.parametrize("environment", ["development", "test", "local"])
    def test_no_problems_outside_production(self, environment: str) -> None:
        """Тест защищает от переусердствования: гейт, кричащий локально, отключат целиком."""
        assert validate_production_security(Settings(ENVIRONMENT=environment)) == []


class TestExistingChecksSurvive:
    """Новые проверки не подменили старые — они складываются, а не заменяют."""

    def test_weak_secret_still_reported(self) -> None:
        settings = Settings(
            ENVIRONMENT="production",
            CORS_ORIGINS=PROD_ORIGINS,
            DATABASE_URL=PROD_DB,
            ADMIN_API_KEY="y" * 20,
            TOKEN_ENCRYPTION_KEY="z" * 44,
            COOKIE_SECURE=True,
        )
        assert _problem_about(settings, "JWT_SECRET")

    def test_full_valid_production_config_is_clean(self) -> None:
        """Полностью правильный прод-конфиг не даёт ни одной проблемы.

        Это и есть тот конфиг, который владелец соберёт по чек-листу деплоя.
        """
        settings = _settings(CORS_ORIGINS=PROD_ORIGINS, DATABASE_URL=PROD_DB)
        assert validate_production_security(settings) == []
