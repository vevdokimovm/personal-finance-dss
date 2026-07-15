"""Общие фикстуры pytest: изолированная БД и TestClient.

Схема строится реальными Alembic-миграциями через startup приложения —
это заодно проверяет применимость миграций (INFRA-03).
"""
from __future__ import annotations

import os
import tempfile

import pytest

# По умолчанию — изолированный SQLite-файл. Но если DATABASE_URL задан извне
# (например, PostgreSQL в CI/локальной верификации) — уважаем его, чтобы прогнать
# тот же набор тестов на боевой СУБД.
if not os.environ.get("DATABASE_URL"):
    _TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.name}"

from fastapi.testclient import TestClient

from app.database.db import Base, SessionLocal, engine
from app.main import app


def _reset_db() -> None:
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
