"""Repo revision checker — статические проверки актуальности docs <-> code.

Гоняется как гейт перед релизом (обёртка `tests/test_repo_revision.py` тянет его
в fast-тир, плюс CLI). Проверки:
  1. Битые ссылки на файлы репо, с делением источника на живой vs замороженный
     (историю не переписываем) и allowlist известно-приемлемых.
  2. Утечка legacy-параметров мат-модели (v2.x) в живые доки.
  3. Счётчики структуры (таблицы / миграции / пути OpenAPI) против пинов —
     форсирует синк доков при изменении схемы/API.
  4. Пары путей, различающиеся только регистром (`docs/GLOSSARY.md` vs
     `docs/glossary.md`) — на macOS/Windows регистронезависимая ФС молча
     схлопывает такую пару в один файл, в Docker/CI (регистрочувствительная
     Linux-ФС) оба живут отдельно и ссылки на «не тот» вариант бьются. Источник
     — `git ls-files` (список путей как строк, не обход диска: коллизия видна
     даже там, где ОС её сама скрывает).

Динамическая проверка календарных мин — отдельным инструментом `tools/timewarp`
(нужен pytest, см. методичку). Процесс и когда запускать —
`knowledge/guides/repo_revision_methodology.md`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = frozenset({
    ".git", "__pycache__", ".venv", "node_modules",
    ".pytest_cache", ".mypy_cache", ".hypothesis",
    # Сборочные/тестовые артефакты фронта (frontend/.gitignore) — генерируются `npm run
    # build`/Playwright, не исходники. Без них CJK-канарейка ловит саму себя на минифицированном
    # KaTeX в dist/ (регекспы шрифтовых диапазонов содержат реальные CJK-символы легитимно) —
    # тот же класс гейта-с-ложной-уверенностью, что уже был у openapi_paths (см. комментарий
    # выше по коду), только не пойман раньше, потому что dist/ обычно не существует на момент
    # прогона.
    "dist", "dist-ssr", "coverage", "playwright-report", "test-results", "blob-report",
    ".tanstack", ".typecheck-tmp",
})

# Источник считается замороженным (ссылки были верны на своей версии — не чиним).
FROZEN_HINTS = (
    "CHANGELOG.md", "/RELEASES.md", "/roadmap_archive/",
    "/reports/merges/", "/reports/releases/", "/reports/incidents/",
    "/reports/investigations/", "/reports/audits/", "/reports/testing/",
    "/reports/decisions/", "/science/",
)

REF_PATTERN = re.compile(
    r"(?<![\w/])((?:docs|knowledge|tools|app|tests|alembic|scripts|frontend|deploy|nginx)"
    r"/[\w./\-]+\.\w+)"
)

# (файл-источник, битая ссылка) -> причина. Известно-приемлемые, не роняют гейт.
LINK_ALLOWLIST = {
    ("docs/WATCHLOG.md", "tools/publish/finpilot_publish.sh"):
        "историческое упоминание переименования скрипта (не ссылка)",
    ("docs/WATCHLOG.md", "docs/math_model_v3_5_0.md"):
        "историческое упоминание переименования канона (v8.9.4: math_model_v3_5_0.md -> "
        "docs/math_model.md) в прозе §0/§3 — не ссылка. Тот же паттерн уже в allowlist для "
        "трёх других файлов (см. ниже), WATCHLOG пропущен при первом проходе.",
    ("docs/test_run_optimization.md", "tests/test_x.py"):
        "плейсхолдер синтаксиса в примере команды pytest",
    ("knowledge/business/android_google_play_pipeline.md", "docs/PWA_УСТАНОВКА.md"):
        "плановый ассет вехи 8 (PWA), ещё не создан",
    ("knowledge/business/ios_app_store_pipeline.md", "docs/PWA_УСТАНОВКА.md"):
        "плановый ассет вехи 8 (PWA), ещё не создан",
    ("knowledge/business/ios_app_store_pipeline.md", "frontend/static/images/icon-512.png"):
        "плановый ассет вехи 8 (иконка), ещё не создан",
    ("docs/frontend_milestone8_plan.md", "docs/ui_visual_direction.md"):
        "плановый артефакт вехи 8 (шаг 1.3, выбор направления дизайна), ещё не создан",
    ("knowledge/project_meta/project_instructions_s.md", "docs/Математическая_модель_v3_0_0.md"):
        "снапшот реальных project-инструкций; правка нужна в источнике",
    ("knowledge/project_meta/project_instructions_v.md", "docs/model_vs_code.md"):
        "снапшот реальных project-инструкций; правка нужна в источнике",
    ("docs/reports/ui_audit_e3.md", "frontend/src/pages/dashboard/ui/ForecastPanel.tsx"):
        "историческая ссылка на состояние Э3 — компонент вынесен в @widgets/forecast-panel "
        "в v8.7.0 (Э4 партия 2), отчёт не переписывается задним числом. Файл лежит в "
        "docs/reports/ напрямую, не в reports/audits/ — под FROZEN_HINTS не подпадает.",
    ("docs/ui_visual_direction.md", "docs/math_model_v3_5_0.md"):
        "историческая ссылка на состояние на момент отчёта (файл лежал в docs/ под этим "
        "именем) — переименован в docs/math_model.md в v8.9.4, отчёт не переписывается "
        "задним числом. Лежит прямо в docs/, не подпадает под FROZEN_HINTS.",
    ("docs/model/expert_certification/iterations/5/round5_model_half.md",
     "docs/math_model_v3_5_0.md"):
        "историческая ссылка на канон-файл на момент раунда 5 — переименован в "
        "docs/math_model.md в v8.9.4, отчёт эксперимента не переписывается задним числом.",
    ("docs/reports/adr/adr_006_reserve_floor_calibration.md", "docs/math_model_v3_5_0.md"):
        "историческая ссылка на канон-файл на момент ADR — переименован в docs/math_model.md "
        "в v8.9.4, ADR не переписывается задним числом.",
    ("docs/design_tokens_audit.md", "frontend/templates/profile.html"):
        "снимок на 2026-08-07/v8.3.2 (до React) — profile.html снесён частичным сносом Jinja "
        "v8.23.0 (docs/reports/decisions/2026-08-14_jinja_frontend_removal.md), аудит "
        "точечных строк не переписывается задним числом. Лежит прямо в docs/, не подпадает "
        "под FROZEN_HINTS — тот же случай, что ui_visual_direction.md выше. dashboard.html/"
        "planning.html/transactions.html из того же снимка НЕ в этом списке — они после "
        "исправления в том же разборе остались на Jinja (React-версии read-only, снос убрал бы "
        "CRUD), ссылки на них живые.",
}

# Паттерны устаревшей мат-модели v2.x (не должны заявляться как текущий факт).
LEGACY_PATTERNS = (
    re.compile(r"21 альтернатив"),
    re.compile(r"шаг 20%"),
    re.compile(r"flow-based"),
    re.compile(r"L_min\s*=\s*0[.,]30"),
    re.compile(r"95%\s*(?:интервал|CI|довер)"),
)

# Живые доки/код, где упоминание legacy легитимно (объяснение перехода v2 -> v3,
# регрессионный тест на ОТСУТСТВИЕ старого значения, или сам файл, определяющий эти
# паттерны — после расширения на .ts/.tsx/.py, 2026-08-19, ROADMAP §9.0 «A»).
LEGACY_ALLOWLIST_FILES = frozenset({
    "docs/model/history/math_model_v3_0_0.md",
    "docs/model/history/math_model_v3_1_0.md",
    "docs/model/model_history.md",  # сквозная история модели: legacy по назначению
    "docs/reference_profiles.md",
    "docs/reports/adr/adr_template.md",
    "tools/revision/revision_check.py",  # определяет сами паттерны — неизбежное самосовпадение
    "tools/survey_analysis/report.py",  # "95% доверительный интервал" — статистика опроса ЦА,
    # не модельный CI прогноза; тот же текст, другой домен
    "tests/test_frontend_static.py",  # регрессия на ОТСУТСТВИЕ "21 вариант"/"шаг 20%" в app.js —
    # упоминание тут и есть цель теста, не утечка факта
})

# Маркеры «это старое / переход» в строке — упоминание legacy легитимно, не факт.
# Сравнение по line.lower() (Python корректно фолдит кириллицу).
LEGACY_CONTEXT_MARKERS = (
    "устар", "старая", "старо", "→", "v2", "не использ",
    "прежн", "раньше", "было", "историч", "legacy", "переход", "заменен",
)

# tables 29: добавлена `user_consents` (юрблок L1, миграция 0030).
# migrations 31: 0030 (раздельные согласия) и 0031 (перенос согласия на
# финданные существующим пользователям).
# openapi_paths 112 (v8.3.1): снимок в docs/api был протухшим на три мажора —
# держал схему 5.14.0 со 106 путями, тогда как код отдавал 112. Недоставало
# ровно юридического контура вехи 7 (/api/consents, /api/legal/documents,
# /legal/cookies, /legal/marketing-consent). Пин был подогнан под протухший
# снимок, поэтому гейт молчал о расхождении, а не ловил его.
# openapi_paths 111 (v8.23.0): -3 — снесены /profile, /forgot-password, /reset-password
# (Jinja-роуты с подтверждённым паритетом в React, docs/reports/decisions/
# 2026-08-14_jinja_frontend_removal.md); снимок пересобран `tools/api_snapshot/dump_openapi.py`.
# openapi_paths 113 (батч 2 CRUD-паритета — Операция + Цель, ROADMAP §9.0 «B»): +1 —
# новый путь POST /api/goals/{goal_id}/contributions. PUT /transactions/{id} и
# PUT /goals/{id} НЕ добавляют путей — операции легли на уже существующие пути
# (там уже были DELETE на тех же URL).
EXPECTED_COUNTS = {"tables": 30, "migrations": 34, "openapi_paths": 113}


# Канарейка CJK: редкий токен-глюк генерации ассистентов — иероглиф вместо
# кириллицы/латиницы, иногда семантический. Реальные случаи этого репо до
# v6.13.1: U+957F («длинный») вместо «долгого» в logo_passport, U+6040 внутри
# слова «Авторизация» в cybersecurity_methodology. Продукт RU/EN: любой
# CJK-символ в дереве — дефект, не контент. Сырые иероглифы в этом файле не
# держим — канарейка не должна ловить саму себя. Диапазоны: кана, CJK Unified
# (+ext-A, +compat), хангыль.
CJK_PATTERN = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]")
CJK_SCAN_SUFFIXES = frozenset({
    ".py", ".md", ".sh", ".html", ".js", ".css", ".json",
    ".yml", ".yaml", ".cfg", ".ini", ".toml", ".txt",
})
# rel-путь -> обоснование легитимного CJK (сегодня пуст; замороженные файлы при
# необходимости попадают сюда с объяснением, историю не переписываем).
CJK_ALLOWLIST: dict[str, str] = {}


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
    """Обход дерева по расширениям. По умолчанию только `.md` (для LinkChecker —
    ссылки живут в прозе доков). LegacyModelChecker передаёт более широкий набор:
    устаревший факт модели может утечь в комментарий кода, не только в докс."""

    def __init__(self, root: Path, suffixes: tuple[str, ...] = (".md",)) -> None:
        self._root = root
        self._suffixes = suffixes

    def files(self) -> list[Path]:
        return [
            path
            for suffix in self._suffixes
            for path in self._root.rglob(f"*{suffix}")
            if not any(part in SKIP_DIRS for part in path.parts)
        ]

    @staticmethod
    def is_frozen(relative: str) -> bool:
        return any(hint in relative for hint in FROZEN_HINTS)

    def relative(self, path: Path) -> str:
        return path.relative_to(self._root).as_posix()


def _exists_with_matching_case(root: Path, ref: str) -> bool:
    """Как Path.exists(), но регистрочувствительно даже на APFS/NTFS.

    (root / ref).exists() схлопывает docs/GLOSSARY.md в реально лежащий
    docs/glossary.md на регистронезависимой ФС (macOS/Windows) — ссылка
    считается живой локально и бьётся в Docker/CI (регистрочувствительный
    Linux). Сверяем каждый сегмент пути с os.listdir() родительского
    каталога — то, что видит Linux, а не то, что резолвит ОС.
    """
    current = root
    for part in Path(ref).parts:
        try:
            entries = os.listdir(current)
        except OSError:
            return False
        if part not in entries:
            return False
        current = current / part
    return True


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
                if _exists_with_matching_case(self._root, ref):
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
        # Не только markdown (2026-08-19, ROADMAP §9.0 «A»): устаревший факт модели
        # утекал в код (комментарии .ts/.tsx/.py), где старый LinkChecker/CJK-стиль
        # markdown-only обход его не видел вовсе.
        self._scanner = _MarkdownScanner(root, suffixes=(".md", ".ts", ".tsx", ".py"))

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


class CjkCanaryChecker:
    name = "CJK-канарейка (токен-глюки генерации)"

    def __init__(self, root: Path) -> None:
        self._root = root

    def run(self) -> CheckResult:
        result = CheckResult(self.name)
        for path in sorted(self._root.rglob("*")):
            if not path.is_file() or path.suffix not in CJK_SCAN_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            rel = path.relative_to(self._root).as_posix()
            if rel in CJK_ALLOWLIST:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for line_no, line in enumerate(lines, 1):
                match = CJK_PATTERN.search(line)
                if match:
                    snippet = line.strip()[:60]
                    result.failures.append(Finding(
                        f"{rel}:{line_no}",
                        f"CJK-символ '{match.group()}' в: {snippet}",
                    ))
        if result.ok:
            result.infos.append(Finding("сводка", "CJK-символов в дереве продукта: 0"))
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


class CaseCollisionChecker:
    name = "Пути, различающиеся только регистром"

    def __init__(self, root: Path, *, paths: list[str] | None = None) -> None:
        self._root = root
        self._injected_paths = paths

    def _tracked_paths(self) -> list[str] | None:
        """Список путей от git ls-files, или None если git недоступен/не репозиторий.

        Намеренно НЕ обход диска (Path.rglob): на регистронезависимой ФС (macOS,
        Windows) `docs/GLOSSARY.md` и `docs/glossary.md` — один и тот же inode,
        обход увидит только одну запись, и коллизия останется невидимой именно
        там, где её удобнее всего поймать — до пуша в Docker/CI. `git ls-files`
        хранит путь как строку в индексе, поэтому видит оба варианта, даже когда
        ОС на диске уже схлопнула их в один файл.
        """
        if self._injected_paths is not None:
            return self._injected_paths
        try:
            proc = subprocess.run(
                ["git", "ls-files"],
                cwd=self._root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        paths = [line for line in proc.stdout.splitlines() if line]
        return paths or None

    def run(self) -> CheckResult:
        result = CheckResult(self.name)
        paths = self._tracked_paths()
        if paths is None:
            result.infos.append(Finding(
                "сводка", "git ls-files недоступен или пуст — проверка пропущена",
            ))
            return result
        by_lower: dict[str, set[str]] = {}
        for p in paths:
            by_lower.setdefault(p.lower(), set()).add(p)
        for lower, variants in sorted(by_lower.items()):
            if len(variants) > 1:
                result.failures.append(Finding(
                    lower,
                    "регистро-дубликаты: " + ", ".join(sorted(variants))
                    + " — молча совпадают на регистронезависимой ФС (macOS/Windows), "
                    "ломаются в Docker/CI",
                ))
        if result.ok:
            result.infos.append(
                Finding("сводка", f"проверено путей: {len(paths)}, коллизий регистра: 0")
            )
        return result


class RevisionChecker:
    def __init__(self, root: Path = REPO_ROOT) -> None:
        self._checks = [LinkChecker(root), LegacyModelChecker(root),
                        CjkCanaryChecker(root), CountChecker(root),
                        CaseCollisionChecker(root)]

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
