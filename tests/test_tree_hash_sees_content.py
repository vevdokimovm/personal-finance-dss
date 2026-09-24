"""Гейт: отпечаток дерева видит СОДЕРЖИМОЕ, а не только статус файлов.

🔴 Дыра найдена замером 24.09.2026 (v9.13.15). `tree_hash` считал
`sha256(HEAD + git status --porcelain)`, а `--porcelain` печатает только СТАТУС
файла (` M путь`), но не его содержимое. Следствие: файл, уже числящийся изменённым,
можно было править после зелёного прогона сколько угодно — отпечаток не менялся,
и `preflight` засчитывал прогон «до правки» за проверку кода «после правки».
Это ровно та подмена объекта, против которой гейт и заводился: он ловил только
появление новых файлов, удаление и смену `HEAD`.

Замер, которым дыра доказана: правка `docs/WATCHLOG.md` после прогона оставила
отпечаток `2c74eab99bd8a6cf` неизменным до и после.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.ci_local import tree_hash


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Крошечный git-репозиторий с одним закоммиченным файлом."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@e.st"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "code.py").write_text("value = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)
    return tmp_path


class TestTrackedFileEdits:
    """Правка отслеживаемого файла обязана менять отпечаток."""

    def test_edit_of_clean_file_changes_hash(self, repo: Path) -> None:
        before = tree_hash(repo)
        (repo / "code.py").write_text("value = 2\n", encoding="utf-8")
        assert tree_hash(repo) != before

    def test_second_edit_of_already_dirty_file_changes_hash(self, repo: Path) -> None:
        """🔴 Сама дыра: файл УЖЕ изменён, правим ещё раз — статус тот же ` M`.

        Прежняя реализация возвращала здесь одинаковый отпечаток, и зелёный прогон
        «до правки» покрывал собой произвольные последующие изменения.
        """
        (repo / "code.py").write_text("value = 2\n", encoding="utf-8")
        dirty = tree_hash(repo)
        (repo / "code.py").write_text("value = 999\n", encoding="utf-8")
        assert tree_hash(repo) != dirty, (
            "правка уже изменённого файла обязана менять отпечаток: иначе прогон "
            "засчитывается за код, который он не проверял"
        )

    def test_edit_of_untracked_file_changes_hash(self, repo: Path) -> None:
        """Новый файл тоже правится после прогона — его содержимое считается."""
        (repo / "new.py").write_text("a = 1\n", encoding="utf-8")
        before = tree_hash(repo)
        (repo / "new.py").write_text("a = 2\n", encoding="utf-8")
        assert tree_hash(repo) != before


class TestStability:
    """Без изменений отпечаток обязан быть тем же — иначе гейт валит всё подряд."""

    def test_hash_is_stable_without_changes(self, repo: Path) -> None:
        assert tree_hash(repo) == tree_hash(repo)

    def test_hash_stable_with_dirty_tree(self, repo: Path) -> None:
        (repo / "code.py").write_text("value = 7\n", encoding="utf-8")
        assert tree_hash(repo) == tree_hash(repo)

    def test_new_file_changes_hash(self, repo: Path) -> None:
        before = tree_hash(repo)
        (repo / "extra.py").write_text("x = 1\n", encoding="utf-8")
        assert tree_hash(repo) != before

    def test_deleted_file_changes_hash(self, repo: Path) -> None:
        before = tree_hash(repo)
        (repo / "code.py").unlink()
        assert tree_hash(repo) != before
