"""Справочник длительностей не отстаёт от журнала замеров.

## Что закрывает

`docs/timing_reference.md` собирается из `tools/timing_lab/timings.csv` командой
`record report --update-doc`, и его собственная шапка объявляет: «Ручное ведение здесь
запрещено сознательно». Но **ничто не делало перегенерацию обязательной** — команда
не вызывается ни из `preflight`, ни из CI.

🔴 **Замер 08.09.2026:** документ показывал `backend-full — 13.8 мин / 13.8 мин / 2
прогона`, тогда как в журнале лежало **12** прогонов, спокойная медиана **14.3 мин**,
а худший случай — **29.5 мин**. Худший занижен в 2.1 раза, и именно эта колонка
существует «чтобы не удивляться». Таблица была верна на момент, когда в журнале
стояли две строки, и с тех пор десять замеров до неё не доехали.

Класс тот же, что у `test_readme_status_is_current.py`: инструмент сделал обновление
возможным, а обязательным его не сделал никто. Найдено третьим проходом независимого
аудита.

## Что делать, когда красный

`python -m tools.timing_lab.record report --update-doc` — одна команда, и она же
печатает свежую таблицу.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "timing_reference.md"


def _doc_rows() -> dict[str, tuple[str, ...]]:
    text = DOC.read_text(encoding="utf-8")
    rows: dict[str, tuple[str, ...]] = {}
    for match in re.finditer(r"^\| `([^`]+)` \|([^\n]+)$", text, re.MULTILINE):
        cells = tuple(cell.strip() for cell in match.group(2).split("|") if cell.strip())
        rows[match.group(1)] = cells
    return rows


def _ledger_rows() -> dict[str, tuple[str, ...]]:
    from tools.timing_lab.record import (
        LEDGER,
        format_report,
        load_measurements,
        summarize,
    )

    report = format_report(summarize(load_measurements(LEDGER)))
    rows: dict[str, tuple[str, ...]] = {}
    for match in re.finditer(r"^\| `([^`]+)` \|([^\n]+)$", report, re.MULTILINE):
        cells = tuple(cell.strip() for cell in match.group(2).split("|") if cell.strip())
        rows[match.group(1)] = cells
    return rows


class TestDocMatchesLedger:
    """Каждая строка справочника совпадает с пересчётом по журналу."""

    def test_no_suite_is_stale(self) -> None:
        """🔴 Мутация «дописать замер и не перегенерировать» роняет тест здесь."""
        doc, ledger = _doc_rows(), _ledger_rows()
        stale = [
            f"{suite}: в документе {doc[suite]}, по журналу {cells}"
            for suite, cells in ledger.items()
            if suite in doc and doc[suite] != cells
        ]
        assert not stale, (
            "справочник отстал от журнала замеров: "
            + "; ".join(stale[:5])
            + " — выполните `python -m tools.timing_lab.record report --update-doc`"
        )

    def test_no_suite_is_missing_from_the_doc(self) -> None:
        """Новый набор появляется в документе, а не только в журнале."""
        missing = sorted(set(_ledger_rows()) - set(_doc_rows()))
        assert not missing, (
            f"наборы есть в журнале и отсутствуют в справочнике: {missing}"
        )


class TestGateItselfWorks:
    """Обе стороны сверки читаются, а не молчат."""

    def test_doc_has_rows(self) -> None:
        assert len(_doc_rows()) > 5, "таблица справочника не разобралась"

    def test_ledger_has_rows(self) -> None:
        assert len(_ledger_rows()) > 5, "журнал замеров не разобрался"
