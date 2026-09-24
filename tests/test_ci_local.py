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

from tools.ci_local import Step, _run, is_install, jobs_with_steps, runnable, WORKFLOW

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

    def test_step_that_installs_AND_checks_is_not_skipped(self) -> None:
        """🔴 Шаг «поставить инструмент и тут же проверить» — это ПРОВЕРКА, не установка.

        Второй случай того же класса, что `playwright install`, и дороже него.
        Шаги bandit, pip-audit и нагрузочного smoke записаны в воркфлоу как две
        строки: `pip install -q <инструмент>` и следом сама проверка. Регулярка
        видела первую строку и выкидывала ВЕСЬ шаг — три проверки не исполнялись
        локально ни разу, а прогон печатал «ЗЕЛЕНО». В CI они исполняются и краснеют:
        инструмент врал ровно в ту сторону, против которой заведён.
        Правило: пропускаем шаг, только если УСТАНОВКА — все его команды.
        """
        for command in (
            "pip install -q bandit\nbandit -q -r app -ll",
            "pip install -q pip-audit\npip-audit -r requirements.txt",
            "pip install -q locust\nlocust -f loadtest/locustfile.py --headless -t 30s",
        ):
            assert not is_install(Step(name="x", run=command, workdir=None)), command

    def test_pure_install_step_with_several_lines_is_skipped(self) -> None:
        """Шаг, где установка — ВСЕ строки, по-прежнему пропускается."""
        assert is_install(
            Step(
                name="deps",
                run="python -m pip install --upgrade pip\npip install -r requirements.txt",
                workdir=None,
            )
        )

    def test_check_steps_are_not_install(self) -> None:
        for command in ("pytest -q", "flake8 .", "mypy app", "npm run build"):
            assert not is_install(Step(name="x", run=command, workdir=None)), command


class TestStepFailsLikeGitHub:
    """🔴 Шаг обязан падать на ПЕРВОЙ упавшей команде, как у GitHub.

    GitHub исполняет блок `run:` через `bash --noprofile --norc -eo pipefail`.
    Флаг `-e` валит шаг на первой же неудаче. Локальный прогон звал `shell=True`,
    то есть `/bin/sh` БЕЗ `-e`, и код возврата шага равнялся коду ПОСЛЕДНЕЙ команды.

    Цена ошибки измерена: шаг «Тесты + покрытие ядра» — это `coverage run -m pytest`
    и следом `coverage report`. Падение pytest (`1 failed, 2436 passed`) исчезало
    бесследно, потому что `coverage report` проходил порог и возвращал ноль. Локальный
    прогон печатал «ЗЕЛЕНО» на упавших тестах — ровно та ложь, против которой
    инструмент заведён, и ровно то, что владелец видел как «локально зелено,
    а в гите упало больше тестов».
    """

    def test_first_failing_command_fails_the_step(self, tmp_path: Path) -> None:
        step = Step(name="две команды", run="false\ntrue", workdir=None)
        ok, _ = _run(step, tmp_path)
        assert not ok, "падение первой команды обязано валить шаг, как `bash -e`"

    def test_all_green_commands_pass(self, tmp_path: Path) -> None:
        step = Step(name="две команды", run="true\ntrue", workdir=None)
        ok, _ = _run(step, tmp_path)
        assert ok

    def test_pipeline_failure_is_caught(self, tmp_path: Path) -> None:
        """`pipefail`: падение слева от пайпа не прячется за успехом справа."""
        step = Step(name="пайп", run="false | cat", workdir=None)
        ok, _ = _run(step, tmp_path)
        assert not ok, "нужен `pipefail`, иначе падение в пайпе теряется"
