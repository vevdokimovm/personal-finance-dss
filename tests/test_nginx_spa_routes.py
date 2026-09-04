"""Согласованность nginx SPA-маршрутизации с реальными React-роутами и легаси-навигацией.

Найдено 2026-08-19: `frontend/templates/base.html` (легаси Jinja-навигация, живёт рядом
с React SPA — v8.23.0, частичный снос) ссылается на `/dashboard`, но React-дашборд живёт
на `/` (`frontend/src/routes/index.tsx`) — по этой ссылке nginx (`nginx/templates/
finpilot.conf.template`) отдаёт легаси Jinja-дашборд с формой бюджета вместо актуального
React-экрана. Разбор — `docs/ROADMAP.md` §9.0 «A».
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NGINX_TEMPLATE = REPO_ROOT / "nginx" / "templates" / "finpilot.conf.template"
ROUTES_DIR = REPO_ROOT / "frontend" / "src" / "routes"

# Файлы, которые не являются страницей приложения: __root.tsx — layout, не роут;
# index.tsx — маршрут "/", покрыт отдельным location-блоком nginx (`location = /`),
# не входит в alternation SPA-regex.
NON_PAGE_ROUTE_FILES = {"__root.tsx", "index.tsx"}


def _spa_regex_alternation() -> str:
    """Список путей внутри `location ~ ^/(...)(/|$)` из nginx-шаблона."""
    text = NGINX_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"location ~ \^/\(([^)]+)\)\(/\|\$\)", text)
    assert match, "SPA location-блок с alternation не найден в nginx-шаблоне"
    return match.group(1)


def _frontend_route_path_segments() -> set[str]:
    """Имена файлов routes/*.tsx (кроме __root.tsx и index.tsx) как ожидаемые URL-сегменты —
    TanStack file-based routing: `forgot-password.tsx` -> `/forgot-password`."""
    return {
        path.stem
        for path in ROUTES_DIR.glob("*.tsx")
        if path.name not in NON_PAGE_ROUTE_FILES
    }


def test_nginx_spa_regex_covers_every_frontend_route_file():
    """Регрессионная защита на будущее: новый корневой роут во фронте обязан попасть
    в nginx SPA-блок, иначе он тихо уедет на FastAPI/Jinja вместо React. Зелёный сейчас
    (все текущие роуты покрыты) — красный автоматически, если кто-то добавит routes/*.tsx
    и забудет обновить nginx-шаблон."""
    alternation = _spa_regex_alternation()
    covered = set(alternation.split("|"))
    missing = _frontend_route_path_segments() - covered
    assert not missing, (
        f"Роуты фронта без покрытия в SPA-блоке nginx: {sorted(missing)} — "
        f"nginx/templates/finpilot.conf.template"
    )


# 🔴 `test_base_html_dashboard_link_points_to_react_dashboard_root` снят в v8.47.0
# вместе с Jinja: он проверял ссылку «Обзор» в `frontend/templates/base.html`, а шаблона
# больше нет (архив — `docs/legacy_jinja/`). Дефект, который он сторожил, закрыт иначе
# и надёжнее: `/dashboard` теперь редиректит на `/` и в nginx (тест ниже), и в самом
# роутере (`frontend/src/routes/dashboard.tsx`) — то есть работает и без nginx.

def test_nginx_redirects_legacy_dashboard_path_to_spa_root():
    """Старые закладки/внешние ссылки на `/dashboard` не должны молча падать на легаси
    Jinja — постоянный редирект на канонический `/` (тот же приём, что нужен для любого
    URL, который раньше существовал, а теперь имеет единственный канонический адрес)."""
    text = NGINX_TEMPLATE.read_text(encoding="utf-8")
    assert re.search(r"location\s*=\s*/dashboard\s*\{[^}]*return\s+301\s+/[;\s]", text), (
        "nginx-шаблон не редиректит /dashboard на канонический '/' — "
        "старые ссылки на /dashboard будут отдавать легаси Jinja вместо React SPA"
    )
