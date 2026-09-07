"""CI-workflow разбирается и делает шаги в исполнимом порядке (v9.1.0).

## Почему гейт на самом workflow

Прогоны CI падали месяцами, и разбор 05.09.2026 нашёл три причины — все три
**невидимы локально**:

1. **`docs/ROADMAP.md` ссылался на `frontend/dist/index.html`.** У того, кто правил,
   фронт собран; `dist/` в `.gitignore`, значит на чистом клоне файла нет, и гейт
   ссылок валил `preflight` и `fast`.
2. **`BudgetStatus` в снимке контракта отставал от схемы.** `tsc` в CI падал
   на `household_id`, локально молчал — клиент был собран из свежего снимка.
3. **`full`-тир запускал E2E ДО сборки фронта.** `frontend/dist` не существовал,
   сервер отдавал 404 на `/`, проверка готовности не проходила — и весь тир падал
   с `E2E live server failed to start`, без единой строки о причине (вывод сервера
   уходил в `/dev/null`).

Общее у всех трёх: **локальная машина находится в состоянии, которого нет у CI**.
Ни один прогон «у себя» этого не покажет, потому что путь «клонировал → собрал»
целиком не проходится (тот же класс, что PIT-020).

🔴 **Плюс сам YAML.** Двоеточие в незакавыченном имени шага ломает разбор — это
поймалось только запуском парсера. Workflow, который не разбирается, не запускает
ни одной проверки: зелёного нет, красного тоже, а причина — знак препинания.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _step_names(job: str) -> list[str]:
    return [step.get("name", "") for step in _workflow()["jobs"][job]["steps"]]


def _step_commands(job: str) -> list[str]:
    return [step.get("run", "") for step in _workflow()["jobs"][job]["steps"]]


def test_workflow_is_valid_yaml() -> None:
    """🔴 Файл вообще разбирается.

    Двоеточие в незакавыченном скаляре читается как ключ отображения, и весь
    workflow становится недействительным: проверки не запускаются ни одной,
    а причина — знак препинания в русском названии шага.
    """
    spec = _workflow()
    assert isinstance(spec, dict) and spec.get("jobs"), "workflow не разобрался в словарь"


@pytest.mark.parametrize("job", ["fast", "full"])
def test_frontend_is_built_before_python_tests(job: str) -> None:
    """🔴 Сборка фронта идёт ДО pytest в каждой джобе, которая гоняет E2E.

    `tests/e2e/conftest.py` поднимает живой сервер и ждёт ответа на `/`. Без
    `frontend/dist` сервер отдаёт 404, готовность не наступает — и тир падает
    с сообщением, по которому причину не определить.

    В `fast` порядок был верным и объяснён комментарием; в `full` то же правило
    не доехало (§7 автономного стандарта: правило, дошедшее не всюду, —
    это расхождение, и живёт оно тем дольше, чем увереннее звучит оригинал).
    """
    commands = _step_commands(job)
    build_at = next(
        (i for i, cmd in enumerate(commands) if "npm run build" in cmd), None
    )
    pytest_at = next(
        (i for i, cmd in enumerate(commands) if cmd.strip().startswith("pytest")
         or "coverage run -m pytest" in cmd),
        None,
    )
    if pytest_at is None:
        pytest.skip(f"джоба {job} не запускает pytest")
    assert build_at is not None, (
        f"джоба {job} гоняет pytest, но фронт не собирает — E2E упрётся в 404"
    )
    assert build_at < pytest_at, (
        f"в джобе {job} сборка фронта (шаг {build_at + 1}) идёт ПОСЛЕ pytest "
        f"(шаг {pytest_at + 1}) — сервер E2E отдаст 404 и тир упадёт"
    )


def test_step_names_do_not_break_yaml() -> None:
    """Имена шагов не содержат конструкций, ломающих разбор.

    Проверка кажется избыточной рядом с `test_workflow_is_valid_yaml` и оставлена
    намеренно: она падает с ИМЕНЕМ шага, а не общим «файл не разобрался», и по ней
    сразу видно, что править.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    offenders = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("- name:") or stripped.startswith("name:")):
            continue
        value = stripped.split("name:", 1)[1]
        if ": " in value and not value.strip().startswith(('"', "'")):
            offenders.append(stripped)
    assert not offenders, (
        "имя шага содержит «: » и не закавычено — YAML прочтёт это как ключ:\n  "
        + "\n  ".join(offenders)
    )


