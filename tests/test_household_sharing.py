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


class TestBudgetCategoryIsPerOwner:
    """🔴 Нашёл `/code-review`: категория бюджета уникальна ГЛОБАЛЬНО.

    `budgets.category` несёт `unique=True` (модель и миграция 0006), а поиск
    существующей строки в `create_budget` идёт через `_owner_filter`, то есть
    в пределах владельца. Значит второй пользователь, заводящий «Продукты»,
    не находит своей строки, идёт на INSERT и получает `IntegrityError` — **500**.

    В однопользовательской разработке это невидимо: конфликт возникает только когда
    людей больше одного. То есть бюджеты ломались бы у всех, кроме первого,
    и только на проде.
    """

    def test_two_users_may_have_the_same_category(self, client: TestClient) -> None:
        """Одноимённые бюджеты у разных людей — норма, а не конфликт."""
        first = _register(client, "budget-a@test.io")
        created = client.post(
            "/api/budgets", headers=first,
            json={"category": "Продукты", "limit_amount": 30000.0},
        )
        assert created.status_code in (200, 201), created.text

        second = _register(client, "budget-b@test.io")
        response = client.post(
            "/api/budgets", headers=second,
            json={"category": "Продукты", "limit_amount": 25000.0},
        )
        assert response.status_code in (200, 201), (
            f"второй пользователь не смог завести «Продукты» ({response.status_code}): "
            "категория уникальна глобально, и бюджеты ломаются у всех, кроме первого"
        )

    def test_repeated_category_updates_the_limit(self, client: TestClient) -> None:
        """🔴 Уникальность не снята, а СУЖЕНА — upsert по категории продолжает работать.

        Мутация «убрать ключ `(user_id, category)`» не ловилась предыдущими тестами:
        они проверяли, что разные люди не мешают друг другу, и это верно и без ключа.
        Ключ держит другое — FR-22, «завести бюджет повторно значит изменить лимит».
        Без него повторное заведение создало бы ВТОРУЮ строку, и человек увидел бы
        две «Еды» с разными лимитами, не понимая, какая действует.
        """
        headers = _register(client, "budget-upsert@test.io")
        first = client.post("/api/budgets", headers=headers,
                            json={"category": "Еда", "limit_amount": 10000.0})
        assert first.status_code in (200, 201), first.text

        second = client.post("/api/budgets", headers=headers,
                             json={"category": "Еда", "limit_amount": 12000.0})
        assert second.status_code in (200, 201), second.text
        assert second.json()["id"] == first.json()["id"], (
            "повторное заведение категории создало вторую строку вместо изменения "
            "лимита — у человека две «Еды», и неясно, какая действует"
        )

        rows = [r for r in client.get("/api/budgets", headers=headers).json()
                if r["category"] == "Еда"]
        assert len(rows) == 1 and rows[0]["limit_amount"] == 12000.0

    def test_each_owner_sees_only_their_own_limit(self, client: TestClient) -> None:
        """Лимиты не перетираются: у каждого свой.

        Без этой пары «починка» уникальности могла бы свестись к тому, что второй
        пользователь молча переписывает бюджет первого, — и это было бы хуже 500,
        потому что беззвучно.
        """
        first = _register(client, "budget-c@test.io")
        client.post("/api/budgets", headers=first,
                    json={"category": "Транспорт", "limit_amount": 9000.0})
        second = _register(client, "budget-d@test.io")
        client.post("/api/budgets", headers=second,
                    json={"category": "Транспорт", "limit_amount": 4000.0})

        first_rows = client.get("/api/budgets", headers=first).json()
        second_rows = client.get("/api/budgets", headers=second).json()
        assert [r["limit_amount"] for r in first_rows if r["category"] == "Транспорт"] == [9000.0]
        assert [r["limit_amount"] for r in second_rows if r["category"] == "Транспорт"] == [4000.0]


