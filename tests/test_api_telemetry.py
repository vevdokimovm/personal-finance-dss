"""Телеметрия принятия совета (волна 0, п. 0.6, docs/model/telemetry_spec.md).

Эндпоинты дормантны за settings.TELEMETRY_COLLECTION_ENABLED (default False) —
правовой контур обезличивания (152-ФЗ, ROADMAP §8.2а) закрывается юристом
отдельно от кода. Тесты явно включают флаг через monkeypatch, чтобы проверить
саму механику; факт, что флаг выключен по умолчанию, проверяется отдельно.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def auth_headers_financial(client: TestClient) -> dict:
    """Пользователь с согласием и на регистрацию, и на финансовые данные —
    эндпоинт телеметрии за тем же гейтом, что transactions/obligations/goals."""
    resp = client.post("/api/auth/register", json={
        "email": "telemetry-fixture@example.com", "password": "verysecret1",
        "consent": True})
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    client.post("/api/consents/financial_data", headers=headers)
    return headers


def _advice_payload() -> dict:
    return {
        "model_version": "3.8.0",
        "app_version": "8.16.1",
        "input_snapshot_hash": "a" * 64,
        "advice": {"x_obligations": 5000, "x_reserve": 3000, "x_goals": 2000},
    }


class TestTelemetryDisabledByDefault:
    def test_post_returns_404_when_flag_off(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        # Флаг НЕ пропатчен — проверяем дефолт settings.TELEMETRY_COLLECTION_ENABLED=False.
        resp = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(),
            headers=auth_headers_financial,
        )
        assert resp.status_code == 404


class TestTelemetryEnabled:
    @pytest.fixture(autouse=True)
    def _enable_flag(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.api import routes_telemetry
        monkeypatch.setattr(routes_telemetry.settings, "TELEMETRY_COLLECTION_ENABLED", True)

    def test_create_event_success(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        resp = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(),
            headers=auth_headers_financial,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["plan_id"]
        assert body["model_version"] == "3.8.0"
        assert body["outcome"] is None
        assert body["shown_at"]
        assert body["decided_at"] is None

    def test_create_requires_auth(self, client: TestClient) -> None:
        resp = client.post("/api/telemetry/advice-events", json=_advice_payload())
        assert resp.status_code == 401

    def test_create_requires_financial_consent(
        self, client: TestClient
    ) -> None:
        resp = client.post("/api/auth/register", json={
            "email": "no-fin-consent@example.com", "password": "verysecret1",
            "consent": True})
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
        resp = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(), headers=headers,
        )
        assert resp.status_code == 403

    def test_create_missing_field_rejected(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        payload = _advice_payload()
        del payload["model_version"]
        resp = client.post(
            "/api/telemetry/advice-events", json=payload, headers=auth_headers_financial,
        )
        assert resp.status_code == 422

    def test_decision_roundtrip(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        created = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(),
            headers=auth_headers_financial,
        ).json()
        plan_id = created["plan_id"]

        decided = client.patch(
            f"/api/telemetry/advice-events/{plan_id}/decision",
            json={"outcome": "modified", "modified_to": {"x_obligations": 6000}},
            headers=auth_headers_financial,
        )
        assert decided.status_code == 200
        body = decided.json()
        assert body["outcome"] == "modified"
        assert body["modified_to"] == {"x_obligations": 6000}
        assert body["decided_at"]

    def test_decision_invalid_outcome_rejected(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        created = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(),
            headers=auth_headers_financial,
        ).json()
        resp = client.patch(
            f"/api/telemetry/advice-events/{created['plan_id']}/decision",
            json={"outcome": "maybe"}, headers=auth_headers_financial,
        )
        assert resp.status_code == 422

    def test_decision_unknown_plan_id_404(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        resp = client.patch(
            "/api/telemetry/advice-events/does-not-exist/decision",
            json={"outcome": "ignored"}, headers=auth_headers_financial,
        )
        assert resp.status_code == 404

    def test_decision_other_users_plan_id_404(
        self, client: TestClient, auth_headers_financial: dict
    ) -> None:
        """Чужой plan_id не должен позволять записать решение за другого
        пользователя — тот же принцип, что у остальных user-scoped ресурсов."""
        created = client.post(
            "/api/telemetry/advice-events", json=_advice_payload(),
            headers=auth_headers_financial,
        ).json()

        other = client.post("/api/auth/register", json={
            "email": "telemetry-other@example.com", "password": "verysecret1",
            "consent": True})
        other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
        client.post("/api/consents/financial_data", headers=other_headers)

        resp = client.patch(
            f"/api/telemetry/advice-events/{created['plan_id']}/decision",
            json={"outcome": "ignored"}, headers=other_headers,
        )
        assert resp.status_code == 404
