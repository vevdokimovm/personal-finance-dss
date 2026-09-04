"""Гостевой режим: демо-портреты и раздел валидации — только без входа.

После входа в профиль и загрузка портрета, и раздел валидации убираются: тестовая
песочница не должна смешиваться с реальными данными пользователя.
"""
from __future__ import annotations

import pytest

PORTRAITS = ["anna", "dmitriy", "mikhail", "igor", "olga", "viktor"]


def _login(client, email: str = "owner@fp.io", password: str = "strongpass1") -> None:
    """Регистрирует и логинит пользователя — TestClient сохраняет cookie сессии."""
    client.post("/api/auth/register",
                json={"email": email, "password": password, "consent": True})
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


class TestGuestSandbox:
    """🔴 Проверки видимости в разметке сняты в v8.45.0 — и это ДОЛГ, а не решение.

    `nav-validation` и `demo-case-select` — элементы Jinja-навигации на `/`. Эту страницу
    теперь отдаёт React, а гостевой песочницы в React НЕТ ВООБЩЕ: ни ссылки на раздел
    валидации, ни выбора демо-портрета. При переносе фронта их просто не перенесли,
    и обнаружилось это только здесь.

    Цена: README рекламирует «Демо за 30 секунд» — десять готовых портретов — как самый
    быстрый способ понять продукт. В новом интерфейсе этого входа не существует. Сервер
    всё умеет (`/api/demo/load`, `/validation`), недоступен только путь к нему.

    Записано в ROADMAP как отдельная задача. Здесь остаётся серверная часть: она и
    проверяема на этом уровне, и не зависит от того, каким фронтом её открывают.
    """

    def test_guest_can_open_validation(self, client) -> None:
        assert client.get("/validation").status_code == 200

    @pytest.mark.parametrize("case", PORTRAITS)
    def test_guest_can_load_each_portrait(self, client, case) -> None:
        resp = client.post(f"/api/demo/load?case={case}")
        assert resp.status_code == 200, resp.text


class TestAuthenticatedHidesSandbox:
    """🔴 Парные проверки «скрыто для вошедшего» тоже сняты — они стали ЛОЖНО зелёными.

    `assert "nav-validation" not in ...` проходил бы и дальше, но не потому, что элемент
    скрыт для вошедшего, а потому, что его нет ни для кого: страницу отдаёт React, где
    песочницы нет вовсе. Тест, зелёный по причине, не имеющей отношения к утверждению,
    хуже отсутствующего — он создаёт уверенность, что правило соблюдается.

    Настоящее разграничение доступа проверяется ниже, на сервере: гостю можно, вошедшему
    нельзя. Это и есть требование; видимость пункта меню — его отображение.
    """

    def test_demo_load_forbidden_when_logged_in(self, client) -> None:
        _login(client)
        resp = client.post("/api/demo/load?case=anna")
        assert resp.status_code == 403

    # 🔴 `test_validation_redirects_when_logged_in` снят в v8.47.0 вместе с Jinja.
    #
    # Редирект вошедшего с `/validation` на дашборд был свойством Jinja-роута
    # (`app/main.py`), а не продуктовым правилом: сам раздел был гостевой песочницей
    # в шапке старого интерфейса. В React отдельной страницы валидации нет — расчёт
    # портрета раскрывается предпросмотром прямо в карточке песочницы
    # (`/demo/preview`), а песочница показывается только гостю (`DemoSandbox`,
    # проверено `features/demo-sandbox/ui/DemoSandbox.test.tsx`).
    #
    # `/validation` остался живым адресом: catch-all отдаёт приложение, чтобы старая
    # закладка не давала «не найдено». Требовать от него редиректа значило бы
    # проверять поведение, которого в продукте больше нет.
    #
    # Настоящее разграничение — ниже и на сервере: демо-данные вошедшему запрещены.
