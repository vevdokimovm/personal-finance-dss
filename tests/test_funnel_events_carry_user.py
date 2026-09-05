"""События воронки пишутся с `user_id` — иначе экран метрик показывает ложные нули (v8.51.0).

## Гипотеза H7, подтверждена чтением кода 2026-09-05

`independent-expert` выдвинул её 19.08.2026 (`docs/research/raw/
12_independent_expert_milestone8_gap_2026-08-19.md`), эмпирически она не проверялась
и пролежала в долге «12 неверифицированных гипотез» три недели.

**Механизм.** `analytics.funnel()` считает `distinct` пользователей по шагу и фильтрует
`Event.user_id.isnot(None)`. При этом `log_event("obligation_created", {...})` вызывается
**без** аргумента `user_id`, и колонка остаётся NULL. Шаги 2 и далее всегда пусты.

🔴 **Цена выросла в v8.48.0**, когда воронка получила экран. До этого дефект был
теоретическим — смотреть на воронку было негде. Теперь владелец видит «после входа
теряем всех» и принимает продуктовые решения по числу, которого не существует.

**Отказ тихий вдвойне:** `log_event` глотает исключения (`event_logger.py`), а нулевой
шаг воронки неотличим от честного нуля — «никто не завёл кредит» и «мы не записали, кто
завёл» выглядят на экране одинаково.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.models import Event
from app.services.analytics import funnel


def _register(client: TestClient, email: str) -> dict[str, str]:
    """Регистрация плюс согласие на финданные: без него гейт `_FIN` вернёт 403,
    и до записи события дело не дойдёт вовсе."""
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert response.status_code in (200, 201), response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    granted = client.post("/api/consents/financial_data", headers=headers, json={})
    assert granted.status_code in (200, 201), granted.text
    return headers


class TestEventsCarryUser:
    """Событие, созданное вошедшим пользователем, знает, кто его создал."""

    def test_obligation_created_event_has_user(self, client: TestClient, db_session) -> None:
        """🔴 Шаг воронки «Добавлен кредит» привязан к пользователю.

        Мутация: убрать `user_id=` из вызова `log_event` в `routes_obligations` —
        тест краснеет, а экран метрик молча вернулся бы к ложным нулям.
        """
        headers = _register(client, "funnel-obligation@test.io")

        created = client.post(
            "/api/obligations",
            headers=headers,
            json={
                "name": "Автокредит",
                "type": "credit",
                "bank": "Тест",
                "amount": 100000,
                "interest_rate": 15.0,
                "monthly_payment": 5000,
                "months_left": 24,
            },
        )
        assert created.status_code in (200, 201), created.text

        event = (
            db_session.query(Event)
            .filter(Event.event_type == "obligation_created")
            .order_by(Event.id.desc())
            .first()
        )
        assert event is not None, "событие не записано вовсе"
        assert event.user_id is not None, (
            "событие записано без user_id — шаг воронки будет пустым независимо от того, "
            "сколько людей на самом деле добавили кредит"
        )

    def test_goal_created_event_has_user(self, client: TestClient, db_session) -> None:
        """То же для целей — второй шаг воронки по умолчанию."""
        headers = _register(client, "funnel-goal@test.io")
        created = client.post(
            "/api/goals",
            headers=headers,
            json={"name": "Отпуск", "target_amount": 100000, "priority": 3},
        )
        assert created.status_code in (200, 201), created.text

        event = (
            db_session.query(Event)
            .filter(Event.event_type == "goal_created")
            .order_by(Event.id.desc())
            .first()
        )
        assert event is not None
        assert event.user_id is not None


class TestFunnelCountsRealPeople:
    """Воронка считает людей, а не молчит из-за потерянной привязки."""

    def test_funnel_second_step_is_not_always_empty(
        self, client: TestClient, db_session
    ) -> None:
        """🔴 Главная проверка: человек прошёл два шага — воронка показывает два.

        Именно это и было сломано: первый шаг (`login_success`) писался с `user_id`
        при входе, остальные — без, и воронка всегда рисовала обрыв на первом же
        переходе. Вывод «теряем всех после входа» был артефактом, а не наблюдением.
        """
        headers = _register(client, "funnel-full@test.io")
        client.post(
            "/api/obligations",
            headers=headers,
            json={
                "name": "Потребительский",
                "type": "credit",
                "bank": "Тест",
                "amount": 50000,
                "interest_rate": 12.0,
                "monthly_payment": 3000,
                "months_left": 18,
            },
        )
        db_session.commit()

        steps = funnel(db_session, steps=["user_registered", "obligation_created"])
        by_name = {step["step"]: step["users"] for step in steps}

        assert by_name["user_registered"] >= 1
        assert by_name["obligation_created"] >= 1, (
            "человек добавил кредит, а воронка показывает ноль — привязка события "
            "к пользователю потеряна"
        )
