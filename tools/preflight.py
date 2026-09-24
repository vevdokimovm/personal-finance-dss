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
    `alembic/versions/` появилась миграция новее этого свидетельства;
  * `tools.revision.revision_check` (битые ссылки, устаревшие упоминания канона
    матмодели, CJK-канарейка, счётчики структуры, коллизии регистра пути) —
    до v8.13.1 preflight его НЕ вызывал: битая ссылка на ещё не созданный файл
    прошла через два прогона preflight подряд и поймалась только полным
    прогоном `pytest` (`tests/test_repo_revision.py`). Один и тот же класс
    проблемы, что PIT-016 — гейт, который заявлен как проверяющий X, но X не
    проверяет, хуже отсутствующего гейта: создаёт ложную уверенность.

Чего инструмент НЕ делает: не заменяет прогон тестов и не подтверждает, что
поведение верное. Он ловит ceremony-дрейф и известные грабли, не более.

Запуск из корня репозитория:
    python -m tools.preflight
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from tools.revision.revision_check import RevisionChecker

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


def readme_version(repo: Path) -> str | None:
    """Значок версии в README.md. Отставал от реальной версии дважды (v7.7.0 — на 15
    версий; v8.24.1 — README не входил в проверку версий вообще, третий повтор того же
    класса — эскалация §1, recurrence_ledger.md)."""
    match = re.search(r"badge/version-(\d+\.\d+\.\d+)-", _read(repo / "README.md"))
    return match.group(1) if match else None


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


# `_base/` — зеркало системы «база», инжектируемое в 63 репозитория снаружи. Судить его
# нашими проверками нельзя: правку туда мы не вносим (следующая раздача её сотрёт), а провал
# preflight по чужому файлу блокирует сдачу батча, не давая способа починки. Тот же вывод уже
# сделан для ревизионного гейта (v8.30.1, `SKIP_DIRS`) и для flake8 (v8.32.0) — здесь он
# доезжает до третьей проверки, которая о нём не знала. Правило «отмена доходит всюду».
FOREIGN_DIRS = frozenset({".git", "_base"})


def _foreign(path: Path) -> bool:
    return any(part in FOREIGN_DIRS for part in path.parts)


# Первичный материал исследований (§9) хранится дословно — мягкий перенос, попавший
# в него из скопированного источника, править запрещено тем же правилом. Разбор класса —
# `RAW_MATERIAL_PREFIX` в `tools/revision/revision_check.py`.
RAW_MATERIAL_PREFIX = "docs/research/raw"


def soft_hyphens(repo: Path) -> list[str]:
    hits = []
    for path in repo.rglob("*.md"):
        if _foreign(path):
            continue
        if path.relative_to(repo).as_posix().startswith(RAW_MATERIAL_PREFIX):
            continue
        if SOFT_HYPHEN in _read(path):
            hits.append(str(path.relative_to(repo)))
    return hits


def grep_in_and_chain(repo: Path) -> list[str]:
    """PIT-001: `grep` с нулём совпадений возвращает 1 и рвёт цепочку `&&`.

    🔴 Строки-комментарии пропускаются. Проверка судила ЛЮБУЮ строку, включая ту, где
    паттерн лишь упоминается — и заблокировала сдачу батча на комментарии, который
    объяснял, почему в коде рядом этого паттерна нет (поймано 04.09.2026, v8.42.0).
    Тот же класс, что у гейта шрифта в v8.39.0: проверка, удовлетворяемая или
    отвергаемая прозой, судит не то, что заявлено.
    """
    hits = []
    pattern = re.compile(r"&&\s*grep\b")
    for suffix in ("*.sh", "*.zsh"):
        for path in repo.rglob(suffix):
            if _foreign(path):
                continue
            for number, line in enumerate(_read(path).splitlines(), 1):
                if line.lstrip().startswith("#"):
                    continue
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


def revision_check_failures(repo: Path) -> list[str]:
    """`tools.revision.revision_check` вызван из preflight (PIT-017, v8.13.2):

    до этого preflight не проверял битые ссылки/устаревший канон/CJK/счётчики
    структуры вообще — только ручная привычка гонять `revision_check` отдельно
    рядом с preflight, не гарантия кода.
    """
    hits: list[str] = []
    for res in RevisionChecker(repo).run():
        for finding in res.failures:
            hits.append(f"revision_check[{res.name}] {finding.location}: "
                        f"{finding.detail}")
    return hits


