"""Риск-профили во фронте совпадают с каноном модели (v8.42.0).

Панель параметров плана (`PlanSettingsSection`) ведёт подписи профилей у себя, и это
вынужденно: бэкенд отдаёт `label` только внутри готового плана
(`app/core/ranking.py::RISK_PROFILES`), а выбрать профиль нужно ДО расчёта — иначе
человеку не из чего выбирать на пустом экране.

Значит копия существует, и вопрос только в том, заметим ли мы её расхождение. Молчаливое
расхождение здесь опаснее обычного: человек выберет «Агрессивный», а модель посчитает по
другому набору весов SAW — и разницы он не увидит, потому что план в любом случае
выглядит правдоподобно.

🔴 Сверяются и НОМЕРА, и подписи. Номер — то, что уходит в `risk_tolerance` и попадает
в `RISK_PROFILES[i]`; сдвиг нумерации на единицу дал бы человеку не тот профиль, который
он выбрал, вообще без внешних признаков.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.core.ranking import RISK_PROFILES

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
SECTION = FRONTEND / "src" / "pages" / "planning" / "ui" / "PlanSettingsSection.tsx"

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)


def _code_only(path: Path) -> str:
    """Комментарии вырезаются: гейт шрифта (v8.39.0) был зелёным на сломанном состоянии
    именно потому, что находил искомые слова в объяснениях рядом с кодом."""
    text = path.read_text(encoding="utf-8")
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", text))


def _frontend_labels() -> dict[int, str]:
    code = _code_only(SECTION)
    match = re.search(r"RISK_LABELS:\s*Record<number, string>\s*=\s*\{(.*?)\n\};", code, re.DOTALL)
    assert match, "карта подписей риск-профилей не найдена во фронте"
    return {
        int(number): label
        for number, label in re.findall(r'(\d+):\s*"([^"]+)"', match.group(1))
    }


def test_all_canon_profiles_are_offered() -> None:
    """Все пять профилей канона доступны для выбора — ни один не потерян."""
    missing = set(RISK_PROFILES) - set(_frontend_labels())
    assert not missing, (
        f"фронт не предлагает риск-профили {sorted(missing)} — человек не сможет их выбрать, "
        "хотя модель их считает"
    )


def test_no_invented_profiles() -> None:
    """Фронт не предлагает того, чего в каноне нет.

    Лишний номер уйдёт в `risk_tolerance`, `RISK_PROFILES.get(...)` вернёт дефолт (3),
    и человек получит «Сбалансированный» под именем выбранного им профиля.
    """
    extra = set(_frontend_labels()) - set(RISK_PROFILES)
    assert not extra, (
        f"фронт предлагает несуществующие профили {sorted(extra)} — модель молча посчитает "
        "их как «Сбалансированный»"
    )


def test_labels_match_canon_exactly() -> None:
    """Подпись профиля совпадает с каноном дословно.

    План отдаёт `risk_profile` меткой (`RISK_PROFILES[i]["label"]`) и показывает её на том
    же экране. Разойдись подписи — человек выбрал бы «Агрессивный», а в результате читал
    «Умеренно-агрессивный»: доверие к рекомендации держится и на таких мелочах.
    """
    frontend = _frontend_labels()
    mismatch = {
        number: (frontend[number], profile["label"])
        for number, profile in RISK_PROFILES.items()
        if number in frontend and frontend[number] != profile["label"]
    }
    assert not mismatch, (
        "подписи риск-профилей разошлись с каноном (фронт → бэкенд): " + str(mismatch)
    )


def test_every_profile_has_a_human_hint() -> None:
    """У каждого профиля есть объяснение простым языком.

    Веса SAW человеку ничего не говорят; без подсказки выбор между пятью словами
    «консервативный… агрессивный» — гадание ([CMP-03]).
    """
    code = _code_only(SECTION)
    match = re.search(r"RISK_HINTS:\s*Record<number, string>\s*=\s*\{(.*?)\n\};", code, re.DOTALL)
    assert match, "карта подсказок риск-профилей не найдена"
    hinted = {int(number) for number, _ in re.findall(r'(\d+):\s*"([^"]+)"', match.group(1))}
    missing = set(RISK_PROFILES) - hinted
    assert not missing, f"профили без объяснения простым языком: {sorted(missing)}"
