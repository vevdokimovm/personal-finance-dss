"""Экран согласий не отстаёт от списка типов на бэкенде (L3, v8.41.0).

🔴 Ровно этот дефект и чинил батч: экран знал ОДНО согласие из трёх — `financial_data`,
вшитое в разметку. Остальные два человек не видел вовсе, то есть отозвать маркетинговое
было невозможно, хотя 152-ФЗ даёт на это право.

Экран переписан так, что строит список из ответа `/consents` и новый тип подхватит сам.
Но `ConsentType` во фронте остаётся рукописным перечислением: в контракте это ключи
словаря (`dict[str, ConsentState]`), и сгенерированный тип даёт `string`. Значит
расхождение возможно — и ловится здесь.

Гейт сверяет ДВА списка: `CONSENT_TYPES` в `app/core/legal.py` и объединение фронтового
`ConsentType` с картой человеческих названий `CONSENT_LABEL`.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.core.legal import CONSENT_TYPES

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
TYPES = FRONTEND / "src" / "entities" / "consents" / "model" / "types.ts"
SECTION = FRONTEND / "src" / "pages" / "profile" / "ConsentsSection.tsx"

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)


def _code_only(path: Path) -> str:
    """Комментарии вырезаются: гейт шрифта (v8.39.0) был зелёным на сломанном состоянии
    именно потому, что находил искомые слова в объяснениях рядом с кодом."""
    text = path.read_text(encoding="utf-8")
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", text))


def test_frontend_type_lists_every_known_consent() -> None:
    code = _code_only(TYPES)
    match = re.search(r"export type ConsentType\s*=\s*([^;]+);", code)
    assert match, "во фронте нет объединения ConsentType — сверять нечего"
    declared = set(re.findall(r'"([a-z_]+)"', match.group(1)))
    missing = set(CONSENT_TYPES) - declared
    assert not missing, (
        f"фронт не знает о типах согласий: {sorted(missing)}. Пользователь не увидит их "
        "на экране согласий — то есть не сможет ни выдать, ни отозвать (L3)"
    )
    extra = declared - set(CONSENT_TYPES)
    assert not extra, (
        f"фронт знает несуществующие типы: {sorted(extra)} — бэкенд ответит 404 "
        "«Неизвестный тип согласия» на любую попытку выдать или отозвать"
    )


def test_every_consent_has_a_human_label() -> None:
    """У каждого типа есть человеческое название.

    Без него в интерфейсе встанет служебный ключ (`financial_data`), а служебные
    значения контракта пользователю ничего не говорят ([CMP-03]). Экран не падает —
    он честно покажет ключ, — но это заметно хуже, чем название.
    """
    code = _code_only(SECTION)
    match = re.search(r"CONSENT_LABEL:\s*Record<string, string>\s*=\s*\{(.*?)\}", code, re.DOTALL)
    assert match, "карта названий согласий не найдена"
    labelled = set(re.findall(r"^\s*([a-z_]+):", match.group(1), re.MULTILINE))
    missing = set(CONSENT_TYPES) - labelled
    assert not missing, (
        f"у типов согласий нет человеческих названий: {sorted(missing)} — в интерфейсе "
        "встанет служебный ключ контракта"
    )
