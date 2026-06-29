"""Тесты helper-функции utcnow (naive UTC).

Заменяет deprecated datetime.utcnow() единой точкой. Контракт: возвращает naive
(tzinfo=None) datetime в UTC — поведение, идентичное старому utcnow(), чтобы замена
во всём коде была чисто механической и не ломала сравнения с naive-колонками БД.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.utils.time import utcnow


def test_utcnow_returns_datetime() -> None:
    assert isinstance(utcnow(), datetime)


def test_utcnow_is_naive() -> None:
    # Контракт варианта A: naive UTC, без tzinfo — совместимо с naive-колонками моделей.
    assert utcnow().tzinfo is None


def test_utcnow_is_close_to_real_utc() -> None:
    reference = datetime.now(timezone.utc).replace(tzinfo=None)
    delta = abs((utcnow() - reference).total_seconds())
    assert delta < 5


def test_utcnow_matches_legacy_utcnow_semantics() -> None:
    # Значение должно совпадать с datetime.utcnow() с точностью до пары секунд:
    # обе функции дают naive UTC.
    legacy = datetime.utcnow()  # noqa: DTZ003 — намеренно сверяемся с заменяемым API
    delta = abs((utcnow() - legacy).total_seconds())
    assert delta < 5
