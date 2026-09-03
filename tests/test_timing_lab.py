"""Временна́я лаборатория: замер и учёт длительности прогонов (v8.33.0).

Заведена по прямому требованию владельца 2026-09-03: «раз ты гоняешь тесты, давай
внесём механику замера времени — сколько каждый сет тестов идёт, чтобы проще было
планировать работу в будущем не просто в токенах, но и по времени», плюс
«и в сети какие-то документы про это поддерживаемые — что сколько времени стоит».

Ключевое требование к замеру, выведенное не из головы, а из пяти эпизодов
`INV-MACHINE-LOAD`: **длительность без нагрузки хоста бессмысленна.** Один и тот же
срез `test_api_demo` шёл 40.8 с при нормальной машине и 83.4 с при load average 74
на 8 ядрах. Поэтому каждая запись обязана нести load average — иначе среднее по
журналу смешивает две разные величины и врёт в обе стороны.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from tools.timing_lab.record import (
    Measurement,
    append_measurement,
    load_measurements,
    summarize,
    format_report,
)


@pytest.fixture()
def ledger(tmp_path: Path) -> Path:
    return tmp_path / "timings.csv"


def _m(suite: str, seconds: float, load: float = 2.0, tests: int | None = 10) -> Measurement:
    return Measurement(
        date="2026-09-03",
        suite=suite,
        seconds=seconds,
        tests=tests,
        load1=load,
        cores=8,
        note="",
    )


class TestLedger:
    def test_first_write_creates_header(self, ledger: Path):
        append_measurement(ledger, _m("vitest-full", 38.4))
        rows = list(csv.DictReader(ledger.open(encoding="utf-8")))
        assert len(rows) == 1
        assert rows[0]["suite"] == "vitest-full"
        assert rows[0]["seconds"] == "38.4"

    def test_appends_without_losing_previous(self, ledger: Path):
        append_measurement(ledger, _m("vitest-full", 38.4))
        append_measurement(ledger, _m("vitest-full", 41.0))
        assert len(load_measurements(ledger)) == 2

    def test_missing_ledger_reads_as_empty_not_error(self, ledger: Path):
        """Отчёт по пустой лаборатории — законный ответ «замеров нет», а не падение:
        иначе первый же запуск на свежей репе выглядел бы поломкой инструмента."""
        assert load_measurements(ledger) == []

    def test_tests_count_may_be_absent(self, ledger: Path):
        """У сборки и preflight числа тестов нет вовсе — колонка обязана это пережить,
        а не заставлять писать ноль, который потом попадёт в статистику."""
        append_measurement(ledger, _m("build-vite", 0.9, tests=None))
        assert load_measurements(ledger)[0].tests is None


class TestSummary:
    def test_reports_median_not_mean(self, ledger: Path):
        """Медиана, а не среднее: один прогон под перегрузкой (83 с против 40 с)
        сдвигает среднее так, что планировать по нему нельзя."""
        for s in (40.0, 41.0, 42.0, 83.0):
            append_measurement(ledger, _m("pytest-slice", s))
        stats = summarize(load_measurements(ledger))["pytest-slice"]
        assert stats.median == pytest.approx(41.5)
        assert stats.runs == 4

    def test_separates_loaded_runs_from_calm_ones(self, ledger: Path):
        """Главное свойство лаборатории. Замер под нагрузкой не выбрасывается — он
        показывает ХУДШИЙ случай, — но и не смешивается со спокойным: это две разные
        величины, и планировать надо по спокойной, а ждать готовым к худшей."""
        append_measurement(ledger, _m("vitest-full", 38.0, load=2.0))
        append_measurement(ledger, _m("vitest-full", 40.0, load=3.0))
        append_measurement(ledger, _m("vitest-full", 87.0, load=74.0))
        stats = summarize(load_measurements(ledger))["vitest-full"]
        assert stats.calm_runs == 2
        assert stats.loaded_runs == 1
        assert stats.calm_median == pytest.approx(39.0)
        assert stats.worst == pytest.approx(87.0)

    def test_load_threshold_is_relative_to_cores(self, ledger: Path):
        """Порог «перегружено» — не абсолютное число, а load average выше числа ядер.
        Абсолютный порог был бы тем же дефектом, что 45-секундный бюджет Stop-гейта:
        величина, измеренная на одной машине и применённая к другой."""
        append_measurement(ledger, Measurement(
            date="2026-09-03", suite="s", seconds=10.0, tests=1,
            load1=7.0, cores=8, note="",
        ))
        append_measurement(ledger, Measurement(
            date="2026-09-03", suite="s", seconds=10.0, tests=1,
            load1=9.0, cores=8, note="",
        ))
        stats = summarize(load_measurements(ledger))["s"]
        assert stats.calm_runs == 1
        assert stats.loaded_runs == 1

    def test_empty_ledger_summarizes_to_nothing(self):
        assert summarize([]) == {}


class TestReport:
    def test_report_names_suite_and_median(self, ledger: Path):
        append_measurement(ledger, _m("vitest-full", 38.0))
        text = format_report(summarize(load_measurements(ledger)))
        assert "vitest-full" in text
        assert "38" in text

    def test_report_says_when_there_is_nothing_to_report(self):
        text = format_report({})
        assert "замеров" in text.lower()

    def test_report_marks_suites_with_only_loaded_runs(self, ledger: Path):
        """Если по набору есть ТОЛЬКО перегруженные замеры, медиана спокойного прогона
        неизвестна — отчёт обязан сказать это словом, а не подставить худшее число
        как норму."""
        append_measurement(ledger, _m("pytest-full", 1471.0, load=57.0))
        text = format_report(summarize(load_measurements(ledger)))
        assert "только под нагрузкой" in text


class TestDocUpdate:
    """Документ «что сколько стоит» обязан обновляться КОМАНДОЙ, а не руками.

    Иначе он повторит судьбу комментария в `plan-summary/model/types.ts`: текст,
    который однажды написали верно, потом разошёлся с фактом и год вводил в
    заблуждение, потому что обновлять его надо было помнить (v8.31.1).
    """

    DOC = (
        "# Сколько стоит время\n\n"
        "Вступление, которое пишет человек и инструмент не трогает.\n\n"
        "<!-- TIMINGS:BEGIN -->\n"
        "старая таблица\n"
        "<!-- TIMINGS:END -->\n\n"
        "Хвост, который тоже остаётся на месте.\n"
    )

    def test_replaces_only_the_marked_block(self, tmp_path: Path, ledger: Path):
        from tools.timing_lab.record import update_doc

        doc = tmp_path / "timing_reference.md"
        doc.write_text(self.DOC, encoding="utf-8")
        append_measurement(ledger, _m("vitest-full", 38.0))

        update_doc(doc, format_report(summarize(load_measurements(ledger))))
        text = doc.read_text(encoding="utf-8")

        assert "Вступление, которое пишет человек" in text
        assert "Хвост, который тоже остаётся на месте." in text
        assert "старая таблица" not in text
        assert "vitest-full" in text

    def test_missing_markers_is_an_error_not_silent_noop(self, tmp_path: Path):
        """Молчаливый пропуск был бы худшим исходом: команда отработала бы «успешно»,
        документ остался бы старым, и расхождение жило бы до следующей ревизии."""
        from tools.timing_lab.record import update_doc

        doc = tmp_path / "no_markers.md"
        doc.write_text("# Без маркеров\n", encoding="utf-8")
        with pytest.raises(ValueError, match="TIMINGS:BEGIN"):
            update_doc(doc, "таблица")
