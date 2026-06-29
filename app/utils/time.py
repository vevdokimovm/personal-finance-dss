"""Время приложения — единая точка получения «сейчас» в UTC.

`datetime.utcnow()` объявлен deprecated и будет удалён в будущих версиях Python.
Эта обёртка заменяет его во всём коде. Контракт намеренно сохраняет старое
поведение: возвращается **naive** datetime (без tzinfo) в UTC. Колонки моделей
сейчас `DateTime` без `timezone=True` (naive), и naive-значение совместимо с ними
без риска сравнений naive↔aware (TypeError).

Когда (и если) timestamp-колонки переведут на `DateTime(timezone=True)`, достаточно
будет убрать `.replace(tzinfo=None)` здесь — все вызывающие места менять не придётся.
"""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Текущий момент в UTC как naive datetime (tzinfo=None)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
