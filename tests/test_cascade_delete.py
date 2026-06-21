"""Целостность удаления (P1.2 / PostgreSQL).

На SQLite внешние ключи по умолчанию не форсятся, поэтому удаление родителя с
дочерними строками проходит молча. На PostgreSQL FK реальны — удаление цели/
обязательства с историей падает, если историю не удалить заранее. Здесь же
проверяется, что удаление аккаунта вычищает все ПДн пользователя (152-ФЗ).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.database import crud
from app.database.models import Event, GoalContribution, ObligationPayment, Recommendation, User


def _user(db, uid="u-del"):
    db.add(User(id=uid, email=f"{uid}@test.io", password_hash="x"))
    db.commit()
    return uid


def test_delete_goal_with_contributions(db_session) -> None:
    uid = _user(db_session, "u-goal")
    goal = crud.create_goal(
        db_session, name="G", target_amount=1000.0, current_amount=0.0,
        deadline=datetime.utcnow() + timedelta(days=30), user_id=uid,
    )
    crud.record_goal_contribution(db_session, goal.id, amount=100.0)
    # На PG это падало бы FK violation без предварительной очистки истории.
    result = crud.delete_goal(db_session, goal.id, user_id=uid)
    assert result is not None
    assert db_session.get(GoalContribution, 1) is None


def test_delete_obligation_with_payments(db_session) -> None:
    uid = _user(db_session, "u-obl")
    obl = crud.create_obligation(
        db_session, name="O", amount=5000.0, interest_rate=0.1, term=12,
        monthly_payment=500.0, payment_day=1, user_id=uid,
    )
    crud.record_obligation_payment(db_session, obl.id, amount=500.0)
    result = crud.delete_obligation(db_session, obl.id, user_id=uid)
    assert result is not None
    assert db_session.query(ObligationPayment).count() == 0


def test_delete_user_purges_all_personal_data(db_session) -> None:
    uid = _user(db_session, "u-full")
    goal = crud.create_goal(
        db_session, name="G", target_amount=1000.0, current_amount=0.0,
        deadline=datetime.utcnow() + timedelta(days=30), user_id=uid,
    )
    crud.record_goal_contribution(db_session, goal.id, amount=100.0)
    obl = crud.create_obligation(
        db_session, name="O", amount=5000.0, interest_rate=0.1, term=12,
        monthly_payment=500.0, payment_day=1, user_id=uid,
    )
    crud.record_obligation_payment(db_session, obl.id, amount=500.0)
    db_session.add(Event(user_id=uid, event_type="test_event"))
    db_session.add(Recommendation(user_id=uid))
    db_session.commit()

    assert crud.delete_user(db_session, uid) is True

    # Ни строки пользователя, ни его истории/аналитики не остаётся.
    assert db_session.get(User, uid) is None
    assert db_session.query(GoalContribution).count() == 0
    assert db_session.query(ObligationPayment).count() == 0
    assert db_session.query(Event).filter(Event.user_id == uid).count() == 0
    assert db_session.query(Recommendation).filter(Recommendation.user_id == uid).count() == 0
