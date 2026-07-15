"""Интеграционные тесты A/B-экспериментов (P3.5): сервис, фиксация, измерение, эндпоинты."""
from __future__ import annotations


import pytest
from fastapi.testclient import TestClient

from app.database import crud  # noqa: F401  (единый стиль импорта в тестах)
from app.database.models import Event
from app.services import experiments as svc
from app.services.analytics import experiment_results
from app.utils.time import utcnow

FIFTY = [{"name": "control", "weight": 50}, {"name": "treatment", "weight": 50}]


def _running(db, key="exp", conversion_event="goal_created", variants=None):
    return svc.create_experiment(
        db, key, name=key, variants=variants or FIFTY,
        conversion_event=conversion_event, status="running",
    )


# ── Валидация и CRUD сервиса ─────────────────────────────────────────────
class TestExperimentCrud:
    def test_create_get_list(self, db_session):
        svc.create_experiment(db_session, "e1", variants=FIFTY)
        assert svc.get_experiment(db_session, "e1").key == "e1"
        assert any(e.key == "e1" for e in svc.list_experiments(db_session))

    @pytest.mark.parametrize("bad", [[], "notlist", [{"name": "x", "weight": 0}], [{"name": "", "weight": 5}], [{"weight": 5}]])  # noqa: E501
    def test_validate_variants_rejects_bad(self, bad):
        with pytest.raises(ValueError):
            svc.validate_variants(bad)

    def test_update_status_and_variants(self, db_session):
        svc.create_experiment(db_session, "e2", variants=FIFTY)
        updated = svc.update_experiment(db_session, "e2", status="running")
        assert updated.status == "running"
        assert svc.update_experiment(db_session, "missing", status="running") is None

    def test_delete(self, db_session):
        svc.create_experiment(db_session, "e3", variants=FIFTY)
        assert svc.delete_experiment(db_session, "e3") is True
        assert svc.get_experiment(db_session, "e3") is None
        assert svc.delete_experiment(db_session, "e3") is False

    def test_create_invalid_status_raises(self, db_session):
        with pytest.raises(ValueError):
            svc.create_experiment(db_session, "bad-st", variants=FIFTY, status="live")

    def test_update_fields_and_invalid_status(self, db_session):
        svc.create_experiment(db_session, "e4", variants=FIFTY)
        upd = svc.update_experiment(
            db_session, "e4", name="Новое имя", description="desc", conversion_event="x_event"
        )
        assert upd.name == "Новое имя"
        assert upd.description == "desc"
        assert upd.conversion_event == "x_event"
        with pytest.raises(ValueError):
            svc.update_experiment(db_session, "e4", status="live")


# ── Назначение и фиксация ────────────────────────────────────────────────
class TestAssignment:
    def test_not_running_returns_none(self, db_session):
        svc.create_experiment(db_session, "draft1", variants=FIFTY, status="draft")
        assert svc.get_or_assign_variant(db_session, "draft1", user_id="u1") is None

    def test_assigns_and_persists(self, db_session):
        _running(db_session, "r1")
        variant = svc.get_or_assign_variant(db_session, "r1", user_id="u1")
        assert variant in {"control", "treatment"}
        # повторно — тот же вариант
        assert svc.get_or_assign_variant(db_session, "r1", user_id="u1") == variant

    def test_assignment_is_locked_against_config_change(self, db_session):
        _running(db_session, "r2")
        first = svc.get_or_assign_variant(db_session, "r2", user_id="u1")
        # резко меняем веса — назначенный subject НЕ должен переехать
        svc.update_experiment(db_session, "r2", variants=[
            {"name": "control", "weight": 1}, {"name": "treatment", "weight": 999},
        ])
        assert svc.get_or_assign_variant(db_session, "r2", user_id="u1") == first

    def test_no_subject_returns_none(self, db_session):
        _running(db_session, "r3")
        assert svc.get_or_assign_variant(db_session, "r3") is None

    def test_anonymous_via_session_id(self, db_session):
        _running(db_session, "r4")
        variant = svc.get_or_assign_variant(db_session, "r4", session_id="sess-xyz")
        assert variant in {"control", "treatment"}
        assert svc.get_or_assign_variant(db_session, "r4", session_id="sess-xyz") == variant


# ── Измерение результатов ────────────────────────────────────────────────
class TestResults:
    def test_results_count_assigned_and_converted(self, db_session):
        _running(db_session, "m1", conversion_event="goal_created",
                 variants=[{"name": "a", "weight": 100}])  # все в "a" для детерминизма
        subjects = [f"u-{i}" for i in range(5)]
        for s in subjects:
            svc.get_or_assign_variant(db_session, "m1", user_id=s)
        # двое конвертнулись (по user_id), один аноним по session_id
        for s in subjects[:2]:
            db_session.add(Event(user_id=s, event_type="goal_created", created_at=utcnow()))
        svc.get_or_assign_variant(db_session, "m1", session_id="anon-1")
        db_session.add(Event(session_id="anon-1", event_type="goal_created", created_at=utcnow()))
        db_session.commit()

        res = experiment_results(db_session, "m1")
        a = next(v for v in res["variants"] if v["variant"] == "a")
        assert a["assigned"] == 6  # 5 + аноним
        assert a["converted"] == 3  # 2 по user_id + 1 по session_id
        assert a["conversion_rate"] == round(3 / 6, 4)

    def test_results_none_for_missing(self, db_session):
        assert experiment_results(db_session, "nope") is None


# ── Эндпоинты ────────────────────────────────────────────────────────────
class TestEndpoints:
    def _create(self, client, key="apiexp", status="running"):
        return client.post("/api/admin/experiments", json={
            "key": key, "name": key, "variants": FIFTY,
            "conversion_event": "goal_created", "status": status,
        })

    def test_admin_create_list(self, client: TestClient):
        assert self._create(client).status_code == 201
        keys = [e["key"] for e in client.get("/api/admin/experiments").json()]
        assert "apiexp" in keys

    def test_create_duplicate_409(self, client: TestClient):
        self._create(client, "dup")
        assert self._create(client, "dup").status_code == 409

    def test_create_bad_variants_422(self, client: TestClient):
        r = client.post("/api/admin/experiments", json={
            "key": "bad", "variants": [{"name": "x", "weight": 0}]})
        assert r.status_code == 422

    def test_patch_status_and_delete(self, client: TestClient):
        self._create(client, "lifecycle", status="draft")
        patched = client.patch("/api/admin/experiments/lifecycle", json={"status": "running"})
        assert patched.status_code == 200 and patched.json()["status"] == "running"
        assert client.delete("/api/admin/experiments/lifecycle").status_code == 204
        assert client.patch("/api/admin/experiments/lifecycle",
                            json={"status": "stopped"}).status_code == 404

    def test_results_404_for_missing(self, client: TestClient):
        assert client.get("/api/admin/experiments/ghost/results").status_code == 404

    def test_variant_endpoint(self, client: TestClient):
        # не running → null
        self._create(client, "ve", status="draft")
        assert client.get("/api/experiments/ve/variant?sid=abc").json()["variant"] is None
        # running → стабильный вариант
        client.patch("/api/admin/experiments/ve", json={"status": "running"})
        first = client.get("/api/experiments/ve/variant?sid=abc").json()["variant"]
        assert first in {"control", "treatment"}
        assert client.get("/api/experiments/ve/variant?sid=abc").json()["variant"] == first
