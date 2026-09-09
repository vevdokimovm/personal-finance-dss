"""Внешние тексты не переусиливают утверждение о новизне (v9.9.2).

## Как обнаружилось

09.09.2026 первичный документ опроверг часть формулировки новизны: патент Capital One
US11023967B1 (выдан, активен) называет порог 7% APR, avalanche и snowball поимённо
и правило `Lump = Liquid Assets − 3×CME`. Утверждение «впервые учитываем процентные
ставки при выборе между погашением и накоплением» после этого недопустимо.

🔴 **Почему нужен механизм, а не внимательность.** Сама опровергнутая фраза в текстах
проекта не нашлась — нашлось другое: питч и разборы рынка утверждали «этого не делает
никто» и «мы единственные». Это утверждение **сильнее собранного материала**: трактовку
«фича есть, но невидима снаружи» публичными каналами опровергнуть нельзя в принципе.
Корректная форма — «не раскрыто ни в одном публично доступном источнике».

Внешний текст пишется редко и разными руками, формулировка дрейфует обратно к красивой
и сильной. Гейт держит границу механизмом, а не памятью автора.

Канон — `docs/novelty_statement.md`.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXTERNAL_TEXTS = (
    "README.md",
    "knowledge/business/pitch/pitch_script_ru.md",
    "knowledge/business/pitch/pitch_script_en.md",
    "knowledge/business/pitch/pitch_intl_script_ru.md",
    "knowledge/business/pitch/pitch_intl_script_en.md",
    "knowledge/business/business_strategy_longterm.md",
    "knowledge/business/international_market_analysis.md",
)

BANNED = {
    "впервые учитывает процентные ставки": r"впервые\s+учитыва\w*\s+процентн\w*\s+ставк",
    "никто не делает / не делает никто": (
        r"(никто\s+не\s+делает|не\s+делает\s+никто"
        r"|не\s+говорит\s+никто|не\s+владеет\s+никто)"
    ),
    "мы единственные": r"[Мм]ы\s+единственн\w*",
    "аналогов не существует": r"аналог\w*\s+не\s+(существует|имеет|найдено)",
    "nobody / no one does it": r"(nobody\s+(does|tells)|no\s+one\s+(does|owns|tells))",
    "we are the only ones": r"[Ww]e(?:'re|\s+are)\s+the\s+only\s+ones",
}

CANON = REPO_ROOT / "docs" / "novelty_statement.md"


def _external_sources() -> list[tuple[str, str]]:
    return [(name, (REPO_ROOT / name).read_text(encoding="utf-8")) for name in EXTERNAL_TEXTS]


def test_canon_exists_and_names_the_refuting_patent() -> None:
    """Канон формулировки на месте и опирается на первичный документ.

    Мутация: убрать номер патента — падает здесь.
    """
    assert CANON.exists(), "нет канона docs/novelty_statement.md"
    text = CANON.read_text(encoding="utf-8")
    assert "US11023967B1" in text
    assert "не раскрыто ни в одном публично доступном источнике" in text


def test_external_texts_carry_no_unqualified_claim() -> None:
    """🔴 Ни один внешний текст не утверждает больше, чем измерено.

    Мутация: вернуть в питч «Мы единственные, кто говорит, что делать» — падает здесь,
    а не на вопросах после показа.
    """
    offences: list[str] = []
    for name, text in _external_sources():
        for label, pattern in BANNED.items():
            for match in re.finditer(pattern, text):
                line = text.count("\n", 0, match.start()) + 1
                offences.append(f"{name}:{line} — {label}: {match.group(0)!r}")
    assert not offences, "переусиленные утверждения о новизне:\n" + "\n".join(offences)


def test_external_texts_are_actually_scanned() -> None:
    """Контроль живости: гейт читает непустые файлы, а не молчит на пустом наборе.

    Без этого предыдущая проверка зелена по чужой причине — ровно тот класс,
    что ловился на рассылке в v9.8.0.
    """
    sources = _external_sources()
    assert len(sources) == len(EXTERNAL_TEXTS)
    for name, text in sources:
        assert len(text) > 500, f"{name} подозрительно пуст — гейт смотрит не туда"
