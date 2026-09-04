"""Импорт выписки отдаёт типизированный ответ (v8.43.0).

`/banks/upload` был размечен `-> dict[str, Any]`, `/banks/list` — `-> list[dict[str, str]]`.
Схема заводится ДО фронта: правило проекта, и здесь оно особенно уместно — ответ импорта
несёт **семь полей**, включая сверку с контрольными итогами выписки, и рукописный тип
разошёлся бы с ним на первой же правке парсера.

🔴 Отдельная тонкость: ошибки разбора возвращаются со статусом **200** и полем
`status: "error"`. Это не оплошность, а осознанное решение — «файл не распознан» это не
сбой сервера, а результат работы. Но фронт обязан различать две ветки одного ответа, и
контракт должен показывать обе: поля успеха необязательны, потому что при ошибке их нет.
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


class TestUploadContract:
    def test_upload_response_is_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/banks/upload", "post")
        assert body.get("type") == "object"
        assert "properties" in body, (
            "ответ /banks/upload не типизирован: фронт получит `{[key: string]: unknown}` "
            "и напишет рукописный тип с кастом"
        )

    @pytest.mark.parametrize("field", ["status", "message"])
    def test_both_branches_share_these(self, schema, field) -> None:
        """`status` и `message` есть и при успехе, и при ошибке — на них строится ветвление."""
        body = _response_schema(schema, "/api/banks/upload", "post")
        assert field in body["properties"], field
        assert field in body.get("required", []), field

    @pytest.mark.parametrize(
        "field", ["added_count", "skipped_duplicates", "total_income", "total_expense"]
    )
    def test_success_fields_are_optional(self, schema, field) -> None:
        """Поля успеха НЕ обязательны: при ошибке разбора их нет вовсе.

        Пометить их обязательными значило бы соврать в контракте и заставить фронт
        читать `added_count` там, где импорт не состоялся.
        """
        body = _response_schema(schema, "/api/banks/upload", "post")
        assert field in body["properties"], field
        assert field not in body.get("required", []), field


class TestBanksListContract:
    def test_list_items_are_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/banks/list", "get")
        assert body.get("type") == "array"
        ref = body["items"]
        name = ref["$ref"].rsplit("/", 1)[-1]
        item = schema["components"]["schemas"][name]
        for field in ("id", "name"):
            assert field in item["properties"], field
            assert field in item.get("required", []), field

    def test_list_is_not_empty(self, client) -> None:
        """Список банков не пуст: пустой выпадающий список — тупик ([IA-04])."""
        banks = client.get("/api/banks/list").json()
        assert banks, "нет ни одного банка — импортировать выписку будет не из чего"
        assert all(b.get("id") and b.get("name") for b in banks)
