"""Функциональные тесты демо-данных (все 6 портретов).

Проверяют загрузку каждого кейса, что после загрузки данные доступны и расчёт
строится, а также preview/clear/список кейсов.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

CASES = ["anna", "dmitriy", "mikhail", "igor", "olga", "viktor",
         "ekaterina", "artyom", "natalya", "pavel"]


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
    body = resp.json()
    assert set(body["keys"]) == set(CASES)
    assert {c["key"] for c in body["cases"]} == set(CASES)


def test_demo_monthly_total_excludes_history(client: TestClient) -> None:
    """Месячный доход = текущий месяц, а не сумма всей многомесячной истории в БД."""
    client.post("/api/demo/clear")
    client.post("/api/demo/load?case=anna")
    n_tx = len(client.get("/api/transactions").json())
    assert n_tx > 7  # в БД лежит многомесячная история операций
    calc = client.post("/api/planning/calculate", json={"risk_tolerance": 3})
    assert calc.status_code == 200
    it = calc.json()["indicators"]["It"]
    value = it["value"] if isinstance(it, dict) else it
    assert abs(float(value) - 180000) < 1  # ровно доход текущего месяца Анны


def test_demo_forecast_is_not_constant(client: TestClient) -> None:
    """Прогноз свободного ресурса не должен быть прямой с одинаковой дельтой."""
    client.post("/api/demo/clear")
    client.post("/api/demo/load?case=dmitriy")
    fc = client.post("/api/planning/forecast", json={"horizon": 6}).json()
    rt = [f["Rt"] for f in fc["forecast"]]
    deltas = [round(rt[i + 1] - rt[i]) for i in range(len(rt) - 1)]
    assert len(set(deltas)) > 1  # дельты различаются


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


def test_demo_forecast_direction_matches_history(client: TestClient) -> None:
    """Прогноз идёт в сторону истории: растущий портрет — вверх, падающий — вниз.
    Проверка через РЕАЛЬНЫЙ роут /planning/forecast, а не юнит-математику."""
    def forecast_income(case: str) -> list[float]:
        client.post("/api/demo/clear")
        client.post(f"/api/demo/load?case={case}")
        fc = client.post("/api/planning/forecast", json={"horizon": 6}).json()
        return [f["income"] for f in fc["forecast"]]

    up = forecast_income("dmitriy")      # история дохода растёт
    assert up[-1] > up[0], "растущая история должна давать растущий прогноз"
    down = forecast_income("mikhail")    # история дохода падает
    assert down[-1] < down[0], "падающая история должна давать падающий прогноз"


def test_demo_preview_matches_planning_forecast(client: TestClient) -> None:
    """Витрина «Валидация» и реальное /planning дают прогноз ОДНОЙ формы — нет расхождения,
    из-за которого раньше был костыль (синтетическая история). Оба трендовые, одно направление."""
    case = "dmitriy"
    client.post("/api/demo/clear")
    client.post(f"/api/demo/load?case={case}")
    planning = [f["Rt"] for f in
                client.post("/api/planning/forecast", json={"horizon": 6}).json()["forecast"]]
    preview = [f["Rt"] for f in
               client.get(f"/api/demo/preview?case={case}").json()["forecast"]["forecast"]]

    def deltas(seq: list[float]) -> set[int]:
        return {round(seq[i + 1] - seq[i]) for i in range(len(seq) - 1)}

    assert len(deltas(preview)) > 1, "прогноз витрины не должен быть прямой с одной дельтой"
    assert len(deltas(planning)) > 1, "прогноз планирования не должен быть прямой с одной дельтой"
    assert (preview[-1] - preview[0]) * (planning[-1] - planning[0]) > 0, \
        "витрина и планирование должны показывать прогноз в одну сторону"
