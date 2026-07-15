"""
Визуальная регрессия через скриншоты Playwright (предрелизный тир `full`).

Идея. UI ломается незаметно: правка CSS сдвигает вёрстку, тема перестаёт
применяться, элемент уезжает. Юнит/E2E на селекторах этого не видят — кнопка
на месте, но страница «поехала». Скриншот-регрессия фиксирует эталонный рендер
ключевых страниц В ОБЕИХ ТЕМАХ и сравнивает с ним каждый предрелизный прогон.

Поведение. Первый прогон (эталона ещё нет) — создаёт baseline в `__screenshots__/`
и скипается. Последующие — сравнивают пиксельно: если доля различий выше порога,
тест падает с указанием страницы и темы.

Эталоны платформо-зависимы (рендер шрифтов отличается между ОС), поэтому
`__screenshots__/` НЕ коммитится (см. .gitignore) и генерируется в CI на
фиксированной платформе (Linux). В песочнице прогон проверяет, что МЕХАНИЗМ
работает: первый проход создаёт эталон, повторный — совпадает в пределах порога.

Покрытие: 14 публичных страниц × 2 темы. Тир `full`: нужен браузер, гоняется
перед тегом/релизом. Pillow используется для диффа; если его нет — тест скипается.
"""
from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.full, pytest.mark.e2e]

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "__screenshots__")
# Допуск на канал: пиксель считается значимо изменённым, только если хотя бы один
# канал отличается больше этого порога. Микро-различия субпиксельного антиалиасинга
# глифов (особенно на текстовых страницах) так не засчитываются, а структурный
# сдвиг вёрстки/смена цвета — да. Аналог threshold в pixelmatch.
CHANNEL_TOLERANCE = 40
# Доля ЗНАЧИМО различающихся пикселей, выше которой считаем регрессией.
DIFF_THRESHOLD = 0.02

# Реальные публичные страницы (200). Битые пути прежней версии убраны: /login —
# страницы нет by design (вход через модалку), /legal — только /legal/{...}.
PAGES = [
    "/", "/dashboard", "/planning", "/transactions", "/obligations", "/goals",
    "/banks", "/validation", "/profile", "/contacts",
    "/legal/privacy", "/legal/terms", "/legal/consent",
    "/forgot-password",
]
THEMES = ["dark", "light"]


def _stabilize(page) -> None:
    """Убирает источники недетерминизма перед снимком: ждёт шрифты, замораживает
    анимации/переходы, скрывает canvas (графики Chart.js анимируются и рендерятся
    по-разному каждый раз — место сохраняется через visibility, layout не плывёт).

    Шапка содержит auth-кнопки, которые auth.js показывает/скрывает асинхронно
    после запроса /api/auth/me — даём этому завершиться, иначе снимок ловит разные
    фазы (различие по верхней зоне страницы)."""
    try:
        page.evaluate("async () => { await document.fonts.ready; }")
    except Exception:
        pass
    page.add_style_tag(content=(
        "*,*::before,*::after{animation:none!important;transition:none!important;"
        "animation-duration:0s!important;animation-delay:0s!important;"
        "transition-duration:0s!important;caret-color:transparent!important}"
        "canvas{visibility:hidden!important}"
    ))
    try:
        page.wait_for_load_state("networkidle")
    except Exception:
        pass
    page.wait_for_timeout(900)


def _pixel_diff_ratio(a_bytes: bytes, b_bytes: bytes) -> float:
    from io import BytesIO

    try:
        from PIL import Image, ImageChops
    except ImportError:
        pytest.skip("Pillow не установлен — дифф скриншотов недоступен")

    img_a = Image.open(BytesIO(a_bytes)).convert("RGB")
    img_b = Image.open(BytesIO(b_bytes)).convert("RGB")
    if img_a.size != img_b.size:
        return 1.0
    diff = ImageChops.difference(img_a, img_b)
    if diff.getbbox() is None:
        return 0.0
    # Значим только пиксель, у которого максимальное отклонение по каналам выше
    # допуска — это отсекает субпиксельный шум антиалиасинга, оставляя реальные сдвиги.
    changed = sum(1 for px in diff.getdata() if max(px) > CHANNEL_TOLERANCE)
    return changed / (img_a.size[0] * img_a.size[1])


@pytest.mark.parametrize("path", PAGES)
@pytest.mark.parametrize("theme", THEMES)
def test_page_matches_baseline(page, base_url: str, path: str, theme: str):
    """Рендер страницы в заданной теме совпадает с эталонным скриншотом (в пределах порога)."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    slug = (path.strip("/") or "home").replace("/", "_")
    baseline_path = os.path.join(SNAPSHOT_DIR, f"{slug}__{theme}.png")

    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(base_url + path, wait_until="networkidle")
    # Тема хранится под ключом finpilot-theme и применяется скриптом base.html
    # при загрузке — ставим значение и перезагружаем перед снимком.
    page.evaluate(f"localStorage.setItem('finpilot-theme', '{theme}')")
    page.reload(wait_until="networkidle")
    _stabilize(page)
    # Маскируем динамическую auth-зону шапки (#auth-widget): её содержимое
    # auth.js обновляет асинхронно (статус/кнопки входа), что даёт нестабильные
    # пиксели между прогонами. Маска закрашивает зону ровным цветом — структурную
    # регрессию вёрстки это не прячет, а шум убирает.
    current = page.screenshot(
        full_page=True,
        mask=[page.locator("#auth-widget")],
        mask_color="#FF00FF",
    )

    if not os.path.exists(baseline_path):
        with open(baseline_path, "wb") as fh:
            fh.write(current)
        pytest.skip(f"baseline создан для {path} [{theme}]")

    with open(baseline_path, "rb") as fh:
        baseline = fh.read()

    ratio = _pixel_diff_ratio(baseline, current)
    assert ratio <= DIFF_THRESHOLD, (
        f"{path} [{theme}]: визуальная регрессия, различий {ratio:.1%}"
    )
