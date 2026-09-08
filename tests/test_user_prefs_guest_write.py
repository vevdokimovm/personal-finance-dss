"""Настройки расчёта — не общая тетрадь для всех посетителей.

## Что закрывает

`user_prefs` при `user_id IS NULL` — **одна глобальная строка на всех гостей сервера**
(`crud.get_user_prefs` фильтрует `UserPrefs.user_id.is_(None)` и заводит её при первом
обращении). Роутер подключался **без единой зависимости**, то есть запрет гостевой
записи v8.53.0 до него не доставал — ровно как до `PUT /fx/rates`, закрытого в v9.6.0.

🔴 **Это не «просто настройки».** `l_min` уходит в фильтр допустимости альтернатив,
`risk_tolerance` — в веса SAW. Один анонимный посетитель молча меняет рекомендацию
всем остальным гостям: они видят план, посчитанный по чужому порогу ликвидности
и чужому отношению к риску.

Гейт ставится **на роутер**, а не на метод: пропуск одной ручки означал бы дыру,
которую нечем заметить, — тот же довод, что у `_FIN` и `_GUEST` в `app/api/router.py`.
Безопасные методы гейт пропускает сам, поэтому чтение настроек остаётся открытым
и гостевая песочница продолжает работать в development.

## Найдено

Вторым проходом независимого аудита 08.09.2026 — по СПИСКУ подключений в `router.py`,
а не по прозе. Соседний случай (`fx_router`) проверили днём раньше, этот пропустили.
"""
from __future__ import annotations

import pytest

from app.config import settings


@pytest.fixture
def _prod(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
    return settings


class TestGuestCannotChangeSharedSettings:
    """На проде аноним не пишет в общую строку настроек."""

    def test_anonymous_patch_is_rejected(self, client, _prod) -> None:
        """🔴 Мутация «снять `_GUEST` с роутера» роняет тест здесь."""
        response = client.patch("/api/user-prefs", json={"l_min": 6})
        assert response.status_code in (401, 403), (
            f"аноним записал общие настройки расчёта (код {response.status_code}) — "
            "его порог ликвидности применится к плану других посетителей"
        )

    def test_reading_settings_stays_open(self, client, _prod) -> None:
        """Чтение не закрывается: гейт пропускает безопасные методы сам.

        Иначе починка сломала бы гостевую песочницу, ради которой анонимный
        режим и существует.
        """
        assert client.get("/api/user-prefs").status_code == 200

    def test_value_is_not_written_by_the_rejected_request(self, client, _prod) -> None:
        before = client.get("/api/user-prefs").json()
        client.patch("/api/user-prefs", json={"l_min": 6})
        assert client.get("/api/user-prefs").json() == before, (
            "отклонённый запрос всё-таки изменил общие настройки"
        )


class TestDevelopmentKeepsTheSandbox:
    """В development гостевая запись остаётся — это рабочий инструмент."""

    def test_anonymous_patch_works_in_development(self, client, monkeypatch) -> None:
        monkeypatch.setattr(settings, "ENVIRONMENT", "development", raising=False)
        assert client.patch("/api/user-prefs", json={"l_min": 3}).status_code == 200
