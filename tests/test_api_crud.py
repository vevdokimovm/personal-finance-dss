"""Функциональные тесты CRUD основных сущностей через API.

Полный жизненный цикл: создание → появление в списке → удаление → исчезновение,
плюс проверка валидации входных данных.
"""
from __future__ import annotations

from fastapi.testclient import TestClient


class TestTransactionsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/transactions", json={
            "amount": 5000, "category": "Продукты", "type": "expense",
            "date": "2026-06-01T00:00:00", "description": "тест"})
        assert created.status_code in (200, 201)
        tid = created.json()["id"]

        listing = client.get("/api/transactions").json()
        assert any(t["id"] == tid for t in listing)

        deleted = client.delete(f"/api/transactions/{tid}")
        assert deleted.status_code in (200, 204)
        assert all(t["id"] != tid for t in client.get("/api/transactions").json())

    def test_income_and_expense_types(self, client: TestClient) -> None:
        for ttype, cat in [("income", "Зарплата"), ("expense", "Транспорт")]:
            r = client.post("/api/transactions", json={
                "amount": 1000, "category": cat, "type": ttype, "date": "2026-06-01T00:00:00"})
            assert r.status_code in (200, 201)

    def test_export_csv(self, client: TestClient) -> None:
        client.post("/api/transactions", json={
            "amount": 1000, "category": "Продукты", "type": "expense", "date": "2026-06-01T00:00:00"})  # noqa: E501
        resp = client.get("/api/transactions/export.csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")

    def test_update_changes_fields(self, client: TestClient) -> None:
        created = client.post("/api/transactions", json={
            "amount": 1000, "category": "Продукты", "type": "expense",
            "date": "2026-06-01T00:00:00", "description": "исходное"}).json()
        tid = created["id"]

        updated = client.put(f"/api/transactions/{tid}", json={
            "amount": 1500, "description": "исправлено"})
        assert updated.status_code == 200
        body = updated.json()
        assert body["amount"] == 1500
        assert body["description"] == "исправлено"
        # Не переданные поля не трогает (partial update)
        assert body["category"] == "Продукты"
        assert body["type"] == "expense"

    def test_update_missing_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/transactions/999999", json={"description": "x"})
        assert r.status_code == 404

    def test_update_ignores_service_fields(self, client: TestClient) -> None:
        """mcc/currency сознательно не выведены в форму (владелец: служебные поля импорта,
        продукт рублёвый) — схема их даже не принимает, лишние поля молча игнорируются."""
        created = client.post("/api/transactions", json={
            "amount": 1000, "category": "Продукты", "type": "expense",
            "date": "2026-06-01T00:00:00"}).json()
        assert created["mcc"] is None
        updated = client.put(f"/api/transactions/{created['id']}", json={
            "mcc": "5411", "currency": "USD", "description": "проверка"})
        assert updated.status_code == 200
        body = updated.json()
        assert body["mcc"] is None
        assert body["description"] == "проверка"


class TestGoalsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/goals", json={
            "name": "Отпуск", "target_amount": 200000, "current_amount": 50000,
            "deadline": "2027-01-01T00:00:00", "category": "emotional"})
        assert created.status_code == 201
        gid = created.json()["id"]
        assert any(g["id"] == gid for g in client.get("/api/goals").json())

        assert client.delete(f"/api/goals/{gid}").status_code in (200, 204)
        assert all(g["id"] != gid for g in client.get("/api/goals").json())

    def test_category_weights_accepted(self, client: TestClient) -> None:
        for cat in ["income_growth", "safety", "material", "emotional"]:
            r = client.post("/api/goals", json={
                "name": f"Цель {cat}", "target_amount": 100000, "current_amount": 0,
                "deadline": "2027-01-01T00:00:00", "category": cat})
            assert r.status_code == 201

    def test_update_changes_fields(self, client: TestClient) -> None:
        created = client.post("/api/goals", json={
            "name": "Отпуск", "target_amount": 200000, "current_amount": 50000,
            "deadline": "2027-01-01T00:00:00", "category": "emotional"}).json()
        gid = created["id"]

        updated = client.put(f"/api/goals/{gid}", json={
            "name": "Отпуск (перенесён)", "target_amount": 250000})
        assert updated.status_code == 200
        body = updated.json()
        assert body["name"] == "Отпуск (перенесён)"
        assert body["target_amount"] == 250000
        # Не переданные поля не трогает (partial update)
        assert body["category"] == "emotional"

    def test_update_missing_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/goals/999999", json={"name": "x"})
        assert r.status_code == 404

    def test_update_ignores_current_amount(self, client: TestClient) -> None:
        """Владелец: не общий edit для прогресса — схема PUT даже не принимает
        current_amount, менять его можно только через POST /contributions."""
        created = client.post("/api/goals", json={
            "name": "Отпуск", "target_amount": 200000, "current_amount": 50000,
            "deadline": "2027-01-01T00:00:00", "category": "emotional"}).json()
        updated = client.put(f"/api/goals/{created['id']}", json={"current_amount": 999999})
        assert updated.status_code == 200
        assert updated.json()["current_amount"] == 50000


class TestGoalContributions:
    def _mk_goal(self, client: TestClient, **overrides) -> dict:
        payload = {
            "name": "Отпуск", "target_amount": 200000, "current_amount": 50000,
            "deadline": "2027-01-01T00:00:00", "category": "emotional",
        }
        payload.update(overrides)
        return client.post("/api/goals", json=payload).json()

    def test_contribution_increases_current_amount(self, client: TestClient) -> None:
        goal = self._mk_goal(client)
        r = client.post(f"/api/goals/{goal['id']}/contributions", json={"amount": 10000})
        assert r.status_code == 200
        assert r.json()["current_amount"] == 60000  # прибавляет, не перезаписывает

        r2 = client.post(f"/api/goals/{goal['id']}/contributions", json={"amount": 5000})
        assert r2.status_code == 200
        assert r2.json()["current_amount"] == 65000

    def test_contribution_missing_goal_404(self, client: TestClient) -> None:
        r = client.post("/api/goals/999999/contributions", json={"amount": 1000})
        assert r.status_code == 404

    def test_contribution_rejects_non_positive_amount(self, client: TestClient) -> None:
        goal = self._mk_goal(client)
        r = client.post(f"/api/goals/{goal['id']}/contributions", json={"amount": 0})
        assert r.status_code == 422

    def test_contribution_rejected_for_linked_asset_goal(self, client: TestClient) -> None:
        asset = client.post("/api/liquid-assets", json={
            "name": "Вклад на отпуск", "amount": 50000, "interest_rate": 0.1,
            "type": "deposit"}).json()
        goal = self._mk_goal(client, linked_asset_id=asset["id"])
        r = client.post(f"/api/goals/{goal['id']}/contributions", json={"amount": 10000})
        assert r.status_code == 409


class TestObligationsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/obligations", json={
            "name": "Кредит", "amount": 300000, "term": 24,
            "monthly_payment": 15000, "interest_rate": 0.15})
        assert created.status_code == 201
        oid = created.json()["id"]
        assert any(o["id"] == oid for o in client.get("/api/obligations").json())

        assert client.delete(f"/api/obligations/{oid}").status_code in (200, 204)

    def test_update_changes_fields(self, client: TestClient) -> None:
        created = client.post("/api/obligations", json={
            "name": "Кредит", "amount": 300000, "term": 24,
            "monthly_payment": 15000, "interest_rate": 0.15}).json()
        oid = created["id"]

        updated = client.put(f"/api/obligations/{oid}", json={
            "name": "Кредит (рефинансирован)", "monthly_payment": 12000})
        assert updated.status_code == 200
        body = updated.json()
        assert body["name"] == "Кредит (рефинансирован)"
        assert body["monthly_payment"] == 12000
        # Не переданные поля не трогает (partial update)
        assert body["amount"] == 300000
        assert body["interest_rate"] == 0.15

    def test_update_missing_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/obligations/999999", json={"name": "x"})
        assert r.status_code == 404

    def test_update_rejects_negative_amount(self, client: TestClient) -> None:
        created = client.post("/api/obligations", json={
            "name": "Кредит", "amount": 300000, "term": 24,
            "monthly_payment": 15000, "interest_rate": 0.15}).json()
        r = client.put(f"/api/obligations/{created['id']}", json={"amount": -100})
        assert r.status_code == 422


class TestLiquidAssetsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/liquid-assets", json={
            "name": "Вклад", "amount": 100000, "interest_rate": 0.16, "type": "deposit"})
        assert created.status_code in (200, 201)
        aid = created.json()["id"]
        assert any(a["id"] == aid for a in client.get("/api/liquid-assets").json())

        assert client.delete(f"/api/liquid-assets/{aid}").status_code in (200, 204)

    def test_update_changes_fields(self, client: TestClient) -> None:
        created = client.post("/api/liquid-assets", json={
            "name": "Вклад", "amount": 100000, "interest_rate": 0.16, "type": "deposit"}).json()
        aid = created["id"]

        updated = client.put(f"/api/liquid-assets/{aid}", json={"amount": 150000})
        assert updated.status_code == 200
        body = updated.json()
        assert body["amount"] == 150000
        # Не переданные поля не трогает (partial update)
        assert body["name"] == "Вклад"
        assert body["interest_rate"] == 0.16

    def test_update_missing_returns_404(self, client: TestClient) -> None:
        r = client.put("/api/liquid-assets/999999", json={"amount": 100})
        assert r.status_code == 404


class TestValidation:
    def test_wrong_type_rejected(self, client: TestClient) -> None:
        # Pydantic валидирует типы: сумма строкой → 422
        r = client.post("/api/goals", json={
            "name": "Плохая", "target_amount": "не число", "current_amount": 0,
            "deadline": "2027-01-01T00:00:00", "category": "material"})
        assert r.status_code == 422

    def test_missing_required_field_rejected(self, client: TestClient) -> None:
        r = client.post("/api/transactions", json={"category": "Продукты", "type": "expense"})
        assert r.status_code == 422


class TestTransactionEndpointEdges:
    """Критичные ветки эндпоинтов операций: фильтры экспорта и 404-пути (P2.7-батч)."""

    def _mk(self, client: TestClient, *, date: str, amount: int = 1000) -> int:
        r = client.post("/api/transactions", json={
            "amount": amount, "category": "Продукты", "type": "expense", "date": date})
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_export_csv_with_date_filters(self, client: TestClient) -> None:
        self._mk(client, date="2026-01-15T00:00:00")
        self._mk(client, date="2026-06-15T00:00:00")
        self._mk(client, date="2026-12-15T00:00:00")
        resp = client.get("/api/transactions/export.csv?date_from=2026-05-01&date_to=2026-08-01")
        assert resp.status_code == 200
        body = resp.text
        assert "2026-06-15" in body
        assert "2026-01-15" not in body  # отсечено date_from
        assert "2026-12-15" not in body  # отсечено date_to

    def test_delete_missing_transaction_404(self, client: TestClient) -> None:
        assert client.delete("/api/transactions/999999").status_code == 404

    def test_restore_missing_transaction_404(self, client: TestClient) -> None:
        resp = client.post("/api/transactions/999999/restore")
        assert resp.status_code == 404

    def test_delete_then_restore_roundtrip(self, client: TestClient) -> None:
        tid = self._mk(client, date="2026-06-01T00:00:00")
        assert client.delete(f"/api/transactions/{tid}").status_code in (200, 204)
        assert all(t["id"] != tid for t in client.get("/api/transactions").json())
        restored = client.post(f"/api/transactions/{tid}/restore")
        assert restored.status_code in (200, 201)
        assert any(t["id"] == tid for t in client.get("/api/transactions").json())