class TestWriteScopeIsStricterThanReadScope:
    """🔴 Нашёл `/code-review`: запись шла через ЧИТАЮЩИЙ скоуп.

    `_owner_filter` объединяет свои строки с общими строками household — это правильный
    скоуп для ЧТЕНИЯ. Но три пути использовали его перед **изменением**: `create_budget`,
    `set_transaction_category`, `apply_category_rule`.

    Следствие: участник семьи — **включая `viewer`, у которого прав на запись нет
    вовсе** — правит чужие записи. `create_budget` перезаписывает лимит общего бюджета,
    а `apply_category_rule` меняет категории пачкой по всем совпавшим общим операциям.

    Что это значит для продукта: правило `can_write_household` (owner/member, но не
    viewer) существует и на этих путях не спрашивалось. Соседние функции — `update_transaction`,
    `delete_transaction`, `delete_budget`, `restore_budget` — сверяют `user_id` строго,
    то есть намерение однозначно, а три пути из него выпали.
    """

    def _member_of(self, client: TestClient, owner: dict[str, str], household_id: int,
                   email: str, role: str) -> dict[str, str]:
        invite = client.post(
            f"/api/households/{household_id}/invites", headers=owner, json={"role": role},
        )
        assert invite.status_code in (200, 201), invite.text
        member = _register(client, email)
        accepted = client.post(
            f"/api/households/invites/{invite.json()['token']}/accept", headers=member
        )
        assert accepted.status_code in (200, 201), accepted.text
        return member

    def test_member_cannot_overwrite_shared_budget_limit(self, client: TestClient) -> None:
        """Чужой общий бюджет не перетирается «своим» созданием той же категории."""
        owner = _register(client, "wscope-owner@test.io")
        household_id = _household(client, owner)
        created = client.post(
            "/api/budgets", headers=owner,
            json={"category": "Продукты", "limit_amount": 50000.0, "household_id": household_id},
        )
        assert created.status_code in (200, 201), created.text

        member = self._member_of(client, owner, household_id, "wscope-member@test.io", "member")
        # Личный бюджет той же категории: `household_id` не передан, значит человек
        # заводит СВОЙ, а не правит общий.
        client.post("/api/budgets", headers=member,
                    json={"category": "Продукты", "limit_amount": 1.0})

        rows = client.get("/api/budgets", headers=owner).json()
        shared = [r for r in rows if r["id"] == created.json()["id"]]
        assert shared and shared[0]["limit_amount"] == 50000.0, (
            "общий бюджет перезаписан лимитом другого участника — запись шла "
            "через читающий скоуп"
        )

    def test_viewer_cannot_recategorise_shared_transaction(self, client: TestClient) -> None:
        """🔴 `viewer` не меняет категорию чужой общей операции.

        У него нет прав на запись по определению (`can_write_household` пропускает
        owner и member), и именно этот случай показывает, что дело не в «участник
        правит участника», а в обходе роли целиком.
        """
        owner = _register(client, "wscope-owner2@test.io")
        household_id = _household(client, owner)
        created = client.post(
            "/api/transactions", headers=owner,
            json={"amount": 1000.0, "type": "expense", "category": "Еда",
                  "date": TODAY, "household_id": household_id},
        )
        assert created.status_code in (200, 201), created.text
        transaction_id = created.json()["id"]

        viewer = self._member_of(client, owner, household_id, "wscope-viewer@test.io", "viewer")
        response = client.post(
            f"/api/transactions/{transaction_id}/category",
            headers=viewer, json={"category": "Развлечения"},
        )
        assert response.status_code in (403, 404), (
            f"viewer переназначил категорию чужой операции ({response.status_code})"
        )

        rows = client.get("/api/transactions", headers=owner).json()
        row = next(r for r in rows if r["id"] == transaction_id)
        assert row["category"] == "Еда", "категория чужой операции изменена"

    def test_owner_still_edits_own_records(self, client: TestClient) -> None:
        """Свои записи по-прежнему правятся — проверка, что защита не сломала работу."""
        owner = _register(client, "wscope-owner3@test.io")
        created = client.post(
            "/api/transactions", headers=owner,
            json={"amount": 500.0, "type": "expense", "category": "Еда", "date": TODAY},
        )
        transaction_id = created.json()["id"]

        response = client.post(
            f"/api/transactions/{transaction_id}/category",
            headers=owner, json={"category": "Развлечения"},
        )
        assert response.status_code in (200, 201), response.text
