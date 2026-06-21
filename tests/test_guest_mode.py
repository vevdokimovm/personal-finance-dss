"""Гостевой режим: демо-портреты и раздел валидации — только без входа.

После входа в профиль и загрузка портрета, и раздел валидации убираются: тестовая
песочница не должна смешиваться с реальными данными пользователя.
"""
from __future__ import annotations

import pytest

PORTRAITS = ["anna", "dmitriy", "mikhail", "igor", "olga", "viktor"]


def _login(client, email: str = "owner@fp.io", password: str = "strongpass1") -> None:
    """Регистрирует и логинит пользователя — TestClient сохраняет cookie сессии."""
    client.post("/api/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


class TestGuestSandbox:
    def test_guest_sees_validation_nav(self, client) -> None:
        assert "nav-validation" in client.get("/").text

    def test_guest_sees_demo_selector(self, client) -> None:
        assert "demo-case-select" in client.get("/").text

    def test_guest_can_open_validation(self, client) -> None:
        assert client.get("/validation").status_code == 200

    @pytest.mark.parametrize("case", PORTRAITS)
    def test_guest_can_load_each_portrait(self, client, case) -> None:
        resp = client.post(f"/api/demo/load?case={case}")
        assert resp.status_code == 200, resp.text


class TestAuthenticatedHidesSandbox:
    def test_no_validation_nav_when_logged_in(self, client) -> None:
        _login(client)
        assert "nav-validation" not in client.get("/").text

    def test_no_demo_selector_when_logged_in(self, client) -> None:
        _login(client)
        assert "demo-case-select" not in client.get("/").text

    def test_demo_load_forbidden_when_logged_in(self, client) -> None:
        _login(client)
        resp = client.post("/api/demo/load?case=anna")
        assert resp.status_code == 403

    def test_validation_redirects_when_logged_in(self, client) -> None:
        _login(client)
        resp = client.get("/validation", follow_redirects=False)
        assert resp.status_code in (302, 303, 307)
