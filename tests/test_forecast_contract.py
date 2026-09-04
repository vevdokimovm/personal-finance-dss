"""Прогноз отдаёт типизированный ответ (последний рукописный тип фронта, v8.48.0).

## Долг, который здесь закрывается

`/planning/forecast` был размечен `-> dict[str, Any]`, то есть приезжал в контракт как
`{[key: string]: unknown}`. Фронт держал под него **рукописный** `ForecastResult`
(`entities/plan-summary/model/types.ts`) — последний в проекте: остальные сущности
реэкспортируют сгенерированные типы.

Цена рукописного типа уже оплачена однажды: v8.31.1, дашборд упал, потому что тип
не знал о поле, которое сервер отдавал.

## 🔴 Что вскрылось при замере формы ответа

Рукописный тип описывал **четыре** поля верхнего уровня (`current`, `horizon`,
`forecast`, `r_bench`, `r_bench_source`, `real_r_bench`), а `forecast_indicators`
возвращает ещё **три**, о которых фронт не знал вовсе:

- `deficit_alert` — предупреждение о месяце, когда денег не хватит. Самое важное,
  что прогноз умеет сказать, и фронт его не показывал.
- `trend` — направление (`improving`/`declining`/`stable`).
- `stable_baseline` — какая часть дохода и расхода регулярна: по ней видно,
  насколько прогнозу вообще можно верить.
- `method` — чем считали точку и интервал.

То есть тип не «отставал на поле», а скрывал целый слой ответа. Это и есть довод
за генерацию из контракта: рукописный тип показывает то, что помнил автор.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"

TOP_LEVEL = ["current", "horizon", "forecast", "trend", "stable_baseline", "method"]
POINT_FIELDS = ["period", "Bt", "income", "expense", "obligations", "cash_flow", "Rt", "Lt", "Dt"]


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def _resolve(schema: dict, node: dict) -> dict:
    if "$ref" in node:
        return schema["components"]["schemas"][node["$ref"].rsplit("/", 1)[-1]]
    return node


@pytest.fixture(scope="module")
def forecast_schema(schema) -> dict:
    op = schema["paths"]["/api/planning/forecast"]["post"]
    return _resolve(schema, op["responses"]["200"]["content"]["application/json"]["schema"])


class TestContract:
    def test_response_is_typed(self, forecast_schema) -> None:
        assert forecast_schema.get("type") == "object", (
            "ответ /planning/forecast не типизирован — фронт получит unknown "
            "и снова напишет рукописный тип (урок v8.31.1)"
        )

    @pytest.mark.parametrize("field", TOP_LEVEL)
    def test_carries_field(self, forecast_schema, field) -> None:
        assert field in forecast_schema["properties"], field
        assert field in forecast_schema.get("required", []), (
            f"{field} необязателен — фронт получит undefined там, где сервер всегда шлёт"
        )

    def test_deficit_alert_is_optional_but_declared(self, forecast_schema) -> None:
        """🔴 `deficit_alert` объявлен, но НЕ обязателен — и это разные вещи.

        Его нет, когда дефицита не предвидится: это нормальный исход, а не отсутствие
        данных. Объявить обязательным значило бы заставить фронт читать `null` как
        значение; не объявить вовсе — то, что было до v8.48.0: фронт о самом важном
        поле прогноза не знал.
        """
        assert "deficit_alert" in forecast_schema["properties"]
        assert "deficit_alert" not in forecast_schema.get("required", [])

    @pytest.mark.parametrize("field", ["r_bench", "r_bench_source", "real_r_bench"])
    def test_rate_fields_declared(self, forecast_schema, field) -> None:
        """Три поля ставки — не дубли.

        `r_bench` эхо'ит ПРИМЕНЁННУЮ (сценарий «что если» или реальную),
        `real_r_bench` — всегда настоящую. Без второго кнопка «вернуть реальную»
        не знала бы, к чему возвращаться (баг найден живой проверкой в браузере).
        """
        assert field in forecast_schema["properties"], field

    @pytest.mark.parametrize("field", POINT_FIELDS)
    def test_forecast_point_is_typed(self, schema, forecast_schema, field) -> None:
        item = _resolve(schema, forecast_schema["properties"]["forecast"]["items"])
        assert field in item["properties"], field

    @pytest.mark.parametrize("field", ["Rt_p10", "Rt_p50", "Rt_p90"])
    def test_interval_bounds_are_typed(self, schema, forecast_schema, field) -> None:
        """Границы интервала Монте-Карло: по ним рисуется коридор неопределённости."""
        item = _resolve(schema, forecast_schema["properties"]["forecast"]["items"])
        assert field in item["properties"], field


class TestServed:
    def test_response_matches_the_schema(self, client) -> None:
        """Ответ содержит объявленное — контракт не расходится с поведением."""
        client.post(
            "/api/transactions",
            json={"amount": 180000, "category": "Зарплата", "type": "income"},
        )
        client.post(
            "/api/transactions",
            json={"amount": 78000, "category": "Продукты", "type": "expense"},
        )
        body = client.post("/api/planning/forecast", json={"horizon": 6}).json()
        for field in TOP_LEVEL:
            assert field in body, f"{field} объявлен в схеме, но не пришёл"
        assert body["forecast"], "прогноз пуст"
        for field in POINT_FIELDS:
            assert field in body["forecast"][0], field
