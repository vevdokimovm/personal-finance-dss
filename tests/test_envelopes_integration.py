"""Интеграционные тесты конвертов (связь цель↔актив) через API.

Главный инвариант: актив, привязанный к цели, не попадает в Bliq (подушку) —
эти деньги учитываются только через цель. Написаны до реализации цепочки (TDD).
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def _seed_income_expense(client: TestClient) -> None:
    client.post("/api/transactions", json={
        "amount": 100000, "category": "Зарплата", "type": "income", "date": "2026-06-01T00:00:00"})
    client.post("/api/transactions", json={
        "amount": 30000, "category": "Продукты", "type": "expense", "date": "2026-06-02T00:00:00"})


def test_linked_asset_excluded_from_bliq(client: TestClient) -> None:
    linked = client.post("/api/liquid-assets", json={
        "name": "Накопительный", "amount": 50000, "interest_rate": 0.16, "type": "savings_account"}).json()  # noqa: E501
    client.post("/api/liquid-assets", json={
        "name": "Резерв", "amount": 30000, "interest_rate": 0.14, "type": "deposit"})

    created = client.post("/api/goals", json={
        "name": "Отпуск", "target_amount": 180000, "current_amount": 0,
        "deadline": "2027-03-13T00:00:00", "category": "emotional",
        "linked_asset_id": linked["id"]})
    assert created.status_code == 201

    _seed_income_expense(client)
    res = client.post("/api/planning/calculate", json={"risk_tolerance": 3}).json()
    # Привязанный к цели актив (50000) исключён; свободный резерв (30000) остаётся.
    assert res["input_summary"]["bliq"] == 30000


def test_unlinked_assets_all_in_bliq(client: TestClient) -> None:
    client.post("/api/liquid-assets", json={"name": "A", "amount": 50000, "type": "deposit"})
    client.post("/api/liquid-assets", json={"name": "B", "amount": 30000, "type": "deposit"})
    client.post("/api/goals", json={
        "name": "Цель", "target_amount": 100000, "current_amount": 10000,
        "deadline": "2027-01-01T00:00:00", "category": "material"})

    _seed_income_expense(client)
    res = client.post("/api/planning/calculate", json={"risk_tolerance": 3}).json()
    # Без привязок Bliq = сумма всех активов (обратная совместимость).
    assert res["input_summary"]["bliq"] == 80000


def test_goal_stores_linked_asset_id(client: TestClient) -> None:
    asset = client.post("/api/liquid-assets", json={"amount": 42000, "interest_rate": 0.16}).json()
    created = client.post("/api/goals", json={
        "name": "Цель", "target_amount": 100000, "current_amount": 0,
        "deadline": "2027-01-01T00:00:00", "category": "material",
        "linked_asset_id": asset["id"]}).json()
    assert created["linked_asset_id"] == asset["id"]


def test_dashboard_bliq_excludes_linked(client: TestClient) -> None:
    # дашборд (/api/recommendation) консистентен с планированием: Bliq без привязанных
    linked = client.post("/api/liquid-assets",
                         json={"amount": 50000, "type": "savings_account"}).json()
    client.post("/api/liquid-assets", json={"amount": 30000, "type": "deposit"})
    client.post("/api/goals", json={
        "name": "Отпуск", "target_amount": 180000, "current_amount": 0,
        "deadline": "2027-03-13T00:00:00", "category": "emotional",
        "linked_asset_id": linked["id"]})
    _seed_income_expense(client)
    res = client.post("/api/recommendation", json={}).json()
    assert res["indicators"]["Bliq"] == 30000
