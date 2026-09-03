"""История планов отдаёт ТИПИЗИРОВАННЫЙ ответ, а не `dict[str, Any]` (v8.34.0).

Заведено при выносе истории планов на фронт. Все четыре эндпоинта `/planning/history`
были размечены `-> dict[str, Any]`, то есть в OpenAPI попадали как
`{[key: string]: unknown}` — фронту оставалось бы писать рукописный тип и каст.

🔴 Именно так родился дефект v8.31.1: рукописный `CalculatePlanResult` пообещал
`ranked` и `top3` обязательными, хотя схема их не требует; TypeScript молчал из-за
каста, и дашборд падал в error boundary на ответе, который контракт разрешает.
Повторять этот путь для новой фичи нельзя — поэтому схемы заводятся на бэкенде
ДО того, как появится фронт, и фронт просто реэкспортирует сгенерированный тип.

Тесты ниже проверяют не «поля на месте» (это делает pytest на роутах), а то, что
КОНТРАКТ существует и обязательность полей в нём совпадает с фактической выдачей.
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
    @pytest.mark.parametrize("path,method", [
        ("/api/planning/history", "get"),
        ("/api/planning/history", "post"),
        ("/api/planning/history/{snapshot_id}", "get"),
    ])
    def test_response_is_not_untyped_dict(self, schema, path, method):
        """`dict[str, Any]` в контракте выглядит как объект без свойств — фронт из
        такого ничего не выведет и вынужден писать тип руками."""
        resp = _response_schema(schema, path, method)
        assert resp.get("properties"), (
            f"{method.upper()} {path} отдаёт нетипизированный объект — "
            f"фронту придётся угадывать форму"
        )

    def test_list_declares_items_and_count(self, schema):
        resp = _response_schema(schema, "/api/planning/history", "get")
        assert set(resp["required"]) >= {"items", "count"}

    def test_snapshot_declares_its_required_fields(self, schema):
        """Обязательность в контракте обязана совпадать с тем, что бэкенд всегда
        отдаёт: `id`, `created_at`, `risk_profile`, `indicators`, `best`. `note`
        необязателен честно — пользователь может не оставить подпись."""
        resp = _response_schema(schema, "/api/planning/history/{snapshot_id}", "get")
        required = set(resp["required"])
        assert {"id", "created_at", "risk_profile", "indicators", "best"} <= required
        assert "note" not in required


class TestBehaviourUnchanged:
    """Схемы не должны менять то, что видит потребитель — иначе это не типизация,
    а переделка контракта под видом уборки."""

    @staticmethod
    def _auth(client):
        token = client.post("/api/auth/register", json={
            "email": "hist@fp.io", "password": "strongpass1", "consent": True,
        }).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/api/consents/financial_data", headers=headers)
        return headers

    def test_empty_history_is_empty_list_not_error(self, client):
        headers = self._auth(client)
        r = client.get("/api/planning/history", headers=headers)
        assert r.status_code == 200
        assert r.json() == {"items": [], "count": 0}

    def test_saved_snapshot_comes_back_in_list_and_by_id(self, client):
        headers = self._auth(client)
        client.post("/api/transactions", headers=headers, json={
            "amount": 180000, "category": "Зарплата", "type": "income",
            "date": "2026-06-01T00:00:00",
        })
        saved = client.post("/api/planning/history", headers=headers,
                            json={"risk_tolerance": 3, "note": "до отпуска"})
        assert saved.status_code == 200, saved.text
        snapshot_id = saved.json()["id"]

        listing = client.get("/api/planning/history", headers=headers).json()
        assert listing["count"] == 1
        assert listing["items"][0]["id"] == snapshot_id
        assert listing["items"][0]["note"] == "до отпуска"

        one = client.get(f"/api/planning/history/{snapshot_id}", headers=headers)
        assert one.status_code == 200
        assert one.json()["id"] == snapshot_id
        # top3 есть в детальном ответе и нет в списочном — это осознанная разница,
        # список не должен таскать три альтернативы на каждую строку.
        assert "top3" in one.json()
        assert "top3" not in listing["items"][0]

    def test_deleted_snapshot_disappears_and_returns_404(self, client):
        headers = self._auth(client)
        saved = client.post("/api/planning/history", headers=headers,
                            json={"risk_tolerance": 3})
        snapshot_id = saved.json()["id"]

        assert client.delete(f"/api/planning/history/{snapshot_id}",
                             headers=headers).status_code == 200
        assert client.get("/api/planning/history", headers=headers).json()["count"] == 0
        assert client.get(f"/api/planning/history/{snapshot_id}",
                          headers=headers).status_code == 404

    def test_history_is_isolated_between_users(self, client):
        mine = self._auth(client)
        client.post("/api/planning/history", headers=mine, json={"risk_tolerance": 3})

        other = client.post("/api/auth/register", json={
            "email": "other@fp.io", "password": "strongpass1", "consent": True,
        }).json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other}"}
        client.post("/api/consents/financial_data", headers=other_headers)

        assert client.get("/api/planning/history",
                          headers=other_headers).json()["count"] == 0
