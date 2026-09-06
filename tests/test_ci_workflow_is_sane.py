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
