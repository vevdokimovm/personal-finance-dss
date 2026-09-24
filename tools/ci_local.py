"""Прогон гейтов CI ЛОКАЛЬНО, до отгрузки — теми же командами, что у GitHub.

Запуск:

    python -m tools.ci_local              # блокирующие джобы: preflight, lint, core, fast, frontend
    python -m tools.ci_local --job full   # одна джоба (мультибраузер, визуал, a11y, security)
    python -m tools.ci_local --list       # что вообще есть и какие шаги исполнимы

Выход ненулевой, если хоть один шаг упал. Печатает команду, код возврата и время.

🔴 **Команды читаются из `.github/workflows/ci.yml`, а не переписаны сюда.** Копия
разошлась бы с оригиналом молча, и локальный прогон стал бы зелёным при красном CI —
ровно тот класс, ради которого инструмент и заведён
(`docs/reports/incidents/ci_red_on_tags_for_a_month.md`).

🔴 **Чего локальный прогон НЕ заменяет.** Шаги-actions (`checkout`, `setup-python`,
`setup-node`) исполнить нельзя — их эквивалент сама рабочая станция; они помечаются
пропущенными. И остаётся разница сред: у раннера нет `~/repos/base-repo`, нет
`pdftotext`/`tesseract`, зато есть три браузера и чистый `npm ci`. Поэтому зелёный
здесь — сильный признак, но вердикт по CI по-прежнему снимает `tools.ci_verdict`
с прогона **по тегу**.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/ci.yml"

# Джобы, которые блокируют прогон на GitHub: их зелёное и означает «CI в порядке».
BLOCKING = ("preflight", "lint", "core", "fast", "frontend")

# Шаги установки окружения: на раннере он чистый, у нас уже собран. Гонять их локально
# значит переустанавливать зависимости на каждый прогон — минуты впустую и риск
# переписать рабочее окружение. Пропускаются по умолчанию, включаются `--with-install`.
# 🔴 `playwright install` СЮДА НЕ ВХОДИТ — и это исправление, оплаченное ложным красным.
# Первая редакция считала его установкой и пропускала; фронтовые E2E тогда шли без
# firefox и webkit и дали **100 падений** там, где CI зелёный. Установка браузеров —
# не обустройство окружения, а предусловие самой проверки: без неё шаг проверяет
# не продукт, а отсутствие браузера.
INSTALL = re.compile(r"\bpip install\b|\bnpm ci\b|pip install --upgrade")

# 🔴 Второй случай того же класса, и дороже первого. Шаги bandit, pip-audit и
# нагрузочного smoke записаны в воркфлоу как ДВЕ строки: `pip install -q <инструмент>`
# и следом сама проверка. Регулярка видела первую строку и выкидывала весь шаг —
# три проверки не исполнялись локально НИ РАЗУ, а прогон печатал «ЗЕЛЕНО», тогда как
# в CI они исполнялись и краснели. Поэтому решение принимается не по шагу целиком,
# а по каждой его команде: пропускаем, только если установка — ВСЕ команды шага.

# 🔴 Отпечаток прогона. Правило владельца 24.09.2026, дословно: «отныне ты должен ВСЕГДА
# ТАКЖЕ КАК ТЕСТЫ ПРОГОНЯТЬ ГИТ ГЕЙТЫ ЗДЕСЬ ПОЛНОСТЬЮ и фиксить все ошибки на месте».
# Правило, которое надо помнить, не работает — поэтому прогон оставляет след с хешем
# дерева, а `tools/preflight.py` этот след проверяет и валит батч, если прогона не было
# или он шёл на другом коде.
STAMP = REPO_ROOT / "reports/ci_local_last_run.json"


@dataclass(frozen=True)
class Step:
    """Шаг джобы: имя, команда (если есть) и рабочий каталог."""

    name: str
    run: str | None
    workdir: str | None


def jobs_with_steps(workflow: Path | None = None) -> dict[str, list[Step]]:
    """Джобы воркфлоу и их шаги, как они записаны в файле CI."""
    data = yaml.safe_load((workflow or WORKFLOW).read_text(encoding="utf-8"))
    result: dict[str, list[Step]] = {}
    for job_name, job in (data.get("jobs") or {}).items():
        # 🔴 Рабочий каталог задаётся ДВУМЯ способами: у шага и один раз на джобу через
        # `defaults.run.working-directory`. Джоба фронта использует второй — без его
        # разбора локальный прогон звал бы `npm ci` в корне репозитория и падал бы там,
        # где CI зелёный. Поймано собственным тестом на первом же запуске.
        default_dir = (
            (job.get("defaults") or {}).get("run") or {}
        ).get("working-directory")
        steps = [
            Step(
                name=str(step.get("name") or step.get("uses") or "шаг"),
                run=step.get("run"),
                workdir=step.get("working-directory") or default_dir,
            )
            for step in (job.get("steps") or [])
        ]
        result[job_name] = steps
    return result


def runnable(step: Step) -> bool:
    """Исполним ли шаг локально: у него должна быть команда, а не `uses`."""
    return bool(step.run and step.run.strip())


def _commands(run: str) -> list[str]:
    """Исполняемые команды шага: без комментариев и пустых строк."""
    return [
        line.strip()
        for line in run.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_install(step: Step) -> bool:
    """Шаг ТОЛЬКО ставит окружение и ничего не проверяет.

    Достаточно одной проверочной команды, чтобы шаг гонялся целиком — ровно так
    его исполняет GitHub. Иначе локальный прогон зеленеет на невыполненной проверке.
    """
    commands = _commands(step.run or "")
    return bool(commands) and all(INSTALL.search(cmd) for cmd in commands)


def _env(repo: Path) -> dict[str, str]:
    """Окружение прогона: венв репозитория впереди PATH.

    🔴 Без этого `flake8`, `mypy` и `pytest` берутся из системного питона, которого
    в них нет, и локальный прогон краснеет там, где CI зелёный — то есть инструмент
    врал бы ровно в ту сторону, против которой заведён. Поймано первым же запуском.
    """
    env = dict(os.environ)
    env["PATH"] = f"{repo / '.venv' / 'bin'}:{env.get('PATH', '')}"
    return env


def _run(step: Step, repo: Path) -> tuple[bool, float]:
    cwd = repo / step.workdir if step.workdir else repo
    started = time.monotonic()
    # Блок `run:` воркфлоу — это shell-скрипт по определению (многострочный, с пайпами
    # и `&&`), и ровно так его исполняет сам GitHub. Источник строки — наш собственный
    # `.github/workflows/ci.yml`, а не пользовательский ввод; разбирать его на аргументы
    # значило бы исполнять НЕ ТО, что исполняет CI, то есть терять смысл инструмента.
    #
    # 🔴 Оболочка и флаги повторяют GitHub ДОСЛОВНО: `bash --noprofile --norc -eo
    # pipefail`. Без `-e` код возврата шага равен коду ПОСЛЕДНЕЙ команды, и падение
    # любой предыдущей исчезает бесследно. Измерено на шаге «Тесты + покрытие ядра»
    # (`coverage run -m pytest` и следом `coverage report`): pytest дал `1 failed`,
    # `coverage report` прошёл порог — и прогон напечатал «ЗЕЛЕНО» на упавших тестах.
    # Это и есть «локально зелено, а в гите упало больше тестов».
    result = subprocess.run(  # noqa: S602
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", step.run or ""],
        cwd=cwd, check=False, env=_env(repo),
    )
    return result.returncode == 0, time.monotonic() - started


def run_job(
    name: str, steps: list[Step], repo: Path, with_install: bool = False
) -> list[str]:
    """Прогнать шаги джобы; вернуть список провалов «джоба → шаг»."""
    failures: list[str] = []
    print(f"\n=== ДЖОБА {name} ===")
    for step in steps:
        if not runnable(step):
            print(f"  ⚪️ пропуск (action, не команда): {step.name}")
            continue
        if is_install(step) and not with_install:
            print(f"  ⚪️ пропуск (установка окружения, есть локально): {step.name}")
            continue
        head = shlex.split(step.run or "")[:6]
        print(f"  ▶ {step.name}\n     {' '.join(head)}…")
        ok, seconds = _run(step, repo)
        mark = "🟢" if ok else "🔴"
        print(f"  {mark} {step.name} — {seconds:.1f} с")
        if not ok:
            failures.append(f"{name} → {step.name}")
    return failures


def tree_hash(repo: Path) -> str:
    """Отпечаток РАБОЧЕГО дерева: что реально проверено, а не что закоммичено."""
    result = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z"],
        capture_output=True, text=True, check=False,
    )
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    import hashlib

    digest = hashlib.sha256((head + "\0" + result.stdout).encode()).hexdigest()
    return digest[:16]


def write_stamp(jobs: list[str], failures: list[str], repo: Path) -> None:
    """Записать след прогона: что гонялось, чем кончилось, на каком дереве."""
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(
        json.dumps(
            {
                "tree": tree_hash(repo),
                "jobs": jobs,
                "green": not failures,
                "failures": failures,
                "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Локальный прогон гейтов CI")
    parser.add_argument("--job", action="append", help="какие джобы гонять")
    parser.add_argument("--list", action="store_true", help="показать джобы и шаги")
    parser.add_argument(
        "--with-install", action="store_true",
        help="гонять и шаги установки окружения (по умолчанию пропускаются)",
    )
    args = parser.parse_args()

    jobs = jobs_with_steps()
    if args.list:
        for name, steps in jobs.items():
            runnable_count = sum(1 for s in steps if runnable(s))
            print(f"{name}: шагов {len(steps)}, исполнимо локально {runnable_count}")
        return 0

    wanted = args.job or list(BLOCKING)
    unknown = [name for name in wanted if name not in jobs]
    if unknown:
        print(f"нет таких джоб в воркфлоу: {', '.join(unknown)}")
        return 1

    failures: list[str] = []
    for name in wanted:
        failures.extend(run_job(name, jobs[name], REPO_ROOT, args.with_install))

    write_stamp(wanted, failures, REPO_ROOT)
    print("\n=== ИТОГ ЛОКАЛЬНОГО ПРОГОНА ===")
    if not failures:
        print("ЗЕЛЕНО. Это сильный признак, но вердикт по CI снимает "
              "`python -m tools.ci_verdict` с прогона ПО ТЕГУ.")
        return 0
    print("КРАСНОЕ:")
    for line in failures:
        print(f"  - {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
