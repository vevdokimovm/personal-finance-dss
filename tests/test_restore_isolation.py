"""Восстановление удалённого не пересекает границу владельца (v8.51.0).

## Как нашлось

Побочно, при починке гипотезы H7: правка `log_event(..., user_id=user_id)` в
`restore_transaction_endpoint` не скомпилировалась — **у эндпоинта не было параметра
`user_id` вовсе**. Чтение соседей показало, почему это важно:

| функция | проверяет владельца |
|---|---|
| `restore_goal` | да (`goal.user_id != user_id`) |
| `restore_obligation` | да |
| `restore_budget` | да |
| `restore_liquid_asset` | да |
| **`restore_transaction`** | **нет** |

Четыре из пяти сделаны одинаково — значит пятое не решение, а пропуск.

🔴 **Что это значило:** любой пользователь (и гость), зная `id`, восстанавливал чужую
удалённую операцию. Она возвращалась владельцу в список, меняя его баланс и, через него,
рекомендацию плана. Прямое нарушение изоляции данных в продукте, где изоляция —
требование 152-ФЗ, а не удобство.

**Почему не ловилось:** тесты мягкого удаления проверяли пару «удалил → восстановил»
одним и тем же пользователем. Путь «чужой восстанавливает» не проходил никто —
тот же зазор, что в PIT-024 («бюджет есть, трат нет»).
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert response.status_code in (200, 201), response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    granted = client.post("/api/consents/financial_data", headers=headers, json={})
    assert granted.status_code in (200, 201), granted.text
    return headers


def _create_transaction(client: TestClient, headers: dict[str, str]) -> int:
    created = client.post(
        "/api/transactions",
        headers=headers,
        json={
            "amount": 1000.0,
            "type": "expense",
            "category": "Еда",
            "date": "2026-09-05T12:00:00+00:00",
        },
    )
    assert created.status_code in (200, 201), created.text
    return created.json()["id"]


class TestRestoreRespectsOwner:
    """Чужое удалённое остаётся удалённым."""

    def test_stranger_cannot_restore_someone_elses_transaction(
        self, client: TestClient
    ) -> None:
        """🔴 Главная проверка: посторонний не возвращает чужую операцию в чужой список.

        Восстановленная операция меняет баланс владельца и, через него, рекомендацию
        плана — то есть вмешательство в чужие финансовые данные, а не косметика.
        """
        owner = _register(client, "restore-owner@test.io")
        transaction_id = _create_transaction(client, owner)
        deleted = client.delete(f"/api/transactions/{transaction_id}", headers=owner)
        assert deleted.status_code == 200

        stranger = _register(client, "restore-stranger@test.io")
        response = client.post(
            f"/api/transactions/{transaction_id}/restore", headers=stranger
        )
        assert response.status_code == 404, (
            "посторонний восстановил чужую удалённую операцию — нарушение изоляции данных"
        )

    def test_guest_cannot_restore_users_transaction(self, client: TestClient) -> None:
        """Гость — тем более: у него нет ни аккаунта, ни прав на чужие записи.

        🔴 Куки чистятся явно. `register` ставит cookie через `_set_auth_cookie`,
        а `TestClient` хранит их между запросами — без очистки «гостевой» запрос
        уходит от последнего зарегистрированного, и тест проверяет не то, что заявлено
        (первый прогон дал ложное зелёное именно так).
        """
        owner = _register(client, "restore-owner2@test.io")
        transaction_id = _create_transaction(client, owner)
        client.delete(f"/api/transactions/{transaction_id}", headers=owner)

        client.cookies.clear()
        assert client.post(f"/api/transactions/{transaction_id}/restore").status_code == 404

    def test_owner_still_restores_own_transaction(self, client: TestClient) -> None:
        """Свою — восстанавливает: проверка, что защита не сломала отмену удаления.

        Без этого теста починка могла бы «закрыть» дефект, запретив восстановление всем,
        и никто бы не заметил до жалобы на пропавшую кнопку отмены.
        """
        owner = _register(client, "restore-owner3@test.io")
        transaction_id = _create_transaction(client, owner)
        client.delete(f"/api/transactions/{transaction_id}", headers=owner)

        restored = client.post(
            f"/api/transactions/{transaction_id}/restore", headers=owner
        )
        assert restored.status_code == 200, restored.text
        assert restored.json()["id"] == transaction_id

    def test_restore_is_logged_with_user(self, client: TestClient, db_session) -> None:
        """Событие восстановления знает, кто восстановил (та же причина, что H7)."""
        from app.database.models import Event

        owner = _register(client, "restore-owner4@test.io")
        transaction_id = _create_transaction(client, owner)
        client.delete(f"/api/transactions/{transaction_id}", headers=owner)
        client.post(f"/api/transactions/{transaction_id}/restore", headers=owner)

        event = (
            db_session.query(Event)
            .filter(Event.event_type == "transaction_restored")
            .order_by(Event.id.desc())
            .first()
        )
        assert event is not None
        assert event.user_id is not None
