"""Гард кэша расчёта плана (P1.2).

`/api/planning/calculate` гоняет Monte Carlo (бутылочное горло по нагрузочному
тесту P0.4). Тяжёлый блок `run_planning` обёрнут TTL-кэшем с отпечатком реальных
входов. Эти тесты фиксируют два инварианта одновременно:
  1. идентичный запрос не пересчитывается (кэш работает, результат идентичен);
  2. кэш не «слипает» разные входы — смена профиля риска или входных данных даёт
     пересчёт (анти-over-caching: нельзя вернуть чужой результат из кэша).

Спай через `wraps=` вызывает настоящую функцию, поэтому результат остаётся
боевым, а мы лишь считаем число реальных пересчётов.
"""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.services.planning import run_planning as real_run_planning

CALC = "/api/planning/calculate"
SPY_TARGET = "app.api.routes_planning.run_planning"


def _load(client: TestClient, case: str = "anna") -> None:
    client.post(f"/api/demo/load?case={case}")


def test_identical_request_uses_cache(client: TestClient) -> None:
    _load(client)
    with patch(SPY_TARGET, wraps=real_run_planning) as spy:
        r1 = client.post(CALC, json={"risk_tolerance": 3})
        r2 = client.post(CALC, json={"risk_tolerance": 3})

    assert r1.status_code == 200 and r2.status_code == 200
    assert spy.call_count == 1, "повторный идентичный запрос обязан попасть в кэш"
    assert r1.json() == r2.json(), "кэшированный результат должен совпадать с исходным"


def test_param_change_recomputes(client: TestClient) -> None:
    _load(client)
    with patch(SPY_TARGET, wraps=real_run_planning) as spy:
        first = client.post(CALC, json={"risk_tolerance": 3}).json()
        second = client.post(CALC, json={"risk_tolerance": 4}).json()

    assert spy.call_count == 2, "другой профиль риска — это другой вход, нужен пересчёт"
    assert first != second, "разные профили обязаны давать разный результат"


def test_input_change_recomputes(client: TestClient) -> None:
    _load(client)
    with patch(SPY_TARGET, wraps=real_run_planning) as spy:
        client.post(CALC, json={"risk_tolerance": 3})
        client.post(CALC, json={"risk_tolerance": 3, "income_override": 500000})

    assert spy.call_count == 2, "изменение эффективного дохода меняет отпечаток входа"


def test_cache_isolated_per_request_data(client: TestClient) -> None:
    # Загрузили один кейс, посчитали; сменили данные на другой кейс — пересчёт.
    _load(client, "anna")
    with patch(SPY_TARGET, wraps=real_run_planning) as spy:
        client.post(CALC, json={"risk_tolerance": 3})
        _load(client, "dmitriy")
        client.post(CALC, json={"risk_tolerance": 3})

    assert spy.call_count == 2, "смена набора данных пользователя должна инвалидировать кэш"
