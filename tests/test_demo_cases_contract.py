"""Список демо-кейсов типизирован (гостевая песочница в React, v8.46.0).

## Зачем

Песочница потеряна при переносе фронта на React: выбор одного из десяти портретов
и раздел валидации были в Jinja, в React их нет (найдено в v8.45.0). Сервер всё умеет,
недоступен только путь — и README рекламирует «Демо за 30 секунд» как самый быстрый
способ понять продукт.

Перед возвратом входа схема заводится на бэкенде: `/demo/cases` размечен
`-> dict[str, Any]`, то есть приезжает во фронт как `{[key: string]: unknown}`, и под
него написали бы рукописный тип с кастом. Урок v8.31.1 — рукописный тип уронил дашборд.

## Что здесь проверяется

Что метаданные портрета **полны у каждого кейса**. Карточка выбора строится из них
целиком: без `name` человек видит пустую кнопку, без `situation` — не понимает, чем
портреты отличаются, а весь смысл экрана в том, чтобы выбрать похожий на себя.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"

REQUIRED_FIELDS = ("key", "name", "role", "tag", "situation", "expect", "accent")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def _response_schema(schema: dict, path: str, method: str) -> dict:
    ref = schema["paths"][path][method]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    if "$ref" in ref:
        return schema["components"]["schemas"][ref["$ref"].rsplit("/", 1)[-1]]
    return ref


class TestContract:
    def test_cases_response_is_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/demo/cases", "get")
        assert body.get("type") == "object", (
            "ответ /demo/cases не типизирован: фронт получит unknown и напишет "
            "рукописный тип с кастом"
        )
        assert "cases" in body["properties"]

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_case_carries_every_field_the_card_shows(self, schema, field) -> None:
        """Все поля обязательны: карточка выбора строится из них целиком.

        Необязательное поле здесь означает `undefined` в вёрстке — пустая кнопка или
        портрет без описания, по которому нельзя понять, похож ли он на тебя.
        """
        body = _response_schema(schema, "/api/demo/cases", "get")
        item_ref = body["properties"]["cases"]["items"]["$ref"]
        item = schema["components"]["schemas"][item_ref.rsplit("/", 1)[-1]]
        assert field in item["properties"], field
        assert field in item.get("required", []), field


class TestServed:
    def test_all_ten_portraits_are_listed(self, client) -> None:
        """Десять портретов — это обещание README, а не круглое число."""
        cases = client.get("/api/demo/cases").json()["cases"]
        assert len(cases) == 10, f"портретов {len(cases)}, README обещает десять"

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_every_case_has_non_empty_field(self, client, field) -> None:
        for case in client.get("/api/demo/cases").json()["cases"]:
            value = case.get(field)
            assert isinstance(value, str) and value.strip(), (
                f"кейс {case.get('key')}: поле {field} пустое — карточка покажет пустоту"
            )

    def test_every_listed_case_actually_loads(self, client) -> None:
        """🔴 Список и загрузка сходятся ПОЛНОСТЬЮ.

        Кейс в списке, который не грузится, — это кнопка, ведущая в ошибку. Проверяется
        каждый ключ из ответа, а не зашитый здесь список: одиннадцатый портрет попадёт
        под проверку сам.
        """
        for case in client.get("/api/demo/cases").json()["cases"]:
            response = client.post(f"/api/demo/load?case={case['key']}")
            assert response.status_code == 200, f"{case['key']} не грузится"

    def test_unknown_case_is_refused(self, client) -> None:
        """Опечатка в ключе — отказ, а не молчаливая загрузка чужого портрета."""
        assert client.post("/api/demo/load?case=no-such-person").status_code in (400, 404, 422)

    def test_cases_are_public(self, client) -> None:
        """Список читается гостем: он для того и нужен — до регистрации."""
        assert client.get("/api/demo/cases").status_code == 200
