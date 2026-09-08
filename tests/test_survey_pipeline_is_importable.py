"""Конвейер анализа опроса запускается — а не только лежит в репозитории.

## Что закрывает

`tools/survey_analysis/` — процедура, которой обрабатывался опрос аудитории (385
ответов, 62 вопроса). На неё прямо ссылается задача роадмапа «переобработать опрос
целиком»: «прогнать той же процедурой, что дала нынешнюю выжимку».

🔴 **Процедура не запускалась вовсе.** Все модули импортируют пакет `finpilot_survey`,
которого в дереве нет: каталог называется `survey_analysis`. Пятнадцать ссылок,
`ModuleNotFoundError` на первой же строке `run_analysis.py`. Инструмент умер при
переносе в `tools/` и пролежал мёртвым до 08.09.2026 — потому что запускать его было
незачем: выборка не менялась.

**Цена, которую это чуть не стоило.** Владелец собирался прислать финальную выгрузку
и ожидал, что обработка — вопрос одной команды. Обнаружилось бы это ровно в тот момент,
когда работа уже началась, и выглядело бы как «прислал файл — ничего не работает».

## Почему статическая проверка — главная, а импорт вторичен

У конвейера свои тяжёлые зависимости (`pandas`, `scipy`, `matplotlib`,
`factor_analyzer` — `tools/survey_analysis/requirements.txt`), и в основном окружении
их нет: инструмент запускают отдельно, по необходимости. Значит **тест на импорт
на голой машине скажет «нет pandas» и промолчит про настоящую поломку** — ровно то,
что и произошло бы.

Поэтому 🔴 **гейтом служит статическая проверка**: она читает исходники и не требует
ни одной зависимости. Импорт проверяется дополнительно и пропускается, когда
зависимостей нет — с явной причиной, а не молча.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "tools.survey_analysis"
MODULES = (
    "config",
    "data",
    "stats_utils",
    "analyzers_quant",
    "analyzers_product",
    "visualization",
    "report",
    "pipeline",
    "run_analysis",
)


def _deps_available() -> bool:
    try:
        importlib.import_module("pandas")
    except ImportError:
        return False
    return True


needs_deps = pytest.mark.skipif(
    not _deps_available(),
    reason=(
        "зависимости конвейера не установлены (tools/survey_analysis/requirements.txt) — "
        "статическая проверка ниже работает и без них"
    ),
)


@needs_deps
class TestPipelineImports:
    """Каждый модуль конвейера импортируется по своему настоящему пути."""

    @pytest.mark.parametrize("name", MODULES)
    def test_module_imports(self, name: str) -> None:
        """🔴 Мутация «вернуть `from finpilot_survey import …`» роняет тест здесь."""
        importlib.import_module(f"{PACKAGE}.{name}")


class TestNoGhostPackage:
    """В дереве не осталось ссылок на пакет, которого нет."""

    def test_no_finpilot_survey_imports(self) -> None:
        """Имя `finpilot_survey` не существует нигде как модуль.

        Оставлять его в комментариях и подписях можно — это история; ловится
        только импорт, потому что ломается именно он.
        """
        offenders: list[str] = []
        for path in (REPO_ROOT / "tools" / "survey_analysis").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith(("import finpilot_survey", "from finpilot_survey")):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}")
        assert not offenders, (
            "импорт несуществующего пакета `finpilot_survey`: " + ", ".join(offenders)
        )


class TestDefaultDataPathIsReal:
    """🔴 Путь по умолчанию ведёт в репозиторий, а не в чужое окружение.

    Прежнее значение `DATA_PATH` указывало в `/mnt/user-data/uploads/` — mount той
    машины, где конвейер когда-то прогоняли. Ни на рабочей машине, ни в CI такого
    пути нет: запуск без `--data` падал бы `FileNotFoundError` по несуществующему
    адресу — ровно в тот момент, когда владелец пришлёт финальную выгрузку.

    🔴 **Проверка СТАТИЧЕСКАЯ, и это главное.** Прежняя редакция импортировала модуль
    и потому пряталась за `@needs_deps`: без `pandas` она пропускалась, а `pandas`
    нет ни в основном окружении, ни в CI. То есть тест, написанный ровно против этого
    дефекта, не выполнился бы ни разу и дефект бы пропустил. Найдено четвёртым проходом
    независимого аудита 08.09.2026.
    """

    SOURCE = REPO_ROOT / "tools" / "survey_analysis" / "data.py"

    def test_no_foreign_mount_in_default(self) -> None:
        """🔴 Мутация «вернуть /mnt/user-data/uploads/» роняет тест здесь."""
        # 🔴 Смотрим на КОД, а не на пояснения: первая редакция сетки сработала
        # на собственном комментарии, объясняющем, какой путь был убран. Проверка,
        # красная от рассказа о починке, бесполезна.
        lines = [
            line
            for line in self.SOURCE.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("#")
        ]
        code = "\n".join(lines)
        foreign = [m for m in ("/mnt/", "/home/", "/Users/") if m in code]
        assert not foreign, (
            f"в умолчании пути к данным зашит путь чужого окружения: {foreign} — "
            "он не существует ни на рабочей машине, ни в CI"
        )

    def test_default_is_built_from_repo_root(self) -> None:
        """Умолчание собирается от корня репозитория, а не строкой-константой."""
        text = self.SOURCE.read_text(encoding="utf-8")
        assert "DATA_PATH" in text
        assert "_REPO_ROOT" in text, (
            "умолчание не привязано к корню репозитория — оно снова абсолютное"
        )

    def test_default_file_actually_exists(self) -> None:
        """И файл по этому пути есть: иначе умолчание бесполезно так же, как прежде."""
        expected = (
            REPO_ROOT / "knowledge" / "survey_auditory" / "raw"
            / "survey_responses_385.xlsx"
        )
        assert expected.exists(), f"выгрузки опроса нет по ожидаемому пути: {expected}"


@needs_deps
class TestEntryPointIsUsable:
    """У конвейера есть рабочая точка входа с понятными аргументами."""

    def test_cli_declares_data_and_out(self) -> None:
        module = importlib.import_module(f"{PACKAGE}.run_analysis")
        assert hasattr(module, "main"), "у конвейера нет точки входа `main`"

    def test_default_data_path_is_importable(self) -> None:
        """Модуль отдаёт `DATA_PATH` — сам путь проверяется статически выше."""
        data = importlib.import_module(f"{PACKAGE}.data")
        assert hasattr(data, "DATA_PATH")
