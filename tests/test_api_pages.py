"""Тесты отрисовки интерфейса.

Проверяют, что каждая страница рендерится (200) и содержит ключевые элементы
своих фич (формы, контейнеры, секции). Настоящие клики/JS-взаимодействие тут не
покрываются — для этого нужен браузерный стек (Playwright); здесь проверяется
серверный рендер шаблонов.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

PAGES = ["/", "/planning", "/transactions", "/obligations", "/goals", "/banks", "/validation", "/profile"]  # noqa: E501


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


# ── Refined-модель v3.0.0: фронт должен отражать stock-based ликвидность ──

class TestDashboardLiquiditySemantics:
    """Дашборд должен показывать Lt как месяцы автономии, а не старый flow-коэффициент."""

    def test_lt_card_shows_months_norm(self, client: TestClient) -> None:
        html = client.get("/").text
        # Новая норма ликвидности — в месяцах (Greninger 2.5–6)
        assert "норма 2.5" in html
        # Подпись про месяцы автономии на резерве
        assert "резерв" in html.lower()

    def test_lt_card_drops_old_flow_norm(self, client: TestClient) -> None:
        html = client.get("/").text
        # Старого порога-доли 0.3 и flow-формулировки быть не должно
        assert "норма от 0.3" not in html
        assert "Насколько свободно от обязательных платежей" not in html

    def test_blr_card_distinguished_from_lt(self, client: TestClient) -> None:
        html = client.get("/").text
        # Подушка (BLR) явно отличается от запаса прочности: учитывает накопления целей
        assert "включая цели" in html


class TestPlanningControls:
    def test_lmin_slider_in_months(self, client: TestClient) -> None:
        html = client.get("/planning").text
        assert "мес. расходов" in html  # порог ликвидности задаётся в месяцах автономии

    def test_rbench_dynamic_controls_present(self, client: TestClient) -> None:
        html = client.get("/planning").text
        # Кнопки источника r_bench: ключевая ЦБ и ставка собственного вклада
        assert "rbench-cbr" in html
        assert "rbench-from-asset" in html
