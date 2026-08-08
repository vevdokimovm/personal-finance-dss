"""Гейт ревизии: статические проверки docs<->code гоняются как обычный тест.

Ловит перед релизом рассинхрон, который иначе всплывает вручную: битые ссылки в
живых доках, утечку legacy мат-модели (v2.x), расхождение счётчиков структуры
(таблицы/миграции/пути OpenAPI). Инструмент и allowlist — tools/revision/revision_check.py.
Процесс и когда гонять полную ревизию — knowledge/guides/repo_revision_methodology.md.
"""
from __future__ import annotations

from tools.revision.revision_check import (
    REPO_ROOT,
    CaseCollisionChecker,
    CjkCanaryChecker,
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

    def test_no_cjk_glitches_in_product_tree(self) -> None:
        result = CjkCanaryChecker(REPO_ROOT).run()
        assert result.ok, "CJK-глюки генерации в файлах:\n" + _fmt(result)

    def test_cjk_checker_detects_synthetic(self, tmp_path) -> None:
        # реальный класс глюка: U+957F («длинный») вместо «долгого»; сырой
        # иероглиф в тестах не держим — конструируем через chr()
        glitch = "Это итог" + chr(0x957F) + " подбора"
        (tmp_path / "note.md").write_text(glitch, encoding="utf-8")
        (tmp_path / "ok.md").write_text("чистый текст, clean text", encoding="utf-8")
        result = CjkCanaryChecker(tmp_path).run()
        assert not result.ok
        assert any("note.md:1" in f.location for f in result.failures)

    def test_no_case_only_path_collisions(self) -> None:
        result = CaseCollisionChecker(REPO_ROOT).run()
        assert result.ok, "Пути-регистро-дубликаты:\n" + _fmt(result)

    def test_case_collision_checker_detects_synthetic(self) -> None:
        # Реальный класс бага (этот батч): docs/GLOSSARY.md vs docs/glossary.md —
        # один inode на macOS (регистронезависимая ФС), два разных файла в Docker/CI.
        # На диске такую пару здесь не создать (тот же коллапс), поэтому список путей
        # подаётся напрямую — так же, как CaseCollisionChecker читает git ls-files.
        paths = ["docs/glossary.md", "docs/GLOSSARY.md", "docs/README.md"]
        result = CaseCollisionChecker(REPO_ROOT, paths=paths).run()
        assert not result.ok
        assert any("docs/glossary.md" in f.location for f in result.failures)

    def test_case_collision_checker_skips_when_no_git(self, tmp_path) -> None:
        result = CaseCollisionChecker(tmp_path).run()
        assert result.ok
        assert any("пропущена" in f.detail for f in result.infos)

    def test_full_revision_clean(self) -> None:
        results = RevisionChecker().run()
        failures = [f for res in results for f in res.failures]
        assert not failures, "\n".join(f"{f.location}: {f.detail}" for f in failures)
