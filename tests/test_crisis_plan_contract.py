"""`crisis_plan` описан схемой, а не `Dict[str, Any]` (v9.1.0).

## 🔴 Что нашлось при занесении тасок владельца

Владелец спросил (список от 24.07.2026, П1): «если ещё не добавлена фича, что при
отрицательном свободном ресурсе алгоритм не давал советы — сделать, чтобы предлагал
рефинансирование, где сократить траты».

Фича **есть с v6.0.0**: `app/core/crisis.py`, канон §12 — закрытие кредита из ликвидности,
сокращение расходов ровно до нуля дефицита, потолок трат, заморозка целей,
реструктуризация/рефинансирование/каникулы самого дорогого кредита, запас хода в месяцах.
Охват 9697/9697 дефицитных портретов, кейс владельца вшит живым тестом.

**Но `grep crisis` по `frontend/src` даёт ноль совпадений вне сгенерированного клиента.**
План считается, кладётся в ответ `/planning/calculate` — и не показывается никому.
Владелец, автор фичи, считал, что её нет: он её не видел.

Тот же класс, что spending-advice до v8.54.0, и цена здесь выше. Человек в дефиците —
тот, кому продукт нужнее всего: у него отрицательный поток, и вместо разбора, что делать,
он видит пустое место. Дефицитных портретов в наборе 9697.

## Почему схема первой

Правило вехи 8 без исключений: схема заводится на бэкенде ДО фронта. `Dict[str, Any]`
даёт в OpenAPI пустой объект, генератор выдаёт `unknown`, и форму приходится дописывать
руками — так появились касты, снятые в v8.50.0.

Действия плана — размеченное объединение по полю `type`, и каждый вариант несёт своё:
у сокращения расходов есть `amount`, у реструктуризации — ставка и опции. Плоская схема
«все поля необязательные» приняла бы любой мусор и не отличила бы один вид от другого.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

TODAY = "2026-09-05T12:00:00+00:00"

TOP_LEVEL = ["deficit", "runway_months", "max_affordable_expenses", "severity",
             "actions", "summary"]


def _register(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert response.status_code in (200, 201), response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    client.post("/api/consents/financial_data", headers=headers, json={})
    return headers


def _deficit_profile(client: TestClient, headers: dict[str, str]) -> None:
    """Профиль с отрицательным свободным потоком: доход меньше расходов и платежей."""
    client.post("/api/transactions", headers=headers, json={
        "amount": 20000.0, "type": "income", "category": "Зарплата", "date": TODAY,
    })
    client.post("/api/transactions", headers=headers, json={
        "amount": 18000.0, "type": "expense", "category": "Продукты", "date": TODAY,
    })
    created = client.post("/api/obligations", headers=headers, json={
        "name": "Кредитная карта", "type": "credit_card", "bank": "Банк",
        # 🔴 Ставка — ДОЛЯ (`Numeric(6, 4)`, 0.39 = 39% годовых), не проценты.
        # Первая редакция подавала 39.0, то есть 3900%, и тест был зелёным: контракт
        # число принимает, а смысл его не проверяет никто. Нашёл design-critic.
        "amount": 150000.0, "interest_rate": 0.39, "monthly_payment": 7000.0,
        "months_left": 36,
    })
    assert created.status_code in (200, 201), created.text


class TestCrisisPlanIsTyped:
    """Гейт против возврата к нетипизированному словарю."""

    def test_schema_describes_crisis_plan(self, client: TestClient) -> None:
        """🔴 `crisis_plan` ссылается на схему, а не на пустой объект.

        Мутация: вернуть `Dict[str, Any]` — падает этот тест, а не разметка экрана.
        """
        spec = client.get("/openapi.json").json()
        plan = spec["components"]["schemas"]["PlanningCalculateResponse"]["properties"]
        crisis = plan["crisis_plan"]
        refs = str(crisis)
        assert "CrisisPlan" in refs, (
            "crisis_plan не описан схемой — генератор выдаст unknown, и фронт "
            "допишет форму руками"
        )

    def test_schema_declares_all_fields(self, client: TestClient) -> None:
        """Все шесть полей плана заведены: потерянное схема молча срежет."""
        spec = client.get("/openapi.json").json()
        properties = spec["components"]["schemas"]["CrisisPlan"]["properties"]
        missing = [field for field in TOP_LEVEL if field not in properties]
        assert not missing, f"схема не знает полей: {missing}"

    def test_actions_are_described_by_item_schema(self, client: TestClient) -> None:
        """🔴 Действия описаны своим типом, а не `list[dict]`.

        `list[dict]` внутри типизированной обёртки — та же дыра на уровень глубже
        (PIT-027): обёртка выглядит контрактом, содержимое нет.
        """
        spec = client.get("/openapi.json").json()
        actions = spec["components"]["schemas"]["CrisisPlan"]["properties"]["actions"]
        assert "$ref" in str(actions.get("items", {})), "элементы `actions` не описаны схемой"


class TestCrisisPlanOnLiveProfile:
    """Ответ на живом дефицитном профиле соответствует объявленному."""

    def test_deficit_profile_gets_a_crisis_plan(self, client: TestClient) -> None:
        """🔴 Главная проверка: при отрицательном потоке план ЕСТЬ.

        Ради этого фича и заводилась в v6.0.0 — человек в дефиците должен получить
        разбор, а не пустой экран.
        """
        headers = _register(client, "crisis-contract@test.io")
        _deficit_profile(client, headers)

        response = client.post("/api/planning/calculate", headers=headers, json={})
        assert response.status_code == 200, response.text
        plan = response.json()["crisis_plan"]
        assert plan is not None, "профиль в дефиците, а кризисного плана нет"
        assert plan["deficit"] > 0
        assert plan["actions"], "план без действий — это не план, а диагноз"

    def test_restructuring_names_the_most_expensive_loan(self, client: TestClient) -> None:
        """Реструктуризация указывает КОНКРЕТНЫЙ кредит и варианты.

        «Обратитесь в банк» без имени кредита и ставки — совет, который человек
        не может исполнить, не открыв другой экран.
        """
        headers = _register(client, "crisis-restructure@test.io")
        _deficit_profile(client, headers)

        plan = client.post("/api/planning/calculate", headers=headers, json={}).json()
        actions = plan["crisis_plan"]["actions"]
        restructure = next((a for a in actions if a["type"] == "restructure_debt"), None)
        assert restructure is not None, "самый дорогой кредит не назван"
        assert restructure["loan"] == "Кредитная карта"
        assert "рефинансирование" in restructure["options"]

    def test_severity_is_one_of_the_known_values(self, client: TestClient) -> None:
        """🔴 Тяжесть — из закрытого перечня, и фронт обязан знать те же три значения.

        `app/core/crisis.py` отдаёт `recoverable_from_liquidity`, `critical`
        и `cut_required`. Фронт объявлял `manageable`, которого не существует, —
        то есть САМЫЙ ЧАСТЫЙ случай попадал в ветку «неизвестное значение»
        и показывал верный текст по совпадению, потому что дефолт назначили тем же
        объектом. Первая правка дефолта сломала бы основной сценарий бесшумно.
        """
        headers = _register(client, "crisis-severity@test.io")
        _deficit_profile(client, headers)

        plan = client.post("/api/planning/calculate", headers=headers, json={}).json()
        assert plan["crisis_plan"]["severity"] in {
            "recoverable_from_liquidity", "critical", "cut_required",
        }

    def test_positive_flow_has_no_crisis_plan(self, client: TestClient) -> None:
        """Плюсовой поток — плана нет, и это не ошибка.

        Тест против переусердствования: показать кризисный разбор тому, у кого
        всё в порядке, значит напугать без повода.
        """
        headers = _register(client, "crisis-positive@test.io")
        client.post("/api/transactions", headers=headers, json={
            "amount": 150000.0, "type": "income", "category": "Зарплата", "date": TODAY,
        })
        client.post("/api/transactions", headers=headers, json={
            "amount": 40000.0, "type": "expense", "category": "Продукты", "date": TODAY,
        })

        plan = client.post("/api/planning/calculate", headers=headers, json={}).json()
        assert plan["crisis_plan"] is None
