"""Право поделиться записью достижимо из интерфейса, а не только из API (v8.55.0).

## Зачем гейт на файлах, а не только тесты компонента

Пункт №5 аудита — ровно тот класс дефекта, где бэкенд умеет, а человек не может:
`household_id` жил в схемах и колонках пяти сущностей, роли работали, приглашения
рассылались, а **формы про поле не знали вовсе**. Тот же класс, что SEV1
`CONSENT-GATE-NO-UI`, где гейт согласия работал 26 дней без способа его пройти.

Тесты компонента `HouseholdScopeField` проверяют, что контрол ведёт себя правильно.
Они ничего не говорят о том, **стоит ли он хоть где-то**. А тесты страниц мокают
его маркером (иначе `useHouseholds` тянет `QueryClientProvider` во все файлы) —
то есть подмена сделала бы удаление контрола из формы незаметным для них.

Этот гейт закрывает именно зазор: сущность, у которой в схеме есть `household_id`,
обязана иметь контрол в своей форме создания.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGES = REPO_ROOT / "frontend" / "src" / "pages"

# Сущность → форма создания. Список ведётся руками сознательно: новая
# shareable-сущность должна попасть сюда осознанно, а не «раствориться» в глобе.
CREATE_FORMS = {
    "transaction": PAGES / "transactions" / "ui" / "TransactionForm.tsx",
    "obligation": PAGES / "obligations" / "ui" / "ObligationForm.tsx",
    "goal": PAGES / "goals" / "ui" / "GoalForm.tsx",
    "liquid_asset": PAGES / "assets" / "ui" / "AssetForm.tsx",
    "budget": PAGES / "dashboard" / "ui" / "BudgetForm.tsx",
}


@pytest.mark.parametrize("entity", sorted(CREATE_FORMS))
def test_create_form_offers_household_choice(entity: str) -> None:
    """Форма создания даёт выбрать, чья запись — личная или семейная."""
    path = CREATE_FORMS[entity]
    assert path.exists(), f"{entity}: форма создания не найдена по пути {path}"
    source = path.read_text(encoding="utf-8")
    assert "HouseholdScopeField" in source, (
        f"{entity}: в форме создания нет выбора владельца записи — «Семейный доступ» "
        "существует, но поделиться этой сущностью из интерфейса нельзя"
    )


@pytest.mark.parametrize("entity", sorted(CREATE_FORMS))
def test_create_form_sends_household_id(entity: str) -> None:
    """Выбранное значение уходит в запрос.

    Контрол, чьё значение никуда не отправляется, выглядит работающим и не работает —
    вторая половина того же дефекта, и заметить её в браузере можно только сравнив
    список записей у двух людей.
    """
    source = CREATE_FORMS[entity].read_text(encoding="utf-8")
    assert "household_id" in source, (
        f"{entity}: форма показывает выбор, но не отправляет `household_id` — "
        "человек выбирает семью, а запись остаётся личной"
    )


# Сущность → строка списка. Выбор без обратной связи — половина функции: человек
# отметил «общая» и проверить это может только сравнив свой список с чужим.
LIST_ROWS = {
    "transaction": PAGES / "transactions" / "ui" / "TransactionRow.tsx",
    "obligation": PAGES / "obligations" / "ui" / "ObligationRow.tsx",
    "goal": PAGES / "goals" / "ui" / "GoalRow.tsx",
    "liquid_asset": PAGES / "assets" / "ui" / "AssetRow.tsx",
    "budget": PAGES / "dashboard" / "ui" / "BudgetRow.tsx",
}


@pytest.mark.parametrize("entity", sorted(LIST_ROWS))
def test_list_row_shows_shared_state(entity: str) -> None:
    """🔴 Строка списка говорит, общая запись или личная.

    Найдено `design-critic` при разборе контрола: выбор появился, а состояние после
    сохранения не читалось нигде — тот же класс дефекта, который батч и чинил.
    """
    path = LIST_ROWS[entity]
    assert path.exists(), f"{entity}: строка списка не найдена по пути {path}"
    source = path.read_text(encoding="utf-8")
    assert "SharedBadge" in source, (
        f"{entity}: в списке не видно, общая запись или личная — человек отметил "
        "«поделиться» и проверить это может только сравнив список с родственником"
    )


def test_shared_control_is_single() -> None:
    """Контрол один на все формы, а не скопирован в каждую.

    Пять копий расходятся при первой правке, и продукт начинает спрашивать «чьё это»
    по-разному в разных местах — [CMP-03] запрещает ровно это.
    """
    feature = REPO_ROOT / "frontend" / "src" / "features" / "household-scope"
    assert (feature / "HouseholdScopeField.tsx").exists()

    own_selects = [
        entity
        for entity, path in CREATE_FORMS.items()
        if "useHouseholds" in path.read_text(encoding="utf-8")
    ]
    assert not own_selects, (
        f"формы завели свой список household вместо общего контрола: {own_selects}"
    )
