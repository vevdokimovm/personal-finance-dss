"""Upsert бюджета не меняет владение молча (v9.2.0).

## Что нашёл `/code-review ultra`

`POST /api/budgets` работает upsert-ом: повторный вызов с той же категорией правит
существующую строку. Ветка обновления трогает **три поля** — `limit_amount`,
`is_deleted`, `deleted_at` — и `household_id` из тела запроса не применяет вовсе.

🔴 **Миграция 0036 сделала эту ветку основной.** До неё `category` была уникальна
глобально, и повторный POST у того же пользователя был краевым случаем. После сужения
ключа до пары `(user_id, category)` любой повторный POST своей же категории попадает
именно сюда.

## Разбор двух сценариев ревью — подтвердился ОДИН

Ревью описало два. Разобраны по коду формы (`BudgetForm.tsx:69`), и они не равны:

**Сценарий «правка лимита разделяет семейный бюджет» — НЕ дефект.** Форма шлёт
`household_id` только при создании (`...(isEdit ? {} : { household_id })`), при правке
поле отсутствует и приходит `None`. Сохранение прежнего владения здесь — **правильное**
поведение: владелец правит лимит СВОЕГО общего бюджета, и бюджет обязан остаться общим.
Применить `None` буквально значило бы расшарить обратно — вот это было бы дефектом.

🔴 **Сценарий «попытка поделиться молча не срабатывает» — дефект, и он реальный.**
Человек с личным бюджетом «Продукты» отправляет тот же `category` с `household_id`,
чтобы сделать его семейным. Гард `ensure_can_share` пропускает (право есть), upsert
находит личную строку, правит лимит и **возвращает 201** — при том что `household_id`
в строке остался `None`. Человек уверен, что поделился; не поделился никто.

Это ровно тот класс, против которого заводился `ensure_can_share` в v8.55.0: «продукт
принимает данные и молча их теряет». Гард закрыл путь INSERT и не закрыл путь UPDATE.

## Почему 409, а не «применить household_id»

Смена владения записи — отдельная операция, и код её не делает нигде: форма не показывает
контрол при правке именно потому, что «PUT `household_id` не принимает». Тихо разрешить
переезд через POST значило бы завести полускрытый способ делать то, что продукт объявляет
неподдерживаемым, — и он сработал бы только для бюджетов, разойдясь с остальными
четырьмя сущностями.

**409 отвечает на вопрос, который человек задал:** запрос не применён, и видно почему.
"""
from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient


def _register(client: TestClient, email: str) -> dict[str, str]:
    """Регистрация с согласиями — форма та же, что в `test_household_sharing.py`.

    🔴 `consent: True` в теле обязателен: без него регистрация отвечает 422,
    и тест падает на `KeyError: access_token`, сообщая про ключ словаря вместо
    настоящей причины.
    """
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


class TestUpsertKeepsExistingScope:
    """Правка лимита не трогает владение — и это правильно, а не упущение."""

    def test_editing_limit_without_household_id_keeps_budget_shared(
        self, client: TestClient
    ) -> None:
        """🔴 Форма при правке `household_id` НЕ шлёт — значит `None` здесь означает
        «не трогай владение», а не «сделай личным».

        Мутация «применять household_id как есть» роняет этот тест: семейный бюджет
        стал бы личным от обычной правки суммы, и остальные члены семьи потеряли бы
        его из виду без единого сообщения.
        """
        owner = _register(client, "upsert-keep@test.io")
        household_id = _household(client, owner)

        created = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Продукты", "limit_amount": 50000, "household_id": household_id},
        )
        assert created.status_code == status.HTTP_201_CREATED
        assert created.json()["household_id"] == household_id

        edited = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Продукты", "limit_amount": 5000},
        )
        assert edited.status_code == status.HTTP_201_CREATED
        assert edited.json()["limit_amount"] == 5000
        assert edited.json()["household_id"] == household_id, (
            "правка лимита разделила семейный бюджет — остальные потеряли его из виду"
        )


class TestUpsertRefusesSilentScopeChange:
    """🔴 Главное: попытка сменить владение не может закончиться тихим успехом."""

    def test_sharing_an_existing_personal_budget_is_refused_loudly(
        self, client: TestClient
    ) -> None:
        """Человек делает личный бюджет семейным — и обязан узнать, что так нельзя.

        До правки эндпоинт отвечал 201 и оставлял бюджет личным: ответ говорил
        «готово», строка говорила «ничего не изменилось».
        """
        owner = _register(client, "upsert-share@test.io")
        household_id = _household(client, owner)

        personal = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Продукты", "limit_amount": 3000},
        )
        assert personal.json()["household_id"] is None

        response = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Продукты", "limit_amount": 3000, "household_id": household_id},
        )
        assert response.status_code == status.HTTP_409_CONFLICT, (
            "попытка поделиться существующим бюджетом вернула успех — "
            f"а поделиться не вышло: {response.status_code}, {response.text[:200]}"
        )

        unchanged = client.get("/api/budgets/status", headers=owner)
        row = next(r for r in unchanged.json() if r["category"] == "Продукты")
        assert row["household_id"] is None, "отказ отказом, а строку всё-таки тронули"

    def test_moving_a_shared_budget_to_another_household_is_refused(
        self, client: TestClient
    ) -> None:
        """Переезд между котлами — та же неподдерживаемая операция, тот же ответ."""
        owner = _register(client, "upsert-move@test.io")
        first = _household(client, owner, "Первая")
        second = _household(client, owner, "Вторая")

        client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Транспорт", "limit_amount": 9000, "household_id": first},
        )
        response = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Транспорт", "limit_amount": 9000, "household_id": second},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_resubmitting_the_same_household_id_is_fine(self, client: TestClient) -> None:
        """Тот же household — не смена владения, а обычная правка. Отказывать не за что.

        🔴 Проверка защищает от переусердствования: отказ на совпадающем значении
        сломал бы обычный сценарий «форма прислала то, что и было».
        """
        owner = _register(client, "upsert-same@test.io")
        household_id = _household(client, owner)

        client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Кафе", "limit_amount": 4000, "household_id": household_id},
        )
        response = client.post(
            "/api/budgets",
            headers=owner,
            json={"category": "Кафе", "limit_amount": 7000, "household_id": household_id},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["limit_amount"] == 7000
        assert response.json()["household_id"] == household_id

    def test_reviving_a_deleted_budget_still_works(self, client: TestClient) -> None:
        """Оживление мягко удалённой строки — законный смысл upsert (P1.7), не смена владения."""
        owner = _register(client, "upsert-revive@test.io")
        created = client.post(
            "/api/budgets", headers=owner, json={"category": "Спорт", "limit_amount": 2000}
        )
        client.delete(f"/api/budgets/{created.json()['id']}", headers=owner)

        revived = client.post(
            "/api/budgets", headers=owner, json={"category": "Спорт", "limit_amount": 2500}
        )
        assert revived.status_code == status.HTTP_201_CREATED
        assert revived.json()["limit_amount"] == 2500
