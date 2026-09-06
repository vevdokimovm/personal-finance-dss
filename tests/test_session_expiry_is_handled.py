"""Каждый экран за авторизацией отличает истёкшую сессию от сбоя связи (v9.1.0).

## Что закрывает

Остаток гипотезы 7 независимого эксперта. `JWT_TTL_HOURS = 168`, refresh-токена нет —
401 в середине работы это регулярное событие, а не экзотика. Разбирал его **только**
профиль; остальные экраны показывали «Проверьте соединение и попробуйте ещё раз»
с кнопкой «Повторить», которая возвращает 401 бесконечно.

🔴 **Человеку с работающим интернетом советовали проверить интернет** и предлагали
кнопку, ведущую в петлю. Единственный работающий выход — войти заново — при этом
прятался в топбаре, а меню в этот момент исчезало целиком.

## Почему гейт на файлах

Юнит-тесты каждого экрана проверяют его собственные ветки. Ни один из них не отвечает
на вопрос «а все ли экраны это умеют» — и новый экран (их за веху 8 добавилось семь)
унаследует старый шаблон обработки ошибки вместе с советом про интернет.

Список ведётся руками сознательно: экран, попавший сюда, — это осознанное решение,
а глоб по `pages/` затянул бы и гостевые страницы, где 401 невозможен по построению.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGES = REPO_ROOT / "frontend" / "src" / "pages"

# Экраны за авторизацией: у каждого своя ветка ошибки, и на каждом 401 достижим.
GUARDED_SCREENS = {
    "transactions": PAGES / "transactions" / "TransactionsPage.tsx",
    "obligations": PAGES / "obligations" / "ObligationsPage.tsx",
    "goals": PAGES / "goals" / "GoalsPage.tsx",
    "assets": PAGES / "assets" / "AssetsPage.tsx",
    "planning": PAGES / "planning" / "PlanningPage.tsx",
    "spending": PAGES / "spending" / "ui" / "SpendingPage.tsx",
}


def _without_comments(source: str) -> str:
    """Код без комментариев.

    🔴 Первая редакция гейта краснела на СОБСТВЕННОМ объяснении: комментарий в `AppNav`
    цитирует прежнее условие `if (!data || error) return null`, рассказывая, чем оно было
    плохо, — и поиск подстроки находил цитату. Тот же класс, что PIT-026: проверка
    считает нарушением текст правила о нарушении.

    Комментарии заменяются пробелами той же длины, чтобы номера строк и смещения
    не поехали, — если по ним когда-нибудь понадобится показать место.
    """
    result = list(source)
    index, length = 0, len(source)
    while index < length:
        if source.startswith("//", index):
            end = source.find("\n", index)
            end = length if end == -1 else end
            result[index:end] = " " * (end - index)
            index = end
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            end = length if end == -1 else end + 2
            for position in range(index, end):
                if source[position] != "\n":
                    result[position] = " "
            index = end
        else:
            index += 1
    return "".join(result)


@pytest.mark.parametrize("screen", sorted(GUARDED_SCREENS))
def test_screen_recognises_expired_session(screen: str) -> None:
    """🔴 Экран различает 401 и сбой связи.

    Мутация «убрать ветку» роняет ровно этот параметр — видно, какой экран
    вернулся к совету про интернет.
    """
    path = GUARDED_SCREENS[screen]
    assert path.exists(), f"{screen}: экран не найден по пути {path}"
    source = path.read_text(encoding="utf-8")
    assert "isSessionExpired" in source, (
        f"{screen}: 401 разбирается как сетевая ошибка — человеку с работающим "
        "интернетом советуют проверить интернет, а «Повторить» возвращает 401 по кругу"
    )


@pytest.mark.parametrize("screen", sorted(GUARDED_SCREENS))
def test_screen_offers_the_way_out(screen: str) -> None:
    """Распознать мало — нужен выход.

    Ветка, распознающая 401 и показывающая тот же текст про соединение, была бы
    хуже прежнего: код выглядит починенным, поведение прежнее.
    """
    source = GUARDED_SCREENS[screen].read_text(encoding="utf-8")
    assert "SessionExpiredPanel" in source, (
        f"{screen}: истёкшая сессия распознана, но выхода не предложено"
    )


def test_the_panel_is_shared() -> None:
    """Панель одна на все экраны, а не скопирована в каждый.

    Шесть копий расходятся при первой правке текста, и продукт начинает объяснять
    одно и то же по-разному ([CMP-03]).
    """
    panel = REPO_ROOT / "frontend" / "src" / "entities" / "auth" / "ui" / "SessionExpiredPanel.tsx"
    assert panel.exists()

    own_text = [
        screen
        for screen, path in GUARDED_SCREENS.items()
        if "Сессия истекла" in path.read_text(encoding="utf-8")
    ]
    assert not own_text, f"экраны пишут свой текст вместо общей панели: {own_text}"


def test_navigation_survives_network_errors() -> None:
    """🔴 Меню исчезает только при истёкшей сессии, а не при любой ошибке.

    `if (!data || error) return null` убирал каркас из-за моргнувшей сети, при том
    что человек вошёл и данные лежат в кэше. Экран «ломался» без объяснения.
    """
    nav = REPO_ROOT / "frontend" / "src" / "widgets" / "app-nav" / "AppNav.tsx"
    source = _without_comments(nav.read_text(encoding="utf-8"))
    assert "if (!data || error) return null" not in source, (
        "навигация исчезает при ЛЮБОЙ ошибке профиля, включая сетевую"
    )
    assert "isSessionExpired" in source, (
        "навигация не различает вид ошибки — значит либо прячется зря, либо ведёт "
        "в тупики после выхода"
    )
