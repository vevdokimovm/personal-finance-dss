"""Таблица параметров канона не расходится с кодом.

## Что закрывает

`docs/math_model.md` §17 — единственное место, куда смотрят, чтобы сверить работающую
модель с описанной: ВКР, патентная заявка, аудит модели, любой внешний читатель.

🔴 **Строка «Floor резерва» держала значение `1 мес` с редакции G6**, тогда как
вторая сертификация (v3.4.0, ADR-006) подняла его до `2.0`, а раунд 4 (v3.5.0)
добавил ослабление до `1.0` только при токсичном долге. Канон противоречил сам себе:
§21 п. 9 в том же файле говорил «Floor (2 месяца, v3.4.0)», а таблица — «1 мес».

Класс PIT-029: обоснование обновили, число, стоявшее на нём, — нет.

## Почему гейт, а не разовая правка

Разойтись они могут снова при следующей калибровке: код меняет тот, кто калибрует,
а таблицу — тот, кто помнит про таблицу. Сверка должна быть механической.

**Что гейт НЕ делает:** не проверяет обоснования и не судит, какое значение верное.
Он утверждает одно — что число в таблице и число в коде совпадают.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.core.ranking import RESERVE_FLOOR_MONTHS, TOXIC_FLOOR_MONTHS

REPO_ROOT = Path(__file__).resolve().parents[1]
CANON = REPO_ROOT / "docs" / "math_model.md"


def _table_row(name: str) -> str:
    text = CANON.read_text(encoding="utf-8")
    match = re.search(rf"^\|\s*{re.escape(name)}\s*\|(.+)$", text, re.MULTILINE)
    assert match, f"в §17 канона нет строки «{name}»"
    return match.group(1)


class TestReserveFloorAgrees:
    """Floor резерва в таблице совпадает с константами ранжирования."""

    def test_table_names_the_calibrated_floor(self) -> None:
        """🔴 Мутация «вернуть 1 мес в таблицу» роняет тест здесь."""
        row = _table_row("Floor резерва")
        expected = f"{RESERVE_FLOOR_MONTHS:g}"
        assert re.search(rf"\${expected}\$", row), (
            f"таблица канона не называет действующий floor {expected} мес: {row.strip()[:120]}"
        )

    def test_table_mentions_the_toxic_debt_relaxation(self) -> None:
        """Ослабление при токсичном долге — часть действующего канона, не сноска.

        Без него таблица утверждает единственное значение там, где их два,
        и читатель сверяет модель по неполному описанию.
        """
        row = _table_row("Floor резерва")
        expected = f"{TOXIC_FLOOR_MONTHS:g}"
        assert re.search(rf"\${expected}\$", row) and "токсич" in row.lower(), (
            f"таблица не упоминает floor {expected} мес при токсичном долге: {row.strip()[:120]}"
        )


class TestCanonDoesNotContradictItself:
    """Разные места канона говорят об одном параметре одно и то же."""

    def test_section_21_agrees_with_the_table(self) -> None:
        """§21 п. 9 объясняет floor словами — число там то же, что в таблице."""
        text = CANON.read_text(encoding="utf-8")
        expected = f"{RESERVE_FLOOR_MONTHS:g}"
        match = re.search(r"\*\*Floor \((\d+)[^)]*\)", text)
        assert match, "в §21 нет пункта про floor"
        assert match.group(1) == expected, (
            f"§21 называет floor {match.group(1)} мес, код — {expected}"
        )


class TestGateItselfWorks:
    """Сетка находит строку и не притворяется зелёной на пустом месте."""

    def test_missing_row_is_an_error_not_a_pass(self) -> None:
        with pytest.raises(AssertionError):
            _table_row("Параметра с таким именем нет")

    def test_row_lookup_returns_content(self) -> None:
        assert len(_table_row("Floor резерва").strip()) > 20
