"""E2E CRUD через реальный браузер: создание, удаление и ВОССТАНОВЛЕНИЕ (undo)
обязательств, целей и операций.

Почему именно это покрытие: удаление обязательства — базовейшее действие — было сломано
несколько версий, а restore (undo) появился совсем недавно. Такие вещи обязаны проверяться
автотестом, а не руками. Здесь весь цикл идёт через UI (модалки, клики, тосты), а нужный
элемент находится по `data-*-id` из ответа создания — поэтому тесты не зависят от demo-данных
в списке и не путают чужие строки со своими.

Операции доступны в гостевом режиме (user_id = NULL), логин не требуется.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e

FUTURE = "2030-12-31"  # для required-полей даты (дедлайн цели, дата операции)


def _uid(prefix: str) -> str:
    return f"{prefix}-{int(time.time() * 1000)}"


# ─────────────────────────── helpers создания (возвращают id) ───────────────────────────

def _create_obligation(page, name: str) -> int:
    page.locator("#open-obligation-modal").click()
    page.wait_for_selector("#obligation-name", state="visible", timeout=5000)
    page.locator("#obligation-name").fill(name)
    page.locator("#obligation-amount").fill("100000")
    page.locator("#obligation-monthly-payment").fill("5000")
    page.locator("#obligation-payment-day").fill("15")
    with page.expect_response(
        lambda r: r.url.rstrip("/").endswith("/api/obligations") and r.request.method == "POST"
    ) as resp:
        page.locator("#obligation-form button[type='submit']").click()
    oid = resp.value.json()["id"]
    page.wait_for_selector(f'.delete-button[data-obligation-id="{oid}"]', timeout=10000)
    return oid


def _create_goal(page, name: str) -> int:
    page.locator("#open-goal-modal").click()
    page.wait_for_selector("#goal-name", state="visible", timeout=5000)
    page.locator("#goal-name").fill(name)
    page.locator("#goal-target-amount").fill("500000")
    page.locator("#goal-deadline").fill(FUTURE)
    with page.expect_response(
        lambda r: r.url.rstrip("/").endswith("/api/goals") and r.request.method == "POST"
    ) as resp:
        page.locator("#goal-form button[type='submit']").click()
    gid = resp.value.json()["id"]
    page.wait_for_selector(f'.delete-button[data-goal-id="{gid}"]', timeout=10000)
    return gid


def _create_transaction(page, category: str) -> int:
    page.locator("#open-expense-modal").click()
    page.wait_for_selector("#transaction-category", state="visible", timeout=5000)
    page.locator("#transaction-category").fill(category)
    page.locator("#transaction-amount").fill("1500")
    page.locator("#transaction-date").fill(FUTURE)
    with page.expect_response(
        lambda r: r.url.rstrip("/").endswith("/api/transactions") and r.request.method == "POST"
    ) as resp:
        page.locator("#transaction-form button[type='submit']").click()
    tid = resp.value.json()["id"]
    page.wait_for_selector(f'.delete-button[data-transaction-id="{tid}"]', timeout=10000)
    return tid


def _delete_by_id(page, attr: str, oid: int) -> None:
    with page.expect_response(
        lambda r: "/api/" in r.url and r.request.method == "DELETE"
    ):
        page.locator(f'.delete-button[{attr}="{oid}"]').click()
    page.wait_for_selector(".undo-toast", timeout=5000)
    page.wait_for_selector(f'.delete-button[{attr}="{oid}"]', state="detached", timeout=5000)


def _restore(page) -> None:
    # restore у obligations/goals — POST на базовый /api/<entity> со snapshot в body
    # (пересоздаёт, id может смениться); у transactions — POST /api/transactions/<id>/restore.
    # Ловим любой POST на /api/ после клика undo и ждём перерендер; возврат проверяет тест по имени.
    with page.expect_response(lambda r: r.request.method == "POST" and "/api/" in r.url):
        page.locator(".undo-toast-btn").click()
    page.wait_for_load_state("networkidle")


# ─────────────────────────────────── obligations ───────────────────────────────────

def test_obligation_create(page, base_url) -> None:
    name = _uid("E2E-Долг")
    page.goto("/obligations")
    page.wait_for_load_state("networkidle")
    _create_obligation(page, name)
    assert name in page.locator("#obligations-list").inner_text()


def test_obligation_delete_and_restore(page, base_url) -> None:
    name = _uid("E2E-ДолгDR")
    page.goto("/obligations")
    page.wait_for_load_state("networkidle")
    oid = _create_obligation(page, name)
    _delete_by_id(page, "data-obligation-id", oid)
    assert name not in page.locator("#obligations-list").inner_text()
    _restore(page)  # undo — тот самый недавно добавленный путь
    page.wait_for_function(
        "(n)=>document.getElementById('obligations-list').textContent.includes(n)", arg=name, timeout=8000  # noqa: E501
    )
    assert name in page.locator("#obligations-list").inner_text()


# ─────────────────────────────────────── goals ───────────────────────────────────────

def test_goal_create(page, base_url) -> None:
    name = _uid("E2E-Цель")
    page.goto("/goals")
    page.wait_for_load_state("networkidle")
    _create_goal(page, name)
    assert name in page.locator("#goals-list").inner_text()


def test_goal_delete_and_restore(page, base_url) -> None:
    name = _uid("E2E-ЦельDR")
    page.goto("/goals")
    page.wait_for_load_state("networkidle")
    gid = _create_goal(page, name)
    _delete_by_id(page, "data-goal-id", gid)
    assert name not in page.locator("#goals-list").inner_text()
    _restore(page)
    page.wait_for_function(
        "(n)=>document.getElementById('goals-list').textContent.includes(n)", arg=name, timeout=8000
    )
    assert name in page.locator("#goals-list").inner_text()


# ──────────────────────────────────── transactions ────────────────────────────────────

def test_transaction_create(page, base_url) -> None:
    cat = _uid("E2E-Опер")
    page.goto("/transactions")
    page.wait_for_load_state("networkidle")
    _create_transaction(page, cat)
    assert cat in page.locator("#transactions-list").inner_text()


def test_transaction_delete_and_restore(page, base_url) -> None:
    cat = _uid("E2E-ОперDR")
    page.goto("/transactions")
    page.wait_for_load_state("networkidle")
    tid = _create_transaction(page, cat)
    _delete_by_id(page, "data-transaction-id", tid)
    assert cat not in page.locator("#transactions-list").inner_text()
    _restore(page)
    page.wait_for_function(
        "(n)=>document.getElementById('transactions-list').textContent.includes(n)", arg=cat, timeout=8000  # noqa: E501
    )
    assert cat in page.locator("#transactions-list").inner_text()
