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

## Принятое допущение

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

    def test_demo_load_is_allowed_and_why(self, client: TestClient, production) -> None:
        """🔴 `/demo/load` гостю на проде РАЗРЕШЁН — решение пересмотрено 08.09.2026.

        Прежняя редакция запрещала его с верным доводом: ручка зовёт
        `_clear_all(user_id=None)`, то есть один гость стирает данные всех остальных
        гостей. Довод остался верным, но перестал быть решающим, и вот почему.

        **Что было ценой запрета.** Гость получал 401 отсюда, а вошедший — 403 от самой
        ручки («демо доступны только в гостевом режиме»). Третьего состояния нет: демо
        на проде было недостижимо ВСЕМ СРАЗУ. Это единственный вход в продукт без
        аккаунта и витрина, обещанная в README; кнопка во фронте показывается только
        гостю — ровно тому, кому она вернёт 401. Локально всё работало, поэтому
        не замечалось.

        **Что стало ценой разрешения.** На проде гостевая ЗАПИСЬ финансовых данных
        запрещена всем остальным периметром (v8.53.0 и далее), поэтому в пуле
        `user_id IS NULL` не остаётся ничего, кроме **синтетических демо-портретов**,
        загруженных такими же гостями. Стереть их — потеря нулевая: следующий клик
        загружает заново.

        🔴 Ошибка в сторону запрета стоила рабочей витрины всем посетителям; ошибка
        в сторону разрешения стоит одному гостю повторного клика. Полное решение —
        сессионный пул с `session_id` (задача вехи 9+), и оно снимает вопрос целиком.
        """
        client.cookies.clear()
        cases = client.get("/api/demo/cases")
        assert cases.status_code == 200, "список демо-портретов должен читаться всегда"
        key = cases.json()["cases"][0]["key"]

        assert client.post(f"/api/demo/load?case={key}").status_code != 401


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


class TestPlanningWritesAreGuardedToo:
    """🔴 Снимки плана и сценарии — тоже финансовые данные, и тоже под запретом.

    Митигация v8.53.0 («на проде гостевая ЗАПИСЬ финансовых данных запрещена») была
    неполной: `planning_router` подключён только с `_FIN`, а гейт согласия гостя
    **пропускает намеренно** — «согласие там означало бы сломать демо ради формальности».
    Значит защиты от гостевой записи у планирования не было вовсе.

    🔴 **И это самый чувствительный объект из всех.** Отдельная транзакция защищена,
    а снимок плана несёт агрегированный портрет целиком: доходы, расходы, обязательства,
    цели, Rt/Lt/Dt. Он же лежит в общем пуле `user_id IS NULL`, то есть виден каждому
    анонимному посетителю того же экземпляра.

    Найдено пятым проходом независимого аудита 08.09.2026. Периметр проверялся
    по прозаическому списку из пяти путей — planning в него не входил.
    """

    def test_guest_cannot_save_plan_snapshot(self, client, monkeypatch) -> None:
        """🔴 Мутация «снять `_GUEST` с сохранения снимка» роняет тест здесь."""
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        response = client.post("/api/planning/history", json={"note": "проба"})
        assert response.status_code in (401, 403), (
            f"гость сохранил снимок плана на проде (код {response.status_code}) — "
            "это агрегированный финансовый портрет в общем пуле"
        )

    def test_guest_cannot_save_scenario(self, client, monkeypatch) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        response = client.post("/api/planning/scenarios", json={})
        assert response.status_code in (401, 403, 422), response.status_code
        assert response.status_code != 200

    def test_guest_cannot_delete_someone_elses_snapshot(self, client, monkeypatch) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        response = client.delete("/api/planning/history/1")
        assert response.status_code in (401, 403), (
            "гость удаляет снимок из общего пула"
        )

    def test_calculation_stays_open_for_the_sandbox(self, client, monkeypatch) -> None:
        """🔴 Расчёт плана гостю по-прежнему доступен — на нём держится песочница.

        `POST /planning/calculate` ничего не сохраняет: это чистый расчёт, и запрет
        на нём сломал бы демо-режим, ради которого анонимный доступ и существует.
        Разделение проходит по «пишет ли ручка», а не по методу HTTP.
        """
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        response = client.post("/api/planning/calculate", json={})
        assert response.status_code not in (401, 403), (
            f"расчёт плана закрылся для гостя (код {response.status_code}) — "
            "песочница сломана"
        )


class TestDemoSandboxStaysReachableOnProduction:
    """🔴 Демо-песочница на проде не должна быть недостижима ВСЕМ сразу.

    Два условия сомкнулись, и каждое по отдельности верно:

    - `demo_router` подключён с `_GUEST` (v8.53.0, против общего пула), а в списке
      исключений `READ_ONLY_WRITE_PATHS` стоит только `/api/demo/analyze` —
      значит гостю на проде `POST /demo/load` отвечает **401**;
    - сами ручки отвечают вошедшему **403**: «демо-портреты доступны только
      в гостевом режиме» — правило старше и написано под другую эпоху.

    Гость → 401. Вошедший → 403. Третьего состояния нет.

    🔴 **Это единственный вход в продукт для человека без аккаунта и одновременно
    витрина.** README обещает «один клик — и перед вами полный расчётный цикл
    на живых данных»; кнопка во фронте показывается **только** гостю, то есть ровно
    тому, кому она вернёт 401. Предпросмотр при этом работает, поэтому экран выглядит
    живым и ломается на главной кнопке — а сообщение об отказе отрицает само себя:
    «демо-портреты доступны для просмотра без регистрации».

    Найдено шестым проходом независимого аудита 08.09.2026. Гейт периметра увидеть
    это не мог по устройству: он проверяет, закрыта ли ручка, а не может ли её
    кто-нибудь пройти.
    """

    def test_guest_can_load_demo_on_production(self, client, monkeypatch) -> None:
        """🔴 Мутация «убрать /demo/load из исключений» роняет тест здесь."""
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        response = client.post("/api/demo/load", json={"case": "student"})
        assert response.status_code != 401, (
            "гость не может загрузить демо-портрет на проде — а это единственный "
            "вход в продукт без аккаунта и витрина, обещанная в README"
        )

    def test_guest_can_clear_demo_on_production(self, client, monkeypatch) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        assert client.post("/api/demo/clear").status_code != 401

    def test_demo_still_refuses_a_logged_in_user(self, client, monkeypatch) -> None:
        """А вошедшему демо по-прежнему отказывает — это отдельное правило.

        Демо-портрет подменяет данные, и вошедшему он затёр бы его собственные.
        Отказ остаётся, меняется только то, что гость до него доходит.
        """
        from app.config import settings

        client.post("/api/auth/register", json={
            "email": "demo-guard@test.io", "password": "verysecret1", "consent": True})
        monkeypatch.setattr(settings, "ENVIRONMENT", "production", raising=False)
        assert client.post("/api/demo/load", json={"case": "student"}).status_code == 403
