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

import argparse
import csv
import sys
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


class TestSelfReviewFindings:
    """Три дефекта, найденных перечитыванием инструмента, пока шёл полный прогон.

    Не заменяет `/code-review` (тот упал на лимите сессии и остался долгом в ROADMAP
    §8.5) — но эти три видны на чтении и закрыты тестами здесь, чтобы не разойтись
    снова.
    """

    def test_zero_median_suite_is_not_sorted_by_worst(self, ledger: Path):
        """`calm_median or worst` проваливался на нулевой медиане: у быстрого набора
        она бывает 0.0, и набор уезжал в сортировке на своё худшее значение."""
        append_measurement(ledger, _m("быстрый", 0.0))
        append_measurement(ledger, _m("быстрый", 0.0, load=99.0))
        append_measurement(ledger, _m("медленный", 30.0))
        report = format_report(summarize(load_measurements(ledger)))
        # Медленный набор обязан стоять выше быстрого.
        assert report.index("медленный") < report.index("быстрый")

    def test_ninety_second_boundary_is_not_a_cliff(self, ledger: Path):
        """До правки 89.6 с показывалось «90 с», а 90.0 с — «2 мин»: два соседних
        замера выглядели разошедшимися вдвое. Инвариант — не конкретная строка,
        а отсутствие скачка: значения по обе стороны порога читаются одинаково."""
        from tools.timing_lab.record import _human

        assert _human(89.4) == "89 с"          # ниже порога — секунды
        assert _human(89.6) == _human(90.0)    # по обе стороны — одно и то же
        assert _human(90.0) == "1.5 мин"       # и это полторы минуты, не две

    def test_missing_command_does_not_crash_the_tool(self, ledger: Path, capsys):
        """Опечатка в команде роняла инструмент трейсбеком вместо записи замера."""
        from tools.timing_lab.record import main

        code = main([
            "--ledger", str(ledger), "run", "--suite", "опечатка",
            "--", "этой-команды-точно-нет",
        ])
        assert code == 127
        assert load_measurements(ledger)[0].note == "exit=127"


class TestLedgerRobustness:
    """Журнал дописывается из РАЗНЫХ процессов (`record run` в фоне, `add` вручную),
    поэтому битая строка в нём — вопрос времени, а не гипотеза: оборванная запись при
    убитом процессе, ручная правка, конкурентный дозапись.

    Проверено эмпирически до правки: одна строка с нечисловым `seconds` роняла
    `load_measurements` целиком, то есть ВЕСЬ отчёт и обновление документа. Ценность
    журнала в ряде замеров — терять двадцать девять хороших строк из-за одной плохой
    неверно.
    """

    def test_corrupt_row_is_skipped_not_fatal(self, ledger: Path):
        append_measurement(ledger, _m("хороший", 10.0))
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write("2026-09-03,битый,НЕ-ЧИСЛО,5,2.0,8,\n")
        append_measurement(ledger, _m("тоже хороший", 20.0))

        got = load_measurements(ledger)
        assert [m.suite for m in got] == ["хороший", "тоже хороший"]

    def test_truncated_row_is_skipped(self, ledger: Path):
        """Оборванная на середине запись — типичный след убитого процесса."""
        append_measurement(ledger, _m("хороший", 10.0))
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write("2026-09-03,обор")

        assert [m.suite for m in load_measurements(ledger)] == ["хороший"]

    def test_report_survives_corrupt_ledger(self, ledger: Path):
        append_measurement(ledger, _m("живой", 10.0))
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write("мусор,без,запятых\n")
        assert "живой" in format_report(summarize(load_measurements(ledger)))


class TestLoadIsMeasuredAroundTheRunNotBeforeIt:
    """🔴 Классификация «спокойно / под нагрузкой» берёт ХУДШИЙ отсчёт, а не первый.

    Прежняя редакция снимала `load average` один раз, **до** `subprocess.run`,
    и по нему решала, был ли прогон спокойным. Для полного pytest окно замера —
    15–25 минут, и следствия оба в одну сторону:

    - отсчёт до старта не включает нагрузку **самого прогона**: набор, который сам
      перегружает машину, записывался как «спокойный»;
    - собственное обоснование лаборатории — эпизод, где load вырос за минуту, —
      делает однократный отсчёт негодным по её же аргументу.

    Смещение систематическое и в одну сторону, поэтому «спокойная медиана», по которой
    планируют батчи, занижена. Найдено третьим проходом независимого аудита 08.09.2026.
    """

    def test_load_after_the_run_wins_when_it_is_higher(self, tmp_path, monkeypatch) -> None:
        """Нагрузка выросла во время прогона — замер помечен как «под нагрузкой»."""
        import tools.timing_lab.record as record

        samples = iter([(2.0, 8), (30.0, 8)])
        monkeypatch.setattr(record, "host_load", lambda: next(samples))
        ledger = tmp_path / "timings.csv"
        args = argparse.Namespace(
            command=[sys.executable, "-c", "pass"], suite="probe",
            tests=None, note=None, ledger=str(ledger),
        )
        record._cmd_run(args)

        rows = record.load_measurements(ledger)
        assert len(rows) == 1
        assert rows[0].load1 == 30.0, "записан отсчёт ДО прогона, а не худший"
        assert rows[0].loaded is True

    def test_quiet_run_stays_quiet(self, tmp_path, monkeypatch) -> None:
        """Оба отсчёта низкие — прогон по-прежнему спокойный.

        Иначе починка объявила бы под нагрузкой всё подряд, и «спокойных» замеров
        не осталось бы вовсе.
        """
        import tools.timing_lab.record as record

        samples = iter([(1.0, 8), (2.0, 8)])
        monkeypatch.setattr(record, "host_load", lambda: next(samples))
        ledger = tmp_path / "timings.csv"
        args = argparse.Namespace(
            command=[sys.executable, "-c", "pass"], suite="probe",
            tests=None, note=None, ledger=str(ledger),
        )
        record._cmd_run(args)

        assert record.load_measurements(ledger)[0].loaded is False


