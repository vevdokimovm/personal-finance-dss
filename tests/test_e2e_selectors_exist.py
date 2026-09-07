"""Селекторы E2E существуют во фронте (v9.4.0).

## 🔴 Что нашлось при заходе на пункт E роадмапа

**38 селекторов из 38** в браузерных тестах отсутствуют во `frontend/src`. Весь E2E-контур
написан под **Jinja-вёрстку**, снесённую в вехе 8: `auth.js`, `#auth-modal` в `base.html`,
`#rt-value`, `#planning-form`. Каталога `app/templates` не существует вовсе.

**И CI при этом зелёный** — джоба `fast` гоняет `pytest -m e2e --browser chromium`.
Значит единственный контур, который смотрит на продукт глазами пользователя,
не смотрит никуда, а зелёный CI это скрывает.

## Почему проверка статическая, а не «прогнать браузер»

Браузерный прогон стоит минут и требует поднятого сервера, собранного фронта
и установленного chromium — то есть падает по десятку причин, к предмету отношения
не имеющих. Расхождение «тест ищет `#foo`, во фронте `#foo` нет» видно **из исходников**,
без единого запуска, и видно **сразу после правки вёрстки**, а не когда до E2E дойдут руки.

🔴 **Это тот же класс, что `test_spa_navigation_reachability.py`**: там экран обязан
попасть в навигацию, здесь селектор теста обязан существовать в разметке. Оба ловят
разрыв между двумя половинами продукта, который каждая половина по отдельности
считает своим нормальным состоянием.

## Что проверка НЕ ловит — назвать честно

Существование `id` в исходниках не значит, что элемент отрисован: он может быть внутри
ветки, до которой сценарий не доходит. Обратное тоже верно — тест может искать элемент
по роли или тексту, и такие обращения здесь не видны. Гейт закрывает **самый грубый**
случай — обращение к тому, чего в коде нет вообще, — и именно он и случился.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
E2E_DIR = REPO_ROOT / "tests" / "e2e"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

# Селекторы, принадлежащие браузеру или служебной разметке, а не нашим компонентам.
EXTERNAL_IDS = frozenset({"root", "app"})


def _frontend_blob() -> str:
    parts = []
    for path in FRONTEND_SRC.rglob("*"):
        if path.suffix not in {".tsx", ".ts", ".html", ".css"}:
            continue
        if "generated" in path.parts or path.name.endswith(".test.tsx"):
            continue
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    index = REPO_ROOT / "frontend" / "index.html"
    if index.exists():
        parts.append(index.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def _ids_used_by(test_file: Path) -> set[str]:
    """`id`-селекторы, которые тест ищет в странице.

    Ищем строковые литералы вида `"#some-id"` — так их пишет Playwright
    (`page.locator("#goal-name")`) и так же они попадают в `wait_for_selector`.
    """
    text = test_file.read_text(encoding="utf-8")
    return set(re.findall(r'"#([a-zA-Z][\w-]*)"', text))


def _e2e_files() -> list[Path]:
    return sorted(E2E_DIR.glob("test_*.py"))


class TestE2ESelectorsAreReal:
    """Каждый `id`, который ищет браузерный тест, есть в разметке фронта."""

    @pytest.mark.parametrize("test_file", _e2e_files(), ids=lambda p: p.name)
    def test_every_selector_exists_in_frontend(self, test_file: Path) -> None:
        """🔴 Тест, ищущий несуществующий элемент, не проверяет ничего.

        Мутация: переименовать `id` в компоненте и не поправить тест — падает здесь,
        а не через полгода, когда кто-то заметит, что E2E молчит.
        """
        used = _ids_used_by(test_file) - EXTERNAL_IDS
        if not used:
            pytest.skip("тест не обращается к элементам по id")

        blob = _frontend_blob()
        missing = sorted(
            selector
            for selector in used
            if f'"{selector}"' not in blob and f"id={selector}" not in blob
        )
        assert not missing, (
            f"{test_file.name} ищет элементы, которых нет во фронте: {missing}. "
            "Либо разметка переименована и тест не поправлен, либо тест написан "
            "под интерфейс, которого больше не существует."
        )


class TestGateItselfWorks:
    """Проверка находит то, ради чего написана."""

    def test_finds_selectors_in_playwright_syntax(self, tmp_path: Path) -> None:
        """Разбор достаёт `id` из обычного вызова локатора."""
        sample = tmp_path / "test_sample.py"
        sample.write_text('page.locator("#goal-name").fill("x")', encoding="utf-8")
        assert _ids_used_by(sample) == {"goal-name"}

    def test_ignores_css_classes_and_roles(self, tmp_path: Path) -> None:
        """Классы и роли — не наш предмет: они не обязаны совпадать буквально."""
        sample = tmp_path / "test_sample.py"
        sample.write_text(
            'page.locator(".fp-panel").click()\npage.get_by_role("button")',
            encoding="utf-8",
        )
        assert _ids_used_by(sample) == set()

    def test_frontend_blob_is_not_empty(self) -> None:
        """🔴 Пустая выборка сделала бы гейт зелёным при любом состоянии тестов.

        Проверка ищет отсутствие подстроки; если искать не в чем, «не найдено»
        означает не «селектора нет», а «мы никуда не посмотрели».
        """
        blob = _frontend_blob()
        assert len(blob) > 100_000, "выборка фронта подозрительно мала — гейт слеп"
        assert "export function" in blob
