"""Функциональные тесты демо-данных (все 6 портретов).

Проверяют загрузку каждого кейса, что после загрузки данные доступны и расчёт
строится, а также preview/clear/список кейсов.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

CASES = ["anna", "dmitriy", "mikhail", "igor", "olga", "viktor"]


@pytest.mark.parametrize("case", CASES)
def test_demo_load_each_case(client: TestClient, case: str) -> None:
    resp = client.post(f"/api/demo/load?case={case}")
    assert resp.status_code == 200

    # После загрузки появились операции и обязательства
    txns = client.get("/api/transactions").json()
    assert len(txns) > 0
    obs = client.get("/api/obligations").json()
    # У каждого обязательства корректный вычисленный остаток (term-фикс)
    for o in obs:
        assert o["months_elapsed"] + o["months_remaining"] == o["term"]


@pytest.mark.parametrize("case", CASES)
def test_demo_case_is_calculable(client: TestClient, case: str) -> None:
    client.post(f"/api/demo/load?case={case}")
    resp = client.post("/api/planning/calculate", json={"risk_tolerance": 3})
    # Либо успешный план, либо честный структурный диагноз (fail-loud) — не 500
    assert resp.status_code in (200, 422)


def test_demo_unknown_case_rejected(client: TestClient) -> None:
    resp = client.post("/api/demo/load?case=nonexistent")
    assert resp.status_code == 400


def test_demo_cases_list(client: TestClient) -> None:
    resp = client.get("/api/demo/cases")
    assert resp.status_code == 200
    assert set(resp.json()["cases"]) == set(CASES)


def test_demo_preview_does_not_persist(client: TestClient) -> None:
    before = len(client.get("/api/transactions").json())
    resp = client.get("/api/demo/preview?case=anna")
    assert resp.status_code == 200
    after = len(client.get("/api/transactions").json())
    assert after == before  # preview не пишет в БД


def test_demo_clear_removes_data(client: TestClient) -> None:
    client.post("/api/demo/load?case=anna")
    assert len(client.get("/api/transactions").json()) > 0
    resp = client.post("/api/demo/clear")
    assert resp.status_code == 200
    assert len(client.get("/api/transactions").json()) == 0
    assert len(client.get("/api/obligations").json()) == 0
