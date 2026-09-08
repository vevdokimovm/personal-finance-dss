"""Удаление аккаунта уносит и рекомендации — а не только обещает это.

## Что закрывает

`crud.delete_user` выполняет
`delete(Recommendation).where(Recommendation.user_id == user_id)` с комментарием
«Аналитика и рекомендации — тоже персональные данные (право на удаление)».

🔴 **Эта строка не удаляла ничего никогда.** Единственный вызов `log_recommendation`
во всём проекте идёт **без** `user_id`, а в сигнатуре у него умолчание `None` — значит
у всех строк `recommendations.user_id IS NULL`, включая созданные вошедшим человеком.

**Что именно оставалось.** Строка `Recommendation` — не служебная отметка, а полный
агрегированный портрет: доходы, расходы, сумма платежей по обязательствам, баланс,
ликвидность, Rt/Lt/Dt/BLR, рекомендованное распределение и обоснование прозой.
`docs/pdn_data_map.md` относит её к финансовым сведениям на основании согласия,
а раздел о правах субъекта обещает каскад по `user_id` при удалении аккаунта.

**Цена.** Человек удаляет аккаунт, продукт отвечает «удалено», портрет остаётся в базе
навсегда — и вернуть его владельцу нельзя даже по запросу на доступ, потому что связи
с ним больше нет. Тот же класс, что «ложное подтверждение исполнения права» у отзыва
согласия, только на удалении.

Найдено шестым проходом независимого аудита 08.09.2026.
"""
from __future__ import annotations

import pytest

from app.database.models import Recommendation, User


@pytest.fixture()
def registered(client, db_session):
    """Вошедший пользователь с активной сессией в клиенте."""
    client.post("/api/auth/register", json={
        "email": "deletion-probe@test.io", "password": "verysecret1", "consent": True})
    return db_session.query(User).filter(User.email == "deletion-probe@test.io").one()


class TestRecommendationsAreAttributedToTheirOwner:
    """Рекомендация вошедшего человека несёт его идентификатор."""

    def test_calculated_plan_is_linked_to_the_user(
        self, client, db_session, registered
    ) -> None:
        """🔴 Мутация «убрать user_id из вызова» роняет тест здесь."""
        client.post("/api/consents/financial_data")
        client.post("/api/planning/calculate", json={})

        rows = db_session.query(Recommendation).all()
        assert rows, "рекомендация не записалась вовсе — проверять нечего"
        assert any(r.user_id == registered.id for r in rows), (
            "рекомендация вошедшего человека записана без владельца — "
            "удаление аккаунта её не унесёт, а карта ПДн обещает обратное"
        )

    def test_guest_recommendation_stays_ownerless(self, client, db_session) -> None:
        """У гостя владельца нет — и это правильно, а не пропуск."""
        client.cookies.clear()
        client.post("/api/planning/calculate", json={})
        rows = db_session.query(Recommendation).all()
        assert all(r.user_id is None for r in rows)


class TestDeletionActuallyRemovesThem:
    """Каскад удаления уносит рекомендации владельца."""

    def test_account_deletion_removes_own_recommendations(
        self, client, db_session, registered
    ) -> None:
        from app.database.crud import delete_user

        client.post("/api/consents/financial_data")
        client.post("/api/planning/calculate", json={})
        assert db_session.query(Recommendation).filter(
            Recommendation.user_id == registered.id).count() >= 1

        delete_user(db_session, registered.id)

        left = db_session.query(Recommendation).filter(
            Recommendation.user_id == registered.id).count()
        assert left == 0, (
            f"после удаления аккаунта осталось {left} рекомендаций с портретом внутри"
        )

    def test_other_peoples_records_survive(self, client, db_session, registered) -> None:
        """И чужие записи при этом не задеты — удаление адресное."""
        from app.database.crud import delete_user

        db_session.add(Recommendation(user_id=None, income_total=1.0))
        db_session.commit()
        before = db_session.query(Recommendation).filter(
            Recommendation.user_id.is_(None)).count()

        delete_user(db_session, registered.id)

        assert db_session.query(Recommendation).filter(
            Recommendation.user_id.is_(None)).count() == before


class TestEventsCarryTheirOwnerToo:
    """🔴 То же самое, но для событий: каскад удаления обязан их находить.

    `delete_user` выполняет `delete(Event).where(Event.user_id == user_id)`, и работает
    это ровно настолько, насколько события помечены владельцем. Правило известно
    и записано ещё в v8.51.0 (гипотеза H7: «события воронки писались без `user_id` —
    экран метрик врал»), но применено наполовину: операции, цели и обязательства
    его соблюдают, бюджеты, ликвидные активы, семейный доступ и планирование — нет.

    Половинчатая миграция хуже единообразного отсутствия: каскад выглядит работающим,
    метрики выглядят полными, а часть данных не попадает ни туда, ни туда.
    """

    def _events_for(self, db_session, user_id: str, event_type: str | None = None) -> int:
        """Сколько событий записано на этого человека.

        🔴 `event_type` обязателен там, где проверяется КОНКРЕТНОЕ действие. Первая
        редакция считала события любого типа — и была зелёной, потому что выдача
        согласия в том же тесте пишет своё событие с владельцем. Мутация «убрать
        `user_id` из события бюджета» не ловилась вовсе: тест держался на соседе.
        """
        from app.database.models import Event

        query = db_session.query(Event).filter(Event.user_id == user_id)
        if event_type is not None:
            query = query.filter(Event.event_type == event_type)
        return query.count()

    def test_budget_action_is_attributed(self, client, db_session, registered) -> None:
        """🔴 Мутация «убрать user_id из log_event бюджета» роняет тест здесь."""
        client.post("/api/consents/financial_data")
        response = client.post("/api/budgets", json={"category": "food", "limit_amount": 15000})
        assert response.status_code in (200, 201), response.text

        assert self._events_for(db_session, registered.id, "budget_set") >= 1, (
            "событие о бюджете записано без владельца — удаление аккаунта его не унесёт, "
            "а экран метрик не свяжет с человеком"
        )

    def test_liquid_asset_action_is_attributed(
        self, client, db_session, registered
    ) -> None:
        client.post("/api/consents/financial_data")
        created = client.post(
            "/api/liquid-assets",
            json={"name": "Вклад", "amount": 100000, "asset_type": "deposit"},
        )
        assert created.status_code in (200, 201), created.text
        asset_id = created.json()["id"]
        client.put(f"/api/liquid-assets/{asset_id}", json={"amount": 120000})

        assert self._events_for(db_session, registered.id, "liquid_asset_updated") >= 1

    def test_deletion_removes_attributed_events(
        self, client, db_session, registered
    ) -> None:
        """И каскад их действительно уносит."""
        from app.database.crud import delete_user

        client.post("/api/consents/financial_data")
        client.post("/api/budgets", json={"category": "food", "limit_amount": 15000})
        assert self._events_for(db_session, registered.id, "budget_set") >= 1

        delete_user(db_session, registered.id)
        assert self._events_for(db_session, registered.id) == 0
