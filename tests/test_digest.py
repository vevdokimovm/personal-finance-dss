"""Периодический дайджест (хвост P2.5).

Месячная сводка доходов/расходов/целей одним письмом. Чистая агрегация + интеграция
в рассылку уведомлений с дедупликацией (один дайджест на месяц).
"""
from __future__ import annotations

from datetime import datetime

from app.database import crud
from app.database.models import NotificationLog
from app.services.notifications import build_monthly_digest, run_user_notifications


def _user(db, email="digest@test.io"):
    return crud.create_user(db, email=email, password_hash="hashed")


class TestBuildDigest:
    def test_aggregates_month(self, db_session) -> None:
        db = db_session
        crud.create_transaction(db, amount=100000, type="income", date=datetime(2026, 5, 10))
        crud.create_transaction(db, amount=30000, type="expense", date=datetime(2026, 5, 12),
                                category="Продукты")
        crud.create_transaction(db, amount=20000, type="expense", date=datetime(2026, 5, 20),
                                category="Кафе и рестораны")
        digest = build_monthly_digest(db, user_id=None, year_month="2026-05")
        assert digest["income"] == 100000
        assert digest["expense"] == 50000
        assert digest["net"] == 50000
        assert digest["transactions"] == 3

    def test_top_expense_category(self, db_session) -> None:
        db = db_session
        crud.create_transaction(db, amount=5000, type="expense", date=datetime(2026, 5, 1),
                                category="Продукты")
        crud.create_transaction(db, amount=9000, type="expense", date=datetime(2026, 5, 2),
                                category="Кафе и рестораны")
        digest = build_monthly_digest(db, user_id=None, year_month="2026-05")
        assert digest["top_expense_category"] == "Кафе и рестораны"

    def test_excludes_other_months(self, db_session) -> None:
        db = db_session
        crud.create_transaction(db, amount=99999, type="income", date=datetime(2026, 4, 10))
        digest = build_monthly_digest(db, user_id=None, year_month="2026-05")
        assert digest["income"] == 0
        assert digest["transactions"] == 0


class TestDigestInRun:
    def test_digest_sent_and_dedups(self, db_session) -> None:
        db = db_session
        u = _user(db, email="digestrun@test.io")
        # операция в прошлом месяце — чтобы дайджесту было что показать
        now = datetime.utcnow()
        prev = (now.replace(day=1) - __import__("datetime").timedelta(days=1))
        crud.create_transaction(db, amount=50000, type="income", date=prev, user_id=u.id)

        first = run_user_notifications(db, u)
        assert first.get("digest") == 1

        second = run_user_notifications(db, u)
        assert second.get("digest") == 0  # дедуп

        logged = db.query(NotificationLog).filter(
            NotificationLog.user_id == u.id, NotificationLog.notification_type == "digest"
        ).count()
        assert logged == 1