def test_blocking_jobs_are_not_silenced() -> None:
    """🔴 Блокирующие джобы не помечены `continue-on-error`.

    До v8.50.0 линтеры стояли с этим флагом целиком, то есть красное ничего
    не значило. Информационным осознанно оставлен только `pylint`.
    """
    jobs = _workflow()["jobs"]
    silenced = [
        name for name, data in jobs.items()
        if data.get("continue-on-error") and name != "pylint"
    ]
    assert not silenced, (
        f"джобы молчат об ошибках: {silenced} — красное в них ничего не значит"
    )


class TestCoverageGatesAreSymmetric:
    """🔴 Обе половины продукта держат одну планку — 90 % (решение владельца 06.09.2026).

    **Что было.** Бэкенд шёл через `coverage report` с `fail_under = 90` в `.coveragerc`;
    фронт гонял `npm test` — голый vitest, без измерения покрытия вовсе. Половина продукта
    держала планку, вторая не измерялась, и разницу не было видно **ниоткуда**: обе джобы
    зелёные, обе называются «тесты».

    Дословно владелец: *«тогда для бэкенда точно такие же требования как и для фронта
    покрытие должно быть больше или равно 90%»* и *«сделай симметрично»*.

    **Почему гейт, а не разовая правка.** Пороги живут в разных файлах и на разных языках:
    `.coveragerc` у Python, `vite.config.ts` у фронта. Поднять один и забыть про второй —
    вопрос одной невнимательной правки, и расхождение снова станет невидимым.
    Тот же класс, что §7 автономного стандарта: правило, дошедшее не всюду, — это
    не правило, а расхождение.
    """

    BACKEND_THRESHOLD = 90

    def test_backend_keeps_its_threshold(self) -> None:
        """Порог бэкенда на месте и равен 90."""
        text = (REPO_ROOT / ".coveragerc").read_text(encoding="utf-8")
        match = re.search(r"^fail_under\s*=\s*(\d+)", text, re.MULTILINE)
        assert match, "в .coveragerc нет fail_under — гейт покрытия бэкенда снят"
        assert int(match.group(1)) == self.BACKEND_THRESHOLD

    def test_frontend_declares_the_same_threshold(self) -> None:
        """🔴 Порог фронта объявлен и совпадает с бэкендом по ВСЕМ четырём метрикам.

        Одних строк мало: `functions` и `branches` расходятся со строками сильнее всего,
        и покрытие, зелёное по строкам при 70 % по веткам, скрывает необработанные случаи.
        """
        text = (REPO_ROOT / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
        found = {
            metric: int(value)
            for metric, value in re.findall(
                r"(lines|statements|functions|branches):\s*(\d+)", text
            )
        }
        missing = [m for m in ("lines", "statements", "functions", "branches") if m not in found]
        assert not missing, f"во фронте не объявлены пороги: {missing}"
        wrong = {m: v for m, v in found.items() if v != self.BACKEND_THRESHOLD}
        assert not wrong, (
            f"пороги фронта разошлись с бэкендом ({self.BACKEND_THRESHOLD}): {wrong}"
        )

    def test_ci_actually_measures_frontend_coverage(self) -> None:
        """🔴 Объявленный порог ничего не значит, если CI гоняет тесты без покрытия.

        Ровно это и было: `thresholds` можно объявить и не запускать `--coverage` —
        конфиг выглядит строгим, а джоба проходит всегда. Проверяется КОМАНДА в workflow,
        а не намерение в конфиге.
        """
        commands = " ".join(_step_commands("frontend"))
        assert "coverage" in commands, (
            "джоба фронта не измеряет покрытие — порог в vite.config.ts не применяется"
        )


class TestCoreIsItsOwnContour:
    """🔴 Ядро модели — третья сущность, и у неё свой контур (решение владельца 06.09.2026).

    Дословно: *«есть тесты бэк, фронт — может сделать и тесты ядра математического?
    как будто это три сущности разные»*.

    **Отличие по цене ошибки, а не по организации кода:**

    | что сломалось | как выглядит | заметит ли человек |
    |---|---|---|
    | бэкенд | 500 | да, и повторит |
    | фронт | пустой экран | да, и пожалуется |
    | **ядро** | **неверный совет о деньгах** | **нет** |

    Третий случай не даёт ни отказа, ни жалобы: продукт работает, числа правдоподобны,
    а человек гасит не тот долг. Отсюда порог **95 %** против общих 90: непокрытая ветка
    в роутере — необработанный запрос, непокрытая ветка в ядре — расчётный путь, по которому
    никто не проходил, и его результат некому оспорить.

    **Почему гейт, а не «мы помним».** Три порога живут в трёх файлах на двух языках
    (`.coveragerc`, `.coveragerc.core`, `vite.config.ts`). Снять один — вопрос одной
    невнимательной правки, и расхождение станет невидимым: джоба продолжит быть зелёной,
    потому что перестанет проверять.
    """

    CORE_THRESHOLD = 95

    def test_core_config_exists_and_targets_core_only(self) -> None:
        """Конфиг ядра существует и считает покрытие ИМЕННО ядра.

        🔴 `source = app` вместо `app/core` дал бы тот же процент, что у общего прогона,
        и порог 95 стал бы недостижимым по причине, не связанной с ядром, — его бы сняли.
        """
        config = REPO_ROOT / ".coveragerc.core"
        assert config.exists(), "нет .coveragerc.core — контур ядра не заведён"
        text = config.read_text(encoding="utf-8")
        assert re.search(r"^source\s*=\s*app/core\s*$", text, re.MULTILINE), (
            "конфиг ядра считает покрытие не по app/core — порог перестанет означать ядро"
        )

    def test_core_threshold_is_stricter_than_backend(self) -> None:
        """Порог ядра выше общего — иначе отдельный контур ничего не добавляет."""
        core = re.search(
            r"^fail_under\s*=\s*(\d+)",
            (REPO_ROOT / ".coveragerc.core").read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        backend = re.search(
            r"^fail_under\s*=\s*(\d+)",
            (REPO_ROOT / ".coveragerc").read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        assert core and backend
        assert int(core.group(1)) == self.CORE_THRESHOLD
        assert int(core.group(1)) > int(backend.group(1)), (
            "порог ядра не строже общего — отдельный контур не даёт ничего, "
            "кроме лишней джобы"
        )

    def test_ci_runs_the_core_job(self) -> None:
        """🔴 Порог, который не гоняется, — это комментарий.

        Проверяется наличие джобы И команды с её конфигом: объявить конфиг и не
        применить его — ровно тот случай, что был у фронта до v9.3.0.
        """
        jobs = _workflow()["jobs"]
        assert "core" in jobs, "в CI нет джобы ядра — порог 95 % нигде не применяется"
        commands = " ".join(_step_commands("core"))
        assert ".coveragerc.core" in commands, (
            "джоба ядра не использует свой конфиг — считается общее покрытие"
        )
        assert "coverage report" in commands, (
            "джоба ядра не проверяет порог: `coverage run` без `report` ничего не валит"
        )

    def test_core_marker_is_declared(self) -> None:
        """Маркер `core` объявлен — иначе `--strict-markers` уронит любой прогон."""
        assert "core:" in (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")
