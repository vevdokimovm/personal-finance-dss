"""Дисклеймер 39-ФЗ приходит ВМЕСТЕ с рекомендацией (L5, v8.40.0).

Требование L5 сформулировано так: дисклеймер выводится **на самой странице
рекомендаций**, а не только в оферте — человек принимает решение о деньгах на этом
экране, здесь же должно стоять предупреждение, что FINPILOT не инвестиционный советник.

🔴 До v8.40.0 `/planning/calculate` дисклеймер НЕ отдавал: константа `DISCLAIMER_39FZ`
существовала и была доступна только через `/legal/documents`. Фронт, показывающий план,
обязан был бы либо сходить за ней вторым запросом, либо — что и происходит в жизни —
перепечатать текст у себя. Перепечатанный юридический текст расходится с каноном молча
и ровно тогда, когда канон меняют.

Поэтому дисклеймер едет полем ответа: один источник, менять — в одном месте.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.legal import DISCLAIMER_39FZ

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"

PORTRAIT = {
    "income": 120000.0,
    "expenses": 70000.0,
    "obligations": [],
    "goals": [],
    "liquid_assets": 50000.0,
    "risk_profile": "balanced",
}


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def test_contract_declares_disclaimer(schema) -> None:
    body = schema["components"]["schemas"]["PlanningCalculateResponse"]
    assert "disclaimer" in body["properties"], (
        "ответ /planning/calculate не несёт дисклеймер: фронт вынужден либо ходить "
        "вторым запросом, либо перепечатать юридический текст у себя"
    )
    assert "disclaimer" in body.get("required", []), (
        "дисклеймер обязателен всегда — необязательное поле фронт вправе не показывать"
    )


def test_calculate_returns_the_canonical_text(client) -> None:
    """Текст РОВНО тот, что в каноне — не пересказ и не сокращение."""
    response = client.post("/api/planning/calculate", json=PORTRAIT)
    assert response.status_code == 200, response.text
    assert response.json()["disclaimer"] == DISCLAIMER_39FZ


def test_disclaimer_names_the_law_essentials(client) -> None:
    """Дисклеймер обязан сказать главное: не советник, не ИИР, решение за вами.

    Проверяется смысл, а не буква: текст можно переписать, но эти три утверждения
    он потерять не вправе — на них держится вся конструкция 39-ФЗ.
    """
    text = client.post("/api/planning/calculate", json=PORTRAIT).json()["disclaimer"]
    assert "не является инвестиционным советником" in text
    assert "индивидуальной инвестиционной рекомендацией" in text
    assert "ответственность" in text
