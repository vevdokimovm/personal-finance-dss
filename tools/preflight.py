"""Предполётная проверка батча — механические контрмеры уровня 3.

Существует потому, что проза не работает. Реестр рецидивов
(`docs/reports/recurrence_ledger.md`) фиксирует: разбор был написан, правило
сформулировано, ошибка всё равно повторилась. По правилу эскалации §1 пункт,
дошедший до третьего повтора, обязан получить проверку кодом, а не текстом.

Проверяется то и только то, что машина может установить сама:

  * согласованность версии в `app/config.py`, CHANGELOG, шапке WATCHLOG и
    файле `VERSION` (стандарт 48 — опознавательные знаки репозитория);
  * наличие и корректность `.repo-id`: без него деплойер опознаёт архив по
    имени файла, а имя можно переименовать — и версия уедет в чужую репу;
  * ровно десять записей в окне §3 WATCHLOG;
  * отсутствие мягких переносов `\\u00ad` в markdown;
  * отсутствие паттерна `&& grep` в скриптах репозитория (PIT-001);
  * наличие свежего свидетельства о прогоне матрицы PostgreSQL, если в
    `alembic/versions/` появилась миграция новее этого свидетельства.

Чего инструмент НЕ делает: не заменяет прогон тестов и не подтверждает, что
поведение верное. Он ловит ceremony-дрейф и известные грабли, не более.

Запуск из корня репозитория:
    python -m tools.preflight
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOFT_HYPHEN = "\u00ad"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def app_version(repo: Path) -> str | None:
    text = _read(repo / "app/config.py")
    match = re.search(r'default="(\d+\.\d+\.\d+)"', text)
    return match.group(1) if match else None


def changelog_version(repo: Path) -> str | None:
    for line in _read(repo / "CHANGELOG.md").splitlines():
        match = re.match(r"##\s*\[(\d+\.\d+\.\d+)\]", line.strip())
        if match:
            return match.group(1)
    return None


def watchlog_version(repo: Path) -> str | None:
    match = re.search(r"ВЕРСИЯ КОДА: `v(\d+\.\d+\.\d+)`",
                      _read(repo / "docs/WATCHLOG.md"))
    return match.group(1) if match else None


def version_file(repo: Path) -> str | None:
    """Стандарт 48: `VERSION` — одна строка, версия БЕЗ префикса `v`."""
    raw = _read(repo / "VERSION").strip()
    return raw or None


def repo_id(repo: Path) -> str | None:
    """Стандарт 48: `.repo-id` — `<владелец>/<имя-репы>`, одна строка."""
    raw = _read(repo / ".repo-id").strip().splitlines()
    return raw[0].strip() if raw else None


EXPECTED_REPO_ID = "vevdokimovm/personal-finance-dss"


def watchlog_window(repo: Path) -> int:
    text = _read(repo / "docs/WATCHLOG.md")
    start = text.find("## §3")
    end = text.find("## §4", start + 1)
    if start < 0 or end < 0:
        return -1
    return len(re.findall(r"^- \*\*v\d", text[start:end], flags=re.M))


def soft_hyphens(repo: Path) -> list[str]:
    hits = []
    for path in repo.rglob("*.md"):
        if ".git" in path.parts:
            continue
        if SOFT_HYPHEN in _read(path):
            hits.append(str(path.relative_to(repo)))
    return hits


def grep_in_and_chain(repo: Path) -> list[str]:
    """PIT-001: `grep` с нулём совпадений возвращает 1 и рвёт цепочку `&&`."""
    hits = []
    pattern = re.compile(r"&&\s*grep\b")
    for suffix in ("*.sh", "*.zsh"):
        for path in repo.rglob(suffix):
            if ".git" in path.parts:
                continue
            for number, line in enumerate(_read(path).splitlines(), 1):
                if pattern.search(line) and "|| true" not in line:
                    hits.append(f"{path.relative_to(repo)}:{number}")
    return hits


def pg_matrix_evidence(repo: Path) -> str | None:
    """Свидетельство о прогоне матрицы: версия в отчёте против миграций."""
    evidence = repo / "docs/reports/testing/pg_matrix_last_run.md"
    migrations = sorted((repo / "alembic/versions").glob("[0-9]*.py"))
    if not migrations:
        return None
    latest = migrations[-1].stem.split("_")[0]
    if not evidence.exists():
        return f"нет свидетельства о прогоне PG; последняя миграция {latest}"
    text = _read(evidence)
    if latest not in text:
        return (f"последняя миграция {latest} не упомянута в "
                f"pg_matrix_last_run.md — матрица могла не гоняться")
    return None


MANUAL_QUESTIONS = (
    "Сработает ли это на ВТОРОМ прогоне подряд, когда входных данных для шага "
    "уже нет, а результат прошлой работы лежит на диске?",
    "Каждое «сделано» подтверждено выводом команды, а не утверждением?",
    "Если что-то объявлено невозможным — исчерпаны ли ВСЕ каналы, включая "
    "установку пакета? Пустой `which` доказательством не является.",
)


def run(repo: Path) -> int:
    failures: list[str] = []

    versions = {"app/config.py": app_version(repo),
                "CHANGELOG.md": changelog_version(repo),
                "WATCHLOG": watchlog_version(repo),
                "VERSION": version_file(repo)}
    if len(set(versions.values())) != 1 or None in versions.values():
        failures.append(f"версии расходятся: {versions}")

    window = watchlog_window(repo)
    if window != 10:
        failures.append(f"окно §3 WATCHLOG: {window} записей вместо 10")

    hyphens = soft_hyphens(repo)
    if hyphens:
        failures.append(f"мягкие переносы в {len(hyphens)} файлах: "
                        f"{', '.join(hyphens[:3])}")

    chains = grep_in_and_chain(repo)
    if chains:
        failures.append(f"`&& grep` без `|| true` (PIT-001): "
                        f"{', '.join(chains[:3])}")

    identity = repo_id(repo)
    if identity is None:
        failures.append("нет `.repo-id` — деплойер опознает архив по имени "
                        "файла (стандарт 48)")
    elif identity != EXPECTED_REPO_ID:
        failures.append(f"`.repo-id` = {identity!r}, ожидается "
                        f"{EXPECTED_REPO_ID!r} — архив уехал бы не в ту репу")
    if version_file(repo) and version_file(repo).startswith("v"):
        failures.append("`VERSION` содержит префикс `v` — стандарт 48 требует "
                        "версию без него")

    pg_problem = pg_matrix_evidence(repo)

    print("=== PREFLIGHT ===")
    for item in failures:
        print(f"  ПРОВАЛ: {item}")
    if pg_problem:
        print(f"  ВНИМАНИЕ: {pg_problem}")
    if not failures:
        print("  механические проверки: чисто")

    print("\n=== ВОПРОСЫ, КОТОРЫЕ МАШИНА НЕ ПРОВЕРИТ ===")
    for question in MANUAL_QUESTIONS:
        print(f"  - {question}")

    print("\nЛидерборд рецидивов — docs/reports/recurrence_ledger.md")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Предполётная проверка батча")
    parser.add_argument("--repo", type=Path, default=REPO)
    return run(parser.parse_args(argv).repo)


if __name__ == "__main__":
    sys.exit(main())
