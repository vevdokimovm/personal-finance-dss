"""Проверка ссылок даёт один вердикт локально и на чистом клоне (v9.2.0).

## 🔴 Дефект, ради которого гейт заведён

`preflight` локально печатал «механические проверки: чисто», а тот же `preflight`
на CI валил сборку тремя строками:

    ПРОВАЛ: битая ссылка -> frontend/dist/index.html   (docs/pitfalls.md)
    ПРОВАЛ: битая ссылка -> frontend/dist/index.html   (docs/ROADMAP.md)
    ПРОВАЛ: битая ссылка -> frontend/dist/index.html   (docs/WATCHLOG.md)

Причина не в ссылках, а в **разнице состояний**: `frontend/dist/` порождается сборкой
и закрыт `.gitignore`. У того, кто только что собрал фронт, каталог есть, и проверка
считает ссылку живой. На чистом клоне его нет никогда.

🔴 **Локальная зелёная проверка была не «проверкой, которая прошла», а проверкой,
которая смотрела на другой репозиторий.** Класс PIT-032, и здесь он проявился
в самом инструменте контроля.

## Почему дефект вернулся после починки

В v9.1.0 битая ссылка была убрана из `docs/ROADMAP.md` — и разбор инцидента,
записанный в три документа, **воспроизвёл её трижды**: текст, объясняющий проблему,
содержит тот самый путь, и `REF_PATTERN` не отличает упоминание в прозе от ссылки.

Поэтому лечение — не три записи в `LINK_ALLOWLIST` (они закрыли бы ровно эти три
упоминания и пропустили четвёртое), а **свойство пути**: порождаемый сборкой путь
не живёт в системе контроля версий, кем бы он ни был упомянут.

## Что проверяет этот гейт

Что ни одна ссылка в документах не держится на файле, который существует **только
локально**. Такая ссылка — зелёная здесь и красная на CI, то есть ровно та ситуация,
которую час разбирали по логам вместо того, чтобы увидеть на месте.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.revision.revision_check import (
    GENERATED_PREFIXES,
    REF_PATTERN,
    _is_generated,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_DIRS = ("docs",)


def _referenced_paths() -> set[str]:
    refs: set[str] = set()
    for directory in DOC_DIRS:
        for path in (REPO_ROOT / directory).rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in REF_PATTERN.finditer(text):
                refs.add(match.group(1).rstrip(".,);:").split("#")[0])
    return refs


def _is_ignored_by_git(relative: str) -> bool:
    """Спрашиваем сам git, а не гадаем по `.gitignore`.

    🔴 Разбор `.gitignore` руками — это второй парсер правил, который разойдётся
    с настоящим на отрицаниях (`!`), вложенных файлах и порядке строк. Тот, кто
    решает на самом деле, — git; его и спрашиваем.
    """
    result = subprocess.run(
        ["git", "check-ignore", "-q", relative],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def _git_available() -> bool:
    return (REPO_ROOT / ".git").exists()


class TestNoLinkDependsOnLocalOnlyFile:
    """Ссылка не может быть живой только у того, кто собрал проект."""

    @pytest.mark.skipif(not _git_available(), reason="без .git состояние клона не спросить")
    def test_no_reference_resolves_only_locally(self) -> None:
        """🔴 Мутация, которая ловится здесь: снять путь из `GENERATED_PREFIXES`.

        Тогда `frontend/dist/index.html` снова станет «живой ссылкой» у того,
        кто собрал фронт, и снова уронит CI. Гейт краснеет на месте.
        """
        offenders = []
        for ref in sorted(_referenced_paths()):
            target = REPO_ROOT / ref
            if not target.exists():
                continue  # битую ссылку ловит сам revision_check
            if _is_generated(ref):
                continue  # свойство названо явно — это и есть лечение
            if _is_ignored_by_git(ref):
                offenders.append(ref)
        assert not offenders, (
            "документы ссылаются на файлы, существующие ТОЛЬКО локально — "
            f"на чистом клоне ссылка битая, и CI покраснеет: {offenders}. "
            "Добавить префикс в GENERATED_PREFIXES (tools/revision/revision_check.py)"
        )

    @pytest.mark.skipif(not _git_available(), reason="без .git состояние клона не спросить")
    def test_declared_generated_prefixes_are_really_ignored(self) -> None:
        """Обратная сторона: список не оправдывает то, что git считает нормальным.

        Префикс, который git НЕ игнорирует, означает, что путь живёт в репозитории,
        и пропускать ссылки на него — значит перестать проверять настоящие ссылки.
        """
        wrong = [
            prefix for prefix in GENERATED_PREFIXES
            if (REPO_ROOT / prefix).exists() and not _is_ignored_by_git(prefix.rstrip("/"))
        ]
        assert not wrong, (
            f"эти префиксы объявлены порождаемыми, но git их не игнорирует: {wrong} — "
            "ссылки на них перестали проверяться зря"
        )


class TestGateItselfWorks:
    """Проверка распознаёт то, ради чего написана."""

    @pytest.mark.parametrize(
        "ref",
        [
            "frontend/dist/index.html",
            "frontend/coverage/coverage-summary.json",
            "frontend/.typecheck-tmp/index.html",
        ],
    )
    def test_generated_paths_are_recognised(self, ref: str) -> None:
        assert _is_generated(ref)

    @pytest.mark.parametrize(
        "ref", ["docs/ROADMAP.md", "app/main.py", "frontend/src/main.tsx"]
    )
    def test_real_paths_are_not_skipped(self, ref: str) -> None:
        """🔴 Слишком широкий префикс страшнее битой ссылки.

        `frontend/` целиком в списке отключил бы проверку всех ссылок на исходники
        фронта — и гейт остался бы зелёным навсегда, ничего не проверяя.
        """
        assert not _is_generated(ref)

    def test_pattern_finds_the_path_in_prose(self) -> None:
        """Путь в обратных кавычках — упоминание, но `REF_PATTERN` видит его как ссылку.

        Это и есть механизм, которым разбор инцидента воспроизвёл сам инцидент.
        Проверка закрепляет факт: лечить надо свойством пути, а не редактурой текста.
        """
        prose = "роадмап ссылался на `frontend/dist/index.html`, которого нет"
        found = [m.group(1) for m in REF_PATTERN.finditer(prose)]
        assert found == ["frontend/dist/index.html"]
