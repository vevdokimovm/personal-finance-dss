"""Ни один чекбокс согласия не отмечен заранее (L2, v8.41.0).

Требование прямое: согласие, проставленное за пользователя, согласием не является.
На момент проверки оно соблюдалось — оба чекбокса регистрации стартуют с `false` —
но держалось это на внимательности, а не на механизме. Достаточно одной правки
«чтобы удобнее», чтобы нарушить его молча: тесты формы проверяют отправку данных,
а не начальное состояние галочки.

Проверка идёт по КОДУ, а не по прозе: `defaultChecked` без явного `false` и
`useState(true)` под именем, похожим на согласие, — оба запрещены.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
SRC = FRONTEND / "src"

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)

# Имена состояний, за которыми стоит согласие пользователя. Проверяется начальное
# значение именно у них: `useState(true)` для «показать подсказку» — не нарушение.
CONSENT_NAMES = ("consent", "agree", "accept", "newsletter", "optin", "opt_in", "marketing")


def _sources() -> list[Path]:
    return [p for p in SRC.rglob("*.tsx") if ".test." not in p.name]


def _code_only(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", text))


def test_no_default_checked_attribute() -> None:
    """`defaultChecked` вообще не используется.

    Единственное законное применение — `defaultChecked={false}`, но оно бессмысленно:
    это и есть поведение по умолчанию. Любое другое ставит галочку за человека.
    """
    hits = []
    for path in _sources():
        code = _code_only(path)
        for number, line in enumerate(code.splitlines(), 1):
            if "defaultChecked" in line and "defaultChecked={false}" not in line:
                hits.append(f"{path.relative_to(FRONTEND)}:{number}")
    assert not hits, (
        "чекбокс отмечен заранее через defaultChecked: " + ", ".join(hits) +
        ". Согласие, проставленное за пользователя, согласием не является (L2)"
    )


@pytest.mark.parametrize("name", CONSENT_NAMES)
def test_consent_state_starts_unchecked(name: str) -> None:
    """Состояние согласия инициализируется `false`.

    Ищем `useState(true)` у переменной, чьё имя говорит о согласии: именно так
    предотмеченная галочка появляется в React — не атрибутом, а начальным состоянием.
    """
    pattern = re.compile(
        rf"const\s*\[\s*\w*{name}\w*\s*,[^\]]+\]\s*=\s*useState(?:<[^>]+>)?\(\s*true\s*\)",
        re.IGNORECASE,
    )
    hits = []
    for path in _sources():
        for number, line in enumerate(_code_only(path).splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path.relative_to(FRONTEND)}:{number}")
    assert not hits, (
        f"состояние согласия «{name}» стартует включённым: " + ", ".join(hits) +
        ". Галочка обязана быть снята, пока человек не поставил её сам (L2)"
    )
