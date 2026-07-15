"""Покрытие CRUD-операций состояния (P2.4).

Закрывают непокрытые ветки: мягкое удаление/восстановление транзакций, закрытие
обязательств, достижение целей, обновление профиля, верификация email, удаление
пользователя, усыновление осиротевших (гостевых) строк при регистрации.
"""
from __future__ import annotations

from datetime import datetime

from app.database import crud


def _user(db, email: str = "u@test.io"):
    return crud.create_user(db, email=email, password_hash="hashed")


class TestTransactionLifecycle:
    def test_delete_and_restore(self, db_session) -> None:
        db = db_session
        tx = crud.create_transaction(db, amount=1000, type="expense", date=datetime(2026, 6, 1))
        deleted = crud.delete_transaction(db, tx.id, user_id=None)
        assert deleted is not None and deleted.is_deleted is True

        restored = crud.restore_transaction(db, tx.id)
        assert restored is not None and restored.is_deleted is False
        assert restored.deleted_at is None

    def test_restore_nonexistent_returns_none(self, db_session) -> None:
        assert crud.restore_transaction(db_session, 999999) is None

    def test_restore_not_deleted_returns_none(self, db_session) -> None:
        tx = crud.create_transaction(db_session, amount=500,
                                     type="income", date=datetime(2026, 6, 1))
        assert crud.restore_transaction(db_session, tx.id) is None

    def test_delete_wrong_owner_returns_none(self, db_session) -> None:
        tx = crud.create_transaction(db_session, amount=500,
                                     type="income", date=datetime(2026, 6, 1))
        assert crud.delete_transaction(db_session, tx.id, user_id="someone-else") is None


class TestObligationGoalState:
    def test_close_obligation(self, db_session) -> None:
        ob = crud.create_obligation(
            db_session, name="Кредит", amount=100000, interest_rate=0.15,
            term=12, monthly_payment=9000, payment_day=10,
        )
        closed = crud.close_obligation(db_session, ob.id)
        assert closed is not None and closed.is_active is False
        assert closed.closed_at is not None

    def test_close_nonexistent_obligation(self, db_session) -> None:
        assert crud.close_obligation(db_session, 999999) is None

    def test_achieve_goal(self, db_session) -> None:
        g = crud.create_goal(db_session, name="Цель", target_amount=50000,
                             current_amount=0, deadline=datetime(2027, 1, 1))
        achieved = crud.achieve_goal(db_session, g.id)
        assert achieved is not None and achieved.is_active is False
        assert achieved.achieved_at is not None

    def test_achieve_nonexistent_goal(self, db_session) -> None:
        assert crud.achieve_goal(db_session, 999999) is None


class TestUserProfileOps:
    def test_update_profile(self, db_session) -> None:
        u = _user(db_session)
        updated = crud.update_user_profile(db_session, u.id, display_name="Новое Имя")
        assert updated is not None and updated.display_name == "Новое Имя"

    def test_update_profile_blank_clears(self, db_session) -> None:
        u = _user(db_session, email="blank@test.io")
        updated = crud.update_user_profile(db_session, u.id, display_name="   ")
        assert updated is not None and updated.display_name is None

    def test_update_profile_nonexistent(self, db_session) -> None:
        assert crud.update_user_profile(db_session, "no-such-id", display_name="X") is None

    def test_mark_email_verified(self, db_session) -> None:
        u = _user(db_session, email="verify@test.io")
        verified = crud.mark_email_verified(db_session, u.id)
        assert verified is not None and verified.email_verified is True

    def test_mark_email_verified_nonexistent(self, db_session) -> None:
        assert crud.mark_email_verified(db_session, "no-id") is None

    def test_delete_user_twice(self, db_session) -> None:
        u = _user(db_session, email="del@test.io")
        assert crud.delete_user(db_session, u.id) is True
        assert crud.delete_user(db_session, u.id) is False  # уже удалён


class TestAdoptOrphanRows:
    def test_adopt_guest_rows(self, db_session) -> None:
        db = db_session
        # гостевые строки (user_id IS NULL)
        crud.create_transaction(db, amount=1000, type="expense", date=datetime(2026, 6, 1))
        crud.create_goal(db, name="Гостевая цель", target_amount=10000,
                         current_amount=0, deadline=datetime(2027, 1, 1))
        u = _user(db, email="adopt@test.io")

        affected = crud.adopt_orphan_rows(db, u.id)
        assert affected >= 2
