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


class TestObligationsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/obligations", json={
            "name": "Кредит", "amount": 300000, "term": 24,
            "monthly_payment": 15000, "interest_rate": 0.15})
        assert created.status_code == 201
        oid = created.json()["id"]
        assert any(o["id"] == oid for o in client.get("/api/obligations").json())

        assert client.delete(f"/api/obligations/{oid}").status_code in (200, 204)


class TestLiquidAssetsCRUD:
    def test_create_list_delete(self, client: TestClient) -> None:
        created = client.post("/api/liquid-assets", json={
            "name": "Вклад", "amount": 100000, "interest_rate": 0.16, "type": "deposit"})
        assert created.status_code in (200, 201)
        aid = created.json()["id"]
        assert any(a["id"] == aid for a in client.get("/api/liquid-assets").json())

        assert client.delete(f"/api/liquid-assets/{aid}").status_code in (200, 204)


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
