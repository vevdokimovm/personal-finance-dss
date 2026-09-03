"""Рефералка отдаёт ТИПИЗИРОВАННЫЙ ответ, а не `dict` (v8.37.0).

Тот же приём, что для истории планов (v8.34.0) и по той же причине: `-> dict` попадает
в OpenAPI как `{[key: string]: unknown}`, и фронт вынужден писать рукописный тип с
кастом. Ровно так родился дефект v8.31.1 — рукописный тип пообещал поля, которых схема
не требует, TypeScript промолчал из-за каста, экран упал в error boundary.

Схема заводится ДО фронта, фронт реэкспортирует сгенерированный тип.
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
    def test_referral_me_is_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/referral/me", "get")
        assert body.get("type") == "object"
        assert "properties" in body, (
            "ответ /referral/me не типизирован: фронт получит "
            "`{[key: string]: unknown}` и напишет рукописный тип с кастом"
        )

    @pytest.mark.parametrize(
        "field", ["referral_code", "invite_url", "invited_count", "milestones"]
    )
    def test_required_fields_present(self, schema, field) -> None:
        body = _response_schema(schema, "/api/referral/me", "get")
        assert field in body["properties"]
        assert field in body.get("required", []), (
            f"{field} приходит всегда — если он не обязателен в схеме, фронт обязан "
            "обрабатывать его отсутствие, которого не бывает"
        )

    def test_optional_fields_are_optional(self, schema) -> None:
        """`referred_by` и `next_milestone` честно необязательны.

        `referred_by` пуст у того, кто пришёл сам; `next_milestone` — `None`, когда
        все вехи достигнуты. Требовать их значит соврать в контракте.
        """
        body = _response_schema(schema, "/api/referral/me", "get")
        required = body.get("required", [])
        assert "referred_by" not in required
        assert "next_milestone" not in required


class TestMilestoneShape:
    def test_milestone_is_object_not_free_dict(self, schema) -> None:
        body = _response_schema(schema, "/api/referral/me", "get")
        items = body["properties"]["milestones"]["items"]
        name = items["$ref"].rsplit("/", 1)[-1]
        milestone = schema["components"]["schemas"][name]
        for field in ("threshold", "title", "reached"):
            assert field in milestone["properties"], field
