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
SRC_DIR = REPO_ROOT / "frontend" / "src"
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
    """Значения `to:` из ОБОИХ списков навигации — общего и владельческого.

    🔴 `OWNER_NAV_ITEMS` (v8.48.0) — разделы, видимые только владельцу продукта
    (`is_owner`). Они достижимы кликом, просто не всеми: сервер отдаёт остальным 403,
    и показывать такой пункт всем значило бы вести в гарантированный отказ ([IA-04]).
    Гейт спрашивает «можно ли дойти кликом», а не «видит ли пункт каждый», поэтому
    оба списка равноправны.

    Читаем исходник, а не импортируем TS — у pytest нет тулчейна фронта, а разбор
    литерала честнее заглушки.
    """
    text = NAV_ITEMS.read_text(encoding="utf-8")
    return set(re.findall(r'\{\s*to:\s*"([^"]+)"', text))


def _is_redirect_only(path: Path) -> bool:
    """Маршрут-редирект — не экран: он ничего не рендерит и мгновенно уводит.

    🔴 Признак СТРУКТУРНЫЙ (`beforeLoad` + `redirect(`, без `component`), а не список
    имён файлов: список пришлось бы пополнять руками при каждом новом редиректе, то есть
    гейт снова держался бы на внимательности. Заведено в v8.46.0 вместе с `/dashboard`,
    который перенаправляет на `/`: адрес остался от Jinja, ссылок на него в продукте нет,
    но есть закладки и внешние ссылки.

    Требовать для такого маршрута пункт меню значило бы завести в навигации второй вход
    в тот же экран.
    """
    text = path.read_text(encoding="utf-8")
    return "redirect(" in text and "component:" not in text


def _screen_route_paths() -> set[str]:
    """Файлы `routes/*.tsx` как URL-пути (TanStack file-based routing:
    `index.tsx` -> `/`, `forgot-password.tsx` -> `/forgot-password`)."""
    paths = set()
    for path in ROUTES_DIR.glob("*.tsx"):
        if path.name in LAYOUT_ROUTE_FILES or path.name in AUTH_ROUTE_FILES:
            continue
        if _is_redirect_only(path):
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
    """Каркас не показывается тому, кто не вошёл.

    🔴 Условие обновлено в v9.1.0. Здесь закреплялось `if (!data || error) return null` —
    и оно убирало меню при ЛЮБОЙ ошибке профиля, включая сетевую, когда человек вошёл
    и данные лежат в кэше. Экран визуально «ломался» из-за моргнувшей сети.

    Теперь вид ошибки различается: 401 меню убирает (человек больше не вошёл, и разделы
    за гейтом отдадут отказ — семь ссылок стали бы семью тупиками), сетевая — нет.
    Гейт проверяет оба условия, а не текст одной строки: проверка на подстроку
    закрепляла бы конкретную формулировку вместо поведения.
    """
    source = (REPO_ROOT / "frontend" / "src" / "widgets" / "app-nav" / "AppNav.tsx").read_text(
        encoding="utf-8"
    )
    assert "if (!data) return null;" in source, (
        "AppNav обязан скрывать каркас от гостя: без данных профиля показывать "
        "нечего, а семь ссылок в 403 — это семь тупиков ([IA-04])"
    )
    assert "isSessionExpired(error)" in source, (
        "AppNav обязан убирать меню при ИСТЁКШЕЙ сессии: разделы за гейтом отдадут "
        "401/403, и ссылки станут тупиками. Сетевую ошибку при живом кэше — не убирать"
    )


def test_navigation_labels_match_screen_headings():
    """[CMP-03]: одно понятие — одно слово везде. Подпись пункта обязана дословно
    совпадать с `<h1>` своего экрана, иначе меню и заголовок называют одно разными
    словами — самый частый разнобой терминологии в интерфейсе."""
    expected = {
        "/": "Финансовый обзор",
        "/planning": "План распределения",
        "/transactions": "Операции",
        "/spending": "Советы по расходам",
        "/obligations": "Кредиты и обязательства",
        "/goals": "Цели",
        "/banks": "Ликвидные активы",
        "/household": "Семейный доступ",
        "/profile": "Профиль",
        # Разделы владельца продукта (`OWNER_NAV_ITEMS`). Регулярка ниже читает ОБА
        # списка одним проходом, поэтому владельческие пункты обязаны быть и здесь.
        #
        # 🔴 Этот тест был красным с v8.48.0: `/insights` завели в навигацию и не
        # пополнили словарь. Увидели только сейчас, потому что полный прогон в том
        # батче не довели до конца — ровно та цена, о которой предупреждает
        # запись «до полного прогона версию считать непроверенной».
        "/insights": "Метрики продукта",
        "/experiments": "A/B-эксперименты",
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
# Тот же адрес, но вместе с именем query-параметра: `/join?token=`, `/register?ref=`.
_BACKEND_PARAM_RE = re.compile(r'\+\s*f?"(/[a-z][a-z0-9\-/]*)\?([a-z_]+)=')


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


def _backend_built_params() -> dict[str, tuple[str, str]]:
    """`{путь: (имя параметра, файл-источник)}` для ссылок вида `/join?token=...`."""
    found: dict[str, tuple[str, str]] = {}
    for source in BACKEND_URL_SOURCES:
        if not source.exists():
            continue
        for match in _BACKEND_PARAM_RE.finditer(source.read_text(encoding="utf-8")):
            path, param = match.group(1), match.group(2)
            if path.startswith("/api/"):
                continue
            found.setdefault(path, (param, source.name))
    return found


def test_backend_built_link_params_are_read_by_the_screen():
    """Мало, чтобы экран СУЩЕСТВОВАЛ — он обязан ЧИТАТЬ параметр из ссылки.

    🔴 Найдено 2026-09-03 при выносе рефералки: `routes_referral.py` строит
    `/register?ref=CODE`, роут `/register` существует и открывается — а `RegisterPage`
    параметр `ref` не читал вовсе и `referral_code` в запрос не клал. То есть
    приглашение открывалось, регистрация проходила и не засчитывалась НИКОМУ.

    Это злее мёртвой ссылки: мёртвую видно сразу (человек упирается в пустоту), а здесь
    всё выглядит рабочим — дефект обнаруживается только тем, что счётчик приглашений
    у всех остаётся нулём. Предыдущий гейт (существование роута) такое пропускает
    по построению, поэтому проверок две, а не одна.
    """
    unread: list[str] = []
    for path, (param, source) in _backend_built_params().items():
        route_file = ROUTES_DIR / f"{path.lstrip('/')}.tsx"
        if not route_file.exists():
            continue  # мёртвый роут ловит соседний тест, здесь не дублируем
        # Экран роута может быть тонкой обёрткой над страницей — ищем по всему `src`,
        # но только в исходниках, не в сгенерированном клиенте.
        hits = [
            candidate
            for candidate in SRC_DIR.rglob("*.tsx")
            if "generated" not in candidate.parts
            and f"{param}?" in candidate.read_text(encoding="utf-8")
        ]
        if not hits:
            unread.append(f"{path}?{param}= ({source})")
    assert not unread, (
        "Бэкенд кладёт параметр в ссылку, а экран его не читает: "
        + ", ".join(sorted(unread))
        + ". Ссылка открывается, всё выглядит рабочим — и не срабатывает."
    )
