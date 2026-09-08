"""Курсы валют меняет только администратор.

## Что закрывает

`fx_rates` — таблица с первичным ключом по валюте, **одна на весь экземпляр**, и она
читается на каждом расчёте: планирование, анализ, рекомендация приводят суммы к базовой
валюте через `to_base_currency`.

🔴 **`PUT /api/fx/rates` не имел ни одной зависимости, кроме сессии БД.** Соседний
`POST /api/fx/refresh` в том же файле закрыт `require_admin`, и сам `require_admin`
в файле импортирован — то есть про защиту знали, а на этот метод её не поставили.
Роутер подключается без гейта гостевой записи, поэтому запрет v8.53.0 сюда тоже
не распространялся.

**Что это давало.** Аноним меняет курс доллара — и у каждого пользователя с записями
в иностранной валюте меняются свободный ресурс, ликвидность, ПДН и рекомендация.
Молча, без следа в интерфейсе: человек видит обычный план, посчитанный по чужому курсу.

## Почему `require_admin`, а не «любой вошедший»

Курс — общий ресурс, а не личные данные. Пользователь, меняющий его «для себя»,
меняет его всем. Права на это нет ни у кого, кроме владельца экземпляра.
"""
from __future__ import annotations

import pytest


PAYLOAD = {"currency": "USD", "rate_to_usd": 0.0001}


@pytest.fixture
def admin_key(monkeypatch) -> str:
    """🔴 Ключ задаётся ЯВНО — иначе тесты зелены по чужой причине.

    `require_admin` в development при пустом `ADMIN_API_KEY` пропускает всех
    намеренно, чтобы не мешать локальной работе. Тест разграничения без ключа
    проверял бы эту ветку, а не защиту эндпоинта: его докстрока прямо об этом
    предупреждает.
    """
    from app.config import settings

    monkeypatch.setattr(settings, "ADMIN_API_KEY", "test-admin-key", raising=False)
    return "test-admin-key"


class TestAnonymousCannotMoveTheMarket:
    """Запись курса закрыта для всех, кто не администратор."""

    def test_anonymous_put_is_rejected(self, client, admin_key) -> None:
        """🔴 Мутация «снять require_admin» роняет тест здесь.

        Ожидается отказ (401 или 403), а не 200: конкретный код зависит от того,
        как `require_admin` различает «не представился» и «нет прав», и тест
        не должен ломаться от этого выбора.
        """
        response = client.put("/api/fx/rates", json=PAYLOAD)
        assert response.status_code in (401, 403), (
            f"аноним записал курс валюты (код {response.status_code}) — "
            "это меняет расчёт всем пользователям экземпляра"
        )

    def test_rate_is_not_written_by_the_rejected_request(self, client, admin_key) -> None:
        """Отказ — не только код ответа: значение в таблице не должно измениться."""
        before = client.get("/api/fx/rates").json()
        client.put("/api/fx/rates", json=PAYLOAD)
        after = client.get("/api/fx/rates").json()
        assert before == after, "отклонённый запрос всё-таки изменил таблицу курсов"


class TestAdminStillWorks:
    """Владелец экземпляра курс менять может — иначе починка ломает функцию."""

    def test_admin_key_is_accepted(self, client, admin_key) -> None:
        response = client.put(
            "/api/fx/rates", json=PAYLOAD, headers={"X-Admin-Key": admin_key}
        )
        assert response.status_code == 200, response.text


class TestNeighbourEndpointStaysClosed:
    """Соседний метод того же роутера не должен открыться заодно."""

    def test_refresh_still_requires_admin(self, client, admin_key) -> None:
        response = client.post("/api/fx/refresh")
        assert response.status_code in (401, 403), (
            "обновление курсов из внешнего источника открылось анониму"
        )
