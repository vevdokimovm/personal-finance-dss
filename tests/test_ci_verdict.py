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

import json

from tools import ci_verdict
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


class TestVerdictIsTakenByCommit:
    """🔴 Вердикт снимается по КОММИТУ, а не по тегу.

    Решение владельца 25.09.2026, дословно: «снимай вердикт по КОММИТУ!» — после того
    как из триггеров воркфлоу убраны теги. Пока `full` и `deep` гонялись только на тегах,
    вердикт по тегу был единственным полным; теперь все три тира идут на каждый push,
    и прогон по тегу дублировал прогон по коммиту один в один — два полных набора джоб
    на один и тот же код, при нуле новой информации.

    Тег остаётся удобным ИМЕНЕМ для человека: `ci_verdict v9.13.21` находит коммит,
    на который тег указывает, и берёт прогон по нему.
    """

    def test_sha_is_resolved_from_a_ref(self, monkeypatch) -> None:
        calls: list[tuple[str, ...]] = []

        def fake_gh(*args: str) -> str:
            calls.append(args)
            return "abc123def456\n"

        monkeypatch.setattr(ci_verdict, "_gh", fake_gh)
        assert ci_verdict.commit_of("v9.13.21") == "abc123def456"
        assert any("v9.13.21" in " ".join(args) for args in calls)

    def test_run_is_found_by_head_sha(self, monkeypatch) -> None:
        runs = [
            {"databaseId": 1, "headSha": "other", "status": "completed"},
            {"databaseId": 2, "headSha": "abc123", "status": "completed"},
        ]

        def fake_gh(*args: str) -> str:
            if args[0] == "run" and args[1] == "list":
                return json.dumps(runs)
            return json.dumps({"jobs": [
                {"name": "Быстрый", "status": "completed", "conclusion": "success"},
            ]})

        monkeypatch.setattr(ci_verdict, "_gh", fake_gh)
        run_id, jobs = ci_verdict.fetch_jobs("abc123")
        assert run_id == "2"
        assert [j.name for j in jobs] == ["Быстрый"]

    def test_missing_run_is_reported_not_guessed(self, monkeypatch) -> None:
        monkeypatch.setattr(ci_verdict, "_gh", lambda *a: json.dumps([]))
        run_id, jobs = ci_verdict.fetch_jobs("nosuchsha")
        assert run_id == "" and jobs == []
