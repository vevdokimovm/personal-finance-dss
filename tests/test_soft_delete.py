"""Гард мягкого удаления и восстановления (P1.7).

Транзакции уже имели soft-delete (BUG-03); здесь фиксируется симметричное поведение
для обязательств, целей, ликвидных активов и бюджетов:
  - delete помечает запись (is_deleted=True) и убирает её из выборок get_*, но строка
    физически остаётся (дочерняя история сохранена для восстановления);
  - restore возвращает запись в выборки;
  - чужой пользователь не может ни удалить, ни восстановить запись (изоляция данных).
Плюс end-to-end проверка REST-эндпоинтов undo на примере обязательства.
"""
from __future__ import annotations

from datetime import timedelta

from fastapi.testclient import TestClient

from app.database import crud
from app.database.models import User
from app.utils.time import utcnow


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
        deadline=utcnow() + timedelta(days=30), user_id=uid,
    )


def _mk_asset(db, uid):
    return crud.create_liquid_asset(
        db, name="Депозит", amount=10000.0, interest_rate=0.16,
        type="deposit", user_id=uid,
    )


def _mk_budget(db, uid, category="Продукты"):
    return crud.create_budget(db, category=category, limit_amount=15000.0, user_id=uid)


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


def test_budget_soft_delete_and_restore(db_session) -> None:
    uid = _user(db_session, "u-b")
    budget = _mk_budget(db_session, uid)
    assert crud.delete_budget(db_session, budget.id, user_id=uid) is True
    assert budget.id not in [b.id for b in crud.get_budgets(db_session, user_id=uid)]
    assert crud.restore_budget(db_session, budget.id, user_id=uid).is_deleted is False
    assert budget.id in [b.id for b in crud.get_budgets(db_session, user_id=uid)]


def test_budget_recreate_after_delete_revives_same_category(db_session) -> None:
    """`create_budget` — упсерт по категории (FR-22): категория глобально уникальна
    (UNIQUE на уровне БД), поэтому после мягкого удаления новый POST той же категории
    обязан ожить, а не упереться в UNIQUE-конфликт со старой удалённой строкой."""
    uid = _user(db_session, "u-b2")
    budget = _mk_budget(db_session, uid, category="Кафе")
    crud.delete_budget(db_session, budget.id, user_id=uid)
    revived = crud.create_budget(db_session, category="Кафе", limit_amount=5000.0, user_id=uid)
    assert revived.id == budget.id
    assert revived.is_deleted is False
    assert revived.limit_amount == 5000.0


def test_obligation_update_partial(db_session) -> None:
    uid = _user(db_session, "u-ou")
    obl = _mk_obligation(db_session, uid)
    updated = crud.update_obligation(db_session, obl.id, user_id=uid, monthly_payment=777.0)
    assert updated is not None
    assert updated.monthly_payment == 777.0
    assert updated.amount == 5000.0  # не переданное поле не тронуто


def test_obligation_update_cross_user_forbidden(db_session) -> None:
    owner = _user(db_session, "owner-ou")
    _user(db_session, "intruder-ou")
    obl = _mk_obligation(db_session, owner)
    assert crud.update_obligation(db_session, obl.id, user_id="intruder-ou", name="X") is None


def test_asset_update_partial(db_session) -> None:
    uid = _user(db_session, "u-au")
    asset = _mk_asset(db_session, uid)
    updated = crud.update_liquid_asset(db_session, asset.id, user_id=uid, amount=20000.0)
    assert updated is not None
    assert updated.amount == 20000.0
    assert float(updated.interest_rate) == 0.16  # не переданное поле не тронуто (Decimal-колонка)


def test_asset_update_cross_user_forbidden(db_session) -> None:
    owner = _user(db_session, "owner-au")
    _user(db_session, "intruder-au")
    asset = _mk_asset(db_session, owner)
    assert crud.update_liquid_asset(db_session, asset.id, user_id="intruder-au", name="X") is None


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


def test_budget_delete_restore_via_api(client: TestClient) -> None:
    created = client.post("/api/budgets", json={
        "category": "Транспорт", "limit_amount": 6000,
    }).json()
    bid = created["id"]
    assert any(b["id"] == bid for b in client.get("/api/budgets").json())

    assert client.delete(f"/api/budgets/{bid}").status_code == 204
    assert not any(b["id"] == bid for b in client.get("/api/budgets").json())

    restored = client.post(f"/api/budgets/{bid}/restore")
    assert restored.status_code == 200
    assert any(b["id"] == bid for b in client.get("/api/budgets").json())
