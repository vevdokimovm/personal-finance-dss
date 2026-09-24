"""Вердикт о зелёном CI выдаёт команда, а не память вахты.

## Зачем инструмент, если можно посмотреть глазами

Смотрели. За сутки вахта трижды объявила CI зелёным, и трижды это было неправдой:
сначала проверялся локальный прогон вместо раннера, потом прогон по **ветке** вместо
прогона по **тегу** — а джоба «Полный» на ветке пропускается и падает только на теге.
Разбор — `docs/reports/incidents/ci_red_on_tags_for_a_month.md`; по шкале эскалации
`docs/reports/recurrence_ledger.md` §1 третий повтор требует **машинной проверки**,
а не очередного правила в тексте.

## Что именно проверяет инструмент

Он отвечает на один вопрос: «зелёный ли прогон по последнему тегу, целиком».
`skipped` не считается провалом (джобы тира `full`/`deep` пропускаются по условию),
а `cancelled`, `failure` и незавершённые — считаются, потому что вердикта по ним нет.
"""
from __future__ import annotations

import pytest

from tools.ci_verdict import Job, verdict


def job(name: str, conclusion: str | None, status: str = "completed") -> Job:
    return Job(name=name, status=status, conclusion=conclusion)


class TestVerdict:
    """Правило вердикта: зелено только если зелены все, кроме пропущенных."""

    def test_all_success_is_green(self) -> None:
        ok, problems = verdict([job("Быстрый", "success"), job("Фронт", "success")])
        assert ok
        assert problems == []

    def test_skipped_does_not_break_green(self) -> None:
        """Тиры `full`/`deep` пропускаются по условию — это не провал."""
        ok, problems = verdict([job("Быстрый", "success"), job("Глубокий", "skipped")])
        assert ok
        assert problems == []

    def test_failure_is_named(self) -> None:
        ok, problems = verdict([job("Быстрый", "success"), job("Полный", "failure")])
        assert not ok
        assert problems == ["Полный: failure"]

    def test_cancelled_is_not_green(self) -> None:
        """🔴 Отменённая джоба — отсутствие вердикта, а не успех.

        Ровно на этом вахта однажды приняла прогон за зелёный: «Ядро модели»
        было `cancelled`, и в списке это выглядело безобидно.
        """
        ok, problems = verdict([job("Ядро", "cancelled")])
        assert not ok
        assert problems == ["Ядро: cancelled"]

    def test_unfinished_job_is_not_green(self) -> None:
        """Пока джоба идёт, вердикта нет — «зелено» объявлять нечем."""
        ok, problems = verdict([job("Быстрый", None, status="in_progress")])
        assert not ok
        assert problems == ["Быстрый: in_progress (не завершена)"]

    def test_every_problem_is_listed_not_just_first(self) -> None:
        ok, problems = verdict(
            [job("A", "failure"), job("B", "success"), job("C", "cancelled")]
        )
        assert not ok
        assert problems == ["A: failure", "C: cancelled"]

    def test_empty_run_is_not_green(self) -> None:
        """🔴 Ноль джоб — это «прогон не нашёлся», а не «всё хорошо»."""
        ok, problems = verdict([])
        assert not ok
        assert problems == ["в прогоне нет ни одной джобы — проверять нечего"]


class TestGateItselfWorks:
    """Канарейка: проверка, которая не может покраснеть, бесполезна."""

    @pytest.mark.parametrize("bad", ["failure", "cancelled", "timed_out", "action_required"])
    def test_any_non_success_conclusion_blocks(self, bad: str) -> None:
        ok, _ = verdict([job("X", bad)])
        assert not ok
