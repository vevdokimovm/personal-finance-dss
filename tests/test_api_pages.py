"""Страницы продукта отдаются сервером (v8.47.0 — файл переписан после сноса Jinja).

## История файла

Изначально здесь проверялась разметка Jinja-шаблонов. В v8.45.0 файл сузился до двух
серверных страниц (`/validation`, `/contacts`), в v8.47.0 Jinja снесена целиком — и
проверять разбором HTML стало нечего: сервер отдаёт SPA, разметку строит браузер.

🔴 **Прежняя редакция стала бы ЛОЖНО зелёной.** Она проверяла `/static/js/app.js` и
`/static/css/styles.css` кодом 200 — а catch-all SPA отвечает `index.html` на любой
неизвестный путь. То есть после сноса статики тест продолжал бы проходить, «подтверждая»
доступность файлов, которых больше нет. Родня PIT-021: проверка отвечала на свой вопрос,
но вопрос был не тот.

Что осталось здесь: адреса, которые продукт обещает снаружи, действительно отвечают
приложением. Содержимое экранов проверяют vitest и Playwright, а факт «сервер отдаёт
React, а не что-то другое» — `tests/test_spa_is_actually_served.py`.
"""
from __future__ import annotations

import pytest

from tests.support.workstation import requires_spa_build
from fastapi.testclient import TestClient

# Публичные адреса: доступны без входа, на них ведут ссылки извне и закладки.
PUBLIC_PATHS = ["/", "/legal/privacy", "/legal/terms", "/legal/cookies", "/login", "/register"]

# Адреса, оставшиеся от Jinja. Ссылок в продукте нет, но есть закладки и история —
# для них это должно быть приложение, а не страница «не найдено».
LEGACY_PATHS = ["/dashboard", "/validation", "/contacts"]


@pytest.mark.parametrize("path", PUBLIC_PATHS + LEGACY_PATHS)
@requires_spa_build
def test_path_serves_the_app(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, path
    assert "text/html" in response.headers.get("content-type", ""), path


def test_removed_static_is_gone_from_the_repo() -> None:
    """🔴 Проверка по ДИСКУ, а не по коду ответа.

    Спрашивать сервер бессмысленно: catch-all отдаёт `index.html` на любой путь, и
    `/static/js/app.js` вернёт 200 независимо от того, существует файл или нет. Именно
    на этом прежняя редакция теста была бы ложно зелёной.

    Каталоги перенесены в `docs/legacy_jinja/` (архив), а не удалены: удаление
    необратимо и остаётся решением владельца.
    """
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    for gone in ("frontend/templates", "frontend/static"):
        assert not (repo / gone).exists(), f"{gone} всё ещё в сборке фронта"
    assert (repo / "docs/legacy_jinja/templates").is_dir(), "архив Jinja потерян"


def test_spa_icons_are_served(client: TestClient) -> None:
    """Фавиконки живут в сборке, а не в снесённой статике.

    До v8.47.0 их подключал только `base.html`; у SPA не было ни иконки, ни описания —
    вкладка стояла безымянной. Не заметили за сорок с лишним версий, потому что React
    работал только в dev (PIT-020).
    """
    from pathlib import Path

    public = Path(__file__).resolve().parents[1] / "frontend" / "public"
    for icon in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
        assert (public / icon).is_file(), f"{icon} не попал в сборку"

    index = (Path(__file__).resolve().parents[1] / "frontend" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'rel="icon"' in index, "index.html не подключает иконку"
    assert 'name="description"' in index, "нет описания страницы — оно идёт в выдачу поиска"
