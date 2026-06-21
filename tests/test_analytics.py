"""Продуктовая аналитика на событийном логе (P3.4)."""
from __future__ import annotations

from datetime import datetime

from app.database.models import Event
from app.services.analytics import active_users, analytics_overview, event_counts, funnel


def _event(db, etype: str, user_id: str | None = None) -> None:
    db.add(Event(event_type=etype, user_id=user_id, created_at=datetime.utcnow()))
    db.commit()


class TestEventCounts:
    def test_counts_by_type(self, db_session) -> None:
        db = db_session
        _event(db, "login_success", "u1")
        _event(db, "login_success", "u2")
        _event(db, "goal_created", "u1")
        counts = event_counts(db)
        assert counts["login_success"] == 2
        assert counts["goal_created"] == 1


class TestActiveUsers:
    def test_unique_users(self, db_session) -> None:
        db = db_session
        _event(db, "login_success", "u1")
        _event(db, "goal_created", "u1")  # тот же юзер
        _event(db, "login_success", "u2")
        _event(db, "login_success", None)  # гость не считается
        assert active_users(db) == 2


class TestFunnel:
    def test_strict_completion(self, db_session) -> None:
        db = db_session
        # u1 прошёл оба шага, u2 только первый
        _event(db, "login_success", "u1")
        _event(db, "goal_created", "u1")
        _event(db, "login_success", "u2")
        steps = funnel(db, ["login_success", "goal_created"])
        assert steps[0]["users"] == 2
        assert steps[0]["conversion_pct"] == 100.0
        assert steps[1]["users"] == 1  # только u1 прошёл оба
        assert steps[1]["conversion_pct"] == 50.0

    def test_empty_funnel_no_division_error(self, db_session) -> None:
        steps = funnel(db_session, ["nonexistent_step"])
        assert steps[0]["users"] == 0
        assert steps[0]["conversion_pct"] == 0.0


class TestOverview:
    def test_overview_structure(self, db_session) -> None:
        db = db_session
        _event(db, "login_success", "u1")
        overview = analytics_overview(db, days=30)
        assert overview["total_events"] >= 1
        assert overview["active_users"] >= 1
        assert "event_counts" in overview


class TestAnalyticsEndpoints:
    def test_overview_endpoint(self, client) -> None:
        r = client.get("/api/analytics/overview?days=30")
        assert r.status_code == 200
        assert "event_counts" in r.json()

    def test_funnel_endpoint_default(self, client) -> None:
        r = client.get("/api/analytics/funnel")
        assert r.status_code == 200
        assert isinstance(r.json()["steps"], list)


class TestAdminGuard:
    def test_dev_open_without_key(self, client) -> None:
        # ADMIN_API_KEY пуст + dev-режим → аналитика открыта
        r = client.get("/api/analytics/overview")
        assert r.status_code == 200

    def test_key_required_when_configured(self, client, monkeypatch) -> None:
        from app.config import settings
        monkeypatch.setattr(settings, "ADMIN_API_KEY", "test-admin-key-1234567890")

        assert client.get("/api/analytics/overview").status_code == 403
        assert client.get("/api/analytics/overview",
                          headers={"X-Admin-Key": "wrong"}).status_code == 403
        ok = client.get("/api/analytics/overview",
                        headers={"X-Admin-Key": "test-admin-key-1234567890"})
        assert ok.status_code == 200


class TestProductionRequiresAdminKey:
    def test_validate_flags_missing_admin_key(self, monkeypatch) -> None:
        from app.config import Settings, validate_production_security
        s = Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a-strong-production-secret-key-32chars-long",
            COOKIE_SECURE=True,
            ADMIN_API_KEY="",
        )
        problems = validate_production_security(s)
        assert any("ADMIN_API_KEY" in p for p in problems)
