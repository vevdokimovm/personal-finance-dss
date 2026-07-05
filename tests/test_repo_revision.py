"""Гейт ревизии: статические проверки docs<->code гоняются как обычный тест.

Ловит перед релизом рассинхрон, который иначе всплывает вручную: битые ссылки в
живых доках, утечку legacy мат-модели (v2.x), расхождение счётчиков структуры
(таблицы/миграции/пути OpenAPI). Инструмент и allowlist — tools/revision/revision_check.py.
Процесс и когда гонять полную ревизию — knowledge/guides/repo_revision_methodology.md.
"""
from __future__ import annotations

from tools.revision.revision_check import (
    REPO_ROOT,
    CountChecker,
    LegacyModelChecker,
    LinkChecker,
    RevisionChecker,
)


def _fmt(result) -> str:
    return "\n".join(f"{f.location}: {f.detail}" for f in result.failures)


class TestRepoRevisionGate:
    def test_no_broken_links_in_living_docs(self) -> None:
        result = LinkChecker(REPO_ROOT).run()
        assert result.ok, "Битые ссылки в живых доках:\n" + _fmt(result)

    def test_no_legacy_model_leak(self) -> None:
        result = LegacyModelChecker(REPO_ROOT).run()
        assert result.ok, "Legacy мат-модели в живых доках:\n" + _fmt(result)

    def test_structural_counts_match(self) -> None:
        result = CountChecker(REPO_ROOT).run()
        assert result.ok, "Рассинхрон счётчиков docs<->code:\n" + _fmt(result)

    def test_full_revision_clean(self) -> None:
        results = RevisionChecker().run()
        failures = [f for res in results for f in res.failures]
        assert not failures, "\n".join(f"{f.location}: {f.detail}" for f in failures)
