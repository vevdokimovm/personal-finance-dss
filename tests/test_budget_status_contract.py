"""`/budgets/status` описан схемой, включая `id` (v8.50.0).

## Что было

Роут возвращал `list[dict]`, хотя схема `BudgetStatus` в `app/schemas/budget.py`
существовала с самого появления бюджетов. Схема при этом **не знала про `id`**, который
`crud.get_budget_status` кладёт в каждый элемент, — то есть даже подключить её напрямую
было нельзя: ответ потерял бы идентификатор, а по нему фронт правит и удаляет бюджет.

Следствие на фронте: `useBudgets.ts` делал `data as unknown as BudgetStatus[]` поверх
рукописного интерфейса — последний двойной каст в продуктовом коде (гейт
`test_no_contract_casts.py`). Каст снимает сверку целиком: добавь бэкенд поле или
переименуй существующее, компилятор промолчит.

🔴 **Порядок починки принципиален.** Сначала схема на бэкенде, потом снятие каста —
наоборот получилось бы «фронт требует того, чего контракт не обещает», ровно дефект
v8.31.1.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient


def _today() -> str:
    """Дата операции — сегодня: окно плана-факта по умолчанию 30 дней назад."""
    return datetime.now(timezone.utc).isoformat()


def _add_budget(client: TestClient, category: str = "Еда", limit: float = 10000.0) -> None:
    response = client.post("/api/budgets", json={"category": category, "limit_amount": limit})
    assert response.status_code in (200, 201), response.text


class TestBudgetStatusSchema:
    """Ответ описан схемой и несёт все поля, которые кладёт сервис."""

    def test_openapi_declares_array_of_schema(self, client: TestClient) -> None:
        """🔴 Гейт против возврата к `list[dict]`.

        Мутация: снять `response_model` — падает именно этот тест, а не разметка экрана.
        """
        schema = client.get("/openapi.json").json()
        response = schema["paths"]["/api/budgets/status"]["get"]["responses"]["200"]
        content = response["content"]["application/json"]["schema"]
        assert content.get("type") == "array", "ответ обязан быть массивом по контракту"
        assert "$ref" in content.get("items", {}), (
            "элементы массива не описаны схемой — генератор выдаст unknown, "
            "и фронт снова допишет тип руками"
        )

    def test_status_row_carries_id(self, client: TestClient) -> None:
        """🔴 `id` в ответе есть: по нему фронт правит и удаляет бюджет.

        Схема без `id` молча выбросила бы его при сериализации — экран потерял бы
        возможность редактировать строку, и виноват был бы «фронт».
        """
        _add_budget(client)
        rows = client.get("/api/budgets/status").json()
        assert rows, "бюджет заведён, а статус пуст"
        assert isinstance(rows[0]["id"], int)

    def test_status_row_carries_all_computed_fields(self, client: TestClient) -> None:
        """Остальные поля плана-факта на месте и нужного типа."""
        _add_budget(client, category="Транспорт", limit=5000.0)
        rows = client.get("/api/budgets/status").json()
        row = next(r for r in rows if r["category"] == "Транспорт")

        assert row["limit_amount"] == 5000.0
        assert isinstance(row["spent"], float)
        assert isinstance(row["pct"], float)
        assert isinstance(row["over"], bool)

    def test_empty_list_when_no_budgets(self, client: TestClient) -> None:
        """Нет бюджетов — пустой массив, а не 404 и не null."""
        assert client.get("/api/budgets/status").json() == []


class TestBudgetWithoutSpending:
    """🔴 Бюджет без единой операции — обычное состояние, а не сбой.

    Найдено 2026-09-05 при заведении контракта: `crud.get_budget_status` считал
    `spent / b.limit_amount`, где `spent` при отсутствии операций подставлялся как
    `0.0` (float), а `limit_amount` приходит из `Numeric(14, 2)` как `Decimal`.
    Деление float на Decimal — `TypeError`, то есть **500 на экране бюджетов**.

    Сценарий тривиален и встречается у каждого нового пользователя: завёл бюджет,
    ещё ничего по нему не потратил. Тесты не ловили, потому что все заводили
    бюджет вместе с операциями по той же категории.
    """

    def test_status_of_untouched_budget_does_not_crash(self, client: TestClient) -> None:
        """Экран бюджетов открывается, когда трат по категории ещё не было."""
        _add_budget(client, category="Отпуск", limit=50000.0)

        response = client.get("/api/budgets/status")
        assert response.status_code == 200, response.text

        row = next(r for r in response.json() if r["category"] == "Отпуск")
        assert row["spent"] == 0.0
        assert row["pct"] == 0.0
        assert row["over"] is False

    def test_percent_is_computed_from_real_spending(self, client: TestClient) -> None:
        """Проценты считаются, когда траты есть: проверка, что починка не занулила расчёт."""
        _add_budget(client, category="Кафе", limit=1000.0)
        created = client.post(
            "/api/transactions",
            json={"amount": 250.0, "type": "expense", "category": "Кафе", "date": _today()},
        )
        assert created.status_code in (200, 201), created.text

        row = next(r for r in client.get("/api/budgets/status").json() if r["category"] == "Кафе")
        assert row["spent"] == 250.0
        assert row["pct"] == 25.0
        assert row["over"] is False

    def test_over_limit_is_flagged(self, client: TestClient) -> None:
        """Превышение лимита помечено — ради этого флага экран и существует."""
        _add_budget(client, category="Такси", limit=100.0)
        client.post(
            "/api/transactions",
            json={"amount": 150.0, "type": "expense", "category": "Такси", "date": _today()},
        )

        row = next(r for r in client.get("/api/budgets/status").json() if r["category"] == "Такси")
        assert row["over"] is True
        assert row["pct"] == 150.0
