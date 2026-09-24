"""Общие фикстуры pytest: изолированная БД и TestClient.

Схема строится реальными Alembic-миграциями через startup приложения —
это заодно проверяет применимость миграций (INFRA-03).
"""
from __future__ import annotations

import os
import tempfile

import re
from functools import lru_cache
from pathlib import Path

import pytest

from tests.db_url import worker_database_url

# По умолчанию — изолированный SQLite-файл. Но если DATABASE_URL задан извне
# (например, PostgreSQL в CI/локальной верификации) — уважаем его, чтобы прогнать
# тот же набор тестов на боевой СУБД.
if not os.environ.get("DATABASE_URL"):
    _TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.name}"
else:
    # Унаследованный адрес — признак воркера xdist: у каждого своя база, иначе
    # восемь процессов создают схему в одном файле. Разбор — tests/db_url.py.
    os.environ["DATABASE_URL"] = worker_database_url(
        os.environ["DATABASE_URL"], os.environ.get("PYTEST_XDIST_WORKER")
    )

from fastapi.testclient import TestClient

from sqlalchemy.orm import close_all_sessions

from app.database.db import Base, SessionLocal, engine
from app.main import app


def _reset_db() -> None:
    # Сначала гасим пул: на PostgreSQL любое незакрытое соединение с открытой
    # транзакцией держит блокировку на таблице, и DROP встаёт намертво —
    # прогон подвисает без единой ошибки. На SQLite этого не видно вообще,
    # поэтому дефект живёт до первого запуска матрицы (правило «SQLite молча
    # прощает» — ровно про такие случаи).
    close_all_sessions()
    engine.dispose()
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    _reset_db()
    with TestClient(app) as test_client:  # startup → init_db → run_migrations
        yield test_client
    _reset_db()


@pytest.fixture
def db_session():
    """Сессия БД для юнит-тестов. Схема строится теми же миграциями (через startup)."""
    _reset_db()
    with TestClient(app):  # поднимает схему (миграции)
        pass
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        _reset_db()


@pytest.fixture(autouse=True)
def _clear_recommendation_cache():
    """Модульные кэши (живут в процессе) чистим перед каждым тестом, чтобы
    результаты не протекали между тестами: кэш рекомендаций и кэш расчёта плана."""
    try:
        from app.api.routes_recommendation import _recommendation_cache
        _recommendation_cache.clear()
    except Exception:
        pass
    try:
        from app.api.routes_planning import _planning_cache
        _planning_cache.clear()
    except Exception:
        pass
    yield


@pytest.fixture(autouse=True)
def _reset_cbr_key_rate_cache():
    """Process-кэш ключевой ставки живёт на модуле cbr_rate. Любой тест, дёрнувший
    живой fetch (сеть к cbr.ru в песочнице/CI закрыта → сбой), ставит 15-мин backoff
    и кэширует неудачу. Без сброса это глушит сеть в последующих тестах и протекает
    между ними. Чистим перед каждым тестом."""
    try:
        from app.services import cbr_rate
        cbr_rate._cache.update(rate=None, source=None, fetched_on=None)
        cbr_rate._fail_until.update(ts=None, detail="")
    except Exception:
        pass
    yield


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """Сброс in-memory rate-limit между тестами.

    Счётчик _hits живёт на инстансе RateLimitMiddleware (= на время жизни app),
    поэтому серии регистраций/логинов в рамках одного прогона ложно упираются в
    429 и «заражают» последующие тесты. Чистим до теста; внутри теста накопление
    сохраняется, так что проверки самого срабатывания лимита не ломаются.
    """
    from app.middleware import RateLimitMiddleware

    mw = getattr(app, "middleware_stack", None)
    while mw is not None:
        if isinstance(mw, RateLimitMiddleware):
            mw._hits.clear()
            break
        mw = getattr(mw, "app", None)
    yield


@lru_cache(maxsize=None)
def _imports_core(path: str) -> bool:
    """Тянет ли файл теста `app.core` — то есть проверяет ли он ядро.

    Кэш обязателен: хук зовётся на каждый собранный тест, а файлов сотни;
    без него разбор одного модуля повторялся бы десятки раз.
    """
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return bool(re.search(r"^\s*(from|import)\s+app\.core", text, re.MULTILINE))


def pytest_collection_modifyitems(config, items):
    """Авто-маркировка категории `fast` (CI-тиры fast/full/deep).

    Чтобы CI отбирал быстрый прогон через `-m fast`, не размечая вручную сотни
    unit/integration-тестов: любой тест, не помеченный явно `full`, `deep` или
    `e2e`, автоматически получает маркер `fast`. Тяжёлые/редкие тиры (визуальная
    регрессия, live-a11y, стресс-property) маркируются явно в своих файлах —
    всё прочее попадает в быстрый прогон по умолчанию.
    """
    tiered = {"full", "deep", "e2e"}
    for item in items:
        own = {marker.name for marker in item.iter_markers()}
        if own.isdisjoint(tiered):
            item.add_marker(pytest.mark.fast)
        # 🔴 Маркер `core` ставится ПО ФАКТУ импорта `app.core`, а не по списку файлов.
        # Список из 42 имён разошёлся бы с кодом при первом же новом тесте, и заметить
        # это было бы нечем: тест просто не попал бы в свою джобу и в свой порог
        # покрытия. Признак «модуль тянет ядро» не устаревает.
        module = getattr(item, "module", None)
        source = getattr(module, "__file__", None)
        if source and _imports_core(source):
            item.add_marker(pytest.mark.core)


# ── Валидный прод-конфиг: ОДНО определение на все тесты ──────────────────────
# 🔴 Заведено v9.6.0 после третьего повтора одного класса. Перечень «полностью
# правильного прода» жил копиями в четырёх файлах, и каждое расширение старт-гарда
# роняло их по очереди: v8.56.0 — `CORS_ORIGINS`/`DATABASE_URL`, v9.1.0 —
# `TRUST_PROXY_HEADERS` (и только на CI), v9.6.0 — SMTP.
#
# Комментарий в одном из тех тестов уже сформулировал правило («перечисляет валидный
# прод ЦЕЛИКОМ, значит обязан пополняться вместе с гардом») — но правило, которое надо
# ПОМНИТЬ, не работает: три повтора это доказали. Теперь место одно, и расширение
# гарда ломает его сразу, а не через файл.
VALID_PRODUCTION_ENV: dict[str, object] = {
    "ENVIRONMENT": "production",
    "JWT_SECRET": "x" * 48,
    "COOKIE_SECURE": True,
    "ADMIN_API_KEY": "k" * 24,
    "TOKEN_ENCRYPTION_KEY": "t" * 44,
    "CORS_ORIGINS": "https://finpilot.ru,https://www.finpilot.ru",
    "TRUST_PROXY_HEADERS": True,
    "DATABASE_URL": "postgresql+psycopg2://finpilot:pass@db:5432/finpilot",
    "SMTP_HOST": "smtp.example",
    "SMTP_USER": "robot@example",
    "SMTP_PASSWORD": "secret",
}


def valid_production_settings(**overrides):
    """Настройки боевого стенда, проходящие старт-гард целиком.

    Args:
        **overrides: поля, которые тест намеренно портит, чтобы проверить свою проверку.

    Returns:
        Экземпляр `Settings` с боевыми значениями и применёнными правками.
    """
    from app.config import Settings

    return Settings(**{**VALID_PRODUCTION_ENV, **overrides})
