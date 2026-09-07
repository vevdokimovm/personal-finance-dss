"""E2E CRUD в реальном браузере: создание, удаление и ВОССТАНОВЛЕНИЕ (переписано, v9.4.0).

## 🔴 Почему файл переписан

Прежняя редакция искала `#obligation-name`, `#goals-list`, `#open-obligation-modal` —
разметку Jinja, снесённую в вехе 8. Прогон 06.09.2026: **6 из 6 падали** по таймауту,
и на живом CI то же самое. В React те же поля называются `#obligation-form-name`,
а список — обычный `<ul>` без id; строка находится по имени записи.

## Что проверяется, чего не видит ничто другое

**Полный цикл обратимого удаления через интерфейс**: создать → увидеть в списке →
удалить → нажать «Вернуть» в тосте → снова увидеть в списке.

🔴 Это единственное место, где схема «удалить сразу + Вернуть» проверяется **целиком**.
Юнит-тесты `AssetRow`/`ObligationRow` проверяют, что хук вызван и тост показан;
здесь проверяется, что запись действительно вернулась в список — то есть что сервер
её восстановил, кэш перечитан и экран перерисован. Продукт выбрал эту схему вместо
диалога подтверждения, и она работает, **только если «Вернуть» доводит до конца**.

**Операции доступны гостю** (`user_id = NULL`), логин не требуется — это тоже решение
продукта: человек должен попробовать до регистрации.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e

FUTURE = "2030-12-31"


def _uid(prefix: str) -> str:
    return f"{prefix}-{int(time.time() * 1000)}"


def _fill_and_submit(page, base_url: str, path: str, add_button: str, fields: dict) -> None:
    """Открыть страницу, нажать «Добавить», заполнить форму, отправить."""
    page.goto(f"{base_url}{path}")
    page.get_by_role("button", name=add_button).click()
    first_field = next(iter(fields))
    page.wait_for_selector(f"#{first_field}", state="visible", timeout=10000)
    for field_id, value in fields.items():
        page.locator(f"#{field_id}").fill(value)
    # 🔴 При СОЗДАНИИ кнопка подписана «Добавить», при правке — «Сохранить»
    # (`isEdit ? "Сохранить" : "Добавить"`). Тест обязан нажимать то, что видит
    # человек: подпись здесь несёт смысл, а не украшает.
    page.get_by_role("button", name="Добавить", exact=True).click()


def _delete_and_undo(page, name: str) -> None:
    """Удалить строку по имени и вернуть её через тост.

    🔴 Кнопка «Вернуть» живёт в тосте и исчезает по таймауту — поэтому клик идёт
    сразу, без промежуточных проверок. Проверка результата — после.
    """
    row = page.locator("li", has_text=name).first
    row.get_by_role("button", name="Удалить").click()
    page.get_by_role("button", name="Вернуть").click()


class TestObligations:
    def test_create_delete_restore(self, page, base_url) -> None:
        """🔴 Полный цикл: обязательство создаётся, удаляется и ВОЗВРАЩАЕТСЯ.

        Удаление обязательства было сломано несколько версий подряд, а отмена появилась
        позже самого удаления. Здесь цикл проходится целиком, как его проходит человек.
        """
        name = _uid("E2E-долг")
        _fill_and_submit(
            page,
            base_url,
            "/obligations",
            "Добавить обязательство",
            {
                "obligation-form-name": name,
                "obligation-form-amount": "100000",
                "obligation-form-payment": "5000",
            },
        )
        page.wait_for_selector(f"text={name}", timeout=15000)

        _delete_and_undo(page, name)
        page.wait_for_selector(f"text={name}", timeout=15000)


class TestGoals:
    def test_create_delete_restore(self, page, base_url) -> None:
        name = _uid("E2E-цель")
        _fill_and_submit(
            page,
            base_url,
            "/goals",
            "Добавить цель",
            {
                "goal-form-name": name,
                "goal-form-target": "200000",
                "goal-form-deadline": FUTURE,
            },
        )
        page.wait_for_selector(f"text={name}", timeout=15000)

        _delete_and_undo(page, name)
        page.wait_for_selector(f"text={name}", timeout=15000)


class TestTransactions:
    def test_create_delete_restore(self, page, base_url) -> None:
        """Операция опознаётся по описанию: у неё нет собственного имени.

        Сумма для этого не годится — совпадения в списке демо-данных случайны,
        и тест удалил бы чужую строку.
        """
        description = _uid("E2E-операция")
        _fill_and_submit(
            page,
            base_url,
            "/transactions",
            "Добавить операцию",
            {
                "transaction-form-amount": "1234",
                "transaction-form-description": description,
            },
        )
        page.wait_for_selector(f"text={description}", timeout=15000)

        _delete_and_undo(page, description)
        page.wait_for_selector(f"text={description}", timeout=15000)
