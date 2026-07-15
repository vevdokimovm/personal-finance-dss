"""Тесты истории планов (P2.6): CRUD снапшотов + REST-эндпоинты."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.crud import (
    create_plan_snapshot,
    get_plan_snapshot,
    get_plan_snapshots,
    soft_delete_plan_snapshot,
)

_RESULT = {
    "risk_profile": "3 Сбалансированный",
    "indicators": {"Rt": 39500, "Lt": 0.405, "Dt": 0.347, "BLR": 1.2},
    "top3": [
        {"name": "Всё в резерв", "x_obligations": 0, "x_reserve": 39500, "x_goals": 0, "utility": 0.805},  # noqa: E501
        {"name": "Долг+резерв", "x_obligations": 10000,
            "x_reserve": 29500, "x_goals": 0, "utility": 0.78},
    ],
}


def _load_anna(client: TestClient) -> None:
    client.post("/api/demo/load?case=anna")


class TestCrud:
    def test_create_stores_summary_and_top3(self, db_session):
        snap = create_plan_snapshot(db_session, _RESULT, user_id=None, note="тест")
        assert snap.id is not None
        assert snap.risk_profile == "3 Сбалансированный"
        assert snap.rt == 39500.0
        assert snap.best_name == "Всё в резерв"
        assert snap.note == "тест"
        assert snap.top3[0]["name"] == "Всё в резерв"

    def test_get_returns_snapshot(self, db_session):
        snap = create_plan_snapshot(db_session, _RESULT)
        got = get_plan_snapshot(db_session, snap.id)
        assert got is not None and got.id == snap.id

    def test_list_newest_first(self, db_session):
        a = create_plan_snapshot(db_session, _RESULT)
        b = create_plan_snapshot(db_session, _RESULT)
        ids = [s.id for s in get_plan_snapshots(db_session)]
        assert ids[:2] == [b.id, a.id]

    def test_soft_delete_excludes_from_queries(self, db_session):
        snap = create_plan_snapshot(db_session, _RESULT)
        assert soft_delete_plan_snapshot(db_session, snap.id) is True
        assert get_plan_snapshot(db_session, snap.id) is None
        assert all(s.id != snap.id for s in get_plan_snapshots(db_session))

    def test_soft_delete_missing_returns_false(self, db_session):
        assert soft_delete_plan_snapshot(db_session, 999999) is False

    def test_empty_result_does_not_crash(self, db_session):
        snap = create_plan_snapshot(db_session, {})
        assert snap.id is not None
        assert snap.best_name == ""


class TestEndpoints:
    def test_save_returns_detail(self, client):
        _load_anna(client)
        r = client.post("/api/planning/history", json={"risk_tolerance": 3, "note": "мой план"})
        assert r.status_code == 200
        body = r.json()
        assert "id" in body
        assert body["note"] == "мой план"
        assert "indicators" in body and "top3" in body and "best" in body

    def test_list_after_save(self, client):
        _load_anna(client)
        client.post("/api/planning/history", json={"risk_tolerance": 3})
        lst = client.get("/api/planning/history")
        assert lst.status_code == 200
        assert lst.json()["count"] >= 1

    def test_get_detail(self, client):
        _load_anna(client)
        sid = client.post("/api/planning/history", json={"risk_tolerance": 3}).json()["id"]
        r = client.get(f"/api/planning/history/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_delete_then_404(self, client):
        _load_anna(client)
        sid = client.post("/api/planning/history", json={"risk_tolerance": 3}).json()["id"]
        assert client.delete(f"/api/planning/history/{sid}").status_code == 200
        assert client.get(f"/api/planning/history/{sid}").status_code == 404

    def test_get_missing_returns_404(self, client):
        assert client.get("/api/planning/history/999999").status_code == 404
