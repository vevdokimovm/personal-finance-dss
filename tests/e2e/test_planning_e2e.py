"""E2E страницы планирования: реальный расчёт через UI.

Главная проверка — что refined-модель работает end-to-end через браузер: выбор
профиля риска и клик «Рассчитать альтернативы» дают разные планы у консервативного
и агрессивного профилей (доказательство ортогонализации критериев на уровне UI).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e

BEST_READY = (
    "() => { const el = document.querySelector('#best-container');"
    " return el && el.textContent.includes('оценка'); }"
)


def _calculate(page, risk: int) -> str:
    """Открывает planning, выбирает профиль, запускает расчёт, ждёт результат."""
    page.goto("/planning")
    page.locator(f'button[data-risk="{risk}"]').click()
    page.locator('#planning-form button[type="submit"]').click()
    page.wait_for_function(BEST_READY, timeout=20000)
    return page.locator("#best-container").inner_text()


def test_planning_loads(page, base_url) -> None:
    page.goto("/planning")
    assert page.locator("#planning-form").is_visible()


def test_calculation_generates_66_alternatives(page, seeded) -> None:
    text = _calculate(page, 3)
    # Шаг дискретизации 10% → 66 альтернатив
    assert "66" in text


def test_profiles_produce_different_plans(page, seeded) -> None:
    conservative = _calculate(page, 1)
    aggressive = _calculate(page, 5)

    # Планы должны различаться — критерии ортогональны, профили реально влияют
    assert conservative != aggressive
    # Консервативный тянет в резерв, агрессивный — в цели
    assert "Резерв" in conservative
    assert "Цел" in aggressive


def test_best_plan_metrics_render(page, seeded) -> None:
    _calculate(page, 3)
    for sel in ("#plan-rt", "#plan-lt", "#plan-dt"):
        assert page.locator(sel).inner_text().strip() != "—", sel
    # Ликвидность плана — в месяцах
    assert "мес" in page.locator("#plan-lt").inner_text()


def test_rbench_cbr_button_keeps_valid_rate(page, base_url) -> None:
    page.goto("/planning")
    page.locator("#rbench-cbr").click()
    page.wait_for_timeout(2500)
    # Независимо от доступности cbr.ru значение остаётся валидной ставкой в %
    assert "%" in page.locator("#rbench-value").inner_text()