MANUAL_QUESTIONS = (
    "Сработает ли это на ВТОРОМ прогоне подряд, когда входных данных для шага "
    "уже нет, а результат прошлой работы лежит на диске?",
    "Каждое «сделано» подтверждено выводом команды, а не утверждением?",
    "Если что-то объявлено невозможным — исчерпаны ли ВСЕ каналы, включая "
    "установку пакета? Пустой `which` доказательством не является.",
)


# 🔴 Гейты гита прогоняются ЗДЕСЬ и целиком — правило владельца 24.09.2026, дословно:
# «отныне ты должен ВСЕГДА ТАКЖЕ КАК ТЕСТЫ ПРОГОНЯТЬ ГИТ ГЕЙТЫ ЗДЕСЬ ПОЛНОСТЬЮ
# и фиксить все ошибки на месте!!!». Правило, которое надо помнить, не работает
# (три ложных отчёта за сутки, два месяца красного на теге —
# `docs/reports/incidents/ci_red_on_tags_for_a_month.md`), поэтому проверяется машиной.
CI_LOCAL_STAMP = "reports/ci_local_last_run.json"
CI_LOCAL_REQUIRED = ("preflight", "lint", "core", "fast", "frontend", "full")


def ci_local_failures(
    repo: Path, tree: str, required: tuple[str, ...] = CI_LOCAL_REQUIRED
) -> list[str]:
    """Прогнаны ли гейты гита локально на ЭТОМ дереве и целиком.

    Args:
        repo: корень репозитория.
        tree: отпечаток рабочего дерева (`tools.ci_local.tree_hash`).
        required: джобы, которые обязаны быть в прогоне.

    Returns:
        Список причин, по которым батч закрывать нельзя; пустой — можно.
    """
    # 🔴 Гейт СУГУБО локальный. На раннере следа нет и быть не может: он снимается
    # на рабочей станции, отпечаток дерева там другой. Без этой строки preflight
    # падал бы в CI всегда — то есть правило «прогоняй гейты локально» сломало бы
    # сами гейты. Поймано до отгрузки, на разборе собственной правки.
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return []
    stamp = repo / CI_LOCAL_STAMP
    if not stamp.exists():
        return ["гейты гита локально не прогонялись: нет "
                f"{CI_LOCAL_STAMP} (запусти `python -m tools.ci_local --job full`)"]
    try:
        data = json.loads(stamp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"след локального прогона нечитаем ({exc}) — прогони гейты заново"]
    if data.get("tree") != tree:
        return ["след локального прогона снят на ДРУГОМ дереве "
                f"({data.get('tree')!r} вместо {tree!r}) — код менялся после проверки"]
    missing = [job for job in required if job not in (data.get("jobs") or [])]
    if missing:
        return [f"локально прогнаны не все гейты, нет: {', '.join(missing)}"]
    if not data.get("green"):
        return ["локальный прогон гейтов КРАСНЫЙ: "
                + "; ".join(data.get("failures") or ["причина не записана"])]
    return []


def run(repo: Path) -> int:
    failures: list[str] = []

    versions = {"app/config.py": app_version(repo),
                "CHANGELOG.md": changelog_version(repo),
                "WATCHLOG": watchlog_version(repo),
                "VERSION": version_file(repo),
                "README.md": readme_version(repo)}
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

    failures.extend(revision_check_failures(repo))

    # 🔴 Гейт локального прогона. Был написан в v9.13.14 вместе с тестами — и НЕ ВЫЗВАН
    # отсюда ни разу: тесты звали функцию напрямую, поэтому зелёное покрытие означало
    # «функция работает», а не «правило исполняется». Полтора батча подряд `preflight`
    # печатал «чисто» при КРАСНОМ следе с чужого дерева. Класс — «проверка написана,
    # но не подключена»; ловится только тестом на факт вызова, он рядом.
    from tools.ci_local import tree_hash

    failures.extend(ci_local_failures(repo, tree_hash(repo)))

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
