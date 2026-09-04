"""Тесты предполётной проверки.

Инструмент — контрмера уровня 3 из реестра рецидивов: его задача поймать то,
что дважды не поймала проза. Поэтому тесты проверяют именно детекцию, а не
удобство вывода.
"""
from __future__ import annotations

import pytest

from tools.preflight import (
    app_version,
    changelog_version,
    grep_in_and_chain,
    readme_version,
    repo_id,
    revision_check_failures,
    soft_hyphens,
    version_file,
    watchlog_version,
    watchlog_window,
)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "config.py").write_text('    default="1.2.3",\n',
                                                encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [1.2.3] — x\n",
                                           encoding="utf-8")
    (tmp_path / "docs").mkdir()
    window = "\n".join(f"- **v1.2.{i}** — запись" for i in range(10))
    (tmp_path / "docs" / "WATCHLOG.md").write_text(
        f"> ## ВЕРСИЯ КОДА: `v1.2.3` · x\n\n## §3\n{window}\n\n## §4\n",
        encoding="utf-8")
    # RevisionChecker::CountChecker читает docs/api/openapi.json безусловно
    # (crash, не graceful skip, при отсутствии файла) — нужен для любого
    # вызова revision_check_failures() на синтетическом дереве, даже если
    # сами счётчики не совпадут с EXPECTED_COUNTS (это ожидаемо и не то,
    # что проверяют тесты ниже).
    (tmp_path / "docs" / "api").mkdir()
    (tmp_path / "docs" / "api" / "openapi.json").write_text(
        '{"paths": {}}', encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "![version](https://img.shields.io/badge/version-1.2.3-blue)\n",
        encoding="utf-8")
    return tmp_path


class TestVersionConsistency:
    def test_reads_all_three_sources(self, repo):
        assert app_version(repo) == "1.2.3"
        assert changelog_version(repo) == "1.2.3"
        assert watchlog_version(repo) == "1.2.3"

    def test_changelog_takes_the_topmost_entry(self, repo):
        (repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [2.0.0] — new\n\n## [1.2.3] — old\n",
            encoding="utf-8")
        assert changelog_version(repo) == "2.0.0"

    def test_missing_source_is_none_not_crash(self, tmp_path):
        assert app_version(tmp_path) is None


class TestReadmeVersion:
    """README.md отставал от реальной версии дважды (v7.7.0 — на 15 версий; v8.24.1 —
    следующий батч это уже не поймал бы, README не входил в проверку). Третий повтор
    того же класса обязан ловиться кодом (§1 эскалации, recurrence_ledger.md)."""

    def test_reads_version_from_badge(self, repo):
        assert readme_version(repo) == "1.2.3"

    def test_missing_readme_is_none_not_crash(self, tmp_path):
        assert readme_version(tmp_path) is None

    def test_stale_badge_is_detected(self, repo):
        (repo / "README.md").write_text(
            "![version](https://img.shields.io/badge/version-0.0.1-blue)\n",
            encoding="utf-8")
        assert readme_version(repo) == "0.0.1"
        assert readme_version(repo) != app_version(repo)


class TestWatchlogWindow:
    def test_exactly_ten_is_the_contract(self, repo):
        assert watchlog_window(repo) == 10

    def test_eleven_is_detected(self, repo):
        path = repo / "docs" / "WATCHLOG.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "\n\n## §4", "\n- **v1.3.0** — лишняя\n\n## §4"), encoding="utf-8")
        assert watchlog_window(repo) == 11


class TestSoftHyphens:
    def test_detected_in_markdown(self, repo):
        (repo / "docs" / "x.md").write_text("сло\u00adво", encoding="utf-8")
        assert "docs/x.md" in soft_hyphens(repo)

    def test_clean_repo_reports_nothing(self, repo):
        assert soft_hyphens(repo) == []

    def test_injected_base_is_not_our_file(self, repo):
        """`_base/` — зеркало системы «база», инжектируемое в 63 репозитория.

        Читать его как свой текст нельзя: правку туда мы не вносим, а провал
        preflight по чужому файлу блокирует сдачу батча, не давая способа
        починки. Тот же вывод уже сделан для flake8 (v8.32.0) и ревизионного
        гейта (v8.30.1) — здесь он доезжает до третьей проверки.
        """
        base = repo / "_base" / "reports"
        base.mkdir(parents=True)
        (base / "pitfalls.md").write_text("сло\u00adво", encoding="utf-8")
        assert soft_hyphens(repo) == []


