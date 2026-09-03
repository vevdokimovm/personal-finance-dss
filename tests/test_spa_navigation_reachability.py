"""Каждый экран продукта достижим кликом из навигационного каркаса.

Найдено 2026-09-02 (v8.30.2), гипотеза H1 independent-expert, подтверждена чтением кода:
в React-SPA не было навигационного каркаса ВООБЩЕ. Топбар состоял из `AuthTopbarLink`
(email + выход) и `ThemeToggle`; все восемь `<Link>` продукта вели на `/login`, `/register`
и `/forgot-password`; переходы между финансовыми экранами существовали в трёх местах
сырыми `<a href>`. Следствие: `/obligations`, `/goals`, `/banks` и `/profile` нельзя было
открыть кликом ниоткуда, а в `/profile` живёт отзыв согласия на обработку финансовых
данных — то есть право по 152-ФЗ было реализовано и недоступно.

Каркас заведён в v8.31.0. Этот тест защищает не его, а КЛАСС дефекта: экран, добавленный
позже и не попавший в навигацию, рождается недостижимым ровно так же и так же молча.
Симметричен `test_nginx_spa_routes.py` — там роут обязан попасть в SPA-блок nginx,
здесь тот же роут обязан попасть в меню.

Тот же класс, что SEV1 `CONSENT-GATE-NO-UI` (`docs/reports/incidents/
consent_gate_no_ui_dead_end_incident.md`): функция есть на бэкенде, пути к ней у
пользователя нет, и молчат обе стороны.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTES_DIR = REPO_ROOT / "frontend" / "src" / "routes"
NAV_ITEMS = REPO_ROOT / "frontend" / "src" / "widgets" / "app-nav" / "navItems.ts"
APP_NAV = REPO_ROOT / "frontend" / "src" / "widgets" / "app-nav" / "AppNav.tsx"

# `__root.tsx` — layout, не экран.
LAYOUT_ROUTE_FILES = {"__root.tsx"}

# Экраны аутентификации в каркас НЕ входят осознанно: каркас показывается только
# авторизованному (см. AppNav — гостю все семь финансовых экранов отдают 401/403,
# ссылки были бы тупиками, [IA-04]). Вход и регистрация достижимы из `AuthTopbarLink`,
# восстановление пароля — со страницы входа. Список закрытый: новый роут сюда
# добавляется только вместе с ответом, откуда на него попадает пользователь.
AUTH_ROUTE_FILES = {
    "login.tsx",
    "register.tsx",
    "forgot-password.tsx",
    "reset-password.tsx",
    # `/join` — приём приглашения по ссылке из письма, а не раздел продукта. Пункта
    # меню у него быть не должно: попасть туда осмысленно можно только по адресу
    # с токеном, а без токена экран честно говорит, что ссылка неполная.
    "join.tsx",
}


def _nav_paths() -> set[str]:
    """Значения `to:` из APP_NAV_ITEMS. Читаем исходник, а не импортируем TS —
    у pytest нет тулчейна фронта, а разбор одного литерала честнее заглушки."""
    text = NAV_ITEMS.read_text(encoding="utf-8")
    return set(re.findall(r'\{\s*to:\s*"([^"]+)"', text))


def _screen_route_paths() -> set[str]:
    """Файлы `routes/*.tsx` как URL-пути (TanStack file-based routing:
    `index.tsx` -> `/`, `forgot-password.tsx` -> `/forgot-password`)."""
    paths = set()
    for path in ROUTES_DIR.glob("*.tsx"):
        if path.name in LAYOUT_ROUTE_FILES or path.name in AUTH_ROUTE_FILES:
            continue
        paths.add("/" if path.name == "index.tsx" else f"/{path.stem}")
    return paths


def test_every_screen_is_reachable_from_navigation():
    """Регрессионная защита на будущее: новый экран во фронте обязан попасть в
    APP_NAV_ITEMS, иначе он существует и недостижим кликом — ровно дефект H1.
    Если экран сознательно вне меню, его файл добавляется в AUTH_ROUTE_FILES
    вместе с ответом, откуда на него попадает пользователь."""
    unreachable = _screen_route_paths() - _nav_paths()
    assert not unreachable, (
        f"Экраны без пункта в навигации: {sorted(unreachable)} — "
        f"frontend/src/widgets/app-nav/navItems.ts. Экран, до которого нельзя "
        f"дойти кликом, для пользователя не существует."
    )


def test_navigation_has_no_links_to_nonexistent_screens():
    """Обратная сторона: пункт меню, ведущий на несуществующий роут, — это 404
    по клику из постоянного каркаса, то есть на каждом экране сразу."""
    all_route_paths = {
        "/" if path.name == "index.tsx" else f"/{path.stem}"
        for path in ROUTES_DIR.glob("*.tsx")
        if path.name not in LAYOUT_ROUTE_FILES
    }
    dangling = _nav_paths() - all_route_paths
    assert not dangling, (
        f"Пункты навигации без роута: {sorted(dangling)} — "
        f"frontend/src/widgets/app-nav/navItems.ts"
    )


def test_navigation_is_hidden_from_guests():
    """Каркас не показывается неавторизованному. Проверка структурная (юнит-тесты
    поведения — `AppNav.test.tsx`), но она ловит снятие условия при рефакторинге:
    без него гость получил бы семь ссылок в гейт согласия, то есть семь тупиков."""
    source = APP_NAV.read_text(encoding="utf-8")
    assert "if (!data || error) return null;" in source, (
        "AppNav обязан скрывать каркас от гостя. Проверка `data` в одиночку "
        "воспроизводит баг stale-if-error, пойманный на топбаре: TanStack Query "
        "держит последние успешные data, когда рефетч упал на 401."
    )


def test_navigation_labels_match_screen_headings():
    """[CMP-03]: одно понятие — одно слово везде. Подпись пункта обязана дословно
    совпадать с `<h1>` своего экрана, иначе меню и заголовок называют одно разными
    словами — самый частый разнобой терминологии в интерфейсе."""
    expected = {
        "/": "Финансовый обзор",
        "/planning": "План распределения",
        "/transactions": "Операции",
        "/obligations": "Кредиты и обязательства",
        "/goals": "Цели",
        "/banks": "Ликвидные активы",
        "/household": "Семейный доступ",
        "/profile": "Профиль",
    }
    text = NAV_ITEMS.read_text(encoding="utf-8")
    actual = dict(re.findall(r'\{\s*to:\s*"([^"]+)",\s*label:\s*"([^"]+)"\s*\}', text))
    assert actual == expected, (
        "Подписи разделов разошлись с заголовками экранов — "
        "frontend/src/widgets/app-nav/navItems.ts"
    )


NOTIFICATIONS = REPO_ROOT / "app" / "services" / "notifications.py"


def _notification_links() -> set[str]:
    """Значения `link=` из уведомлений, которые создаёт бэкенд."""
    text = NOTIFICATIONS.read_text(encoding="utf-8")
    return set(re.findall(r'link="([^"]+)"', text))


def test_notification_links_point_to_existing_screens():
    """Уведомление ведёт туда, где экран есть (гипотеза H12 independent-expert).

    Найдено 2026-09-03 при выносе уведомлений на фронт (v8.32.0): бэкенд ставил
    `link="/budgets"`, а роута `/budgets` в SPA нет вовсе — бюджеты живут секцией
    на дашборде (`BudgetsSection`, v8.30.0). До этого батча промах был невидим:
    ссылку никто не открывал, потому что ленты на фронте не существовало. С
    колокольчиком клик по такому уведомлению уводил бы пользователя в никуда —
    причём по уведомлению «Превышен бюджет», то есть ровно там, где он ждёт помощи.

    Тест сравнивает адреса из `app/services/notifications.py` с реальными файлами
    роутов, а не со списком в голове: список разойдётся, файлы — нет.
    """
    all_routes = {
        "/" if path.name == "index.tsx" else f"/{path.stem}"
        for path in ROUTES_DIR.glob("*.tsx")
        if path.name not in LAYOUT_ROUTE_FILES
    }
    dead = _notification_links() - all_routes
    assert not dead, (
        f"Уведомления ведут на несуществующие экраны: {sorted(dead)} — "
        f"app/services/notifications.py. Клик по такому уведомлению уводит "
        f"пользователя в никуда."
    )


# Бэкенд строит ссылки во ФРОНТ в нескольких местах: приглашение в household, сброс
# пароля, реферальная ссылка. Все они уходят пользователю письмом или копированием —
# то есть проверить их «глазами при разработке» невозможно, а сломанная ссылка
# обнаруживается только жалобой.
BACKEND_URL_SOURCES = (
    REPO_ROOT / "app" / "api" / "routes_households.py",
    REPO_ROOT / "app" / "api" / "routes_auth.py",
    REPO_ROOT / "app" / "api" / "routes_referral.py",
)

# `/api/...` — обращения к самому бэкенду, во фронт они не ведут и роутом SPA быть
# не обязаны (напр. `/api/auth/verify?token=` — серверный эндпоинт подтверждения).
_FRONTEND_URL_RE = re.compile(r'\+\s*f?"(/[a-z][a-z0-9\-/]*)')


def _backend_built_frontend_paths() -> dict[str, str]:
    """Пути во фронт, которые бэкенд склеивает с `base_url`. Ключ — путь,
    значение — файл, где он собран (чтобы сообщение теста называло адрес починки)."""
    found: dict[str, str] = {}
    for source in BACKEND_URL_SOURCES:
        if not source.exists():
            continue
        for match in _FRONTEND_URL_RE.finditer(source.read_text(encoding="utf-8")):
            path = match.group(1)
            if path.startswith("/api/"):
                continue
            found.setdefault(path, source.name)
    return found


def test_backend_built_links_point_to_existing_screens():
    """Ссылка, которую бэкенд кладёт в письмо или отдаёт для копирования, обязана вести
    на существующий экран (гипотеза H12 independent-expert, второй случай класса).

    Найдено 2026-09-03: `routes_households.py::_invite_url` строит `/join?token=...`,
    а роута `/join` в SPA нет вовсе — приглашение в семейный доступ вело в никуда.
    Первый случай того же класса (`link="/budgets"` в уведомлениях) был починен в
    v8.34.0, и тогда гейт закрыл ТОЛЬКО уведомления. Класс шире: любая ссылка,
    собранная на сервере, уходит пользователю письмом или копированием, и проверить
    её при разработке глазами невозможно — сломанная обнаруживается жалобой.

    Проверка идёт по РЕАЛЬНЫМ файлам роутов, а не по списку в голове: список
    разойдётся с деревом, дерево — нет.
    """
    all_routes = {
        "/" if path.name == "index.tsx" else f"/{path.stem}"
        for path in ROUTES_DIR.glob("*.tsx")
        if path.name not in LAYOUT_ROUTE_FILES
    }
    dead = {
        path: source
        for path, source in _backend_built_frontend_paths().items()
        if path not in all_routes
    }
    assert not dead, (
        "Бэкенд строит ссылки на несуществующие экраны: "
        + ", ".join(f"{path} ({source})" for path, source in sorted(dead.items()))
        + ". Пользователь получит такую ссылку письмом и упрётся в пустоту."
    )
