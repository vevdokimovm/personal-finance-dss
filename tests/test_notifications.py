"""Email-уведомления (P2.5): условия и дедупликация.

Проверяет чистую логику определения «о чём уведомить» и защиту от повторной отправки
(NotificationLog). Сама отправка через EmailService — no-op без SMTP-конфига.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.database import crud
from app.database.models import NotificationLog
from app.services.notifications import (
    budgets_over,
    goals_near_deadline,
    record_notification,
    run_user_notifications,
    was_notified,
)


def _user(db, email="notify@test.io"):
    return crud.create_user(db, email=email, password_hash="hashed")


def _goal(db, days_from_now: int, name="Цель", user_id=None):
    return crud.create_goal(
        db, name=name, target_amount=100000, current_amount=10000,
        deadline=datetime.utcnow() + timedelta(days=days_from_now), user_id=user_id,
    )


class TestGoalDeadlines:
    def test_near_deadline_included(self, db_session) -> None:
        _goal(db_session, days_from_now=5)
        near = goals_near_deadline(db_session, user_id=None, within_days=7)
        assert len(near) == 1

    def test_far_deadline_excluded(self, db_session) -> None:
        _goal(db_session, days_from_now=60)
        assert goals_near_deadline(db_session, user_id=None, within_days=7) == []

    def test_achieved_goal_excluded(self, db_session) -> None:
        g = _goal(db_session, days_from_now=3)
        crud.achieve_goal(db_session, g.id)  # is_active=False
        assert goals_near_deadline(db_session, user_id=None, within_days=7) == []


class TestBudgetOverruns:
    def test_over_budget_detected(self, db_session) -> None:
        db = db_session
        crud.create_budget(db, category="Кафе и рестораны", limit_amount=1000, user_id=None)
        crud.create_transaction(db, amount=1500, type="expense", date=datetime.utcnow(),
                                category="Кафе и рестораны")
        over = budgets_over(db, user_id=None)
        assert any(b["category"] == "Кафе и рестораны" for b in over)

    def test_within_budget_not_flagged(self, db_session) -> None:
        db = db_session
        crud.create_budget(db, category="Развлечения", limit_amount=5000, user_id=None)
        crud.create_transaction(db, amount=1000, type="expense", date=datetime.utcnow(),
                                category="Развлечения")
        assert budgets_over(db, user_id=None) == []


class TestDeduplication:
    def test_was_notified_after_record(self, db_session) -> None:
        u = _user(db_session)
        key = "budget_overrun:Кафе:2026-06"
        assert was_notified(db_session, u.id, key) is False
        record_notification(db_session, u.id, "budget_overrun", key)
        assert was_notified(db_session, u.id, key) is True


class TestRunUserNotifications:
    def test_run_sends_and_dedups(self, db_session) -> None:
        db = db_session
        u = _user(db, email="run@test.io")
        _goal(db, days_from_now=4, user_id=u.id)

        first = run_user_notifications(db, u)
        assert first["goal_deadline"] == 1

        # повторный прогон в том же месяце — дедуп, ничего не шлём
        second = run_user_notifications(db, u)
        assert second["goal_deadline"] == 0

        logged = db.query(NotificationLog).filter(NotificationLog.user_id == u.id).count()
        assert logged == 1


class TestRunEndpoint:
    def test_run_endpoint_returns_totals(self, client) -> None:
        r = client.post("/api/notifications/run")
        assert r.status_code == 200
        assert "users" in r.json()
