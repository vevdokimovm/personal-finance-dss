"""`plaid_router` под гейтом согласия на финансовые данные (остаток H3, v8.42.0).

Plaid обменивает public_token на access_token банка и тянет транзакции — это финансовые
данные в самом прямом смысле, и обрабатывать их без согласия нельзя. Периметр `_FIN`
(`app/api/router.py`) его не покрывал: гипотеза H3 independent-expert, подтверждена
в v8.30.2.

## Почему это делается сейчас, а не «вместе с фронтом»

Решение владельца от v8.27.0 требует ставить гейт ТОЛЬКО вместе с фронтом — иначе экран
отдаёт 403 без объяснения (SEV1 `CONSENT-GATE-NO-UI`). Разбор
`docs/reports/decisions/2026-09-04_h3_and_jinja_removal_order.md` проверил по диску:
**у `plaid_router` фронта нет вообще.**

    grep -rn "api/plaid" frontend/static/js/app.js frontend/src → ничего
    routes_plaid.py:4 — в РФ-сборке любой вызов отвечает 404

Оговорка защищает от отказа без объяснения; там, где интерфейса нет, защищать нечего.
`banks_router` — другой случай, у него единственный потребитель `app.js`, и он приедет
вместе с переносом импорта выписки в React.

## Порядок проверок внутри эндпоинта

Гейт стоит на уровне роутера, то есть срабатывает ДО тела функции: без согласия ответ 403,
а не 404 «Plaid не активирован». Это верно и юридически, и по смыслу — отказ по согласию
не должен раскрывать, включена ли интеграция.
"""
from __future__ import annotations

import pytest

PLAID_ROUTES: list[tuple[str, str]] = [
    ("post", "/api/plaid/exchange"),
    ("post", "/api/plaid/sync"),
]


def _register(client, email: str, *, with_consent: bool) -> None:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    if with_consent:
        client.post("/api/consents/financial_data")


@pytest.mark.parametrize("method,path", PLAID_ROUTES)
def test_plaid_requires_financial_consent(client, method, path) -> None:
    """Без согласия — 403, и это не должно зависеть от того, включён ли Plaid."""
    _register(client, f"plaid-{path.replace('/', '-')}@test.io", with_consent=False)
    response = getattr(client, method)(path, json={"public_token": "x", "item_id": "y"})
    assert response.status_code == 403, (
        f"{method.upper()} {path} обработал бы финансовые данные без согласия — "
        f"получен {response.status_code}"
    )


@pytest.mark.parametrize("method,path", PLAID_ROUTES)
def test_consent_given_gate_passes(client, method, path) -> None:
    """С согласием гейт пропускает — дальше отвечает сама ручка.

    В РФ-сборке это 404 «не активировано»: PLAID_* не заданы. Проверяется именно то,
    что 403 больше нет — то есть гейт не заперт наглухо.
    """
    _register(client, f"plaid-ok-{path.replace('/', '-')}@test.io", with_consent=True)
    response = getattr(client, method)(path, json={"public_token": "x", "item_id": "y"})
    assert response.status_code != 403


def test_gate_answers_before_plaid_availability(client) -> None:
    """Отказ по согласию не раскрывает, включена ли интеграция.

    Без гейта неавторизованный по согласию пользователь получил бы 404 «Plaid не
    активирован» — то есть узнал бы о конфигурации сервера раньше, чем ему отказали
    в обработке его данных. Гейт на уровне роутера отвечает первым.
    """
    _register(client, "plaid-order@test.io", with_consent=False)
    response = client.post("/api/plaid/sync")
    assert response.status_code == 403
    assert "404" not in response.text
