"""Функциональные тесты фичи бюджетов (план-факт по категориям, FR-22)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_budget_create_list_delete(client: TestClient) -> None:
    created = client.post("/api/budgets", json={"category": "Кафе и рестораны", "limit_amount": 8000})
    assert created.status_code == 201
    bid = created.json()["id"]

    listing = client.get("/api/budgets").json()
    assert any(b["id"] == bid for b in listing)

    assert client.delete(f"/api/budgets/{bid}").status_code in (200, 204)
    assert all(b["id"] != bid for b in client.get("/api/budgets").json())


def test_budget_rejects_nonpositive_limit(client: TestClient) -> None:
    r = client.post("/api/budgets", json={"category": "Кафе", "limit_amount": 0})
    assert r.status_code == 422


def test_budget_status_plan_fact(client: TestClient) -> None:
    client.post("/api/demo/load?case=anna")
    client.post("/api/budgets", json={"category": "Продукты", "limit_amount": 20000})
    resp = client.get("/api/planning/budgets/status" if False else "/api/budgets/status?days=30")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
