"""`banks_router` под гейтом согласия на финансовые данные (остаток H3 закрыт, v8.43.0).

Самый чувствительный пункт всей гипотезы H3. Импорт банковской выписки пачкой обрабатывал
финансовые данные **без согласия**, тогда как ручное добавление ОДНОЙ операции его
требовало (`transactions_router` под `_FIN` с v8.27.0). То есть чем больше данных человек
загружал за раз, тем меньше проверок стояло на пути — прямо наоборот тому, как должно быть.

## Почему гейт ставится именно сейчас

Решение владельца от v8.27.0: гейт ставится ТОЛЬКО вместе с фронтом, иначе экран отдаёт
403 без объяснения (SEV1 `CONSENT-GATE-NO-UI`). Единственным потребителем `banks_router`
был `app.js`, и `grep "403|consent"` по нему даёт **ноль совпадений на 2658 строк**:
человек увидел бы невнятную ошибку без слова «согласие».

В этом батче импорт переехал в React, где `ConsentRequiredPanel` работает с v8.27.0 —
условие снято, и гейт ставится тем же батчем. Не раньше (окно с невнятной ошибкой)
и не позже (окно с обработкой финданных без гейта).

Разбор — `docs/reports/decisions/2026-09-04_h3_and_jinja_removal_order.md`.
"""
from __future__ import annotations

import io

import pytest

BANK_ROUTES: list[tuple[str, str]] = [
    ("get", "/api/banks/list"),
    ("post", "/api/banks/sync"),
    ("post", "/api/banks/sync/tinkoff"),
]


def _register(client, email: str, *, with_consent: bool) -> None:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    if with_consent:
        client.post("/api/consents/financial_data")


@pytest.mark.parametrize("method,path", BANK_ROUTES)
def test_bank_routes_require_financial_consent(client, method, path) -> None:
    _register(client, f"banks-{path.replace('/', '-')}@test.io", with_consent=False)
    response = getattr(client, method)(path)
    assert response.status_code == 403, (
        f"{method.upper()} {path} доступен без согласия на финансовые данные — "
        f"получен {response.status_code}"
    )


def test_statement_upload_requires_consent(client) -> None:
    """🔴 Главный пункт H3: импорт выписки ПАЧКОЙ без согласия.

    Ручное добавление одной операции согласия требовало, а загрузка сотен строк
    из файла — нет.
    """
    _register(client, "banks-upload@test.io", with_consent=False)
    response = client.post(
        "/api/banks/upload",
        files={"file": ("statement.csv", io.BytesIO(b"date,amount\n"), "text/csv")},
        data={"bank_id": "tinkoff"},
    )
    assert response.status_code == 403


def test_consent_given_upload_reaches_the_parser(client) -> None:
    """С согласием гейт пропускает — дальше отвечает сам разбор.

    Пустой CSV распознать нельзя, и ответ будет `status="error"` со статусом 200:
    «файл не распознан» — результат работы, а не сбой. Проверяется, что 403 больше нет,
    то есть гейт не заперт наглухо.
    """
    _register(client, "banks-upload-ok@test.io", with_consent=True)
    response = client.post(
        "/api/banks/upload",
        files={"file": ("statement.csv", io.BytesIO(b"date,amount\n"), "text/csv")},
        data={"bank_id": "tinkoff"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "error"


def test_gate_message_names_the_consent(client) -> None:
    """Отказ объясняет, ЧТО нужно сделать, а не просто «нельзя».

    Ровно этого не умел `app.js` — и потому гейт нельзя было ставить, пока импорт жил
    в нём. React читает `detail` и показывает `ConsentRequiredPanel` с кнопкой.
    """
    _register(client, "banks-detail@test.io", with_consent=False)
    body = client.get("/api/banks/list").json()
    detail = body.get("detail")
    assert detail, "403 без объяснения — это тупик, человек не поймёт, что делать"
    text = detail if isinstance(detail, str) else str(detail)
    assert "соглас" in text.lower()
