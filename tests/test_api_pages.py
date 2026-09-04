"""Серверный рендер страниц, которые сервер ДЕЙСТВИТЕЛЬНО рендерит.

🔴 Файл сузился в v8.45.0. Раньше здесь проверялась разметка Jinja-шаблонов `/`,
`/planning`, `/transactions`, `/obligations`, `/goals`, `/banks` — но эти экраны с v8.45.0
отдаёт React, и сервер присылает пустой shell: разметка строится в браузере, разбирать
ответ нечего. Оставить проверки как были значило бы получить зелёный тест, не проверяющий
ничего, — ровно то, ради чего заведён PIT-020.

**Покрытие не потеряно, оно переехало туда, где разметка существует:**

| Что проверялось здесь | Где проверяется теперь |
|---|---|
| контейнер прогноза и советы по тратам (`/planning`) | `pages/planning/**` — vitest |
| привязка цели к активу (`/goals`) | `pages/goals/**` — vitest |
| поле срока обязательства (`/obligations`) | `pages/obligations/**` — vitest |
| Lt в месяцах автономии, BLR отдельно от Lt | `widgets/metrics-grid/MetricsGrid.test.tsx` |
| `l_min` в месяцах, источники `r_bench` | `pages/planning/ui/PlanSettingsSection.tsx` |

Плюс Playwright в трёх браузерах на тех же экранах и `tests/test_spa_is_actually_served.py`
— проверка, что сервер вообще отдаёт React, а не старый интерфейс.

Здесь остались страницы, которые остаются серверными: `/validation` (гостевая песочница)
и `/contacts`.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

PAGES = ["/validation", "/contacts"]


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(client: TestClient, path: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert len(resp.text) > 500  # не пустая заглушка


def test_app_js_and_css_served(client: TestClient) -> None:
    """Статика Jinja-страниц отдаётся.

    Она нужна, пока живы `/validation` и `/contacts`: их шаблоны наследуют `base.html`
    и подключают эти файлы. Уйдёт вместе с ними при сносе Jinja-остатка.
    """
    js = client.get("/static/js/app.js")
    css = client.get("/static/css/styles.css")
    assert js.status_code == 200
    assert css.status_code == 200
