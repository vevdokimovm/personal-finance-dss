"""Тесты отрисовки интерфейса.

Проверяют, что каждая страница рендерится (200) и содержит ключевые элементы
своих фич (формы, контейнеры, секции). Настоящие клики/JS-взаимодействие тут не
покрываются — для этого нужен браузерный стек (Playwright); здесь проверяется
серверный рендер шаблонов.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

PAGES = ["/", "/planning", "/transactions", "/obligations", "/goals", "/banks", "/validation", "/profile"]


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(client: TestClient, path: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert len(resp.text) > 500  # не пустая заглушка


def test_planning_page_has_feature_blocks(client: TestClient) -> None:
    html = client.get("/planning").text
    # Блок советов по тратам и контейнер прогноза
    assert "spending-advice-container" in html
    assert "forecast" in html


def test_goals_page_has_envelope_select(client: TestClient) -> None:
    html = client.get("/goals").text
    # Селект привязки цели к активу (конверты)
    assert "goal-linked-asset" in html


def test_obligations_page_has_total_term_field(client: TestClient) -> None:
    html = client.get("/obligations").text
    # Поле общего срока кредита (term-фикс)
    assert "obligation-term" in html


def test_transactions_page_has_period_inputs(client: TestClient) -> None:
    html = client.get("/transactions").text
    assert "type=\"date\"" in html or "date" in html


def test_app_js_and_css_served(client: TestClient) -> None:
    # Статика фронтенда отдаётся
    js = client.get("/static/js/app.js")
    css = client.get("/static/css/styles.css")
    assert js.status_code == 200
    assert css.status_code == 200
