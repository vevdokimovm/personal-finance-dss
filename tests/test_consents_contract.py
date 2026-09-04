"""Состояние согласий отдаётся ТИПИЗИРОВАННЫМ ответом (L3, v8.41.0).

Тот же приём, что для истории планов (v8.34.0), рефералки (v8.37.0) и реестра документов
(v8.40.0), и по той же причине: `-> dict` попадает в OpenAPI как
`{[key: string]: unknown}`, и фронт вынужден писать рукописный тип с кастом.

🔴 Здесь цена ошибки максимальна из всех. По этому ответу строится экран выдачи и отзыва
согласий — требование L3. Разошедшийся с контрактом тип означает не «страница поехала»,
а невозможность отозвать согласие: пользователь по 152-ФЗ имеет на это право, и
отсутствие механизма — нарушение, а не дефект интерфейса.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.legal import CONSENT_TYPES, UNWITHDRAWABLE

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
    def test_consents_response_is_typed(self, schema) -> None:
        body = _response_schema(schema, "/api/consents", "get")
        assert body.get("type") == "object"
        assert "properties" in body, (
            "ответ /consents не типизирован: фронт получит `{[key: string]: unknown}` "
            "и напишет рукописный тип с кастом — путь, которым в v8.31.1 упал дашборд"
        )
        assert "consents" in body["properties"]
        assert "consents" in body.get("required", [])

    def test_consent_state_fields_are_declared(self, schema) -> None:
        """`granted`, `version`, `withdrawable` — на них держится весь экран L3.

        `withdrawable` особенно: по нему интерфейс решает, показывать ли кнопку отзыва.
        Необязательное поле фронт вправе не обработать — и покажет кнопку там, где
        сервер ответит 409, либо спрячет там, где отзыв разрешён.
        """
        body = _response_schema(schema, "/api/consents", "get")
        ref = body["properties"]["consents"].get("additionalProperties", {})
        name = ref["$ref"].rsplit("/", 1)[-1]
        state = schema["components"]["schemas"][name]
        for field in ("granted", "version", "withdrawable"):
            assert field in state["properties"], field
            assert field in state.get("required", []), field


class TestAllTypesReachable:
    def test_every_known_consent_type_comes_back(self, client) -> None:
        """Ответ несёт ВСЕ типы, включая невыданные.

        Фронту нужно знать не только что выдано, но и что предстоит спросить: экран
        согласий обязан показать все три, иначе часть из них человек не увидит вовсе
        и не сможет ни выдать, ни отозвать.
        """
        client.post(
            "/api/auth/register",
            json={"email": "consents@test.io", "password": "password123", "consent": True},
        )
        state = client.get("/api/consents").json()["consents"]
        assert set(state) == set(CONSENT_TYPES)

    def test_unwithdrawable_marked_as_such(self, client) -> None:
        """Согласие-основание помечено `withdrawable: false`, а не спрятано.

        Прятать его нельзя: человек имеет право знать, что оно выдано. Но и кнопку
        отзыва показывать нельзя — сервер ответит 409, и это был бы тупик ([IA-04]).
        """
        client.post(
            "/api/auth/register",
            json={"email": "consents2@test.io", "password": "password123", "consent": True},
        )
        state = client.get("/api/consents").json()["consents"]
        for consent_type in UNWITHDRAWABLE:
            assert state[consent_type]["withdrawable"] is False
        for consent_type in set(CONSENT_TYPES) - set(UNWITHDRAWABLE):
            assert state[consent_type]["withdrawable"] is True
