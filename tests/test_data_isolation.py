"""Изоляция данных по пользователю (multi-user, 4.0.0).

Пользователь видит и меняет только свои данные; гость (user_id=None) — только
анонимные. Чужие строки не читаются и не удаляются по id.
"""
from __future__ import annotations


import pytest

from app.database import crud
from app.database.models import User
from app.utils.time import utcnow


@pytest.fixture(autouse=True)
def _seed_users(db_session):
    """Тесты используют синтетические user_id; на PostgreSQL FK требует реальных
    строк в users. Создаём их, чтобы проверять именно логику изоляции, а не FK."""
    for uid in ("user-a", "user-b"):
        if db_session.get(User, uid) is None:
            db_session.add(User(id=uid, email=f"{uid}@test.io", password_hash="x"))
    db_session.commit()


def _txn(db, user_id, amount=100.0):
    return crud.create_transaction(
        db, amount=amount, type="expense", date=utcnow(),
        category="Еда", user_id=user_id,
    )


class TestReadIsolation:
    def test_user_sees_only_own_transactions(self, db_session):
        _txn(db_session, "user-a", 10)
        _txn(db_session, "user-b", 20)
        _txn(db_session, None, 30)

        a = crud.get_transactions(db_session, user_id="user-a")
        assert len(a) == 1 and a[0].amount == 10

    def test_guest_sees_only_anonymous(self, db_session):
        _txn(db_session, "user-a", 10)
        _txn(db_session, None, 30)

        guest = crud.get_transactions(db_session, user_id=None)
        assert all(t.user_id is None for t in guest)
        assert len(guest) == 1

    def test_budgets_scoped_by_user(self, db_session):
        crud.create_budget(db_session, category="Еда", limit_amount=5000, user_id="user-a")
        crud.create_budget(db_session, category="Авто", limit_amount=3000, user_id="user-b")

        a = crud.get_budgets(db_session, user_id="user-a")
        assert len(a) == 1 and a[0].category == "Еда"

    def test_spending_scoped_by_user(self, db_session):
        _txn(db_session, "user-a", 100)
        _txn(db_session, "user-b", 999)

        spend = crud.get_spending_by_category(db_session, user_id="user-a")
        assert spend["total_expense"] == 100.0


class TestDeleteOwnership:
    def test_user_cannot_delete_foreign_transaction(self, db_session):
        t = _txn(db_session, "user-b", 50)
        # user-a пытается удалить транзакцию user-b
        result = crud.delete_transaction(db_session, t.id, user_id="user-a")
        assert result is None
        # запись жива
        assert crud.get_transactions(db_session, user_id="user-b")[0].is_deleted is False

    def test_user_can_delete_own_transaction(self, db_session):
        t = _txn(db_session, "user-a", 50)
        result = crud.delete_transaction(db_session, t.id, user_id="user-a")
        assert result is not None and result.is_deleted is True

    def test_guest_cannot_delete_user_obligation(self, db_session):
        ob = crud.create_obligation(
            db_session, name="Кредит", amount=100000, interest_rate=0.2,
            term=12, monthly_payment=9000, payment_day=5, user_id="user-a",
        )
        assert crud.delete_obligation(db_session, ob.id, user_id=None) is None

    def test_user_cannot_delete_foreign_goal(self, db_session):
        g = crud.create_goal(
            db_session, name="Отпуск", target_amount=100000, current_amount=0,
            deadline=utcnow(), user_id="user-b",
        )
        assert crud.delete_goal(db_session, g.id, user_id="user-a") is None

    def test_user_cannot_delete_foreign_asset(self, db_session):
        a = crud.create_liquid_asset(db_session, name="Вклад", amount=50000, user_id="user-b")
        assert crud.delete_liquid_asset(db_session, a.id, user_id="user-a") is None
