"""Каждая пишущая ручка стоит за проверкой прав — или названа исключением.

## Что закрывает

`PUT /api/fx/rates` жил без единой зависимости, кроме сессии БД: аноним писал в общую
таблицу курсов, которую читает каждый расчёт, и менял рекомендацию всем пользователям
сразу. Соседний метод того же файла был закрыт `require_admin` с самого начала — защиту
знали, к этому методу не применили.

Через сутки тем же способом нашёлся `PATCH /api/user-prefs`: роутер подключён без
`_GUEST`, и аноним писал в общую строку настроек, откуда `l_min` идёт в фильтр
допустимости альтернатив.

🔴 **Оба раза дефект находили ЧТЕНИЕМ списка подключений** — глазами, по одному.
Проверка, которая держится на внимательности, повторяется ровно столько раз, сколько
раз в проект добавят роутер.

## Как устроено

Обход **реальных маршрутов приложения** (`app.routes`), а не исходников: берётся дерево
зависимостей каждой ручки целиком, включая унаследованные от роутера. Метод, меняющий
состояние, обязан иметь в этом дереве хотя бы одну проверку прав.

Публичные по замыслу ручки перечислены поимённо с причиной — список короткий и не
должен расти незаметно.
"""
from __future__ import annotations

from app.main import app

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

#: Зависимости, любая из которых означает «права проверены».
#
# 🔴 `require_financial_consent` сюда НЕ входит, хотя стоит на роутерах рядом.
# Это гейт СОГЛАСИЯ, а не прав: гостя он пропускает намеренно («согласие там
# означало бы сломать демо ради формальности», `_consent_guard.py`). Первая редакция
# этого списка его засчитывала — и гейт объявил защищённым `planning_router`,
# подключённый только с `_FIN`, где гость пишет снимки плана в общий пул.
# То есть проверка периметра сама пропустила ровно тот класс, против которого
# заведена. Найдено пятым проходом независимого аудита 08.09.2026.
AUTH_DEPENDENCIES = {
    "require_user",
    "require_admin",
    "require_account_for_writes",
}

#: Пишущие ручки, открытые НАМЕРЕННО. Каждая — с причиной.
PUBLIC_BY_DESIGN: dict[str, str] = {
    "/api/auth/register": "завести аккаунт может только тот, у кого его ещё нет",
    "/api/auth/login": "вход по определению до аутентификации",
    "/api/auth/logout": "выход не должен требовать живой сессии — иначе тупик",
    "/api/auth/forgot-password": "человек, забывший пароль, не может представиться",
    "/api/auth/reset-password": "право входа даёт одноразовый токен из письма",
    "/api/auth/mfa/verify": "второй фактор проверяется до выдачи полной сессии",
    "/api/fx/convert": "чистый расчёт: читает курсы и ничего не пишет",
    # 🔴 POST у этих трёх — не признак записи, а способ передать данные телом:
    # портрет для расчёта не помещается в query string. На них держится демо-песочница,
    # и запрет сломал бы её.
    #
    # 🔴 **Поправка к первой редакции этого списка.** Я написал «ни одна из них не пишет
    # в БД (проверено чтением)» — для `/planning/calculate` это НЕВЕРНО: она кладёт
    # две строки на каждый вызов, `Recommendation` и `Event`, через `log_*`. Чтением
    # этого не видно, потому что запись спрятана за именем логгера и идёт в собственной
    # сессии, а не в `db: Session = Depends(get_db)` роута. Найдено шестым проходом
    # независимого аудита. Ручка остаётся открытой сознательно — без неё нет песочницы, —
    # но обоснование теперь описывает то, что есть.
    "/api/planning/calculate": (
        "расчёт плана; данные приходят телом, а не query. Пишет журнальные "
        "`Recommendation` и `Event` — это телеметрия, не пользовательские данные"
    ),
    "/api/planning/forecast": "чистый прогноз; ничего не сохраняет",
    "/api/recommendation": "текстовая рекомендация по показателям; ничего не сохраняет",
    "/api/telegram/webhook": (
        "вызывает Telegram, а не пользователь; защищён секретом заголовка "
        "`X-Telegram-Bot-Api-Secret-Token` (см. routes_telegram.py)"
    ),
}


def _auth_names(dependant) -> set[str]:
    """Имена всех зависимостей ручки, включая унаследованные от роутера."""
    names: set[str] = set()
    stack = list(dependant.dependencies)
    while stack:
        dep = stack.pop()
        call = getattr(dep, "call", None)
        if call is not None:
            names.add(getattr(call, "__name__", ""))
        stack.extend(dep.dependencies)
    return names


def _unguarded_writes() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for route in app.routes:
        methods = getattr(route, "methods", set()) - SAFE_METHODS
        path = str(getattr(route, "path", ""))
        if not methods or not path.startswith("/api"):
            continue
        if _auth_names(route.dependant) & AUTH_DEPENDENCIES:
            continue
        found.append((",".join(sorted(methods)), path))
    return sorted(found, key=lambda item: item[1])


class TestEveryWriteIsGuarded:
    """Ни одна пишущая ручка не открыта молча."""

    def test_no_unlisted_open_write(self) -> None:
        """🔴 Мутация «снять require_admin с PUT /fx/rates» роняет тест здесь."""
        unlisted = [
            f"{methods} {path}"
            for methods, path in _unguarded_writes()
            if path not in PUBLIC_BY_DESIGN
        ]
        assert not unlisted, (
            "пишущие ручки без проверки прав: "
            + ", ".join(unlisted)
            + " — закройте зависимостью или назовите в PUBLIC_BY_DESIGN с причиной"
        )

    def test_exception_list_does_not_rot(self) -> None:
        """Ручка закрылась — исключение снимается, иначе список врёт о периметре."""
        open_paths = {path for _, path in _unguarded_writes()}
        stale = sorted(set(PUBLIC_BY_DESIGN) - open_paths)
        assert not stale, (
            f"в списке публичных ручки, которые уже закрыты: {stale}"
        )

    def test_every_exception_states_a_reason(self) -> None:
        empty = [path for path, why in PUBLIC_BY_DESIGN.items() if len(why.strip()) < 20]
        assert not empty, f"публичная ручка без внятной причины: {empty}"


class TestGateItselfWorks:
    """Обход действительно видит маршруты и их зависимости."""

    def test_walk_finds_many_writes(self) -> None:
        writes = [
            route
            for route in app.routes
            if getattr(route, "methods", set()) - SAFE_METHODS
            and str(getattr(route, "path", "")).startswith("/api")
        ]
        assert len(writes) > 30, f"пишущих ручек найдено подозрительно мало: {len(writes)}"

    def test_known_guarded_route_is_recognised(self) -> None:
        """Опора: закрытая ручка распознаётся как закрытая."""
        # 🔴 Именно PUT: путь `/api/fx/rates` объявлен дважды — GET (чтение, открыт
        # намеренно) и PUT (запись, закрыт админом). Опора, цеплявшаяся за путь,
        # брала первый попавшийся и падала на чтении.
        for route in app.routes:
            if (
                str(getattr(route, "path", "")) == "/api/fx/rates"
                and "PUT" in getattr(route, "methods", set())
            ):
                assert _auth_names(route.dependant) & AUTH_DEPENDENCIES
                return
        raise AssertionError("маршрут PUT /api/fx/rates не найден — обход сломан")
