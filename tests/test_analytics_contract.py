"""Аналитика отдаёт типизированный ответ (экран владельца, v8.48.0).

Схема заводится ДО фронта: `/analytics/overview` и `/analytics/funnel` были размечены
`-> dict`, то есть приезжали в контракт как `{[key: string]: unknown}`.

Экран собирается для владельца продукта — решение владельца от 04.09.2026: смотреть
метрики в интерфейсе, а не через `curl` с ключом (`tests/test_owner_access.py`).

🔴 **Отдельная тонкость — `event_counts`.** Это словарь «тип события → сколько раз»,
и ключи в нём заранее неизвестны: появится новое событие в коде — появится новый ключ
без правки схемы. Поэтому он остаётся свободным отображением, а не перечислением полей:
жёсткая схема здесь потребовала бы менять контракт при каждом новом логируемом действии
и всё равно отставала бы от реальности.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def _resolve(schema: dict, node: dict) -> dict:
    if "$ref" in node:
        return schema["components"]["schemas"][node["$ref"].rsplit("/", 1)[-1]]
    return node


def _response(schema: dict, path: str) -> dict:
    op = schema["paths"][path]["get"]
    return _resolve(schema, op["responses"]["200"]["content"]["application/json"]["schema"])


class TestOverviewContract:
    @pytest.mark.parametrize(
        "field", ["period_days", "total_events", "active_users", "event_counts"]
    )
    def test_field_is_declared(self, schema, field) -> None:
        body = _response(schema, "/api/analytics/overview")
        assert body.get("type") == "object", "ответ /analytics/overview не типизирован"
        assert field in body["properties"], field
        assert field in body.get("required", []), (
            f"{field} необязателен — экран покажет пустоту вместо числа"
        )

    def test_event_counts_stays_open(self, schema) -> None:
        """🔴 Свободное отображение — намеренно, а не недоделка.

        Ключи — типы событий, они появляются вместе с новым логируемым действием.
        Перечислить их в схеме значило бы править контракт при каждом таком действии
        и всё равно отставать: событие уже пишется, а схема о нём не знает.
        """
        body = _response(schema, "/api/analytics/overview")
        counts = body["properties"]["event_counts"]
        assert counts.get("type") == "object", "event_counts перестал быть отображением"


class TestFunnelContract:
    def test_steps_are_typed(self, schema) -> None:
        body = _response(schema, "/api/analytics/funnel")
        assert "steps" in body["properties"]
        item = _resolve(schema, body["properties"]["steps"]["items"])
        for field in ("step", "users", "conversion_pct"):
            assert field in item["properties"], field
            assert field in item.get("required", []), field


class TestServed:
    def test_overview_answers(self, client) -> None:
        body = client.get("/api/analytics/overview").json()
        for field in ("period_days", "total_events", "active_users", "event_counts"):
            assert field in body, field

    def test_funnel_answers(self, client) -> None:
        steps = client.get("/api/analytics/funnel").json()["steps"]
        assert steps, "воронка пуста — шаги по умолчанию не заданы"
        for field in ("step", "users", "conversion_pct"):
            assert field in steps[0], field

    def test_period_is_bounded(self, client) -> None:
        """Период ограничен: запрос за 10 000 дней сканировал бы всю таблицу событий."""
        assert client.get("/api/analytics/overview?days=100000").status_code == 422
        assert client.get("/api/analytics/overview?days=0").status_code == 422
