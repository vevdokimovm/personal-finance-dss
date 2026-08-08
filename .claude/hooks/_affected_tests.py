"""Быстрый срез тестов для Stop-гейта: файлы, изменённые в ЭТОЙ сессии
(по logs/agent-audit.jsonl), плюс тесты, которые их импортируют.

Не претендует на полный dependency-граф — это осознанно узкий, быстрый
срез для Stop-хука (полная суита остаётся в церемонии батча, см. CLAUDE.md
правило 1 и 4). Эвристика: dataKey-путь app/a/b.py -> модуль app.a.b ->
grep по tests/**/*.py на вхождение этой строки (ловит import/from-формы).
Изменённый файл, который сам является tests/test_*.py, включается напрямую.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def changed_py_files(session_id: str) -> set[str]:
    log = ROOT / "logs" / "agent-audit.jsonl"
    if not log.exists():
        return set()
    changed = set()
    with log.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("session") != session_id:
                continue
            if rec.get("tool") not in ("Edit", "Write", "MultiEdit"):
                continue
            path = rec.get("path")
            if not path or not path.endswith(".py"):
                continue
            try:
                rel = Path(path).resolve().relative_to(ROOT).as_posix()
            except ValueError:
                continue
            changed.add(rel)
    return changed


def affected_test_files(changed: set[str]) -> set[str]:
    test_files = sorted((ROOT / "tests").rglob("test_*.py"))
    result: set[str] = set()

    for rel in changed:
        if rel.startswith("tests/") and Path(rel).name.startswith("test_"):
            result.add(rel)
            continue
        if not rel.startswith("app/") and not rel.startswith("alembic/"):
            continue
        module = rel[: -len(".py")].replace("/", ".")
        for tf in test_files:
            try:
                text = tf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if module in text:
                result.add(tf.resolve().relative_to(ROOT).as_posix())

    return result


if __name__ == "__main__":
    session_id = sys.argv[1] if len(sys.argv) > 1 else ""
    changed = changed_py_files(session_id)
    affected = affected_test_files(changed)
    for path in sorted(affected):
        print(path)
