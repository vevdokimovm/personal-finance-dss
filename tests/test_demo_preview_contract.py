"""Предпросмотр портрета типизирован и считает БЕЗ записи в БД (v8.47.0).

## Зачем это ключевой эндпоинт, а не «ещё один»

Загрузка портрета (`/demo/load`) **деструктивна**: вызывает `_clear_all` и стирает всё,
что гость успел внести, мимо мягкого удаления и отмены. В v8.46.0 это закрыли
подтверждением, но человек всё равно выбирал вслепую: чем портрет «Анна» отличается
от «Михаила», было видно только из абзаца прозы.

`/demo/preview` считает портрет **целиком и ничего не пишет**: метрики, прогноз,
рекомендацию с готовым объяснением человеческим языком. Сначала посмотрел — потом решил,
загружать ли. Это снимает необратимость выбора, а не украшает экран.

В Jinja предпросмотр был («Показать расчёт — метрики, прогноз, рекомендация»,
`templates/validation.html`) и потерялся при переносе фронта — как и сама песочница.

## 🔴 Проверяется отсутствие записи, а не только форма ответа

«Считает без записи в БД» — обещание, на котором держится вся ценность: предпросмотр,
который что-то пишет, ничем не лучше загрузки. Проверяется прямым сравнением состояния
базы до и после, а не чтением докстроки.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def _resolve(schema: dict, node: dict) -> dict:
    if "$ref" in node:
        return schema["components"]["schemas"][node["$ref"].rsplit("/", 1)[-1]]
    return node


class TestContract:
    def test_preview_is_typed(self, schema) -> None:
        op = schema["paths"]["/api/demo/preview"]["get"]
        body = _resolve(schema, op["responses"]["200"]["content"]["application/json"]["schema"])
        assert body.get("type") == "object", (
            "ответ /demo/preview не типизирован: фронт получит unknown и напишет "
            "рукописный тип с кастом (урок v8.31.1)"
        )

    @pytest.mark.parametrize("field", ["metrics", "plan", "forecast"])
    def test_carries_the_three_things_worth_previewing(self, schema, field) -> None:
        """Метрики, план и прогноз — ровно то, ради чего смотрят до загрузки."""
        op = schema["paths"]["/api/demo/preview"]["get"]
        body = _resolve(schema, op["responses"]["200"]["content"]["application/json"]["schema"])
        assert field in body["properties"], field
        assert field in body.get("required", []), (
            f"{field} необязателен — фронт получит undefined на главном содержимом экрана"
        )


class TestServed:
    def test_preview_returns_a_human_explanation(self, client) -> None:
        """🔴 Объяснение — то единственное, что человек реально читает.

        Числа сами по себе не отвечают на вопрос «чем этот портрет отличается»;
        отвечает фраза «рекомендуем направить … потому что …».
        """
        body = client.get("/api/demo/preview?case=anna").json()
        insight = body["plan"]["best"]["explanation"]["insight"]
        assert isinstance(insight, str) and len(insight) > 40, "объяснение пустое"

    def test_preview_writes_nothing(self, client) -> None:
        """🔴 Главное обещание эндпоинта: предпросмотр НЕ трогает данные.

        Если бы писал — он ничем не отличался бы от загрузки, и подтверждение,
        заведённое в v8.46.0, защищало бы от одного пути и пропускало другой.
        """
        before = len(client.get("/api/transactions").json())
        client.get("/api/demo/preview?case=mikhail")
        after = len(client.get("/api/transactions").json())
        assert before == after, "предпросмотр изменил данные — он обязан только считать"

    def test_every_case_previews(self, client) -> None:
        """Список и предпросмотр сходятся: карточка без расчёта — кнопка в ошибку."""
        for case in client.get("/api/demo/cases").json()["cases"]:
            response = client.get(f"/api/demo/preview?case={case['key']}")
            assert response.status_code == 200, f"{case['key']} не считается"

    def test_unknown_case_is_refused(self, client) -> None:
        assert client.get("/api/demo/preview?case=no-such").status_code in (400, 404, 422)

    def test_preview_is_public(self, client) -> None:
        """Гостю — можно: он и есть адресат. В отличие от `/demo/load`, здесь нет
        причины требовать гостевой режим: запись не производится, смешивать нечего."""
        assert client.get("/api/demo/preview?case=anna").status_code == 200
