"""household-хвост (P3.7): производные (scenarios, plan_snapshots) видны семье.

Колонка household_id есть на этих таблицах с миграции 0022, но имела два пробела:
1. При создании household_id не проставлялся — производные всегда оставались личными
   (household_id IS NULL), поэтому семейный план/сценарий не был виден членам семьи.
2. get_plan_snapshots фильтровал вручную по user_id, игнорируя household-ось (в отличие
   от get_scenarios, который уже шёл через _owner_filter).

Этот батч закрывает оба: проброс household_id при создании (с валидацией членства —
чужой household проставить нельзя) + household-aware чтение снапшотов.

Контракт:
1. Снапшот/сценарий, созданный с household_id, виден другому члену той же семьи.
2. Личный производный (household_id=None) виден только автору.
3. Нельзя проставить чужой household_id: resolve_household_id возвращает None
   (производное становится личным), а не кладёт данные в чужую семью.
"""
from __future__ import annotations

from app.database import crud
from app.database.db import SessionLocal
from app.database.models import HouseholdMembership


# ─────────────────────────── helpers ───────────────────────────

def _user(db, email: str) -> str:
    return crud.create_user(db, email=email, password_hash="hashed").id


def _add_member(db, household_id: int, user_id: str, role: str = "member") -> None:
    db.add(HouseholdMembership(household_id=household_id, user_id=user_id, role=role))
    db.commit()


# ─────────────────────── видимость в семье ───────────────────────

