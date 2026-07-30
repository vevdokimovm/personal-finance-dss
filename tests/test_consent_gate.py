"""Гейт согласия на обработку финансовых данных (юрблок L1).

Смысл этих тестов — не «эндпоинт отвечает 403», а то, что согласие ПЕРЕСТАЛО
быть декоративным. До гейта запись в `user_consents` существовала и ничего не
ограничивала: финансовый портрет обрабатывался по основанию для ПДн, хотя
документ обещает отдельное основание.
"""
from __future__ import annotations

import pytest

from app.core.legal import CONSENT_FINANCIAL_DATA


def _register(client, email: str = "gate@fp.io"):
    return client.post("/api/auth/register", json={
        "email": email, "password": "strongpass1", "consent": True})


def _headers(client, email: str = "gate@fp.io") -> dict[str, str]:
    token = _register(client, email).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestGateClosed:
    def test_obligations_are_refused_without_financial_consent(self, client):
        r = client.get("/api/obligations", headers=_headers(client))
        assert r.status_code == 403

    def test_refusal_is_machine_readable(self, client):
        r = client.get("/api/goals", headers=_headers(client))
        detail = r.json()["detail"]
        assert detail["code"] == "consent_required"
        assert detail["consent_type"] == CONSENT_FINANCIAL_DATA
        assert detail["document"]["url"]

    @pytest.mark.parametrize("path", ["/api/transactions", "/api/obligations",
                                      "/api/goals", "/api/liquid-assets"])
    def test_every_financial_router_is_gated(self, client, path):
        assert client.get(path, headers=_headers(client)).status_code == 403


class TestGateOpen:
    def test_granting_consent_opens_access(self, client):
        headers = _headers(client)
        granted = client.post(f"/api/consents/{CONSENT_FINANCIAL_DATA}",
                              headers=headers)
        assert granted.status_code in (200, 201)
        assert client.get("/api/obligations", headers=headers).status_code == 200

    def test_withdrawal_closes_access_again(self, client):
        headers = _headers(client)
        client.post(f"/api/consents/{CONSENT_FINANCIAL_DATA}", headers=headers)
        client.delete(f"/api/consents/{CONSENT_FINANCIAL_DATA}",
                      headers=headers)
        assert client.get("/api/obligations", headers=headers).status_code == 403


class TestAnonymousIsNotGated:
    """Демо-режим не относится к определённому субъекту — 152-ФЗ неприменим.

    Требовать согласие у анонима означало бы сломать демо ради формальности,
    не дав никакой защиты: защищать нечего, персональных данных нет.
    """

    @pytest.mark.parametrize("path", ["/api/transactions", "/api/obligations",
                                      "/api/goals", "/api/liquid-assets"])
    def test_anonymous_passes(self, client, path):
        assert client.get(path).status_code != 403
