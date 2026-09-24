"""Батч не закрывается, пока гейты гита не прогнаны ЗДЕСЬ и целиком.

## Правило владельца, 24.09.2026, дословно

«отныне ты должен ВСЕГДА ТАКЖЕ КАК ТЕСТЫ ПРОГОНЯТЬ ГИТ ГЕЙТЫ ЗДЕСЬ ПОЛНОСТЬЮ
и фиксить все ошибки на месте!!!»

## Почему правилом это быть не может

За одни сутки вахта трижды заявила о зелёном CI, не проверив его; красное на теге
прожило два месяца (`docs/reports/incidents/ci_red_on_tags_for_a_month.md`). По шкале
эскалации `docs/reports/recurrence_ledger.md` §1 после третьего повтора допустима
только машинная проверка. Поэтому `tools/ci_local.py` оставляет след прогона
(`reports/ci_local_last_run.json`), а `preflight` — обязательный шаг сдачи батча —
этот след проверяет.

🔴 **След привязан к отпечатку РАБОЧЕГО дерева, а не к коммиту.** Иначе прогон
«до правки» засчитывался бы как проверка кода «после правки» — ровно та подмена
объекта, из-за которой всё и случилось.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.preflight import ci_local_failures

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_stamp(tmp: Path, payload: dict) -> None:
    target = tmp / "reports"
    target.mkdir(parents=True, exist_ok=True)
    (target / "ci_local_last_run.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


class TestStampGate:
    """Гейт следа: нет прогона — нет батча."""

    def test_missing_stamp_blocks(self, tmp_path: Path) -> None:
        assert ci_local_failures(tmp_path, tree="abc", required=("full",))

    def test_red_run_blocks(self, tmp_path: Path) -> None:
        write_stamp(tmp_path, {"tree": "abc", "jobs": ["full"], "green": False,
                               "failures": ["full → bandit"]})
        problems = ci_local_failures(tmp_path, tree="abc", required=("full",))
        assert problems and "bandit" in problems[0]

    def test_stamp_from_other_tree_blocks(self, tmp_path: Path) -> None:
        """🔴 Прогон «до правки» не засчитывается за проверку кода «после»."""
        write_stamp(tmp_path, {"tree": "СТАРОЕ", "jobs": ["full"], "green": True,
                               "failures": []})
        problems = ci_local_failures(tmp_path, tree="НОВОЕ", required=("full",))
        assert problems and "ДРУГОМ" in problems[0]

    def test_missing_job_blocks(self, tmp_path: Path) -> None:
        """Прогнать половину джоб — не значит прогнать гейты."""
        write_stamp(tmp_path, {"tree": "abc", "jobs": ["lint"], "green": True,
                               "failures": []})
        problems = ci_local_failures(tmp_path, tree="abc", required=("lint", "full"))
        assert problems and "full" in problems[0]

    def test_green_full_run_passes(self, tmp_path: Path) -> None:
        write_stamp(tmp_path, {"tree": "abc", "jobs": ["lint", "full"], "green": True,
                               "failures": []})
        assert ci_local_failures(tmp_path, tree="abc", required=("lint", "full")) == []


class TestGateItselfWorks:
    """Канарейка: гейт, который нельзя уронить, бесполезен."""

    def test_broken_stamp_file_blocks(self, tmp_path: Path) -> None:
        target = tmp_path / "reports"
        target.mkdir(parents=True, exist_ok=True)
        (target / "ci_local_last_run.json").write_text("{не json", encoding="utf-8")
        assert ci_local_failures(tmp_path, tree="abc", required=("full",))


class TestGateIsLocalOnly:
    """🔴 На раннере гейт молчит — иначе правило сломало бы сами гейты.

    След снимается на рабочей станции и несёт её отпечаток дерева; в CI его нет
    и быть не может. Без этой оговорки `preflight` падал бы в CI всегда.
    """

    def test_ci_environment_skips_the_gate(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("CI", "true")
        assert ci_local_failures(tmp_path, tree="abc", required=("full",)) == []

    def test_github_actions_environment_skips_the_gate(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert ci_local_failures(tmp_path, tree="abc", required=("full",)) == []

    def test_local_environment_still_gates(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        assert ci_local_failures(tmp_path, tree="abc", required=("full",))
