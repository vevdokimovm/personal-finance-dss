"""Граница «уезжает наружу / остаётся внутри» — одна на все гейты гигиены.

Контур **считывается из публикатора** `tools/publish/finpilot_publish_public.sh`:
белые списки `ALLOW_DIRS`, `ALLOW_FILES`, `ALLOW_DOCS` плюс два механических правила
отсева внутри `tests/` (тесты внутренних инструментов и тесты хуков рабочей станции).
Копия списка в питоне разошлась бы с оригиналом молча — гейт охранял бы вчерашнюю
границу и выглядел исправным.

Зачем разделение — `tests/test_publication_scope.py` и ВЛ-29: внутри репозитория
материалы лежать могут (правило §7 `CLAUDE.md`), наружу не уходит ничего.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = REPO_ROOT / "tools/publish/finpilot_publish_public.sh"

# Ссылка на внутренний инструмент или на хук рабочей станции: и то, и другое
# публикатор отсекает механически, по факту ссылки, а не по списку имён.
_INTERNAL_REFERENCE = re.compile(r"""(from|import) tools[. ]|["']tools\.|\.claude""")


def _array(script: str, name: str) -> list[str]:
    """Элементы bash-массива `name=( ... )` без комментариев и пустых строк."""
    match = re.search(rf"^{name}=\((.*?)^\)", script, re.S | re.M)
    if not match:
        return []
    items: list[str] = []
    for line in match.group(1).splitlines():
        value = line.split("#", 1)[0].strip()
        if value:
            items.extend(value.split())
    return items


def _script(publisher: Path | None = None) -> str:
    return (publisher or PUBLISHER).read_text(encoding="utf-8")


def published_dirs(publisher: Path | None = None) -> tuple[str, ...]:
    """Каталоги, которые публикатор копирует в зеркало целиком (`ALLOW_DIRS`)."""
    return tuple(_array(_script(publisher), "ALLOW_DIRS"))


def published_root_files(publisher: Path | None = None) -> tuple[str, ...]:
    """Файлы корня из белого списка (`ALLOW_FILES`)."""
    return tuple(_array(_script(publisher), "ALLOW_FILES"))


def published_docs(publisher: Path | None = None) -> tuple[str, ...]:
    """Документы, уезжающие в зеркало поимённо (`ALLOW_DOCS`), без закомментированных."""
    return tuple(_array(_script(publisher), "ALLOW_DOCS"))


def _is_internal_test(relative: str) -> bool:
    """Тест внутри `tests/`, который публикатор отсекает по ссылке на внутренний контур."""
    if not relative.startswith("tests/") or not relative.endswith(".py"):
        return False
    path = REPO_ROOT / relative
    if not path.exists():
        return False
    try:
        return bool(_INTERNAL_REFERENCE.search(path.read_text(encoding="utf-8")))
    except (UnicodeDecodeError, OSError):
        return False


def is_published(relative: str, publisher: Path | None = None) -> bool:
    """Уедет ли файл в публичное зеркало при следующей публикации.

    Args:
        relative: путь от корня репозитория в POSIX-виде.
        publisher: альтернативный публикатор (для проверки самого парсера).

    Returns:
        True, если файл попадает в зеркало по белым спискам публикатора.
    """
    relative = relative.lstrip("./")
    head = relative.split("/", 1)[0]
    if "/" not in relative:
        return relative in published_root_files(publisher)
    if relative.startswith("docs/"):
        return relative.removeprefix("docs/") in published_docs(publisher)
    if head not in published_dirs(publisher):
        return False
    return not _is_internal_test(relative)
