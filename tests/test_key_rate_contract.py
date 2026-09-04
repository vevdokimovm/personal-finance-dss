"""Ключевая ставка отдаётся типизированным ответом (v8.42.0).

`/planning/key-rate` был размечен `-> dict[str, object]`, то есть в OpenAPI попадал как
`{[key: string]: unknown}`. Фронту это стоило бы рукописного типа с кастом — путь,
которым в v8.31.1 упал дашборд.

🔴 Здесь ошибка была бы особенно тихой: поле называется `key_rate`, и рукописный тип
с полем `rate` дал бы `undefined` без единого предупреждения компилятора. Кнопка «взять
ключевую ставку» просто не появлялась бы, а понять почему — только отладкой.

`source` и `as_of` — не украшение: ставка может прийти из живого запроса к cbr.ru, из
кэша или из резервного значения настроек, и человек вправе знать, насколько она свежая.
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


def _response_schema(schema: dict, path: str, method: str) -> dict:
    op = schema["paths"][path][method]
    ref = op["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in ref:
        name = ref["$ref"].rsplit("/", 1)[-1]
        return schema["components"]["schemas"][name]
    return ref


def test_key_rate_is_typed(schema) -> None:
    body = _response_schema(schema, "/api/planning/key-rate", "get")
    assert body.get("type") == "object"
    assert "properties" in body, (
        "ответ /planning/key-rate не типизирован: фронт напишет рукописный тип с кастом, "
        "и опечатка в имени поля не будет замечена компилятором"
    )


@pytest.mark.parametrize("field", ["key_rate", "source", "as_of"])
def test_required_fields(schema, field) -> None:
    body = _response_schema(schema, "/api/planning/key-rate", "get")
    assert field in body["properties"], field
    assert field in body.get("required", []), (
        f"{field} приходит всегда — необязательность заставила бы фронт обрабатывать "
        "отсутствие, которого не бывает"
    )


def test_rate_comes_as_fraction(client) -> None:
    """Ставка — доля (0.16), а не проценты (16).

    Весь расчёт работает в долях (`r_bench` в `UserPrefsUpdate`: `ge=0.0, le=1.0`).
    Если бы эндпоинт отдавал проценты, подстановка «взять ключевую» записала бы
    в настройки 16 вместо 0.16 — ставку 1600% годовых, и план перестал бы иметь смысл.
    """
    body = client.get("/api/planning/key-rate").json()
    assert 0.0 <= body["key_rate"] <= 1.0, (
        f"ключевая ставка вне диапазона долей: {body['key_rate']} — похоже на проценты"
    )
