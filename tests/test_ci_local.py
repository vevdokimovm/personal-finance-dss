"""Гейты CI прогоняются локально ДО отгрузки — из того же файла, что читает GitHub.

## Зачем

Ожидание вердикта GitHub стоило суток и трёх ложных отчётов: прогон по тегу идёт
20–30 минут, а узнать результат хочется до того, как тег поставлен. Владелец сказал
это прямо: «можешь прогонять гейты гита сразу здесь перед деплоем? чтобы не ждать
гита а здесь сразу прогнать и точно знать результат».

🔴 **Ключевое требование — не «похожие команды», а ТЕ ЖЕ.** Список шагов читается
из `.github/workflows/ci.yml`; копия команд в скрипте разошлась бы с оригиналом молча,
и локальный прогон стал бы зелёным при красном CI — ровно тот класс ошибки, который
этот инструмент и должен закрыть (`docs/reports/incidents/ci_red_on_tags_for_a_month.md`).

## Чего инструмент НЕ делает

Шаги, у которых нет `run:` (actions GitHub — checkout, setup-python, setup-node),
локально не исполняются и помечаются пропущенными: их эквивалент — сама рабочая станция.
"""
from __future__ import annotations

from pathlib import Path

from tools.ci_local import Step, is_install, jobs_with_steps, runnable, WORKFLOW

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestStepsComeFromTheWorkflow:
    """Команды берутся из файла CI, а не из копии в скрипте."""

    def test_workflow_file_exists(self) -> None:
        assert WORKFLOW.exists(), f"нет файла воркфлоу: {WORKFLOW}"

    def test_known_jobs_are_found(self) -> None:
        names = set(jobs_with_steps())
        for expected in ("preflight", "core", "fast", "lint", "frontend", "full"):
            assert expected in names, f"джоба {expected} не распознана в ci.yml"

    def test_steps_carry_real_commands(self) -> None:
        """У шага с `run:` команда не пустая и это строка из воркфлоу."""
        steps = jobs_with_steps()["preflight"]
        commands = [s.run for s in steps if s.run]
        assert any("tools.preflight" in c for c in commands), commands

    def test_parser_reacts_to_the_file(self, tmp_path: Path) -> None:
        """🔴 Мутация: подменить воркфлоу — список джоб обязан измениться.

        Без этой проверки парсер мог бы возвращать константу и выглядеть работающим.
        """
        fake = tmp_path / "ci.yml"
        fake.write_text(
            "jobs:\n  only_one:\n    steps:\n      - name: x\n        run: echo 1\n",
            encoding="utf-8",
        )
        assert set(jobs_with_steps(fake)) == {"only_one"}


class TestRunnableFilter:
    """Локально исполняются только шаги с командой."""

    def test_action_steps_are_not_runnable(self) -> None:
        assert not runnable(Step(name="Run actions/checkout@v4", run=None, workdir=None))

    def test_command_steps_are_runnable(self) -> None:
        assert runnable(Step(name="Тесты", run="pytest -q", workdir=None))

    def test_step_keeps_working_directory(self) -> None:
        """`working-directory` из воркфлоу обязан доехать: фронтовые шаги живут в `frontend/`."""
        steps = jobs_with_steps()["frontend"]
        with_dir = [s for s in steps if s.workdir]
        assert with_dir, "ни один шаг фронта не несёт working-directory"
        assert all(s.workdir == "frontend" for s in with_dir)


class TestEnvironmentSteps:
    """🔴 Шаги установки окружения локально не гоняются, и это названо.

    На раннере окружение чистое, у нас собрано: переустановка на каждый прогон —
    минуты впустую и риск переписать рабочий венв. Пропуск включается обратно
    флагом `--with-install`.
    """

    def test_pip_install_is_an_install_step(self) -> None:
        assert is_install(Step(name="deps", run="pip install -r requirements.txt", workdir=None))

    def test_npm_ci_is_an_install_step(self) -> None:
        assert is_install(Step(name="deps", run="npm ci", workdir="frontend"))

    def test_playwright_install_is_NOT_skipped(self) -> None:
        """🔴 Установка браузеров — предусловие проверки, а не обустройство окружения.

        Первая редакция фильтра пропускала её, фронтовые E2E шли без firefox и webkit
        и дали **100 падений** там, где CI зелёный. Ложное красное учит не доверять
        инструменту — это дороже сэкономленных минут.
        """
        assert not is_install(
            Step(name="browsers", run="npx playwright install --with-deps firefox", workdir=None)
        )

    def test_check_steps_are_not_install(self) -> None:
        for command in ("pytest -q", "flake8 .", "mypy app", "npm run build"):
            assert not is_install(Step(name="x", run=command, workdir=None)), command