class TestSharedWithHousehold:
    def test_plan_snapshot_shared_visible_to_member(self, db_session) -> None:
        db = db_session
        owner = _user(db, "snap_owner@test.io")
        member = _user(db, "snap_member@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        _add_member(db, hh.id, member)

        # owner сохраняет снапшот как общий (household_id проставлен).
        crud.create_plan_snapshot(
            db, result={"risk_profile": "3", "indicators": {}, "top3": []},
            user_id=owner, household_id=hh.id,
        )

        # member видит снапшот семьи.
        seen = crud.get_plan_snapshots(db, user_id=member)
        assert len(seen) == 1
        assert seen[0].household_id == hh.id

    def test_scenario_shared_visible_to_member(self, db_session) -> None:
        db = db_session
        owner = _user(db, "scen_owner@test.io")
        member = _user(db, "scen_member@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        _add_member(db, hh.id, member)

        crud.save_scenario(
            db, name="Что если ипотека", parameters={}, result={},
            user_id=owner, household_id=hh.id,
        )

        seen = crud.get_scenarios(db, user_id=member)
        assert len(seen) == 1
        assert seen[0].name == "Что если ипотека"


class TestPrivateDerived:
    def test_personal_snapshot_not_visible_to_member(self, db_session) -> None:
        db = db_session
        owner = _user(db, "priv_snap_owner@test.io")
        member = _user(db, "priv_snap_member@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        _add_member(db, hh.id, member)

        # Личный снапшот (household_id не указан).
        crud.create_plan_snapshot(
            db, result={"risk_profile": "3", "indicators": {}, "top3": []},
            user_id=owner,
        )

        assert crud.get_plan_snapshots(db, user_id=member) == []
        # А автор своё личное видит.
        assert len(crud.get_plan_snapshots(db, user_id=owner)) == 1

    def test_personal_scenario_not_visible_to_member(self, db_session) -> None:
        db = db_session
        owner = _user(db, "priv_scen_owner@test.io")
        member = _user(db, "priv_scen_member@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        _add_member(db, hh.id, member)

        crud.save_scenario(db, name="Личный", parameters={}, result={}, user_id=owner)

        assert crud.get_scenarios(db, user_id=member) == []
        assert len(crud.get_scenarios(db, user_id=owner)) == 1


# ─────────────────── валидация чужого household ───────────────────

class TestHouseholdIdValidation:
    def test_resolve_returns_id_for_member(self, db_session) -> None:
        db = db_session
        owner = _user(db, "resolve_owner@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        assert crud.resolve_household_id(db, user_id=owner, requested=hh.id) == hh.id

    def test_resolve_returns_none_for_nonmember(self, db_session) -> None:
        db = db_session
        owner = _user(db, "resolve_real_owner@test.io")
        outsider = _user(db, "resolve_outsider@test.io")
        hh = crud.create_household(db, user_id=owner, name="Семья")
        # Чужак не член — проставить этот household нельзя.
        assert crud.resolve_household_id(db, user_id=outsider, requested=hh.id) is None

    def test_resolve_none_when_not_requested(self, db_session) -> None:
        db = db_session
        owner = _user(db, "resolve_norequest@test.io")
        assert crud.resolve_household_id(db, user_id=owner, requested=None) is None

    def test_foreign_household_id_falls_back_to_personal(self, db_session) -> None:
        """Снапшот с чужим household_id создаётся как личный, не утекает в чужую семью."""
        db = db_session
        owner = _user(db, "foreign_owner@test.io")
        outsider = _user(db, "foreign_outsider@test.io")
        hh = crud.create_household(db, user_id=owner, name="Чужая семья")

        # outsider пытается сохранить в чужой household — резолвим в None.
        safe_hh = crud.resolve_household_id(db, user_id=outsider, requested=hh.id)
        crud.create_plan_snapshot(
            db, result={"risk_profile": "3", "indicators": {}, "top3": []},
            user_id=outsider, household_id=safe_hh,
        )

        # owner чужой семьи НЕ видит снапшот outsider'а.
        assert crud.get_plan_snapshots(db, user_id=owner) == []


# ─────────────────── регрессия: snapshot household-aware ───────────────────

class TestPlanSnapshotHouseholdAware:
    """get_plan_snapshots должен идти через _owner_filter (как get_scenarios),
    а не игнорировать household-ось ручным фильтром по user_id."""

    def test_two_members_share_snapshots(self, db_session) -> None:
        db = db_session
        a = _user(db, "aware_a@test.io")
        b = _user(db, "aware_b@test.io")
        hh = crud.create_household(db, user_id=a, name="Семья")
        _add_member(db, hh.id, b)

        # Оба кладут по общему снапшоту.
        crud.create_plan_snapshot(db, result={"risk_profile": "2", "indicators": {}, "top3": []},
                                  user_id=a, household_id=hh.id)
        crud.create_plan_snapshot(db, result={"risk_profile": "4", "indicators": {}, "top3": []},
                                  user_id=b, household_id=hh.id)

        # Каждый видит оба (свой + общий другого).
        assert len(crud.get_plan_snapshots(db, user_id=a)) == 2
        assert len(crud.get_plan_snapshots(db, user_id=b)) == 2


# ─────────────────── endpoint-проброс household_id через API ───────────────────

class TestEndpointProxy:
    """POST /planning/scenarios и /planning/history принимают household_id в payload
    и прокидывают его через resolve_household_id (валидация членства) в CRUD."""

    def _register(self, client, email: str) -> str:
        r = client.post("/api/auth/register",
                        json={"email": email, "password": "password123", "consent": True})
        assert r.status_code == 201, r.text
        return r.json()["access_token"]

    def _uid(self, email: str) -> str:
        from app.database.models import User
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first().id
        finally:
            db.close()

    def test_scenario_endpoint_sets_household_for_member(self, client) -> None:
        token = self._register(client, "ep_owner@test.io")
        uid = self._uid("ep_owner@test.io")
        # owner создаёт household через CRUD (он сразу owner-член).
        db = SessionLocal()
        try:
            hh = crud.create_household(db, user_id=uid, name="Семья")
            hid = hh.id
        finally:
            db.close()

        r = client.post("/api/planning/scenarios",
                        json={"name": "Общий сценарий", "parameters": {}, "result": {},
                              "household_id": hid},
                        headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text

        # household_id проставлен в БД.
        from app.database.models import Scenario
        db = SessionLocal()
        try:
            sc = db.query(Scenario).filter(Scenario.user_id == uid).first()
            assert sc.household_id == hid
        finally:
            db.close()

    def test_scenario_endpoint_ignores_foreign_household(self, client) -> None:
        # Чужой household существует, но текущий юзер в нём не состоит.
        owner_token = self._register(client, "ep_real@test.io")  # noqa: F841
        owner_uid = self._uid("ep_real@test.io")
        db = SessionLocal()
        try:
            hh = crud.create_household(db, user_id=owner_uid, name="Чужая")
            foreign_hid = hh.id
        finally:
            db.close()

        intruder_token = self._register(client, "ep_intruder@test.io")
        intruder_uid = self._uid("ep_intruder@test.io")

        r = client.post("/api/planning/scenarios",
                        json={"name": "Попытка", "parameters": {}, "result": {},
                              "household_id": foreign_hid},
                        headers={"Authorization": f"Bearer {intruder_token}"})
        assert r.status_code == 200, r.text

        # household_id НЕ проставлен (резолв вернул None) — сценарий личный.
        from app.database.models import Scenario
        db = SessionLocal()
        try:
            sc = db.query(Scenario).filter(Scenario.user_id == intruder_uid).first()
            assert sc.household_id is None
        finally:
            db.close()
