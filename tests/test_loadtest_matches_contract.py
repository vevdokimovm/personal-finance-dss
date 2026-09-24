"""Гейт: нагрузочный сценарий шлёт то, что принимает схема.

🔴 Оплачено месяцами невидимого красного. Юрблок L1 сделал `consent` обязательным
полем регистрации (v8.40.0), нагрузочный сценарий не обновили — и шаг «Нагрузка»
с тех пор падал со 100 % отказов `register HTTP 422`. Увидеть это было нельзя:
GitHub останавливает джобу на первом упавшем шаге, а до нагрузки очередь не доходила
ни разу. Класс ошибки — «сценарий отстал от контракта», и ловится он только сверкой
полезной нагрузки со схемой, а не чтением кода.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest

LOCUSTFILE = Path(__file__).resolve().parents[1] / "loadtest/locustfile.py"


def _register_payloads() -> list[ast.Dict]:
    """Словари-литералы файла нагрузки, где есть и email, и password.

    Разбор кода, а не импорт: `locust` не входит в зависимости прогона тестов,
    а гейт обязан работать в любом тире.
    """
    tree = ast.parse(LOCUSTFILE.read_text(encoding="utf-8"))
    found: list[ast.Dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if "email" in keys and "password" in keys:
            found.append(node)
    return found


def _fields(node: ast.Dict) -> dict:
    """Поля словаря; неконстантные значения заменяются годным для схемы образцом."""
    result = {}
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant):
            continue
        result[key.value] = value.value if isinstance(value, ast.Constant) else "x" * 12
    result["email"] = "load@example.com"
    return result


class TestRegisterPayloadMatchesSchema:
    """Тело регистрации из нагрузки обязано проходить `RegisterRequest`."""

    def test_payload_exists(self) -> None:
        assert _register_payloads(), "в нагрузочном сценарии не нашлось тела регистрации"

    def test_every_payload_passes_schema(self) -> None:
        for node in _register_payloads():
            try:
                RegisterRequest(**_fields(node))
            except ValidationError as exc:
                missing = [e["loc"][-1] for e in exc.errors() if e["type"] == "missing"]
                pytest.fail(
                    "тело регистрации в нагрузочном сценарии не проходит схему; "
                    f"строка {node.lineno}, не хватает полей: {missing}"
                )
