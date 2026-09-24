"""Публикуемый контур считается по публикатору, а не переписывается руками.

## Зачем отдельный модуль

Гейты гигиены (`test_no_personal_data_in_tree.py`, `test_no_secrets_in_repo.py`)
до ВЛ-29 судили всё дерево одинаково: находка в `app/` и находка в `docs/research/raw/`
роняли прогон с одинаковой силой. Правило §7 `CLAUDE.md` при этом прямо разрешает
хранить и анализировать опубликованные в интернете материалы **внутри** репозитория
и оставляет ровно один инвариант — **наружу ничего не уходит**.

Отсюда разделение, принятое владельцем (ВЛ-29, вариант 3):

- **публикуемый контур** — жёстко: находка валит прогон;
- **внутренний корпус** — мягко: находка печатается предупреждением.

🔴 **Контур не выписывается в константу, а СЧИТЫВАЕТСЯ из публикатора.** Копия белого
списка разошлась бы с оригиналом молча, и гейт охранял бы вчерашнюю границу — тот же
класс, что `PIT-032` (отсутствие красного как отсутствие проверки).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.publication_scope import (
    PUBLISHER,
    is_published,
    published_dirs,
    published_root_files,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestContourIsReadFromPublisher:
    """Граница берётся из белого списка `finpilot_publish_public.sh`."""

    def test_publisher_script_exists(self) -> None:
        assert PUBLISHER.exists(), f"публикатор не найден: {PUBLISHER}"

    def test_allow_dirs_are_parsed(self) -> None:
        """Каталоги читаются из `ALLOW_DIRS`, а не из копии списка в тесте."""
        dirs = published_dirs()
        for expected in ("app", "tests", "frontend", "scripts"):
            assert expected in dirs, f"{expected} не распознан в ALLOW_DIRS"
        assert "docs" not in dirs, "docs публикуется поштучно, а не целиком"
        assert "tools" not in dirs, "tools наружу не уезжает"

    def test_allow_files_are_parsed(self) -> None:
        files = published_root_files()
        assert "README.md" in files
        assert "CHANGELOG.md" not in files, "журнал версий в белом списке корня не стоит"

    def test_parser_reacts_to_the_script(self, tmp_path: Path) -> None:
        """🔴 Мутация: убрать каталог из скрипта — контур обязан сузиться.

        Без этой проверки парсер мог бы возвращать константу и выглядеть работающим.
        """
        script = PUBLISHER.read_text(encoding="utf-8").replace("\n  loadtest\n", "\n", 1)
        fake = tmp_path / "publish.sh"
        fake.write_text(script, encoding="utf-8")
        assert "loadtest" in published_dirs()
        assert "loadtest" not in published_dirs(fake)


class TestScopeVerdicts:
    """Что считается публикуемым, а что внутренним."""

    @pytest.mark.parametrize(
        "relative",
        ["app/main.py", "frontend/src/App.tsx", "scripts/x.sh", "README.md", "docs/DEPLOY.md"],
    )
    def test_published_paths(self, relative: str) -> None:
        assert is_published(relative)

    @pytest.mark.parametrize(
        "relative",
        [
            "docs/research/raw/bank_statement_corpus_2026-09-17.md",
            "docs/WATCHLOG.md",
            "knowledge/launch/waitlist_survey_2026-09-12.csv",
            "tools/preflight.py",
            "mutants/tests/test_watch_identity_hook.py",
        ],
    )
    def test_internal_paths(self, relative: str) -> None:
        assert not is_published(relative)

    def test_tests_of_workstation_hooks_are_internal(self) -> None:
        """🔴 `tests/` публикуется целиком, но тесты хуков публикатор отсекает.

        Хуки живут в `.claude/hooks/` — контур рабочей станции, которого в зеркале нет
        вовсе. Правило то же, что у тестов внутренних инструментов: предмет не публикуется,
        значит и тест не публикуется. Считается по факту ссылки, а не списком имён.
        """
        assert not is_published("tests/test_watch_identity_hook.py")
        assert not is_published("tests/test_exa_gate_hook.py")
        assert is_published("tests/test_import_dedup.py")

    def test_tests_of_internal_tooling_are_internal(self) -> None:
        """Тест, импортирующий `tools.`, в зеркало не уезжает — правило публикатора."""
        assert not is_published("tests/test_generator_v3.py")
