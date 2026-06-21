"""TTL-кэш (P3.3)."""
from __future__ import annotations

import time

from app.services.cache import TTLCache


class TestTTLCache:
    def test_set_and_get(self) -> None:
        cache = TTLCache(ttl_seconds=10)
        cache.set("k", {"v": 1})
        assert cache.get("k") == {"v": 1}

    def test_miss_returns_none(self) -> None:
        assert TTLCache().get("absent") is None

    def test_expiry(self) -> None:
        cache = TTLCache(ttl_seconds=0.05)
        cache.set("k", "value")
        assert cache.get("k") == "value"
        time.sleep(0.08)
        assert cache.get("k") is None

    def test_eviction_when_full(self) -> None:
        cache = TTLCache(ttl_seconds=100, max_size=2)
        cache.set("a", 1)
        time.sleep(0.01)
        cache.set("b", 2)
        time.sleep(0.01)
        cache.set("c", 3)  # вытеснит самый старый ('a')
        assert len(cache) == 2
        assert cache.get("a") is None
        assert cache.get("c") == 3

    def test_clear(self) -> None:
        cache = TTLCache()
        cache.set("k", 1)
        cache.clear()
        assert cache.get("k") is None
        assert len(cache) == 0

    def test_overwrite_same_key_no_eviction(self) -> None:
        cache = TTLCache(ttl_seconds=100, max_size=1)
        cache.set("k", 1)
        cache.set("k", 2)  # тот же ключ — не вытеснение
        assert cache.get("k") == 2
        assert len(cache) == 1


class TestRecommendationCache:
    def test_cached_then_invalidated_on_data_change(self, client, db_session) -> None:
        from datetime import datetime

        from app.api.routes_recommendation import _recommendation_cache
        from app.database import crud

        db = db_session
        crud.create_transaction(db, amount=120000, type="income", date=datetime(2026, 6, 1))
        crud.create_transaction(db, amount=40000, type="expense", date=datetime(2026, 6, 2))

        r1 = client.post("/api/recommendation")
        assert r1.status_code == 200
        assert len(_recommendation_cache) >= 1  # результат закэширован

        # повторный запрос с теми же данными — ответ идентичен (из кэша)
        r2 = client.post("/api/recommendation")
        assert r2.json() == r1.json()

        # изменение данных меняет отпечаток → новый ключ (пересчёт), кэш растёт
        before = len(_recommendation_cache)
        crud.create_transaction(db, amount=7000, type="expense", date=datetime(2026, 6, 3))
        r3 = client.post("/api/recommendation")
        assert r3.status_code == 200
        assert len(_recommendation_cache) > before
