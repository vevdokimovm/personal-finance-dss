"""
Детерминированное назначение варианта A/B-эксперимента (P3.5).

Назначение чистое и воспроизводимое: один и тот же subject в одном и том же эксперименте
всегда попадает в один и тот же вариант (стабильный хеш). Никакого ML — чистая арифметика
по весам. Применяется ТОЛЬКО при первом назначении; результат фиксируется в БД (lock на
уровне сервиса), поэтому изменение конфигурации эксперимента не перекидывает уже
назначенных пользователей между вариантами.
"""
from __future__ import annotations

import hashlib
from collections.abc import Sequence


def assign_variant(
    experiment_key: str,
    subject_id: str | None,
    variants: Sequence[tuple[str, int]],
) -> str | None:
    """Возвращает имя варианта для subject в эксперименте — детерминированно по весам.

    `variants` — последовательность `(name, weight)` с положительными весами. Subject стабильно
    раскладывается в бакет хешем `sha256(experiment_key:subject_id)`, вариант выбирается по
    кумулятивной границе веса (распределение пропорционально весам, гранулярность — сами веса).
    Без subject или без валидных вариантов — `None` (вызывающий код трактует как control /
    отсутствие участия).
    """
    if not subject_id:
        return None
    total = sum(weight for _, weight in variants if weight > 0)
    if total <= 0:
        return None
    digest = hashlib.sha256(f"{experiment_key}:{subject_id}".encode()).hexdigest()
    bucket = int(digest, 16) % total
    cumulative = 0
    for name, weight in variants:
        if weight <= 0:
            continue
        cumulative += weight
        if bucket < cumulative:
            return name
    return None  # недостижимо при total > 0; защита типов
