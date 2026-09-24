"""Контур рабочей станции: что есть у владельца на маке и чего нет на раннере CI.

Часть проверок в `tests/` судит не продукт, а **рабочую станцию**: хуки в `~/repos/base-repo`,
локальные `curl`/`pdftotext`/`tesseract`, собранный SPA в `frontend/dist`. На чужой машине
их нет по построению, и красный там означает «этой машины нет», а не «продукт сломан».

🔴 **Пропуск здесь ИМЕНОВАННЫЙ и с причиной, а не `try/except`.** Тихий пропуск — это
ровно тот класс, против которого заведены сами гейты: вердикт «зелено» начинает значить
«не проверялось» (`PIT-020`). `pytest -rs` печатает причину каждого пропуска, и она
называет, чего именно не хватает на этой машине.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Утилиты, которые проверяет гейт каналов исследования: PDF и OCR (Г20, Г25).
WORKSTATION_BINS = ("curl", "pdftotext", "tesseract")

# Хуки рабочей станции живут в каноне `base-repo` и раздаются оттуда симлинком.
BASE_REPO_HOOKS = Path.home() / "repos" / "base-repo" / ".claude" / "hooks"

SPA_INDEX = REPO_ROOT / "frontend" / "dist" / "index.html"


def missing_workstation_bins() -> tuple[str, ...]:
    """Каких локальных утилит контура нет в PATH."""
    return tuple(name for name in WORKSTATION_BINS if shutil.which(name) is None)


def base_repo_hook(name: str) -> Path | None:
    """Путь к хуку канона, если он на месте; иначе None."""
    hook = BASE_REPO_HOOKS / name
    return hook if hook.exists() else None


def spa_is_built() -> bool:
    """Собран ли фронт: без `frontend/dist` сервер отдаёт 404 на адресах SPA."""
    return SPA_INDEX.exists()


requires_workstation_bins = pytest.mark.skipif(
    bool(missing_workstation_bins()),
    reason=(
        "контур рабочей станции неполон: нет "
        + ", ".join(missing_workstation_bins() or ("—",))
        + " (проверка про машину владельца, не про продукт)"
    ),
)

requires_base_repo_hooks = pytest.mark.skipif(
    not BASE_REPO_HOOKS.exists(),
    reason=f"нет каталога хуков канона {BASE_REPO_HOOKS} — машина не рабочая станция",
)

requires_spa_build = pytest.mark.skipif(
    not spa_is_built(),
    reason=(
        "frontend/dist отсутствует: SPA не собрана, сервер отдаёт 404 на её адресах. "
        "Собрать — `npm ci && npm run build` в `frontend/`"
    ),
)
