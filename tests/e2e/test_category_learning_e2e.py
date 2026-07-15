"""E2E обучения категоризации (P2.7) через реальный браузер.

Сценарий целиком через UI: переназначить категорию операции (кнопка ↻ → модалка),
правило запоминается и ретроактивно применяется к похожей операции; правило видно в списке
и удаляется. Операции с описанием сеются через API (модалка создания описание не запрашивает),
дальше всё — клики и проверки DOM. Гостевой режим, логин не требуется.

Браузер для прогона ставится отдельно: `playwright install chromium`. В песочнице CDN браузеров
заблокирован, поэтому спека гоняется на Mac/GitHub CI (как остальные e2e).
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e

FUTURE = "2030-12-31T00:00:00"


def _seed_txn(page, base_url, description: str, category: str = "Прочее") -> int:
    """Создаёт операцию с описанием через API (в контексте браузера — CSRF/origin проходят)."""
    resp = page.request.post(f"{base_url}/api/transactions", data={
        "amount": 1000, "category": category, "type": "expense",
        "date": FUTURE, "description": description,
    })
    assert resp.ok, resp.text()
    return resp.json()["id"]


def test_recategorize_learns_applies_and_rule_is_manageable(page, base_url) -> None:
    tag = f"ozonshop{int(time.time() * 1000)}"
    t1 = _seed_txn(page, base_url, f"{tag} заказ 1")
    _seed_txn(page, base_url, f"оплата {tag} заказ 2")

    page.goto("/transactions")
    page.wait_for_selector(f'.recat-button[data-transaction-id="{t1}"]', timeout=10000)

    # открыть модалку переназначения у первой операции
    page.locator(f'.recat-button[data-transaction-id="{t1}"]').click()
    page.wait_for_selector("#recat-category", state="visible", timeout=5000)
    page.locator("#recat-category").fill("Покупки")
    page.locator("#recat-token").fill(tag)

    # сохранить → POST /transactions/{id}/category, обучение + ретроактив
    with page.expect_response(
        lambda r: "/category" in r.url and r.request.method == "POST"
    ) as resp:
        page.locator("#recat-form button[type='submit']").click()
    body = resp.value.json()
    assert body["transaction"]["category"] == "Покупки"
    assert body["updated_count"] == 1  # вторая совпадающая операция подхвачена ретроактивно

    # правило появилось в списке выученных правил
    page.wait_for_selector("#category-rules-list .rule-del", timeout=8000)
    assert tag in page.locator("#category-rules-list").inner_text().lower()

    # удалить правило → DELETE, строка исчезает
    with page.expect_response(
        lambda r: "/api/category-rules/" in r.url and r.request.method == "DELETE"
    ):
        page.locator("#category-rules-list .rule-del").first.click()
    page.wait_for_function(
        "() => !document.querySelector('#category-rules-list .rule-del')", timeout=8000
    )
