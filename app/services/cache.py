"""Generic in-memory TTL-кэш (P3.3).

Потокобезопасный (FastAPI обслуживает запросы в пуле потоков). Хранит значения с
истечением по времени и ограничением размера (вытеснение самого старого). Используется
для дорогих детерминированных расчётов — ключ строится из хеша входных данных, поэтому
изменение данных естественно инвалидирует кэш (новый ключ → пересчёт).
"""
from __future__ import annotations

import time
from threading import Lock
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 256) -> None:
        self._ttl = ttl_seconds
        self._max = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            value, expires_at = item
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key not in self._store and len(self._store) >= self._max:
                oldest = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest]
            self._store[key] = (value, time.monotonic() + self._ttl)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)
