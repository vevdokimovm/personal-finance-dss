"""
Live-проверка доступности через axe-core (предрелизный тир `full`).

Чем отличается от `test_a11y_mechanical.py`. Механический тест парсит HTML и
проверяет инварианты разметки на статике. Этот — поднимает реальный браузер,
рендерит страницу со всем CSS/JS и прогоняет промышленный движок axe-core
(тот же, что Lighthouse/axe DevTools). Это ловит проблемы контраста, ARIA и
фокуса в РЕНДЕРЕ, а не только в исходнике.

Тир `full`: гоняется перед релизом/тегом, не в каждом push (нужен браузер).
axe-core подгружается с CDN в страницу; если CDN недоступен (офлайн-песочница)
или браузер не поставлен — тест аккуратно скипается, а не падает.
"""
from __future__ import annotations

import pytest

pytestmark = [pytest.mark.full, pytest.mark.e2e]

# Версия axe-core фиксирована для воспроизводимости результатов между прогонами.
AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"

# Страницы под аудит (публичные, без авторизации). Серьёзные нарушения (critical)
# недопустимы; серьёзность ниже трактуется как замечание и не валит прогон.
PAGES = ["/", "/planning", "/transactions", "/login", "/legal", "/contacts"]


def _run_axe(page, url: str) -> list[dict]:
    page.goto(url, wait_until="networkidle")
    try:
        page.add_script_tag(url=AXE_CDN)
    except Exception as exc:  # CDN недоступен в офлайн-песочнице
        pytest.skip(f"axe-core CDN недоступен: {exc}")
    results = page.evaluate(
        "async () => await axe.run(document, "
        "{runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa']}})"
    )
    return results.get("violations", [])


@pytest.mark.parametrize("path", PAGES)
def test_no_critical_a11y_violations(page, base_url: str, path: str):
    """На публичных страницах нет критических нарушений WCAG 2.1 A/AA (axe-core)."""
    violations = _run_axe(page, base_url + path)
    critical = [v for v in violations if v.get("impact") == "critical"]
    assert not critical, (
        f"{path}: критические нарушения a11y: "
        + ", ".join(v.get("id", "?") for v in critical)
    )
