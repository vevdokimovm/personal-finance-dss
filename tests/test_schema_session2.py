"""Тесты целевой ER-схемы v2.1.0 (DATA-04/06/09, INFRA-03)."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.crud import (
    get_goal_contributions,
    get_obligation_payments,
    record_obligation_payment,
)
from app.database.db import engine


# ── DATA-04: справочник категорий ─────────────────────────────────────────
def test_system_categories_seeded(client: TestClient) -> None:
    categories = client.get("/api/categories").json()
    names = {c["name"] for c in categories}
    assert "Продукты" in names
    assert "Зарплата" in names
    assert all("type" in c and "is_system" in c for c in categories)


def test_categories_filter_by_type(client: TestClient) -> None:
    income = client.get("/api/categories?type=income").json()
    assert income and all(c["type"] == "income" for c in income)


# ── DATA-04: поля транзакции ───────────────────────────────────────────────
def test_transaction_response_has_new_fields(client: TestClient) -> None:
    created = client.post("/api/transactions", json={
        "amount": 1500,
        "category": "Кафе и рестораны",
        "type": "expense",
        "date": "2025-03-01T00:00:00",
        "description": "Кофейня на углу",
    }).json()

    assert created["description"] == "Кофейня на углу"
    assert created["is_synced"] is False
    assert created["created_at"] is not None
    assert "category_id" in created and "external_id" in created


# ── DATA-06/09: жизненный цикл обязательств ────────────────────────────────
def test_obligation_lifecycle_fields(client: TestClient) -> None:
    created = client.post("/api/obligations", json={
        "name": "Ипотека",
        "amount": 3_000_000,
        "interest_rate": 0.085,
        "term": 240,
        "monthly_payment": 35000,
        "payment_day": 5,
        "bank": "Сбербанк",
        "type": "mortgage",
    }).json()

    assert created["bank"] == "Сбербанк"
    assert created["type"] == "mortgage"
    assert created["is_active"] is True
    assert created["start_date"] is not None
    assert created["closed_at"] is None


# ── DATA-06: жизненный цикл целей + начальное пополнение ────────────────────
def test_goal_lifecycle_and_initial_contribution(client: TestClient) -> None:
    created = client.post("/api/goals", json={
        "name": "Подушка безопасности",
        "target_amount": 300000,
        "current_amount": 50000,
        "deadline": "2026-01-01T00:00:00",
        "category": "safety",
        "priority": 2,
    }).json()

    assert created["priority"] == 2
    assert created["is_active"] is True
    assert created["achieved_at"] is None

    # Стартовое накопление должно попасть в историю (source="initial").
    with Session(engine) as session:
        contributions = get_goal_contributions(session, created["id"])
    assert len(contributions) == 1
    assert contributions[0].source == "initial"
    assert contributions[0].amount == 50000


def test_goal_without_initial_amount_has_no_contribution(client: TestClient) -> None:
    created = client.post("/api/goals", json={
        "name": "Отпуск",
        "target_amount": 100000,
        "current_amount": 0,
        "deadline": "2026-06-01T00:00:00",
        "category": "emotional",
    }).json()

    with Session(engine) as session:
        assert get_goal_contributions(session, created["id"]) == []


# ── DATA-06: история платежей по обязательству ──────────────────────────────
def test_obligation_payment_history(client: TestClient) -> None:
    obligation = client.post("/api/obligations", json={
        "name": "Автокредит",
        "amount": 800000,
        "interest_rate": 0.129,
        "term": 36,
        "monthly_payment": 25000,
        "payment_day": 15,
    }).json()

    with Session(engine) as session:
        record_obligation_payment(session, obligation["id"], amount=25000, is_early=False, remaining_after=775000)
        record_obligation_payment(session, obligation["id"], amount=100000, is_early=True, remaining_after=675000)
        payments = get_obligation_payments(session, obligation["id"])

    assert len(payments) == 2
    assert payments[1].is_early is True
