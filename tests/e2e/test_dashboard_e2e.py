"""E2E дашборда: реальный браузерный рендер и клики.

Проверяют то, что не видят SSR-тесты: что JS отрисовывает показатели в браузере,
ликвидность подаётся в месяцах (refined-модель v3.0.0), а попап по клику на карточку
Lt показывает stock-based формулу. Маркер e2e — запускаются отдельно с браузером.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e

LT_POPULATED = (
    "() => { const el = document.querySelector('#lt-value');"
    " return el && el.textContent.trim() !== '—'; }"
)
BLR_POPULATED = (
    "() => { const el = document.querySelector('#blr-value');"
    " return el && el.textContent.trim() !== '—'; }"
)


def test_dashboard_loads(page, base_url) -> None:
    page.goto("/")
    assert page.locator("body").is_visible()


def test_metric_cards_render_after_seed(page, seeded) -> None:
    page.goto("/")
    page.wait_for_function(LT_POPULATED, timeout=15000)
    # Все четыре карточки заполнены (не плейсхолдер)
    for sel in ("#rt-value", "#lt-value", "#dt-value", "#blr-value"):
        assert page.locator(sel).inner_text().strip() != "—", sel


def test_liquidity_card_shows_months(page, seeded) -> None:
    page.goto("/")
    page.wait_for_function(LT_POPULATED, timeout=15000)
    # Stock-based ликвидность отображается в месяцах автономии
    assert "мес" in page.locator("#lt-value").inner_text()


def test_blr_card_shows_months(page, seeded) -> None:
    page.goto("/")
    page.wait_for_function(BLR_POPULATED, timeout=15000)
    assert "мес" in page.locator("#blr-value").inner_text()


def test_lt_card_click_opens_stock_based_popup(page, seeded) -> None:
    page.goto("/")
    page.wait_for_function(LT_POPULATED, timeout=15000)

    page.locator('article[data-metric="lt"]').click()
    explain = page.locator("#metric-explain")
    explain.wait_for(state="visible", timeout=5000)

    text = explain.inner_text()
    # Новая формула: ликвидная подушка ÷ месячные расходы
    assert "Ликвидная подушка" in text
    assert "Месячные расходы" in text
    # Старой flow-семантики быть не должно
    assert "Обязательные траты (расходы + кредиты)" not in text
