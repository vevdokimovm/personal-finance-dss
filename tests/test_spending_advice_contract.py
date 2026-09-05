"""`/planning/spending-advice` описан схемой, а не `dict[str, Any]` (v8.54.0).

## Почему это первый шаг, а не фронт

Пункт §8.2 «spending-advice слои 1-3» аудит нашёл незакрытым: эндпоинт живёт
с мат-модели v3.0.0, фронта у него нет вовсе. Правило вехи 8 без исключений —
**схема заводится на бэкенде ДО фронта**, иначе генератор клиента выдаёт `unknown`,
и экран дописывает типы руками. Именно так появились двойные касты, снятые в v8.50.0.

Ответ несёт пять коллекций разной природы (советы, статистика по категориям,
мерчанты, тренды, влияние на цели) — рукописный интерфейс на такое расходится
с бэкендом молча и быстро.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

TOP_LEVEL_FIELDS = [
    "current_period",
    "months_window",
    "months_with_data",
    "advice",
    "stats",
    "merchant_insights",
    "temporal_patterns",
    "goal_impact",
    "total_potential_saving",
]

COLLECTIONS = ["advice", "stats", "merchant_insights", "temporal_patterns", "goal_impact"]


def _schema(client: TestClient) -> dict:
    spec = client.get("/openapi.json").json()
    path = spec["paths"]["/api/planning/spending-advice"]["get"]
    return path["responses"]["200"]["content"]["application/json"]["schema"]


class TestResponseIsTyped:
    """Гейт против возврата к нетипизированному словарю."""

    def test_response_references_a_schema(self, client: TestClient) -> None:
        """🔴 `dict[str, Any]` даёт в OpenAPI пустой объект — генератор выдаёт `unknown`.

        Мутация: снять `response_model` — падает этот тест, а не разметка экрана.
        """
        assert "$ref" in _schema(client), (
            "ответ не описан схемой — клиент получит unknown, и фронт допишет тип руками"
        )

    def test_schema_declares_all_top_level_fields(self, client: TestClient) -> None:
        """Все девять полей ответа заведены: схема, потерявшая поле, молча его срежет."""
        spec = client.get("/openapi.json").json()
        name = _schema(client)["$ref"].rsplit("/", 1)[-1]
        properties = spec["components"]["schemas"][name]["properties"]
        missing = [f for f in TOP_LEVEL_FIELDS if f not in properties]
        assert not missing, f"схема не знает полей: {missing}"

    def test_collections_are_described_by_item_schemas(self, client: TestClient) -> None:
        """🔴 Каждая коллекция описана СВОИМ типом элемента.

        `list[dict]` внутри типизированной обёртки — та же дыра, что и раньше,
        просто на уровень глубже: обёртка выглядит контрактом, а содержимое нет.
        """
        spec = client.get("/openapi.json").json()
        name = _schema(client)["$ref"].rsplit("/", 1)[-1]
        properties = spec["components"]["schemas"][name]["properties"]
        for field in COLLECTIONS:
            items = properties[field].get("items", {})
            assert "$ref" in items, f"элементы `{field}` не описаны схемой"


class TestResponseShape:
    """Ответ на живом запросе соответствует объявленному."""

    def test_empty_profile_returns_all_collections(self, client: TestClient) -> None:
        """Пустой профиль — валидный ответ с пустыми списками, не 404 и не null.

        Это состояние КАЖДОГО нового пользователя: экран обязан открыться и объяснить,
        что данных пока мало, а не показать ошибку.
        """
        response = client.get("/api/planning/spending-advice")
        assert response.status_code == 200, response.text
        payload = response.json()
        for field in COLLECTIONS:
            assert payload[field] == [], f"`{field}` должен быть пустым списком"
        assert payload["total_potential_saving"] == 0.0

    def test_window_is_echoed_back(self, client: TestClient) -> None:
        """Окно анализа возвращается в ответе — экран подписывает им период.

        Без этого подпись «за 6 месяцев» пришлось бы хардкодить во фронте, и она
        разошлась бы с фактическим запросом при первой же смене умолчания.
        """
        payload = client.get("/api/planning/spending-advice?months=3").json()
        assert payload["months_window"] == 3
