"""Регрессионные тесты дефектов из юзабилити-сессий (Сессия 1 v2.1.0)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _income(client: TestClient, amount: float = 100000) -> None:
    client.post("/api/transactions", json={
        "amount": amount,
        "category": "Зарплата",
        "type": "income",
        "date": "2025-01-01T00:00:00",
    })


def _obligation(client: TestClient, payment: float = 20000) -> None:
    client.post("/api/obligations", json={
        "name": "Кредит",
        "amount": 500000,
        "interest_rate": 0.2,
        "term": 24,
        "monthly_payment": payment,
        "payment_day": 10,
    })


# ── BUG-01: первое добавление создаёт ровно одну запись ───────────────────
def test_bug01_single_post_creates_one_transaction(client: TestClient) -> None:
    r = client.post("/api/transactions", json={
        "amount": 1000,
        "category": "Зарплата",
        "type": "income",
        "date": "2025-01-01T00:00:00",
    })
    assert r.status_code == 201
    transactions = client.get("/api/transactions").json()
    assert len(transactions) == 1


def test_bug01_single_post_creates_one_liquid_asset(client: TestClient) -> None:
    r = client.post("/api/liquid-assets", json={
        "name": "Депозит", "amount": 50000, "interest_rate": 0.14, "type": "deposit",
    })
    assert r.status_code == 201
    assets = client.get("/api/liquid-assets").json()
    assert len(assets) == 1


# ── BUG-02: ликвидный актив можно удалить ─────────────────────────────────
def test_bug02_liquid_asset_can_be_deleted(client: TestClient) -> None:
    created = client.post("/api/liquid-assets", json={
        "name": "Депозит", "amount": 50000, "interest_rate": 0.14, "type": "deposit",
    }).json()
    asset_id = created["id"]

    deleted = client.delete(f"/api/liquid-assets/{asset_id}")
    assert deleted.status_code == 204
    assert client.get("/api/liquid-assets").json() == []


def test_bug02_delete_missing_asset_returns_404(client: TestClient) -> None:
    assert client.delete("/api/liquid-assets/999999").status_code == 404


# ── BUG-04: доход 0 + обязательства → 422, а не 500 ───────────────────────
def test_bug04_zero_income_with_obligation_returns_422_on_analysis(client: TestClient) -> None:
    _obligation(client, payment=20000)
    assert client.get("/api/analysis").status_code == 422


def test_bug04_zero_income_with_obligation_returns_422_on_recommendation(client: TestClient) -> None:  # noqa: E501
    _obligation(client, payment=20000)
    assert client.post("/api/recommendation", json={}).status_code == 422


def test_bug04_zero_income_with_obligation_returns_422_on_planning(client: TestClient) -> None:
    _obligation(client, payment=20000)
    assert client.post("/api/planning/calculate", json={}).status_code == 422


def test_bug04_empty_profile_does_not_500(client: TestClient) -> None:
    # Пустой профиль (ни дохода, ни обязательств) — валидный кейс онбординга.
    assert client.get("/api/analysis").status_code == 200


def test_bug04_income_present_is_calculable(client: TestClient) -> None:
    _income(client, amount=100000)
    _obligation(client, payment=20000)
    assert client.get("/api/analysis").status_code == 200