class TestFailedRunsDoNotPoisonTheMedian:
    """🔴 Упавший прогон не участвует в «спокойной медиане».

    `note` при провале несёт `exit=N`, а сводка это поле не читала вовсе. Следствия:

    - опечатка в команде писала замер `0.0 с` под именем набора и навсегда тянула
      его медиану вниз;
    - прогон, упавший на пятой минуте из двадцати, засчитывался как полноценный.

    Для «худшего случая» упавший прогон учитывать осмысленно — время потрачено.
    Для медианы, по которой ПЛАНИРУЮТ, — нет: она должна отвечать на вопрос
    «сколько занимает полный прогон», а неполный на него не отвечает.
    """

    def test_failed_run_is_excluded_from_median(self, tmp_path) -> None:
        import tools.timing_lab.record as record

        ledger = tmp_path / "timings.csv"
        for seconds, note in ((100.0, ""), (102.0, ""), (0.0, "exit=127")):
            record.append_measurement(ledger, record.Measurement(
                date="2026-09-08", suite="probe", seconds=seconds,
                tests=None, load1=1.0, cores=8, note=note,
            ))

        summary = record.summarize(record.load_measurements(ledger))
        assert summary["probe"].calm_median == 101.0, (
            "провалившийся прогон попал в медиану и утянул её вниз"
        )

    def test_failed_run_still_counts_for_the_worst_case(self, tmp_path) -> None:
        """Но время, потраченное на упавший прогон, из «худшего» не исчезает."""
        import tools.timing_lab.record as record

        ledger = tmp_path / "timings.csv"
        record.append_measurement(ledger, record.Measurement(
            date="2026-09-08", suite="probe", seconds=50.0,
            tests=None, load1=1.0, cores=8, note="",
        ))
        record.append_measurement(ledger, record.Measurement(
            date="2026-09-08", suite="probe", seconds=900.0,
            tests=None, load1=1.0, cores=8, note="exit=1",
        ))

        summary = record.summarize(record.load_measurements(ledger))
        assert summary["probe"].worst == 900.0, (
            "потраченное на упавший прогон время исчезло из худшего случая"
        )


class TestFailureMarkerSurvivesCustomNote:
    """🔴 Свой `--note` не вытесняет отметку провала.

    `note=args.note or ("" if ok else f"exit={N}")` — при переданном `--note`
    маркер `exit=N` терялся, а сводка отсеивает упавшие прогоны именно по нему.
    То есть дефект, закрытый в этом же батче, восстанавливался **любым**
    использованием флага, который сам инструмент и предлагает.

    Найдено четвёртым проходом независимого аудита 08.09.2026.
    """

    def test_exit_marker_is_kept_alongside_the_note(self, tmp_path, monkeypatch) -> None:
        import tools.timing_lab.record as record

        monkeypatch.setattr(record, "host_load", lambda: (1.0, 8))
        ledger = tmp_path / "timings.csv"
        args = argparse.Namespace(
            command=[sys.executable, "-c", "raise SystemExit(3)"], suite="probe",
            tests=None, note="фон: сборка", ledger=str(ledger),
        )
        record._cmd_run(args)

        note = record.load_measurements(ledger)[0].note
        assert "exit=3" in note, f"отметка провала потеряна: {note!r}"
        assert "фон: сборка" in note, f"пояснение потеряно: {note!r}"

    def test_such_run_stays_out_of_the_median(self, tmp_path, monkeypatch) -> None:
        """И такой прогон по-прежнему не участвует в медиане."""
        import tools.timing_lab.record as record

        monkeypatch.setattr(record, "host_load", lambda: (1.0, 8))
        ledger = tmp_path / "timings.csv"
        record.append_measurement(ledger, record.Measurement(
            date="2026-09-08", suite="probe", seconds=10.0,
            tests=None, load1=1.0, cores=8, note="",
        ))
        args = argparse.Namespace(
            command=[sys.executable, "-c", "raise SystemExit(1)"], suite="probe",
            tests=None, note="ручная пометка", ledger=str(ledger),
        )
        record._cmd_run(args)

        summary = record.summarize(record.load_measurements(ledger))
        assert summary["probe"].calm_median == 10.0


class TestAllRunsFailed:
    """Набор, где упали ВСЕ прогоны, не выдаёт медиану как ни в чём не бывало.

    Прежде при пустом списке завершившихся медиана тихо считалась по упавшим,
    а отчёт печатал «— только под нагрузкой» — формулировку, не описывающую
    происходящее.
    """

    def test_median_is_absent_when_nothing_completed(self, tmp_path) -> None:
        import tools.timing_lab.record as record

        ledger = tmp_path / "timings.csv"
        for seconds in (5.0, 7.0):
            record.append_measurement(ledger, record.Measurement(
                date="2026-09-08", suite="probe", seconds=seconds,
                tests=None, load1=1.0, cores=8, note="exit=1",
            ))

        stats = record.summarize(record.load_measurements(ledger))["probe"]
        assert stats.calm_median is None, (
            "медиана посчитана по прогонам, ни один из которых не завершился"
        )
        assert stats.worst == 7.0, "потраченное время всё равно должно быть видно"
