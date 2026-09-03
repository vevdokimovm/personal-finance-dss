"""Временна́я лаборатория: сколько стоит по времени каждый прогон.

Заведена по требованию владельца 2026-09-03: планировать работу не только в токенах,
но и в минутах — «что сколько времени стоит», с поддерживаемым документом.

🟡 ГЛАВНОЕ СВОЙСТВО, из-за которого лаборатория устроена именно так.
Длительность прогона без нагрузки хоста — бессмысленное число. Это не теория:
`docs/reports/investigations/machine_load_gate_timeout_investigation.md` описывает
ПЯТЬ эпизодов, где один и тот же набор шёл вдвое дольше из-за посторонних процессов.
Замер того же среза `test_api_demo`: 40.8 с на спокойной машине и 83.4 с при load
average 74 на 8 ядрах. Смешать их в одно среднее — получить число, по которому
нельзя ни планировать, ни ловить регрессию.

Поэтому каждая запись несёт `load1` и `cores`, а отчёт разводит спокойные прогоны и
прогоны под нагрузкой. Порог — ОТНОСИТЕЛЬНЫЙ (load average выше числа ядер), а не
абсолютное число: абсолютный порог был бы тем же дефектом, что 45-секундный бюджет
Stop-гейта — величиной, измеренной на одной машине и применённой к другой.

Запуск:
    python -m tools.timing_lab.record run --suite vitest-full -- npx vitest run
    python -m tools.timing_lab.record report
    python -m tools.timing_lab.record add --suite pytest-full --seconds 1471 --tests 1632
"""
from __future__ import annotations

import argparse
import csv
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "tools" / "timing_lab" / "timings.csv"

FIELDS = ("date", "suite", "seconds", "tests", "load1", "cores", "note")


@dataclass(frozen=True)
class Measurement:
    date: str
    suite: str
    seconds: float
    tests: int | None
    load1: float
    cores: int
    note: str

    @property
    def loaded(self) -> bool:
        """Прогон считается «под нагрузкой», если 1-минутный load average выше числа
        ядер. Именно на этой границе машина перестаёт успевать за собственными
        процессами, и длительность начинает измерять не набор, а очередь к CPU."""
        return self.cores > 0 and self.load1 > self.cores


@dataclass(frozen=True)
class SuiteStats:
    suite: str
    runs: int
    median: float
    calm_runs: int
    loaded_runs: int
    calm_median: float | None
    worst: float
    tests: int | None


def host_load() -> tuple[float, int]:
    """Нагрузка и число ядер прямо сейчас. Читается в момент замера, а не берётся
    из памяти: между двумя прогонами машина меняется (см. INV-MACHINE-LOAD эп. 5,
    где load average вырос с 57 до 74 за минуту)."""
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):  # pragma: no cover — не POSIX
        load1 = 0.0
    return round(load1, 2), os.cpu_count() or 0


def append_measurement(ledger: Path, m: Measurement) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    is_new = not ledger.exists()
    with ledger.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "date": m.date,
            "suite": m.suite,
            "seconds": m.seconds,
            # Пусто, а не 0: у сборки и preflight тестов нет вовсе, и ноль попал бы
            # в статистику как настоящее измерение.
            "tests": "" if m.tests is None else m.tests,
            "load1": m.load1,
            "cores": m.cores,
            "note": m.note,
        })


def load_measurements(ledger: Path) -> list[Measurement]:
    """Пустая или отсутствующая лаборатория — законный ответ «замеров нет».
    Падение здесь означало бы, что первый запуск на свежей репе выглядит поломкой."""
    if not ledger.exists():
        return []
    out: list[Measurement] = []
    with ledger.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                raw_tests = (row.get("tests") or "").strip()
                out.append(Measurement(
                    date=row["date"],
                    suite=row["suite"],
                    seconds=float(row["seconds"]),
                    tests=int(raw_tests) if raw_tests else None,
                    load1=float(row["load1"]),
                    cores=int(row["cores"]),
                    note=row.get("note", ""),
                ))
            except (KeyError, TypeError, ValueError):
                # Битая строка ПРОПУСКАЕТСЯ, а не роняет чтение. Журнал дописывается из
                # разных процессов (`record run` в фоне, `add` вручную), поэтому
                # оборванная запись — вопрос времени: убитый процесс, ручная правка,
                # конкурентный дозапись. Проверено эмпирически: до этой правки одна
                # строка с нечисловым `seconds` роняла ВЕСЬ отчёт. Ценность журнала
                # в ряде замеров — терять двадцать девять хороших строк из-за одной
                # плохой неверно.
                continue
    return out


def summarize(measurements: list[Measurement]) -> dict[str, SuiteStats]:
    """Медиана, а не среднее: один прогон под перегрузкой сдвигает среднее так,
    что планировать по нему нельзя, а выбрасывать его тоже неверно — он показывает
    реальный худший случай."""
    by_suite: dict[str, list[Measurement]] = {}
    for m in measurements:
        by_suite.setdefault(m.suite, []).append(m)

    stats: dict[str, SuiteStats] = {}
    for suite, items in by_suite.items():
        calm = [m.seconds for m in items if not m.loaded]
        loaded = [m.seconds for m in items if m.loaded]
        counts = [m.tests for m in items if m.tests is not None]
        stats[suite] = SuiteStats(
            suite=suite,
            runs=len(items),
            median=statistics.median([m.seconds for m in items]),
            calm_runs=len(calm),
            loaded_runs=len(loaded),
            calm_median=statistics.median(calm) if calm else None,
            worst=max(m.seconds for m in items),
            tests=max(counts) if counts else None,
        )
    return stats