class TestGrepInAndChain:
    def test_pattern_is_flagged(self, repo):
        (repo / "run.sh").write_text("ls && grep x file\n", encoding="utf-8")
        assert any("run.sh" in hit for hit in grep_in_and_chain(repo))

    def test_comment_mentioning_the_pattern_is_not_a_violation(self, repo):
        """🔴 Упоминание в комментарии — не нарушение.

        Проверка судила ЛЮБУЮ строку и заблокировала сдачу батча на комментарии,
        который объяснял, почему в коде рядом этого паттерна нет (v8.42.0). Гейт,
        отвергающий прозу, судит не то, что заявлено, — тот же класс, что у гейта
        шрифта в v8.39.0.
        """
        (repo / "run.sh").write_text(
            "# без `&& grep` в цепочке (PIT-001): опасно при set -e\n"
            "if grep -q x file; then echo ok; fi\n",
            encoding="utf-8",
        )
        assert grep_in_and_chain(repo) == []

    def test_guarded_pattern_is_allowed(self, repo):
        (repo / "ok.sh").write_text("ls && grep x file || true\n",
                                    encoding="utf-8")
        assert grep_in_and_chain(repo) == []

    def test_plain_grep_is_not_flagged(self, repo):
        (repo / "fine.sh").write_text("grep x file\n", encoding="utf-8")
        assert grep_in_and_chain(repo) == []


class TestRepoIdentity:
    """Стандарт 48: опознавательные знаки читаются изнутри дерева.

    Смысл проверки — не аккуратность, а защита от реального сценария: архив
    переименовали, деплойер опознал репу по имени файла и опубликовал версию
    в чужой репозиторий. `.repo-id` внутри дерева переименовать нельзя.
    """

    def test_repo_id_is_read(self, repo):
        (repo / ".repo-id").write_text("vevdokimovm/x\n", encoding="utf-8")
        assert repo_id(repo) == "vevdokimovm/x"

    def test_missing_repo_id_is_none(self, repo):
        assert repo_id(repo) is None

    def test_only_first_line_counts(self, repo):
        (repo / ".repo-id").write_text("vevdokimovm/x\nмусор\n",
                                       encoding="utf-8")
        assert repo_id(repo) == "vevdokimovm/x"

    def test_version_file_is_read_without_prefix(self, repo):
        (repo / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        assert version_file(repo) == "1.2.3"

    def test_version_with_v_prefix_is_returned_as_is_for_the_check(self, repo):
        (repo / "VERSION").write_text("v1.2.3\n", encoding="utf-8")
        assert version_file(repo).startswith("v")

    def test_empty_version_is_none(self, repo):
        (repo / "VERSION").write_text("\n", encoding="utf-8")
        assert version_file(repo) is None


class TestRevisionCheckIntegration:
    """PIT-017 (v8.13.2): preflight не вызывал revision_check вообще — битая
    ссылка на ещё не созданный файл прошла через два прогона preflight подряд,
    поймалась только полным pytest. Эти тесты — единственная защита от
    повторного «тихого» разрыва этой интеграции."""

    def test_broken_link_in_living_doc_is_caught(self, repo):
        (repo / "docs" / "x.md").write_text(
            "ссылка на docs/reports/testing/nonexistent_probe.md\n",
            encoding="utf-8")
        failures = revision_check_failures(repo)
        assert any("битая ссылка" in f for f in failures)

    def test_clean_repo_reports_no_broken_links(self, repo):
        failures = revision_check_failures(repo)
        assert not any("битая ссылка" in f for f in failures)

    def test_findings_are_prefixed_with_check_name(self, repo):
        (repo / "docs" / "x.md").write_text(
            "ссылка на docs/reports/testing/nonexistent_probe.md\n",
            encoding="utf-8")
        failures = revision_check_failures(repo)
        assert any(f.startswith("revision_check[") for f in failures)
