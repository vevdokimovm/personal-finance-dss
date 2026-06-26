"""
Визуальная регрессия через скриншоты Playwright (предрелизный тир `full`).

Идея. UI ломается незаметно: правка CSS сдвигает вёрстку, тема перестаёт
применяться, элемент уезжает. Юнит/E2E на селекторах этого не видят — кнопка
на месте, но страница «поехала». Скриншот-регрессия фиксирует эталонный рендер
ключевых страниц и сравнивает с ним каждый предрелизный прогон.

Поведение. Первый прогон (эталона ещё нет) — создаёт baseline в
`__screenshots__/` и скипается. Последующие — сравнивают пиксельно: если доля
различий выше порога, тест падает с указанием страницы. Эталоны привязаны к
платформе рендера, поэтому генерируются и хранятся в CI (Linux), а не в песочнице.

Тир `full`: нужен браузер, гоняется перед тегом/релизом, не в каждом push.
Pillow используется только для диффа; если его нет — тест аккуратно скипается.
"""
from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.full, pytest.mark.e2e]

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "__screenshots__")
# Доля различающихся пикселей, выше которой считаем регрессией (антиалиасинг
# шрифтов даёт небольшой естественный шум — порог его поглощает).
DIFF_THRESHOLD = 0.02
PAGES = ["/", "/planning", "/transactions", "/login"]


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
    bbox = diff.getbbox()
    if bbox is None:
        return 0.0
    changed = sum(1 for px in diff.getdata() if px != (0, 0, 0))
    return changed / (img_a.size[0] * img_a.size[1])


@pytest.mark.parametrize("path", PAGES)
def test_page_matches_baseline(page, base_url: str, path: str):
    """Рендер страницы совпадает с эталонным скриншотом (в пределах порога)."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    name = (path.strip("/") or "home").replace("/", "_") + ".png"
    baseline_path = os.path.join(SNAPSHOT_DIR, name)

    page.goto(base_url + path, wait_until="networkidle")
    page.set_viewport_size({"width": 1280, "height": 800})
    current = page.screenshot(full_page=True)

    if not os.path.exists(baseline_path):
        with open(baseline_path, "wb") as fh:
            fh.write(current)
        pytest.skip(f"baseline создан для {path}")

    with open(baseline_path, "rb") as fh:
        baseline = fh.read()

    ratio = _pixel_diff_ratio(baseline, current)
    assert ratio <= DIFF_THRESHOLD, f"{path}: визуальная регрессия, различий {ratio:.1%}"