def _human(seconds: float) -> str:
    """Секунды до минуты с половиной, дальше минуты. Порог сравнивается ПОСЛЕ
    округления: иначе 89.6 показывалось бы как «90 с», а 90.0 — как «2 мин»,
    и два соседних замера выглядели бы разошедшимися вдвое."""
    if round(seconds) < 90:
        return f"{seconds:.0f} с"
    return f"{seconds / 60:.1f} мин".replace(".0 мин", " мин")


def format_report(stats: dict[str, SuiteStats]) -> str:
    if not stats:
        return "Замеров пока нет — прогоните `record run`, и лаборатория наполнится."

    lines = [
        "| набор | спокойный прогон | худший | прогонов | тестов |",
        "|---|---|---|---|---|",
    ]

    def _sort_key(name: str) -> float:
        st = stats[name]
        # Явная проверка на None, а не `or`: у быстрого набора медиана бывает 0.0,
        # и `or` провалился бы на худшее значение — набор уехал бы не на своё место.
        return -(st.worst if st.calm_median is None else st.calm_median)

    for suite in sorted(stats, key=_sort_key):
        st = stats[suite]
        if st.calm_median is None:
            # Не подставляем худшее как норму: «медианы спокойного прогона нет»
            # это отдельный, честный ответ.
            calm = "— только под нагрузкой"
        else:
            calm = _human(st.calm_median)
        tests = str(st.tests) if st.tests is not None else "—"
        lines.append(
            f"| `{suite}` | {calm} | {_human(st.worst)} | {st.runs} | {tests} |"
        )
    return "\n".join(lines)


DOC = REPO_ROOT / "docs" / "timing_reference.md"
_BEGIN = "<!-- TIMINGS:BEGIN -->"
_END = "<!-- TIMINGS:END -->"


def update_doc(doc: Path, table: str) -> None:
    """Заменить таблицу в документе между маркерами, не трогая остальной текст.

    Отсутствие маркеров — ошибка, а не тихий пропуск: команда, которая «успешно»
    ничего не сделала, оставляет документ расходиться с фактом молча, и это ровно
    тот класс, что чинили в v8.31.1 (устаревший комментарий поддерживал ручное
    ведение типа и год вводил в заблуждение).
    """
    text = doc.read_text(encoding="utf-8")
    if _BEGIN not in text or _END not in text:
        raise ValueError(
            f"в {doc} нет маркеров {_BEGIN} / {_END} — вставьте их в место таблицы"
        )
    head, _, rest = text.partition(_BEGIN)
    _, _, tail = rest.partition(_END)
    doc.write_text(f"{head}{_BEGIN}\n{table}\n{_END}{tail}", encoding="utf-8")


def _cmd_run(args: argparse.Namespace) -> int:
    if not args.command:
        print("нечего запускать: укажите команду после `--`", file=sys.stderr)
        return 2
    load1, cores = host_load()
    started = time.monotonic()
    try:
        returncode = subprocess.run(args.command).returncode
    except OSError as exc:
        # Опечатка в команде не должна ронять инструмент трейсбеком: замер всё равно
        # состоялся (ноль секунд), и записать его честнее, чем промолчать.
        print(f"не удалось запустить {args.command[0]!r}: {exc}", file=sys.stderr)
        returncode = 127
    elapsed = round(time.monotonic() - started, 2)

    append_measurement(Path(args.ledger), Measurement(
        date=date.today().isoformat(),
        suite=args.suite,
        seconds=elapsed,
        tests=args.tests,
        load1=load1,
        cores=cores,
        # Провал тоже записывается: упавший прогон занимает время так же, как
        # успешный, и при планировании это время всё равно тратится.
        note=args.note or ("" if returncode == 0 else f"exit={returncode}"),
    ))
    print(f"замер: {args.suite} — {_human(elapsed)} (load {load1} на {cores} ядрах)")
    return returncode


def _cmd_add(args: argparse.Namespace) -> int:
    load1, cores = host_load()
    append_measurement(Path(args.ledger), Measurement(
        date=args.date or date.today().isoformat(),
        suite=args.suite,
        seconds=args.seconds,
        tests=args.tests,
        load1=args.load1 if args.load1 is not None else load1,
        cores=args.cores if args.cores is not None else cores,
        note=args.note or "",
    ))
    print(f"записано: {args.suite} — {_human(args.seconds)}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    table = format_report(summarize(load_measurements(Path(args.ledger))))
    if args.update_doc:
        update_doc(Path(args.doc), table)
        print(f"обновлено: {args.doc}")
    else:
        print(table)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ledger", default=str(LEDGER), help="файл журнала замеров")
    sub = parser.add_subparsers(dest="mode", required=True)

    run = sub.add_parser("run", help="запустить команду и записать её длительность")
    run.add_argument("--suite", required=True)
    run.add_argument("--tests", type=int, default=None)
    run.add_argument("--note", default="")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=_cmd_run)

    add = sub.add_parser("add", help="записать замер, снятый вручную")
    add.add_argument("--suite", required=True)
    add.add_argument("--seconds", type=float, required=True)
    add.add_argument("--tests", type=int, default=None)
    add.add_argument("--load1", type=float, default=None)
    add.add_argument("--cores", type=int, default=None)
    add.add_argument("--date", default=None)
    add.add_argument("--note", default="")
    add.set_defaults(func=_cmd_add)

    rep = sub.add_parser("report", help="таблица «что сколько стоит»")
    rep.add_argument("--update-doc", action="store_true",
                     help="вписать таблицу в docs/timing_reference.md между маркерами")
    rep.add_argument("--doc", default=str(DOC))
    rep.set_defaults(func=_cmd_report)

    args = parser.parse_args(argv)
    # REMAINDER оставляет ведущий `--` — убираем, иначе он уедет в команду.
    if getattr(args, "command", None) and args.command and args.command[0] == "--":
        args.command = args.command[1:]
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
