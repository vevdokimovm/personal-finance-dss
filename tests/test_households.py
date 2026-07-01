"""Семейные/многопользовательские бюджеты (P3.7) — аддитивный household-оверлей.

Базовый принцип: FINPILOT — про ЛИЧНЫЕ финансы. Household — дополнительный скоуп
поверх персонального владения, а НЕ замена ему. Поэтому контракт этих тестов:

1. Личные данные (household_id IS NULL) — приватны и видны только владельцу,
   ровно как до P3.7 (аддитивность, ничего не сломано).
2. Общие данные (household_id задан) — видны всем членам household.
3. Роли owner/member/viewer ограничивают запись и управление членством.
4. Инвайт-флоу: токен → accept → членство; протухший/отозванный/использованный — нет.
5. Кросс-household изоляция: член одной семьи не видит данные другой.

Тесты идут через публичный API (TestClient) — это и проверяет права на уровне
эндпоинтов. Аутентификация — Bearer-токеном (в dependencies он приоритетнее cookie),
чтобы в одном тесте держать несколько независимых пользователей.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from app.database.db import SessionLocal
from app.database.models import HouseholdInvite
from app.utils.time import utcnow

FUTURE = "2030-12-31T00:00:00"


# ─────────────────────────── helpers ───────────────────────────

def _register(client, email: str) -> str:
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_household(client, token: str, name: str = "Семья") -> int:
    r = client.post("/api/households", json={"name": name}, headers=_h(token))
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _invite(client, token: str, hid: int, role: str = "member", email: str | None = None) -> str:
    body: dict = {"role": role}
    if email is not None:
        body["email"] = email
    r = client.post(f"/api/households/{hid}/invites", json=body, headers=_h(token))
    assert r.status_code == 201, r.text
    return r.json()["token"]


def _accept(client, token: str, invite_token: str):
    return client.post(f"/api/households/invites/{invite_token}/accept", headers=_h(token))


def _add_member(client, owner_token: str, hid: int, member_token: str, role: str = "member") -> None:  # noqa: E501
    """Полный цикл «пригласить → принять» для удобства настройки тестов."""
    inv = _invite(client, owner_token, hid, role=role)
    r = _accept(client, member_token, inv)
    assert r.status_code == 200, r.text


def _create_goal(client, token: str, name: str, household_id: int | None = None):
    body: dict = {"name": name, "target_amount": 100000, "deadline": FUTURE}
    if household_id is not None:
        body["household_id"] = household_id
    return client.post("/api/goals", json=body, headers=_h(token))


def _goal_names(client, token: str) -> set[str]:
    r = client.get("/api/goals", headers=_h(token))
    assert r.status_code == 200, r.text
    return {g["name"] for g in r.json()}


# ─────────────────────────── household CRUD ───────────────────────────

class TestHouseholdCRUD:
    def test_create_household_makes_owner(self, client):
        token = _register(client, "owner1@test.io")
        r = client.post("/api/households", json={"name": "Моя семья"}, headers=_h(token))
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["name"] == "Моя семья"
        assert data["role"] == "owner"
        assert "id" in data

    def test_create_requires_auth(self, client):
        r = client.post("/api/households", json={"name": "X"})
        assert r.status_code == 401

    def test_list_shows_only_my_households(self, client):
        a = _register(client, "a@test.io")
        b = _register(client, "b@test.io")
        hid = _create_household(client, a, "A-семья")

        a_list = client.get("/api/households", headers=_h(a)).json()
        b_list = client.get("/api/households", headers=_h(b)).json()
        assert hid in [h["id"] for h in a_list]
        assert hid not in [h["id"] for h in b_list]

    def test_get_detail_member_only(self, client):
        a = _register(client, "a2@test.io")
        b = _register(client, "b2@test.io")
        hid = _create_household(client, a)

        assert client.get(f"/api/households/{hid}", headers=_h(a)).status_code == 200
        assert client.get(f"/api/households/{hid}", headers=_h(b)).status_code == 404

    def test_rename_owner_only(self, client):
        a = _register(client, "a3@test.io")
        b = _register(client, "b3@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        assert client.patch(
            f"/api/households/{hid}", json={"name": "Новое"}, headers=_h(a)).status_code == 200
        assert client.patch(
            f"/api/households/{hid}", json={"name": "Нельзя"}, headers=_h(b)).status_code == 403

    def test_delete_owner_only(self, client):
        a = _register(client, "a4@test.io")
        b = _register(client, "b4@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        assert client.delete(f"/api/households/{hid}", headers=_h(b)).status_code == 403
        assert client.delete(f"/api/households/{hid}", headers=_h(a)).status_code == 204
        # после удаления — не виден никому
        assert client.get(f"/api/households/{hid}", headers=_h(a)).status_code == 404


# ─────────────────────────── членство и инвайты ───────────────────────────

class TestMembershipAndInvites:
    def test_invite_and_accept_grants_membership(self, client):
        a = _register(client, "ai@test.io")
        b = _register(client, "bi@test.io")
        hid = _create_household(client, a)

        token = _invite(client, a, hid, role="member")
        r = _accept(client, b, token)
        assert r.status_code == 200, r.text
        assert r.json()["role"] == "member"
        # B теперь видит household в своём списке
        assert hid in [h["id"] for h in client.get("/api/households", headers=_h(b)).json()]

    def test_members_list_includes_both(self, client):
        a = _register(client, "am@test.io")
        b = _register(client, "bm@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b)

        members = client.get(f"/api/households/{hid}/members", headers=_h(a)).json()
        roles = {m["role"] for m in members}
        assert len(members) == 2
        assert "owner" in roles and "member" in roles

    def test_invite_owner_only(self, client):
        a = _register(client, "ao@test.io")
        b = _register(client, "bo@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")
        # member не может приглашать
        r = client.post(f"/api/households/{hid}/invites", json={"role": "member"}, headers=_h(b))
        assert r.status_code == 403

    def test_invite_role_cannot_be_owner(self, client):
        a = _register(client, "aq@test.io")
        hid = _create_household(client, a)
        r = client.post(f"/api/households/{hid}/invites", json={"role": "owner"}, headers=_h(a))
        assert r.status_code == 422

    def test_invite_expired_rejected(self, client):
        a = _register(client, "ae@test.io")
        b = _register(client, "be@test.io")
        hid = _create_household(client, a)
        token = _invite(client, a, hid)

        # искусственно протухаем приглашение в БД
        session = SessionLocal()
        try:
            inv = session.query(HouseholdInvite).filter(HouseholdInvite.token == token).one()
            inv.expires_at = utcnow() - timedelta(hours=1)
            session.commit()
        finally:
            session.close()

        r = _accept(client, b, token)
        assert r.status_code in (400, 410)
        # членство не выдано
        assert hid not in [h["id"] for h in client.get("/api/households", headers=_h(b)).json()]

    def test_invite_revoked_rejected(self, client):
        a = _register(client, "ar@test.io")
        b = _register(client, "br@test.io")
        hid = _create_household(client, a)
        token = _invite(client, a, hid)

        # узнаём id приглашения и отзываем
        invites = client.get(f"/api/households/{hid}/invites", headers=_h(a)).json()
        iid = invites[0]["id"]
        assert client.post(f"/api/households/{hid}/invites/{iid}/revoke",
                           headers=_h(a)).status_code in (200, 204)

        r = _accept(client, b, token)
        assert r.status_code in (400, 410)

    def test_invite_double_accept_rejected(self, client):
        a = _register(client, "ad@test.io")
        b = _register(client, "bd@test.io")
        hid = _create_household(client, a)
        token = _invite(client, a, hid)

        assert _accept(client, b, token).status_code == 200
        # повторный accept тем же или другим — отвергается
        c = _register(client, "cd@test.io")
        assert _accept(client, c, token).status_code in (400, 410)

    def test_remove_member_owner_only(self, client):
        a = _register(client, "arm@test.io")
        b = _register(client, "brm@test.io")
        c = _register(client, "crm@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b)
        _add_member(client, a, hid, c)

        # b (member) не может удалить c
        c_id = client.get("/api/auth/me", headers=_h(c)).json()["id"]
        assert client.delete(
            f"/api/households/{hid}/members/{c_id}", headers=_h(b)).status_code == 403
        # owner может
        assert client.delete(
            f"/api/households/{hid}/members/{c_id}", headers=_h(a)).status_code == 204
        # c больше не член
        assert hid not in [h["id"] for h in client.get("/api/households", headers=_h(c)).json()]

    def test_cannot_remove_owner(self, client):
        a = _register(client, "arr@test.io")
        hid = _create_household(client, a)
        a_id = client.get("/api/auth/me", headers=_h(a)).json()["id"]
        # owner нельзя удалить как обычного члена
        assert client.delete(
            f"/api/households/{hid}/members/{a_id}", headers=_h(a)).status_code == 400

    def test_member_can_leave(self, client):
        a = _register(client, "al@test.io")
        b = _register(client, "bl@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b)

        assert client.post(f"/api/households/{hid}/leave", headers=_h(b)).status_code == 204
        assert hid not in [h["id"] for h in client.get("/api/households", headers=_h(b)).json()]

    def test_owner_cannot_leave(self, client):
        a = _register(client, "aol@test.io")
        hid = _create_household(client, a)
        # owner должен сначала удалить household или передать владение (вне фазы 1)
        assert client.post(f"/api/households/{hid}/leave", headers=_h(a)).status_code == 400


# ─────────────────────────── скоуп общих данных ───────────────────────────

class TestSharedDataScope:
    def test_personal_data_unchanged(self, client):
        """Аддитивность: без household личные цели видны владельцу как раньше."""
        a = _register(client, "sp@test.io")
        assert _create_goal(client, a, "Личная").status_code == 201
        assert "Личная" in _goal_names(client, a)

    def test_shared_goal_visible_to_members(self, client):
        a = _register(client, "ss1@test.io")
        b = _register(client, "ss2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        assert _create_goal(client, a, "Отпуск семьёй", household_id=hid).status_code == 201
        assert "Отпуск семьёй" in _goal_names(client, b)

    def test_personal_goal_not_visible_to_members(self, client):
        a = _register(client, "pn1@test.io")
        b = _register(client, "pn2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        # A создаёт ЛИЧНУЮ цель (без household_id) — приватная подушка
        assert _create_goal(client, a, "Личная подушка").status_code == 201
        assert "Личная подушка" not in _goal_names(client, b)
        assert "Личная подушка" in _goal_names(client, a)

    def test_outsider_does_not_see_shared(self, client):
        a = _register(client, "od1@test.io")
        b = _register(client, "od2@test.io")
        c = _register(client, "od3@test.io")  # не член
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        _create_goal(client, a, "Общая цель", household_id=hid)
        assert "Общая цель" not in _goal_names(client, c)

    def test_cross_household_isolation(self, client):
        a = _register(client, "ch1@test.io")
        b = _register(client, "ch2@test.io")
        hid1 = _create_household(client, a, "Семья-1")
        _create_household(client, b, "Семья-2")

        _create_goal(client, a, "Цель семьи 1", household_id=hid1)
        # b — член только семьи 2, не должен видеть цель семьи 1
        assert "Цель семьи 1" not in _goal_names(client, b)

    def test_viewer_cannot_write_shared(self, client):
        a = _register(client, "vw1@test.io")
        b = _register(client, "vw2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="viewer")

        # viewer не может создавать общие строки
        r = _create_goal(client, b, "Нельзя viewer", household_id=hid)
        assert r.status_code == 403

    def test_viewer_can_read_shared(self, client):
        a = _register(client, "vr1@test.io")
        b = _register(client, "vr2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="viewer")

        _create_goal(client, a, "Видно viewer", household_id=hid)
        assert "Видно viewer" in _goal_names(client, b)

    def test_member_can_write_shared(self, client):
        a = _register(client, "mw1@test.io")
        b = _register(client, "mw2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        r = _create_goal(client, b, "Member добавил", household_id=hid)
        assert r.status_code == 201
        # видно владельцу тоже
        assert "Member добавил" in _goal_names(client, a)

    def test_write_to_foreign_household_forbidden(self, client):
        a = _register(client, "fw1@test.io")
        b = _register(client, "fw2@test.io")
        hid = _create_household(client, a)  # b не член
        r = _create_goal(client, b, "Чужой котёл", household_id=hid)
        assert r.status_code == 403


# ─────────────────────────── жизненный цикл общих данных ───────────────────────────

class TestSharedDataLifecycle:
    def test_delete_household_returns_rows_to_authors(self, client):
        """152-ФЗ/приватность: после удаления household общие строки возвращаются
        автору в личное владение (household_id → NULL), а не теряются и не висят
        обезличенными."""
        a = _register(client, "dl1@test.io")
        b = _register(client, "dl2@test.io")
        hid = _create_household(client, a)
        _add_member(client, a, hid, b, role="member")

        _create_goal(client, a, "Бывшая общая", household_id=hid)
        assert "Бывшая общая" in _goal_names(client, b)  # пока общая — видна B

        assert client.delete(f"/api/households/{hid}", headers=_h(a)).status_code == 204

        # теперь строка снова личная у автора A; B её не видит
        assert "Бывшая общая" in _goal_names(client, a)
        assert "Бывшая общая" not in _goal_names(client, b)
