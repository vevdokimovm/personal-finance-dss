"""«Семейный доступ» делает общими все финансовые сущности, а не одни цели (v8.55.0).

## Что нашёл аудит

`household_id` заведён в схеме **пяти** сущностей (транзакции, обязательства, цели,
ликвидные активы, бюджеты) и в колонках их таблиц. Проверка права `can_write_household`
при этом стоит **только в целях** (`routes_goals.py:42`), а остальные эндпоинты поле
из тела запроса **не читают вовсе**: `create_transaction_endpoint` не передаёт его
в `crud.create_transaction`, хотя параметр там есть.

🔴 **Как это выглядит для человека.** Он приглашает жену в household, отправляет
операцию с `household_id` — сервер отвечает `201`, поле в ответе `null`, операция
остаётся личной. Продукт **принял данные и молча их потерял**: не отказ, который
можно заметить, а тихое расхождение между тем, что человек сказал, и тем, что
записано. Раздел «Семейный доступ» при этом существует и приглашения рассылает.

## Вторая половина той же дыры

Там, где поле игнорируется, нет и проверки права. Стоит начать его передавать,
не добавив `can_write_household`, — и любой пользователь запишет операцию в чужой
household, зная его `id`. Поэтому оба утверждения проверяются вместе: поле доезжает
И право проверяется. Порознь каждое из них — половина дефекта.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

TODAY = "2026-09-05T12:00:00+00:00"


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


def _household(client: TestClient, headers: dict[str, str], name: str = "Семья") -> int:
    created = client.post("/api/households", headers=headers, json={"name": name})
    assert created.status_code in (200, 201), created.text
    return created.json()["id"]


# Сущность → путь и тело. Цели уже умеют общий доступ и остаются здесь как эталон:
# ими проверяется, что починка не сломала работающее.
SHAREABLE = {
    "transaction": ("/api/transactions", {
        "amount": 1000.0, "type": "expense", "category": "Еда", "date": TODAY,
    }),
    "obligation": ("/api/obligations", {
        "name": "Ипотека", "type": "mortgage", "bank": "Банк", "amount": 1000000.0,
        "interest_rate": 12.0, "monthly_payment": 15000.0, "months_left": 120,
    }),
    "goal": ("/api/goals", {"name": "Отпуск", "target_amount": 200000.0, "priority": 1}),
    "liquid_asset": ("/api/liquid-assets", {
        "name": "Вклад", "amount": 300000.0, "type": "deposit",
    }),
    "budget": ("/api/budgets", {"category": "Продукты", "limit_amount": 30000.0}),
}


class TestHouseholdIdIsHonoured:
    """🔴 Поле доезжает до базы, а не теряется молча."""

    @pytest.mark.parametrize("entity", sorted(SHAREABLE))
    def test_created_entity_keeps_household_id(
        self, client: TestClient, entity: str
    ) -> None:
        """Отправленный `household_id` возвращается в ответе.

        Мутация «перестать передавать поле в crud» роняет ровно этот тест: ответ
        отдаст `null`, и станет видно, что запись ушла в личные данные.
        """
        path, payload = SHAREABLE[entity]
        owner = _register(client, f"hh-{entity}@test.io")
        household_id = _household(client, owner)

        created = client.post(path, headers=owner, json={**payload, "household_id": household_id})
        assert created.status_code in (200, 201), created.text
        assert created.json().get("household_id") == household_id, (
            f"{entity}: продукт принял household_id и потерял его — человек думает, "
            "что запись общая, а она личная"
        )


class TestHouseholdIdIsGuarded:
    """Вторая половина: чужой household недоступен для записи."""

    @pytest.mark.parametrize("entity", sorted(SHAREABLE))
    def test_stranger_cannot_write_into_someone_elses_household(
        self, client: TestClient, entity: str
    ) -> None:
        """🔴 403 постороннему, знающему `id`.

        Без этой проверки починка предыдущего теста открыла бы запись в чужой
        семейный котёл всем, кто угадает число, — и это было бы хуже исходного
        дефекта, потому что данные не теряются, а появляются у посторонних.
        """
        path, payload = SHAREABLE[entity]
        owner = _register(client, f"hh-guard-owner-{entity}@test.io")
        household_id = _household(client, owner)

        stranger = _register(client, f"hh-guard-stranger-{entity}@test.io")
        response = client.post(
            path, headers=stranger, json={**payload, "household_id": household_id}
        )
        assert response.status_code == 403, (
            f"{entity}: посторонний записал данные в чужой household ({response.status_code})"
        )

    @pytest.mark.parametrize("entity", sorted(SHAREABLE))
    def test_nonexistent_household_is_refused(
        self, client: TestClient, entity: str
    ) -> None:
        """Несуществующий household — тот же отказ, а не 500 и не тихая запись."""
        path, payload = SHAREABLE[entity]
        owner = _register(client, f"hh-missing-{entity}@test.io")

        response = client.post(path, headers=owner, json={**payload, "household_id": 999999})
        assert response.status_code == 403, response.text


class TestPersonalStaysPersonal:
    """Без `household_id` всё работает как раньше — починка не меняет умолчание."""

    @pytest.mark.parametrize("entity", sorted(SHAREABLE))
    def test_entity_without_household_is_personal(
        self, client: TestClient, entity: str
    ) -> None:
        """Умолчание — личная запись.

        Тест защищает от переусердствования: подставить household «по умолчанию»
        значило бы раздать чужим людям данные, которых им не показывали.
        """
        path, payload = SHAREABLE[entity]
        owner = _register(client, f"hh-personal-{entity}@test.io")

        created = client.post(path, headers=owner, json=payload)
        assert created.status_code in (200, 201), created.text
        assert created.json().get("household_id") is None


class TestSharedRecordIsVisibleToFamily:
    """🔴 Ради этого функция и существует: второй участник ВИДИТ общую запись.

    Проверки выше говорят, что поле доезжает до базы и что чужой household закрыт.
    Ни одна из них не отвечает на вопрос, ради которого человек нажимает «поделиться»:
    увидит ли это жена. Чтение через household живёт в `_owner_filter` с P3.7 —
    но до этого батча в общий котёл ничего не попадало, и вся ветка была мёртвой.
    """

    def _invite_and_accept(
        self, client: TestClient, owner: dict[str, str], household_id: int, guest_email: str
    ) -> dict[str, str]:
        invite = client.post(
            f"/api/households/{household_id}/invites",
            headers=owner,
            json={"role": "member"},
        )
        assert invite.status_code in (200, 201), invite.text
        token = invite.json()["token"]

        member = _register(client, guest_email)
        accepted = client.post(f"/api/households/invites/{token}/accept", headers=member)
        assert accepted.status_code in (200, 201), accepted.text
        return member

    def test_family_member_sees_shared_transaction(self, client: TestClient) -> None:
        """Операция, положенная в общий котёл, видна второму участнику семьи."""
        owner = _register(client, "share-owner@test.io")
        household_id = _household(client, owner)
        member = self._invite_and_accept(client, owner, household_id, "share-member@test.io")

        created = client.post(
            "/api/transactions",
            headers=owner,
            json={
                "amount": 4200.0, "type": "expense", "category": "Продукты",
                "date": TODAY, "household_id": household_id,
            },
        )
        assert created.status_code in (200, 201), created.text

        seen = client.get("/api/transactions", headers=member).json()
        assert any(row["id"] == created.json()["id"] for row in seen), (
            "общая операция не видна второму участнику — «поделиться» ничего не дало"
        )

    def test_personal_transaction_stays_invisible_to_family(self, client: TestClient) -> None:
        """🔴 Обратная сторона: личное остаётся личным даже внутри семьи.

        Без этого теста починка могла бы «заработать», раздав родственникам всё подряд, —
        и заметил бы это пользователь, а не гейт.
        """
        owner = _register(client, "share-owner2@test.io")
        household_id = _household(client, owner)
        member = self._invite_and_accept(client, owner, household_id, "share-member2@test.io")

        personal = client.post(
            "/api/transactions",
            headers=owner,
            json={"amount": 999.0, "type": "expense", "category": "Личное", "date": TODAY},
        )
        assert personal.status_code in (200, 201), personal.text

        seen = client.get("/api/transactions", headers=member).json()
        assert not any(row["id"] == personal.json()["id"] for row in seen), (
            "личная операция видна другому участнику семьи — утечка внутри household"
        )
