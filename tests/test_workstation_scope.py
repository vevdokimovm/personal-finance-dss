"""Пропуск «этой машины нет» обязан быть виден и обоснован.

Проверки контура рабочей станции (хуки канона, локальные утилиты, собранный SPA) на раннере
CI красили прогон в красный по причине, не имеющей отношения к продукту: `pdftotext`
и `tesseract` на ubuntu-latest не установлены, `~/repos/base-repo` там не существует,
а `frontend/dist` собирается не во всех джобах.

🔴 **Опасность лечения — не в самом пропуске, а в его тихости.** Пропуск без причины
превращает зелёный прогон в «не проверялось» (`PIT-020`), и заметить это нечем. Поэтому
условия пропуска проверяются здесь: они обязаны быть ПРЕДИКАТАМИ о машине, а не
заглушками, и обязаны нести текст причины.
"""
from __future__ import annotations

from pathlib import Path

from tests.support.workstation import (
    BASE_REPO_HOOKS,
    WORKSTATION_BINS,
    base_repo_hook,
    missing_workstation_bins,
    requires_base_repo_hooks,
    requires_spa_build,
    requires_workstation_bins,
    spa_is_built,
)


class TestPredicatesAnswerAboutTheMachine:
    """Каждый предикат отвечает на вопрос о машине, а не возвращает константу."""

    def test_missing_bins_is_a_subset_of_the_declared_list(self) -> None:
        assert set(missing_workstation_bins()) <= set(WORKSTATION_BINS)

    def test_binary_list_names_what_the_gate_needs(self) -> None:
        """Список сверен с гейтом каналов: он проверяет ровно эти три утилиты."""
        gate = Path(__file__).resolve().parents[1] / ".claude/hooks/research-channels-gate.py"
        text = gate.read_text(encoding="utf-8")
        for name in WORKSTATION_BINS:
            assert f'"{name}"' in text, f"{name} не упоминается в гейте — список разошёлся"

    def test_hook_lookup_returns_none_for_absent_hook(self) -> None:
        assert base_repo_hook("no-such-hook-in-canon.sh") is None

    def test_hook_lookup_returns_path_when_present(self) -> None:
        if not BASE_REPO_HOOKS.exists():
            return
        existing = next(iter(sorted(BASE_REPO_HOOKS.glob("*.sh"))), None)
        if existing is None:
            return
        assert base_repo_hook(existing.name) == existing

    def test_spa_predicate_matches_the_file_on_disk(self) -> None:
        index = Path(__file__).resolve().parents[1] / "frontend/dist/index.html"
        assert spa_is_built() == index.exists()


class TestSkipMarkersCarryAReason:
    """🔴 Пропуск без причины неотличим от пропуска по ошибке."""

    def test_every_marker_states_why(self) -> None:
        for marker in (requires_workstation_bins, requires_base_repo_hooks, requires_spa_build):
            reason = marker.kwargs.get("reason", "")
            assert len(reason) > 30, f"причина пропуска слишком короткая: {reason!r}"

    def test_reasons_name_the_missing_thing(self) -> None:
        assert "frontend/dist" in requires_spa_build.kwargs["reason"]
        assert "base-repo" in requires_base_repo_hooks.kwargs["reason"]
        assert "контур рабочей станции" in requires_workstation_bins.kwargs["reason"]
