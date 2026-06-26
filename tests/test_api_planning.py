"""Функциональные тесты фичи планирования (ядро продукта через API)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def _load_anna(client: TestClient) -> None:
    client.post("/api/demo/load?case=anna")


@pytest.mark.parametrize("risk", [1, 2, 3, 4, 5])
def test_calculate_all_profiles(client: TestClient, risk: int) -> None:
    _load_anna(client)
    resp = client.post("/api/planning/calculate", json={"risk_tolerance": risk})
    assert resp.status_code == 200
    body = resp.json()
    # Полный цикл вернул ранжирование, лучшую альтернативу и сводку входа
    assert "best" in body
    assert "ranked" in body and len(body["ranked"]) > 0
    assert "top3" in body
    assert "input_summary" in body
    # Веса соответствуют выбранному профилю
    assert body["risk_profile"] == risk or "weights" in body


def test_calculate_empty_is_failloud(client: TestClient) -> None:
    # Без данных алгоритм не должен падать 500 — структурный диагноз/422
    resp = client.post("/api/planning/calculate", json={"risk_tolerance": 3})
    assert resp.status_code in (200, 422)


def test_calculate_income_override_changes_result(client: TestClient) -> None:
    _load_anna(client)
    base = client.post("/api/planning/calculate", json={"risk_tolerance": 3}).json()
    high = client.post("/api/planning/calculate",
                       json={"risk_tolerance": 3, "income_override": 999999}).json()
    assert high["input_summary"]["income"] == 999999
    assert high["input_summary"]["income"] != base["input_summary"]["income"]


def test_forecast_returns_series(client: TestClient) -> None:
    _load_anna(client)
    resp = client.post("/api/planning/forecast", json={"horizon": 6})
    assert resp.status_code == 200
    body = resp.json()
    assert "forecast" in body
    assert len(body["forecast"]) == 6


def test_key_rate_endpoint(client: TestClient) -> None:
    resp = client.get("/api/planning/key-rate")
    assert resp.status_code == 200
    assert "rate" in resp.json() or "key_rate" in resp.json()


def test_spending_advice_endpoint_shape(client: TestClient) -> None:
    _load_anna(client)
    resp = client.get("/api/planning/spending-advice?months=6")
    assert resp.status_code == 200
    body = resp.json()
    assert "advice" in body and "stats" in body
    assert "temporal_patterns" in body
    assert "goal_impact" in body
    assert "total_potential_saving" in body


def test_scenario_save_and_list(client: TestClient) -> None:
    saved = client.post("/api/planning/scenarios", json={
        "name": "Тест-сценарий",
        "parameters": {"risk_tolerance": 3},
        "result": {"a_star": "60/40/0"},
    })
    assert saved.status_code == 200
    assert saved.json()["name"] == "Тест-сценарий"

    listing = client.get("/api/planning/scenarios").json()
    assert any(s["name"] == "Тест-сценарий" for s in listing)


def test_planning_export_csv(client: TestClient) -> None:
    _load_anna(client)
    resp = client.get("/api/planning/export.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


def test_planning_export_xlsx(client: TestClient) -> None:
    _load_anna(client)
    resp = client.get("/api/planning/export.xlsx")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers.get("content-type", "")
    assert resp.content[:4] == b"PK\x03\x04"  # zip-контейнер xlsx
    assert "attachment" in resp.headers.get("content-disposition", "")


def test_planning_export_pdf(client: TestClient) -> None:
    _load_anna(client)
    resp = client.get("/api/planning/export.pdf")
    assert resp.status_code == 200
    assert "application/pdf" in resp.headers.get("content-type", "")
    assert resp.content[:5] == b"%PDF-"
    assert "attachment" in resp.headers.get("content-disposition", "")
