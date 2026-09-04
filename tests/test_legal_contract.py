"""Реестр юридических документов отдаёт ТИПИЗИРОВАННЫЙ ответ, а не `dict` (v8.40.0).

Тот же приём, что для истории планов (v8.34.0) и рефералки (v8.37.0), и по той же
причине: `-> dict` попадает в OpenAPI как `{[key: string]: unknown}`, и фронт вынужден
писать рукописный тип с кастом — путь, которым в v8.31.1 родился упавший дашборд.

Здесь цена ошибки выше обычной: по этим полям фронт строит юридический контур — ссылки
на политику, оферту и cookie в футере (L7), дисклеймер 39-ФЗ на экране рекомендаций (L5).
Рукописный тип, разошедшийся с контрактом, означает не «страница поехала», а отсутствие
обязательного по закону элемента.
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


class TestContractExists:
    def test_legal_documents_is_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/legal/documents", "get")
        assert body.get("type") == "object"
        assert "properties" in body, (
            "ответ /legal/documents не типизирован: фронт получит "
            "`{[key: string]: unknown}` и напишет рукописный тип с кастом"
        )

    @pytest.mark.parametrize("field", ["documents", "disclaimer_39fz"])
    def test_required_fields_present(self, schema, field) -> None:
        body = _response_schema(schema, "/api/legal/documents", "get")
        assert field in body["properties"]
        assert field in body.get("required", []), (
            f"{field} приходит всегда; необязательность в схеме заставила бы фронт "
            "обрабатывать отсутствие, которого не бывает"
        )


class TestDocumentShape:
    def test_document_is_object_not_free_dict(self, schema) -> None:
        """У каждого документа есть заголовок, версия, дата и адрес.

        Версия и дата вступления — не украшение: по 152-ФЗ согласие даётся на
        КОНКРЕТНУЮ редакцию, и интерфейс обязан показывать, на какую именно.
        """
        body = _response_schema(schema, "/api/legal/documents", "get")
        documents = body["properties"]["documents"]
        ref = documents.get("additionalProperties", {})
        name = ref["$ref"].rsplit("/", 1)[-1]
        document = schema["components"]["schemas"][name]
        for field in ("title", "version", "effective_from", "url"):
            assert field in document["properties"], field
            assert field in document.get("required", []), field
