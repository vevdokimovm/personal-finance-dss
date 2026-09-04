"""React-приложение реально отдаётся сервером, а не только живёт в dev (v8.45.0).

## Что вскрылось

Веха 8 закрыла сорок с лишним версий фронта — и **ни одна из них не работала нигде,
кроме машины разработчика**. Проверено запуском (`TestClient`, редакция v8.44.1):

    GET /transactions  → 200, Jinja-шаблон
    GET /legal/privacy → 200, Jinja-шаблон
    GET /              → 200, Jinja-шаблон

React отвечал только через `npm run dev`: Vite на 5173 с прокси `/api` на 8000. В
продакшн-контейнере его нет вовсе — `Dockerfile` фронт не собирает (нет node-стадии,
нет `npm run build`), `frontend/dist` лежит в `.gitignore` и потому не попадает даже
в `COPY . .`, а FastAPI никуда его не монтирует.

CI собирает фронт (`ci.yml`: `npm run build`) — и **выбрасывает артефакт**: сборка там
служит проверкой, что код компилируется, а не источником того, что поедет в прод.

## Почему это не заметили сорок версий

Каждый батч проверялся vitest, playwright и глазами на `localhost:5173` — там всё
работает. Никто ни разу не открыл `localhost:8000` без Vite. «E2E зелёный» ничего об
этом не говорит: Playwright поднимает тот же dev-сервер.

Тот же класс, что PIT-019 (e2e шёл в одном браузере из трёх): проверка была, покрывала
не то, и зелёный означал «не проверялось».

## Почему гейт стоит здесь, а не в e2e

E2E работает через Vite по построению. Единственное место, где видно, что отдаёт САМ
сервер, — вызов приложения напрямую. Поэтому проверка живёт в pytest.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DIST = REPO_ROOT / "frontend" / "dist"

# Маршруты вехи 8: их обслуживает React, и Jinja-версия для них снесена или снимается.
SPA_ROUTES = ["/transactions", "/goals", "/obligations", "/planning", "/legal/privacy"]

pytestmark = pytest.mark.skipif(
    not (DIST / "index.html").is_file(),
    reason=(
        "frontend/dist не собран (`npm run build`). Пропуск ЗДЕСЬ законен: dist лежит "
        "в .gitignore, и на чистом клоне его нет. В CI сборка обязательна — джоба "
        "frontend делает build до этого гейта."
    ),
)


def _is_spa(html: str) -> bool:
    """Отдана сборка Vite, а не шаблон Jinja.

    Признак — корневой узел приложения и подключённый бандл. Проверять по отсутствию
    Jinja-разметки нельзя: отрендеренный шаблон синтаксиса уже не содержит, и такая
    проверка была бы зелёной на чём угодно.
    """
    return 'id="root"' in html and "/assets/" in html


@pytest.mark.parametrize("path", SPA_ROUTES)
def test_spa_routes_serve_the_app(client, path) -> None:
    """🔴 Главный пункт: сервер отдаёт React, а не Jinja.

    До v8.45.0 здесь приходил Jinja-шаблон — то есть в продакшене работала старая
    версия продукта, а вся веха 8 существовала только в dev.
    """
    response = client.get(path)
    assert response.status_code == 200, path
    assert _is_spa(response.text), (
        f"{path} отдаёт не SPA. В проде это означает старый интерфейс вместо нового: "
        f"первые 200 символов — {response.text[:200]!r}"
    )


def test_deep_link_survives_reload(client) -> None:
    """Прямой заход по адресу вложенного маршрута отдаёт приложение, а не 404.

    Маршрутизация клиентская: сервер о `/legal/privacy` ничего не знает и обязан отдать
    `index.html`, дальше роутер разберётся сам. Без этого ссылка из письма, закладка
    и обычный F5 на любом экране дают 404 — при том, что переход внутри приложения
    работает, и дефект незаметен в разработке.
    """
    response = client.get("/legal/privacy")
    assert response.status_code == 200
    assert _is_spa(response.text)


def test_api_is_not_swallowed_by_the_spa(client) -> None:
    """🔴 Fallback не съедает API.

    Catch-all, поставленный слишком широко, отвечает `index.html` на `/api/...` — и фронт
    получает HTML там, где ждёт JSON. Ломается всё сразу и непонятно: запросы «проходят»
    с кодом 200.
    """
    response = client.get("/api/legal/documents")
    assert response.headers["content-type"].startswith("application/json")
    assert "documents" in response.json()


def test_unknown_api_path_is_404_not_index(client) -> None:
    """Несуществующий эндпоинт остаётся 404, а не превращается в страницу.

    Иначе опечатка в адресе запроса выглядит как успешный ответ, и разбираться в этом
    приходится по содержимому, а не по коду.
    """
    assert client.get("/api/no-such-endpoint").status_code == 404


def test_static_assets_are_served(client) -> None:
    """Бандл и стили доступны по тем адресам, которые прописаны в `index.html`.

    Отданный `index.html` без ассетов — белый экран: страница есть, приложения нет.
    Адреса берутся из самой сборки, а не выдумываются: имена файлов содержат хеш
    и меняются при каждой сборке.
    """
    import re

    html = (DIST / "index.html").read_text(encoding="utf-8")
    assets = re.findall(r'(?:src|href)="(/assets/[^"]+)"', html)
    assert assets, "в index.html нет ссылок на /assets — сборка выглядит пустой"
    for asset in assets:
        response = client.get(asset)
        assert response.status_code == 200, f"{asset} не отдаётся — будет белый экран"
