"""Гость не пишет финансовые данные в общий пул на проде (v8.53.0).

## Что нашёл аудит

`get_current_user_id` возвращает `None` гостю, а `_owner_filter(query, model, None)`
даёт `model.user_id IS NULL` — то есть **один глобальный пул на всех неавторизованных
посетителей сервера**. Привязки к сессии нет никакой.

Продукт при этом **ведёт** гостя туда: primary-кнопка «Внести операции» на пустом
дашборде, импорт выписки в пустом состоянии операций. `upload_statement` берёт тот же
`get_current_user_id`, то есть **реальная банковская выписка** уезжает в общий пул.

**Три сценария, все реальные:**

1. **Утечка.** Посетитель Б открывает сайт и видит операции, цели и кредиты, которые
   внёс посетитель А десять минут назад.
2. **Порча.** Гость А загружает демо-портрет (`/demo/load` зовёт `_clear_all`)
   и стирает данные гостя Б.
3. **Мимо демо.** Новый гость не увидит песочницу вовсе: дашборд считает себя
   «не пустым» из-за чужих данных.

## Решение вахты (допущение, принятое за владельца)

🔴 **В production гостевая ЗАПИСЬ финансовых данных запрещена; чтение демо остаётся.**

Правильная архитектурная починка — свой `session_id` каждому гостю с колонкой в БД
и фильтрацией по ней. Это изменение схемы всех финансовых таблиц и правка каждого
запроса; в вехе 8 такой объём не помещается, а утечка чужих финансов не может ждать
следующей вехи.

**Цена ошибки в обе стороны.** Запретить запись: гость смотрит демо-портреты, а чтобы
вносить своё — регистрируется; потеря обратима одной строкой конфига. Оставить как есть:
чужие финансовые данные видны каждому посетителю — необратимо и незаконно по 152-ФЗ.
Вторая ошибка кратно дороже, поэтому выбрана первая.

**В development поведение не меняется** — иначе сломается локальная разработка
и демо-сценарии, на которых стоят десятки тестов.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings

# Пути, которыми гость мог писать финансовые данные в общий пул.
GUEST_WRITE_PATHS = [
    ("post", "/api/transactions", {
        "amount": 100.0, "type": "expense", "category": "Еда",
        "date": "2026-09-05T12:00:00+00:00",
    }),
    ("post", "/api/obligations", {
        "name": "Кредит", "type": "credit", "bank": "Банк", "amount": 1000.0,
        "interest_rate": 10.0, "monthly_payment": 100.0, "months_left": 12,
    }),
    ("post", "/api/goals", {"name": "Цель", "target_amount": 1000.0, "priority": 1}),
    ("post", "/api/liquid-assets", {"name": "Вклад", "amount": 1000.0, "type": "deposit"}),
    ("post", "/api/budgets", {"category": "Еда", "limit_amount": 1000.0}),
]


@pytest.fixture
def production(monkeypatch):
    """Прод-режим. Гейт различает окружения намеренно: в dev гостевая запись —
    рабочий инструмент, в проде — общий пул на всех посетителей."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")


class TestGuestCannotWriteInProduction:
    """🔴 На проде запись финансовых данных требует аккаунта."""

    @pytest.mark.parametrize("method,path,payload", GUEST_WRITE_PATHS)
    def test_guest_write_is_refused(
        self, client: TestClient, production, method, path, payload
    ) -> None:
        """Гость получает 401, а не молча пишет в чужой пул.

        Именно 401, а не 403: человек не «не имеет права», он **не представился**.
        403 предложил бы ему запрашивать доступ, которого не существует.
        """
        client.cookies.clear()
        response = getattr(client, method)(path, json=payload)
        assert response.status_code == 401, (
            f"{method.upper()} {path} принял запись от гостя на проде "
            f"({response.status_code}) — данные уйдут в общий пул, видимый всем"
        )

    def test_statement_upload_is_refused(self, client: TestClient, production) -> None:
        """🔴 Импорт выписки — самое чувствительное: это банковские данные пачкой."""
        client.cookies.clear()
        response = client.post(
            "/api/banks/upload",
            files={"file": ("statement.csv", b"date,amount\n", "text/csv")},
        )
        assert response.status_code == 401

    def test_demo_load_is_refused(self, client: TestClient, production) -> None:
        """`/demo/load` зовёт `_clear_all(user_id=None)` — один гость стирает
        данные всех остальных гостей."""
        client.cookies.clear()
        cases = client.get("/api/demo/cases")
        assert cases.status_code == 200, "список демо-портретов должен читаться всегда"
        key = cases.json()["cases"][0]["key"]

        assert client.post(f"/api/demo/load?case={key}").status_code == 401


class TestReadingStaysOpen:
    """Демо остаётся доступным: запрещена запись, а не знакомство с продуктом."""

    def test_demo_cases_are_readable(self, client: TestClient, production) -> None:
        """Список портретов виден гостю — иначе на лендинге показывать нечего."""
        client.cookies.clear()
        assert client.get("/api/demo/cases").status_code == 200

    def test_demo_preview_works_without_writing(
        self, client: TestClient, production
    ) -> None:
        """Предпросмотр портрета считает БЕЗ записи в БД (v8.47.0) — значит
        общего пула не касается и остаётся открытым."""
        client.cookies.clear()
        cases = client.get("/api/demo/cases").json()["cases"]
        response = client.get(f"/api/demo/preview?case={cases[0]['key']}")
        assert response.status_code == 200

    def test_portrait_validation_stays_open(self, client: TestClient, production) -> None:
        """🔴 `/demo/analyze` — POST, который НИЧЕГО не пишет: `db` он не берёт вовсе
        (проверено по сигнатуре), считает портрет в памяти и возвращает метрики.

        Исключение проверяется тестом, потому что без него гейт «все небезопасные
        методы» отрезал бы гостю единственный способ прогнать СВОИ числа до
        регистрации — то есть закрыл бы воронку, починяя утечку. Мутация
        «убрать исключение» роняет ровно этот тест и никакой другой.
        """
        client.cookies.clear()
        response = client.post(
            "/api/demo/analyze",
            json={
                "income": [{"amount": 100000.0, "category": "Зарплата"}],
                "expenses": [{"amount": 40000.0, "category": "Еда"}],
                "obligations": [],
                "goals": [],
                "liquid_assets": [],
                "income_history": [],
                "expense_history": [],
                "risk_tolerance": 3,
            },
        )
        assert response.status_code == 200, response.text


class TestDevelopmentUnchanged:
    """В development ничего не менялось: локальная разработка и демо-сценарии живы."""

    def test_guest_write_still_works_in_dev(self, client: TestClient) -> None:
        """Фикстура `client` работает в dev-конфигурации — запись проходит.

        Этот тест защищает от переусердствования: запретить гостевую запись всюду
        значило бы сломать десятки существующих тестов и локальный сценарий
        «открыл и попробовал», ради проблемы, которой в dev нет.
        """
        client.cookies.clear()
        response = client.post(
            "/api/transactions",
            json={
                "amount": 100.0, "type": "expense", "category": "Еда",
                "date": "2026-09-05T12:00:00+00:00",
            },
        )
        assert response.status_code in (200, 201), response.text
