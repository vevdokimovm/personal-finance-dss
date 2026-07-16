"""Repo revision checker — статические проверки актуальности docs <-> code.

Гоняется как гейт перед релизом (обёртка `tests/test_repo_revision.py` тянет его
в fast-тир, плюс CLI). Три проверки:
  1. Битые ссылки на файлы репо, с делением источника на живой vs замороженный
     (историю не переписываем) и allowlist известно-приемлемых.
  2. Утечка legacy-параметров мат-модели (v2.x) в живые доки.
  3. Счётчики структуры (таблицы / миграции / пути OpenAPI) против пинов —
     форсирует синк доков при изменении схемы/API.

Динамическая проверка календарных мин — отдельным инструментом `tools/timewarp`
(нужен pytest, см. методичку). Процесс и когда запускать —
`knowledge/guides/repo_revision_methodology.md`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = frozenset({
    ".git", "__pycache__", ".venv", "node_modules",
    ".pytest_cache", ".mypy_cache", ".hypothesis",
})

# Источник считается замороженным (ссылки были верны на своей версии — не чиним).
FROZEN_HINTS = (
    "CHANGELOG.md", "/RELEASES.md", "/roadmap_archive/",
    "/reports/merges/", "/reports/releases/", "/reports/incidents/",
    "/reports/investigations/", "/reports/audits/", "/reports/testing/",
    "/science/",
)

REF_PATTERN = re.compile(
    r"(?<![\w/])((?:docs|knowledge|tools|app|tests|alembic|scripts|frontend|deploy|nginx)"
    r"/[\w./\-]+\.\w{1,6})"
)

# (файл-источник, битая ссылка) -> причина. Известно-приемлемые, не роняют гейт.
LINK_ALLOWLIST = {
    ("docs/WATCHLOG.md", "tools/publish/finpilot_publish.sh"):
        "историческое упоминание переименования скрипта (не ссылка)",
    ("docs/test_run_optimization.md", "tests/test_x.py"):
        "плейсхолдер синтаксиса в примере команды pytest",
    ("knowledge/business/android_google_play_pipeline.md", "docs/PWA_УСТАНОВКА.md"):
        "плановый ассет вехи 8 (PWA), ещё не создан",
    ("knowledge/business/ios_app_store_pipeline.md", "docs/PWA_УСТАНОВКА.md"):
        "плановый ассет вехи 8 (PWA), ещё не создан",
    ("knowledge/business/ios_app_store_pipeline.md", "frontend/static/images/icon-512.png"):
        "плановый ассет вехи 8 (иконка), ещё не создан",
    ("knowledge/project_meta/project_instructions_s.md", "docs/Математическая_модель_v3_0_0.md"):
        "снапшот реальных project-инструкций; правка нужна в источнике",
    ("knowledge/project_meta/project_instructions_v.md", "docs/model_vs_code.md"):
        "снапшот реальных project-инструкций; правка нужна в источнике",
}

# Паттерны устаревшей мат-модели v2.x (не должны заявляться как текущий факт).
LEGACY_PATTERNS = (
    re.compile(r"21 альтернатив"),
    re.compile(r"шаг 20%"),
    re.compile(r"flow-based"),
    re.compile(r"L_min\s*=\s*0[.,]30"),
    re.compile(r"95%\s*(?:интервал|CI|довер)"),
)

# Живые доки, где упоминание legacy легитимно (объяснение перехода v2 -> v3).
LEGACY_ALLOWLIST_FILES = frozenset({
    "docs/math_model_v3_0_0.md",
    "docs/model/model_history.md",  # сквозная история модели: legacy по назначению
    "docs/reference_profiles.md",
    "docs/reports/adr/adr_template.md",
})

# Маркеры «это старое / переход» в строке — упоминание legacy легитимно, не факт.
# Сравнение по line.lower() (Python корректно фолдит кириллицу).
LEGACY_CONTEXT_MARKERS = (
    "устар", "старая", "старо", "→", "v2", "не использ",
    "прежн", "раньше", "было", "историч", "legacy", "переход", "заменен",
)

EXPECTED_COUNTS = {"tables": 28, "migrations": 29, "openapi_paths": 106}


@dataclass(frozen=True)
class Finding:
    location: str
    detail: str


@dataclass
class CheckResult:
    name: str
    failures: list[Finding] = field(default_factory=list)
    infos: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


class _MarkdownScanner:
    def __init__(self, root: Path) -> None:
        self._root = root

    def files(self) -> list[Path]:
        return [
            path for path in self._root.rglob("*.md")
            if not any(part in SKIP_DIRS for part in path.parts)
        ]

    @staticmethod
    def is_frozen(relative: str) -> bool:
        return any(hint in relative for hint in FROZEN_HINTS)

    def relative(self, path: Path) -> str:
        return path.relative_to(self._root).as_posix()


class LinkChecker:
    name = "Битые ссылки"

    def __init__(self, root: Path) -> None:
        self._root = root
        self._scanner = _MarkdownScanner(root)

    def run(self) -> CheckResult:
        result = CheckResult(self.name)
        frozen_broken = 0
        allowed = 0
        for path in self._scanner.files():
            rel = self._scanner.relative(path)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in REF_PATTERN.finditer(text):
                ref = match.group(1).rstrip(".,);:").split("#")[0]
                if (self._root / ref).exists():
                    continue
                if self._scanner.is_frozen(rel):
                    frozen_broken += 1
                elif (rel, ref) in LINK_ALLOWLIST:
                    allowed += 1
                else:
                    result.failures.append(Finding(rel, f"битая ссылка -> {ref}"))
        result.infos.append(Finding("сводка", f"замороженных пропущено: {frozen_broken}"))
        result.infos.append(Finding("сводка", f"allowlist принято: {allowed}"))
        return result


class LegacyModelChecker:
    name = "Legacy мат-модели в живых доках"

    def __init__(self, root: Path) -> None:
        self._root = root
        self._scanner = _MarkdownScanner(root)

    def run(self) -> CheckResult:
        result = CheckResult(self.name)
        for path in self._scanner.files():
            rel = self._scanner.relative(path)
            if self._scanner.is_frozen(rel) or rel in LEGACY_ALLOWLIST_FILES:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line_no, line in enumerate(lines, 1):
                lowered = line.lower()
                if any(marker in lowered for marker in LEGACY_CONTEXT_MARKERS):
                    continue
                for pattern in LEGACY_PATTERNS:
                    if pattern.search(line):
                        result.failures.append(
                            Finding(f"{rel}:{line_no}", f"legacy-паттерн '{pattern.pattern}'")
                        )
        return result


class CountChecker:
    name = "Счётчики структуры docs<->code"

    def __init__(self, root: Path) -> None:
        self._root = root

    def _count_tables(self) -> int:
        total = 0
        for path in (self._root / "app").rglob("*.py"):
            total += sum(
                1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
                if re.search(r"__tablename__\s*=", line)
            )
        return total

    def _count_migrations(self) -> int:
        versions = self._root / "alembic" / "versions"
        return len([p for p in versions.glob("*.py") if p.name != "__init__.py"])

    def _count_openapi_paths(self) -> int:
        snapshot = self._root / "docs" / "api" / "openapi.json"
        data = json.loads(snapshot.read_text(encoding="utf-8"))
        return len(data.get("paths", {}))

    def run(self) -> CheckResult:
        result = CheckResult(self.name)
        actual = {
            "tables": self._count_tables(),
            "migrations": self._count_migrations(),
            "openapi_paths": self._count_openapi_paths(),
        }
        for key, expected in EXPECTED_COUNTS.items():
            got = actual[key]
            if got != expected:
                result.failures.append(Finding(
                    key,
                    f"ожидалось {expected}, в коде {got} — обнови доки и пин EXPECTED_COUNTS",
                ))
            else:
                result.infos.append(Finding(key, f"{got} (совпадает)"))
        return result


class RevisionChecker:
    def __init__(self, root: Path = REPO_ROOT) -> None:
        self._checks = [LinkChecker(root), LegacyModelChecker(root), CountChecker(root)]

    def run(self) -> list[CheckResult]:
        return [check.run() for check in self._checks]

    def report(self, results: list[CheckResult]) -> str:
        lines: list[str] = []
        for res in results:
            status = "OK" if res.ok else f"FAIL ({len(res.failures)})"
            lines.append(f"[{status}] {res.name}")
            for finding in res.failures:
                lines.append(f"    ✗ {finding.location}: {finding.detail}")
            for finding in res.infos:
                lines.append(f"    · {finding.location}: {finding.detail}")
        overall = "CLEAN" if all(r.ok for r in results) else "DRIFT"
        lines.append(f"\nИТОГ: {overall}")
        return "\n".join(lines)


def main() -> int:
    checker = RevisionChecker()
    results = checker.run()
    print(checker.report(results))
    return 0 if all(res.ok for res in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
