"""Целостность удаления (P1.2 / PostgreSQL).

На SQLite внешние ключи по умолчанию не форсятся, поэтому удаление родителя с
дочерними строками проходит молча. На PostgreSQL FK реальны — удаление цели/
обязательства с историей падает, если историю не удалить заранее. Здесь же
проверяется, что удаление аккаунта вычищает все ПДн пользователя (152-ФЗ).
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import text

from app.database import crud
from app.database.models import Event, GoalContribution, ObligationPayment, Recommendation, User
from app.utils.time import utcnow


def _user(db, uid="u-del"):
    db.add(User(id=uid, email=f"{uid}@test.io", password_hash="x"))
    db.commit()
    return uid


def test_delete_goal_is_soft_and_keeps_contributions(db_session) -> None:
    uid = _user(db_session, "u-goal")
    goal = crud.create_goal(
        db_session, name="G", target_amount=1000.0, current_amount=0.0,
        deadline=utcnow() + timedelta(days=30), user_id=uid,
    )
    crud.record_goal_contribution(db_session, goal.id, amount=100.0)
    # P1.7: мягкое удаление — запись помечается, история взносов сохраняется для restore.
    result = crud.delete_goal(db_session, goal.id, user_id=uid)
    assert result is not None
    assert result.is_deleted is True
    assert goal.id not in [g.id for g in crud.get_goals(db_session, user_id=uid)]
    kept = db_session.query(GoalContribution).filter(GoalContribution.goal_id == goal.id).count()
    assert kept == 1
    # restore возвращает цель в выборку
    restored = crud.restore_goal(db_session, goal.id, user_id=uid)
    assert restored is not None and restored.is_deleted is False
    assert goal.id in [g.id for g in crud.get_goals(db_session, user_id=uid)]


def test_delete_obligation_is_soft_and_keeps_payments(db_session) -> None:
    uid = _user(db_session, "u-obl")
    obl = crud.create_obligation(
        db_session, name="O", amount=5000.0, interest_rate=0.1, term=12,
        monthly_payment=500.0, payment_day=1, user_id=uid,
    )
    crud.record_obligation_payment(db_session, obl.id, amount=500.0)
    result = crud.delete_obligation(db_session, obl.id, user_id=uid)
    assert result is not None
    assert result.is_deleted is True
    assert obl.id not in [o.id for o in crud.get_obligations(db_session, user_id=uid)]
    kept = db_session.query(ObligationPayment).filter(
        ObligationPayment.obligation_id == obl.id
    ).count()
    assert kept == 1


def test_delete_user_purges_all_personal_data(db_session) -> None:
    uid = _user(db_session, "u-full")
    goal = crud.create_goal(
        db_session, name="G", target_amount=1000.0, current_amount=0.0,
        deadline=utcnow() + timedelta(days=30), user_id=uid,
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


class TestForeignKeysAreEnforcedDuringDeletion:
    """🔴 Удаление аккаунта проверяется с ВКЛЮЧЁННЫМИ внешними ключами.

    Шапка этого файла честно предупреждает: «на SQLite внешние ключи по умолчанию
    не форсятся, поэтому удаление родителя с дочерними строками проходит молча».
    Предупреждение стояло — а проверка нет, и `PRAGMA foreign_keys` нигде не включался.

    🔴 **Чего это стоило.** `delete_user` не удаляет пять таблиц с настоящим FK
    на `users.id`: снимки планов, правила категоризации, события совета, членства
    в семьях и токены банков. На SQLite это невидимо; на PostgreSQL (а прод только
    на нём — SQLite запрещён старт-гардом) `DELETE /api/auth/me` отдал бы **500**
    каждому, кто хоть раз сохранил снимок плана, переназначил категорию операции
    или состоит в семье. Это активный пользователь, не краевой случай.

    Право на удаление по 152-ФЗ не исполнялось бы вовсе, и отказ выглядел бы
    как поломка сервера. Отдельно: `PlanSnapshot` — тот самый объект, который
    комментарий в коде называет самым чувствительным (Rt/Lt/Dt/BLR и top3 целиком), —
    из каскада выпал.

    Найдено седьмым проходом независимого аудита 08.09.2026.

    ## Почему проверка именно такая

    Включаем `PRAGMA foreign_keys=ON` на время теста — это делает SQLite достаточно
    строгим, чтобы поведение совпало с боевой БД. Проверять «глазами по списку
    моделей» бессмысленно: список и есть то, что разошлось.
    """

    @pytest.fixture()
    def strict_fk(self, db_session):
        """SQLite с включённой проверкой внешних ключей — как PostgreSQL."""
        db_session.execute(text("PRAGMA foreign_keys=ON"))
        yield db_session
        db_session.execute(text("PRAGMA foreign_keys=OFF"))

    def test_deletion_succeeds_with_plan_snapshot(self, client, strict_fk) -> None:
        """🔴 Мутация «убрать PlanSnapshot из каскада» роняет тест здесь."""
        from app.database.crud import delete_user
        from app.database.models import PlanSnapshot, User

        client.post("/api/auth/register", json={
            "email": "fk-snapshot@test.io", "password": "verysecret1", "consent": True})
        user = strict_fk.query(User).filter(User.email == "fk-snapshot@test.io").one()
        strict_fk.add(PlanSnapshot(user_id=user.id, risk_profile="balanced"))
        strict_fk.commit()

        assert delete_user(strict_fk, user.id) is True
        assert strict_fk.query(PlanSnapshot).filter(
            PlanSnapshot.user_id == user.id).count() == 0

    def test_deletion_succeeds_with_category_rule(self, client, strict_fk) -> None:
        from app.database.crud import delete_user
        from app.database.models import User, UserCategoryRule

        client.post("/api/auth/register", json={
            "email": "fk-rule@test.io", "password": "verysecret1", "consent": True})
        user = strict_fk.query(User).filter(User.email == "fk-rule@test.io").one()
        strict_fk.add(UserCategoryRule(
            user_id=user.id, match_token="кофе", category="Еда"))
        strict_fk.commit()

        assert delete_user(strict_fk, user.id) is True
        assert strict_fk.query(UserCategoryRule).filter(
            UserCategoryRule.user_id == user.id).count() == 0

    def test_deletion_succeeds_for_household_member(self, client, strict_fk) -> None:
        """Членство в семье — тоже FK, и тоже валило бы удаление."""
        from app.database.crud import delete_user
        from app.database.models import Household, HouseholdMembership, User

        client.post("/api/auth/register", json={
            "email": "fk-household@test.io", "password": "verysecret1", "consent": True})
        user = strict_fk.query(User).filter(User.email == "fk-household@test.io").one()
        household = Household(name="Семья", owner_id=user.id)
        strict_fk.add(household)
        strict_fk.flush()
        strict_fk.add(HouseholdMembership(
            household_id=household.id, user_id=user.id, role="owner"))
        strict_fk.commit()

        assert delete_user(strict_fk, user.id) is True
        assert strict_fk.query(HouseholdMembership).filter(
            HouseholdMembership.user_id == user.id).count() == 0


class TestDeletingOwnerDoesNotOrphanOthersData:
    """🔴 Удаление владельца семьи не оставляет чужие записи с битой ссылкой.

    `delete_household` возвращает общие строки авторам (`household_id → NULL`)
    и объясняет почему: «данные не теряются и не повисают обезличенными (152-ФЗ)»,
    и обнуление делается ЯВНО, потому что на SQLite `ON DELETE SET NULL` не форсится.

    Каскад удаления аккаунта, достроенный часом раньше, удалял семью **напрямую** —
    мимо этой логики. Записи других участников, положенные в общий котёл, сохраняли
    `household_id` уже несуществующей семьи: на PostgreSQL это либо блокирует удаление,
    либо оставляет висячую ссылку, а для владельца записи — данные, пропавшие
    из его списка без всякого его действия.

    Найдено разбором собственной правки, до сдачи батча.
    """

    @pytest.fixture()
    def strict_fk(self, db_session):
        db_session.execute(text("PRAGMA foreign_keys=ON"))
        yield db_session
        db_session.execute(text("PRAGMA foreign_keys=OFF"))

    def test_shared_rows_return_to_their_authors(self, client, strict_fk) -> None:
        """🔴 Мутация «удалить семью напрямую» роняет тест здесь."""
        from app.database.crud import delete_user
        from app.database.models import (
            Household,
            HouseholdMembership,
            Transaction,
            User,
        )

        client.post("/api/auth/register", json={
            "email": "owner@test.io", "password": "verysecret1", "consent": True})
        client.post("/api/auth/register", json={
            "email": "member@test.io", "password": "verysecret1", "consent": True})
        owner = strict_fk.query(User).filter(User.email == "owner@test.io").one()
        member = strict_fk.query(User).filter(User.email == "member@test.io").one()

        household = Household(name="Семья", owner_id=owner.id)
        strict_fk.add(household)
        strict_fk.flush()
        for person in (owner, member):
            strict_fk.add(HouseholdMembership(
                household_id=household.id, user_id=person.id, role="member"))
        shared = Transaction(
            user_id=member.id, household_id=household.id,
            amount=1000.0, type="expense", category="Еда", date=utcnow().date(),
        )
        strict_fk.add(shared)
        strict_fk.commit()
        shared_id = shared.id

        assert delete_user(strict_fk, owner.id) is True

        strict_fk.expire_all()
        left = strict_fk.get(Transaction, shared_id)
        assert left is not None, "запись участника исчезла вместе с чужим аккаунтом"
        assert left.user_id == member.id
        assert left.household_id is None, (
            "запись участника осталась привязанной к удалённой семье — "
            "висячая ссылка, и на проде это либо 500, либо пропавшие данные"
        )
