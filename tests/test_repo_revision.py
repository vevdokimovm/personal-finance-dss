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

    def test_link_checker_catches_case_mismatch_even_on_case_insensitive_fs(
        self, tmp_path
    ) -> None:
        # Реальный класс бага (этот батч): docs/GLOSSARY.md vs docs/glossary.md.
        # Path.exists() схлопывает регистр на APFS/NTFS (macOS/Windows) — молча
        # резолвит "docs/GLOSSARY.md" в реально лежащий "docs/glossary.md" и
        # считает ссылку живой. В Docker/CI (регистрочувствительная Linux-ФС)
        # та же ссылка бьётся. В отличие от CaseCollisionChecker (два файла
        # одновременно) здесь нет коллизии на диске — только ссылка не в том
        # регистре, поэтому воспроизводится реальными файлами, не инъекцией.
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "glossary.md").write_text("термины", encoding="utf-8")
        (tmp_path / "note.md").write_text(
            "См. docs/GLOSSARY.md за определениями.", encoding="utf-8"
        )
        result = LinkChecker(tmp_path).run()
        assert not result.ok
        assert any(
            "docs/GLOSSARY.md" in f.detail and f.location == "note.md"
            for f in result.failures
        )

    def test_no_legacy_model_leak(self) -> None:
        result = LegacyModelChecker(REPO_ROOT).run()
        assert result.ok, "Legacy мат-модели в живых доках:\n" + _fmt(result)

    def test_legacy_model_checker_scans_ts_tsx_py_not_only_markdown(self, tmp_path) -> None:
        # Найдено 2026-08-19 (ROADMAP §9.0 «A»): три версии канона (v3.0.0/v3.5.0/v3.5.0)
        # висели на одном и том же инварианте ПДН<=0.40 в .ts/.tsx/.py — LegacyModelChecker
        # до этого ходил только по markdown, устаревший факт в коде проходил незамеченным.
        # Собираем строки НЕ литералом — иначе сканирование .py-файлов подхватит сам этот
        # тест как «утечку» при прогоне LegacyModelChecker на реальном репо (self-match,
        # тот же класс, что CJK-канарейка ловит себя же — chr()-приём там, конкатенация тут).
        old_default = "L_min" + " = 0" + ".30"  # старый дефолт до калибровки
        old_count = "21" + " альтернатив"
        (tmp_path / "core.py").write_text(old_default + "\n", encoding="utf-8")
        (tmp_path / "Widget.tsx").write_text("// раскраска для " + old_count + "\n",
                                             encoding="utf-8")
        result = LegacyModelChecker(tmp_path).run()
        assert not result.ok
        assert any("core.py" in f.location for f in result.failures)
        assert any("Widget.tsx" in f.location for f in result.failures)

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
