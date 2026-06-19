"""Тест динамического остатка срока обязательства.

term трактуется как ОБЩИЙ срок кредита; «осталось» и «выплачено» вычисляются от
даты взятия и убывают/растут со временем сами (раньше «осталось» было статичным
числом и не уменьшалось). Написан до реализации (TDD).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient


def test_obligation_remaining_is_computed_from_start(client: TestClient) -> None:
    # Общий срок 60 мес, взят ~20 месяцев назад → выплачено ~20, осталось ~40.
    start = (datetime.now() - timedelta(days=30 * 20)).isoformat()
    created = client.post("/api/obligations", json={
        "name": "Автокредит", "amount": 600000, "term": 60,
        "monthly_payment": 15000, "interest_rate": 0.12, "start_date": start,
    }).json()

    assert created["months_elapsed"] in (19, 20, 21)
    assert created["months_remaining"] in (39, 40, 41)
    # Инвариант: выплачено + осталось = общий срок
    assert created["months_elapsed"] + created["months_remaining"] == created["term"]


def test_obligation_remaining_capped_when_overdue(client: TestClient) -> None:
    # Взят раньше, чем весь срок (общий 12, прошло ~20) → остаток не уходит в минус.
    start = (datetime.now() - timedelta(days=30 * 20)).isoformat()
    created = client.post("/api/obligations", json={
        "name": "Старый", "amount": 0, "term": 12,
        "monthly_payment": 5000, "interest_rate": 0.1, "start_date": start,
    }).json()
    assert created["months_remaining"] == 0
    assert created["months_elapsed"] == 12


def test_obligation_without_start_date_no_crash(client: TestClient) -> None:
    created = client.post("/api/obligations", json={
        "name": "Без даты", "amount": 100000, "term": 24, "monthly_payment": 5000,
    }).json()
    assert created["months_elapsed"] == 0
    assert created["months_remaining"] == 24
