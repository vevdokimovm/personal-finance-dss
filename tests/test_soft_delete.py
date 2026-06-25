"""Гард мягкого удаления и восстановления (P1.7).

Транзакции уже имели soft-delete (BUG-03); здесь фиксируется симметричное поведение
для обязательств, целей и ликвидных активов:
  - delete помечает запись (is_deleted=True) и убирает её из выборок get_*, но строка
    физически остаётся (дочерняя история сохранена для восстановления);
  - restore возвращает запись в выборки;
  - чужой пользователь не может ни удалить, ни восстановить запись (изоляция данных).
Плюс end-to-end проверка REST-эндпоинтов undo на примере обязательства.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import crud
from app.database.models import User


def _user(db, uid: str) -> str:
    db.add(User(id=uid, email=f"{uid}@test.io", password_hash="x"))
    db.commit()
    return uid


def _mk_obligation(db, uid):
    return crud.create_obligation(
        db, name="O", amount=5000.0, interest_rate=0.1, term=12,
        monthly_payment=500.0, payment_day=1, user_id=uid,
    )


def _mk_goal(db, uid):
    return crud.create_goal(
        db, name="G", target_amount=1000.0, current_amount=0.0,
        deadline=datetime.utcnow() + timedelta(days=30), user_id=uid,
    )


def _mk_asset(db, uid):
    return crud.create_liquid_asset(
        db, name="Депозит", amount=10000.0, interest_rate=0.16,
        type="deposit", user_id=uid,
    )


def test_obligation_soft_delete_and_restore(db_session) -> None:
    uid = _user(db_session, "u-o")
    obl = _mk_obligation(db_session, uid)
    assert crud.delete_obligation(db_session, obl.id, user_id=uid).is_deleted is True
    assert obl.id not in [o.id for o in crud.get_obligations(db_session, user_id=uid)]
    assert crud.restore_obligation(db_session, obl.id, user_id=uid).is_deleted is False
    assert obl.id in [o.id for o in crud.get_obligations(db_session, user_id=uid)]


def test_goal_soft_delete_and_restore(db_session) -> None:
    uid = _user(db_session, "u-g")
    goal = _mk_goal(db_session, uid)
    assert crud.delete_goal(db_session, goal.id, user_id=uid).is_deleted is True
    assert goal.id not in [g.id for g in crud.get_goals(db_session, user_id=uid)]
    assert crud.restore_goal(db_session, goal.id, user_id=uid).is_deleted is False
    assert goal.id in [g.id for g in crud.get_goals(db_session, user_id=uid)]


def test_asset_soft_delete_and_restore(db_session) -> None:
    uid = _user(db_session, "u-a")
    asset = _mk_asset(db_session, uid)
    assert crud.delete_liquid_asset(db_session, asset.id, user_id=uid).is_deleted is True
    assert asset.id not in [a.id for a in crud.get_liquid_assets(db_session, user_id=uid)]
    assert crud.restore_liquid_asset(db_session, asset.id, user_id=uid).is_deleted is False
    assert asset.id in [a.id for a in crud.get_liquid_assets(db_session, user_id=uid)]


def test_cross_user_cannot_delete_or_restore(db_session) -> None:
    owner = _user(db_session, "owner")
    _user(db_session, "intruder")
    obl = _mk_obligation(db_session, owner)
    # Чужой не может удалить
    assert crud.delete_obligation(db_session, obl.id, user_id="intruder") is None
    # Владелец удаляет, чужой не может восстановить
    crud.delete_obligation(db_session, obl.id, user_id=owner)
    assert crud.restore_obligation(db_session, obl.id, user_id="intruder") is None
    assert crud.restore_obligation(db_session, obl.id, user_id=owner) is not None


def test_double_delete_is_noop(db_session) -> None:
    uid = _user(db_session, "u-dd")
    obl = _mk_obligation(db_session, uid)
    assert crud.delete_obligation(db_session, obl.id, user_id=uid) is not None
    # Повторное удаление уже удалённого — None (нечего удалять)
    assert crud.delete_obligation(db_session, obl.id, user_id=uid) is None


def test_obligation_delete_restore_via_api(client: TestClient) -> None:
    created = client.post("/api/obligations", json={
        "name": "Кредит", "amount": 100000, "monthly_payment": 5000,
        "interest_rate": 0.2, "term": 24,
    }).json()
    oid = created["id"]
    assert any(o["id"] == oid for o in client.get("/api/obligations").json())

    assert client.delete(f"/api/obligations/{oid}").status_code == 204
    assert not any(o["id"] == oid for o in client.get("/api/obligations").json())

    restored = client.post(f"/api/obligations/{oid}/restore")
    assert restored.status_code == 200
    assert any(o["id"] == oid for o in client.get("/api/obligations").json())
