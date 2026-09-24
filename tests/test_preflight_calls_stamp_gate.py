"""Гейт: `preflight` действительно ЗОВЁТ проверку следа локального прогона.

🔴 Найдено 25.09.2026. `ci_local_failures` была написана в v9.13.14 вместе с шестью
тестами — и не вызывалась из `run()` ни разу. Тесты звали функцию напрямую, поэтому
зелёное покрытие означало «функция работает», а не «правило исполняется». Полтора
батча подряд `preflight` печатал «механические проверки: чисто» при КРАСНОМ следе,
снятом на другом дереве.

Класс ошибки — «проверка написана, но не подключена». Он не ловится ни покрытием,
ни тестами самой функции: ловится только проверкой ФАКТА ВЫЗОВА из `run()`.
Поэтому тесты подменяют гейт и смотрят, дошёл ли его вердикт до вывода и до кода
возврата, а не читают исходный текст модуля.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import preflight

REPO = Path(__file__).resolve().parents[1]


class TestStampGateIsWired:
    """Вердикт гейта обязан доходить до вывода и до кода возврата `preflight`."""

    def test_gate_is_called(self, monkeypatch, capsys) -> None:
        calls: list[Path] = []

        def spy(repo: Path, tree: str, *args, **kwargs) -> list[str]:
            calls.append(repo)
            return []

        monkeypatch.setattr(preflight, "ci_local_failures", spy)
        preflight.run(REPO)
        capsys.readouterr()
        assert calls, "preflight не зовёт гейт следа — правило не исполняется"

    def test_gate_receives_the_real_tree_hash(self, monkeypatch, capsys) -> None:
        """Отпечаток обязан считаться по факту, а не подставляться из следа."""
        from tools.ci_local import tree_hash

        seen: list[str] = []
        monkeypatch.setattr(
            preflight, "ci_local_failures",
            lambda repo, tree, *a, **k: seen.append(tree) or [],
        )
        preflight.run(REPO)
        capsys.readouterr()
        assert seen and seen[0] == tree_hash(REPO)

    def test_red_verdict_reaches_output(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            preflight, "ci_local_failures",
            lambda *a, **k: ["локальный прогон гейтов КРАСНЫЙ: шаг X"],
        )
        preflight.run(REPO)
        assert "КРАСНЫЙ" in capsys.readouterr().out

    def test_red_verdict_makes_exit_code_nonzero(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            preflight, "ci_local_failures",
            lambda *a, **k: ["локальный прогон гейтов КРАСНЫЙ"],
        )
        code = preflight.run(REPO)
        capsys.readouterr()
        assert code != 0, "красный след обязан валить батч, а не печататься мимо"

    def test_green_gate_adds_no_noise(self, monkeypatch, capsys) -> None:
        """Зелёный след не должен добавлять шума — иначе гейт заглушат как ложный."""
        monkeypatch.setattr(preflight, "ci_local_failures", lambda *a, **k: [])
        preflight.run(REPO)
        assert "ci_local_last_run.json" not in capsys.readouterr().out


class TestGateStaysLocal:
    """На раннере следа нет и быть не может — там гейт обязан молчать."""

    @pytest.mark.parametrize("variable", ["CI", "GITHUB_ACTIONS"])
    def test_gate_is_silent_in_ci(self, monkeypatch, variable: str) -> None:
        monkeypatch.setenv(variable, "true")
        assert preflight.ci_local_failures(REPO, "любой-отпечаток") == []
