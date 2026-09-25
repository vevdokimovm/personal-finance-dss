"""Гейт: структурные диаграммы не отстают от кода.

🔴 Замер 25.09.2026 (`docs/reports/engineering/diagrams_drifted_from_code.md`):
`06_c4_component` знала 3 роутера из 27 и не знала 20 сервисов, `10_er_database` —
28 таблиц из 31, `14_dependency_graph` — 10 модулей ядра из 22. По диаграммам продукт
выглядел вдвое меньше, чем есть: код прошёл вехи 7 и 8 целиком, а диаграммы остались
на уровне v6.8.0.

Причина системная и того же класса, что весь разбор `gates_that_did_not_run.md`:
**артефакт объявлен актуальным и никем не проверяется**. Диаграмма остаётся валидным
XML и не краснеет ни в одном гейте — «зелёность» означает лишь то, что файл существует.
Узнать об отставании можно единственным способом: сверить содержимое с кодом.

Гейт судит ТОЛЬКО структурные диаграммы — те, чьё содержание однозначно выводится
из дерева исходников. Смысловые (`01_main_pipeline_GOST`, `17_bpmn`, `13_usecase`
и прочие) описывают замысел, а не структуру, и проверке кодом не поддаются.

🔴 Судится ИСТОЧНИК (`.drawio`), а не превью: PNG рендерится только вручную на Mac
(в песочнице CDN Chromium заблокирован), и гейт на превью краснел бы на том,
что машина в CI починить не может.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DIAGRAMS = REPO / "docs/diagrams"


def _text(name: str) -> str:
    path = DIAGRAMS / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _tables() -> list[str]:
    """Имена таблиц из моделей SQLAlchemy."""
    source = (REPO / "app/database/models.py").read_text(encoding="utf-8")
    return sorted(set(re.findall(r'__tablename__\s*=\s*"([a-z_]+)"', source)))


def _routers() -> list[str]:
    """Домены HTTP-слоя: `routes_<домен>.py`."""
    return sorted(p.stem.removeprefix("routes_") for p in (REPO / "app/api").glob("routes_*.py"))


def _core_modules() -> list[str]:
    """Модули математического ядра."""
    return sorted(
        p.stem for p in (REPO / "app/core").glob("*.py") if p.stem != "__init__"
    )


def _missing(names: list[str], diagram: str) -> list[str]:
    haystack = _text(diagram).lower()
    return [name for name in names if name.lower() not in haystack]


class TestErDiagramKnowsEveryTable:
    """Каждая таблица базы обязана быть на ER-диаграмме."""

    def test_diagram_exists(self) -> None:
        assert _text("10_er_database.drawio"), "нет источника ER-диаграммы"

    def test_no_table_is_missing(self) -> None:
        missing = _missing(_tables(), "10_er_database.drawio")
        assert not missing, (
            "ER-диаграмма не знает таблиц, которые есть в коде: "
            + ", ".join(missing)
        )


class TestComponentDiagramKnowsEveryDomain:
    """Каждый роутер и сервис обязан быть на диаграмме компонентов."""

    def test_no_router_is_missing(self) -> None:
        missing = _missing(_routers(), "06_c4_component.drawio")
        assert not missing, (
            "C4-component не знает роутеров: " + ", ".join(missing)
        )

    def test_no_core_module_is_missing(self) -> None:
        missing = _missing(_core_modules(), "06_c4_component.drawio")
        assert not missing, (
            "C4-component не знает модулей ядра: " + ", ".join(missing)
        )


class TestDependencyGraphKnowsEveryCoreModule:
    """Граф зависимостей ядра обязан содержать все его модули."""

    def test_no_core_module_is_missing(self) -> None:
        missing = _missing(_core_modules(), "14_dependency_graph.drawio")
        assert not missing, (
            "граф зависимостей не знает модулей ядра: " + ", ".join(missing)
        )


class TestGateItself:
    """Проверки самого гейта: он обязан видеть реальные сущности, а не пустоту."""

    @pytest.mark.parametrize("extractor", [_tables, _routers, _core_modules])
    def test_extractors_find_something(self, extractor) -> None:
        found = extractor()
        assert len(found) > 5, (
            f"{extractor.__name__} вернул {found} — гейт судил бы пустой список "
            "и был бы зелёным всегда"
        )

    def test_missing_detects_absence(self) -> None:
        assert _missing(["заведомо-отсутствующая-сущность"], "10_er_database.drawio")


class TestNoDeadTechnologyOnDiagrams:
    """🔴 Диаграмма не вправе упоминать то, чего в коде больше нет.

    Замер 25.09.2026: `05_c4_container` десять версий описывала фронт как
    «Jinja2 + ванильный JS, 7 страниц» — после того, как Jinja была снесена целиком
    (веха 8), а приложение стало отдавать собранный React. `15_forecast_GOST`
    содержала «Этап 2. Оценка тренда b», отменённый каноном v3.10.0 по замеру Г43
    на 300 портретах (ошибка 0.606 против 0.205 у простого среднего).

    Это опаснее устаревшего списка сущностей: список молчит о новом, а мёртвая
    технология УТВЕРЖДАЕТ неверное. Читающий поймёт архитектуру и модель неправильно
    и будет уверен, что понял правильно.
    """

    # Признак и условие, при котором он считается мёртвым.
    DEAD = {
        "Jinja": "app/templates",  # снесён вместе с каталогом шаблонов
    }

    def _sources(self) -> list[Path]:
        return sorted(DIAGRAMS.glob("*.drawio")) + sorted((DIAGRAMS / "src").glob("*.dot"))

    def test_dead_technology_is_not_mentioned(self) -> None:
        offenders: list[str] = []
        for token, evidence in self.DEAD.items():
            if (REPO / evidence).exists():
                continue  # технология жива — упоминать можно
            for path in self._sources():
                if token.lower() in path.read_text(encoding="utf-8").lower():
                    offenders.append(f"{path.name} упоминает {token}")
        assert not offenders, (
            "диаграммы описывают снесённую технологию: " + "; ".join(offenders)
        )

    def test_forecast_diagram_has_no_trend(self) -> None:
        """Канон v3.10.0 §15: точечный прогноз плоский, компоненты тренда нет."""
        source = (DIAGRAMS / "src/15_forecast_GOST.dot").read_text(encoding="utf-8")
        assert "тренда НЕТ" in source, (
            "схема прогноза обязана называть отсутствие тренда явно: именно здесь "
            "она десять версий описывала отменённый алгоритм"
        )

    def test_every_authored_diagram_has_a_source(self) -> None:
        """У каждого превью смысловой диаграммы есть источник, который его родил."""
        authored = ("01_main_pipeline_GOST", "04_c4_context", "05_c4_container",
                    "08_sequence_import", "11_uml_class", "13_usecase",
                    "15_forecast_GOST")
        for name in authored:
            assert (DIAGRAMS / f"src/{name}.dot").exists(), f"нет источника {name}.dot"
            assert (DIAGRAMS / f"{name}.drawio.png").exists(), f"нет превью {name}"


class TestEveryDiagramNamesItsVersion:
    """🔴 Диаграмма обязана называть версию, которой соответствует.

    Требование владельца 25.09.2026: «пиши какой версии они соответствуют».
    Без подписи свежая диаграмма неотличима от отставшей на десять версий —
    ровно та слепота, из-за которой `05_c4_container` описывала снесённую Jinja,
    а `15_forecast_GOST` — отменённый каноном тренд.
    """

    def test_authored_sources_carry_the_stamp(self) -> None:
        from tools.diagrams.generate import code_version

        version = code_version()
        naked = [
            path.name for path in sorted((DIAGRAMS / "src").glob("*.dot"))
            if f"v{version}" not in path.read_text(encoding="utf-8")
        ]
        assert not naked, (
            "диаграммы не называют версию, которой соответствуют: " + ", ".join(naked)
        )

    def test_canon_version_is_read_from_the_model(self) -> None:
        """Версия канона берётся из `docs/math_model.md`, а не вписана руками."""
        from tools.diagrams.generate import canon_version

        assert canon_version() != "?", "версия канона не читается из math_model.md"
