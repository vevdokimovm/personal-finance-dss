"""Фронт не выбрасывает сгенерированный тип двойным кастом (v8.50.0).

## Что именно запрещено и почему

`data as unknown as SomeType` — не сужение типа, а его **подмена**: первый шаг стирает
всё, что TypeScript знал об ответе, второй объявляет новую правду. Компилятор после
этого не может сказать, что фронт ждёт полей, которых контракт не обещает.

Так и родился дефект v8.31.1: рукописный `CalculatePlanResult` обещал `ranked`, `top3`
и `Explanation.gains/costs` обязательными, схема — нет, а каст в `usePlan.ts` держал
компилятор в неведении. Дашборд уходил в error boundary на ответе, который контракт
разрешает.

🔴 **Каст переживает починку типов.** Типы `plan-summary` перевели на реэкспорт
сгенерированных ещё в v8.40.0, а каст остался жить рядом — и снимал сверку ещё девять
версий, уже ни от чего не защищая. Убран в v8.50.0 одной строкой: `tsc` прошёл без
единой правки, то есть каст был мёртвым грузом с самого перехода на генерацию.

## Почему гейт в pytest, а не в eslint

Правило eslint (`@typescript-eslint/no-unnecessary-type-assertion`) ловит только
заведомо лишние утверждения и молчит на `as unknown as`, потому что формально оно
корректно. Здесь запрет продуктовый, а не языковой: сверка с контрактом — механизм
проекта, и охраняется он там же, где остальные механизмы.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "frontend" / "src"

# Двойной каст в любом виде: `as unknown as`, `as any as`, с переносами строк.
DOUBLE_CAST = re.compile(r"\bas\s+(?:unknown|any)\s+as\b", re.MULTILINE)

# Тесты и моки живут по другим правилам: там подделка типа — способ собрать фикстуру,
# а не способ обмануть сверку с сервером.
SKIP_SUFFIXES = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")

# Сгенерированный клиент не редактируется руками; `lib/test` — оснастка тестов,
# там каст стоит по той же причине, что в самих тестах.
SKIP_DIRS = {"generated", "node_modules", "dist"}
SKIP_PATH_PARTS = (("shared", "lib", "test"),)

# Строчные и блочные комментарии: запись правила В ТЕКСТЕ — не нарушение правила.
# Без этого docstring, объясняющий, чего нельзя делать, роняет собственный гейт
# (поймано на первом же запуске: `plan-summary/model/types.ts:13` — цитата в комментарии).
COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


def _source_files() -> list[Path]:
    files = []
    for path in SRC.rglob("*.ts*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if any(
            all(part in path.parts for part in parts) for parts in SKIP_PATH_PARTS
        ):
            continue
        if path.name.endswith(SKIP_SUFFIXES):
            continue
        files.append(path)
    return files


def _strip_comments(text: str) -> str:
    """Комментарии заменяются пробелами той же длины — номера строк не съезжают."""
    return COMMENTS.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def test_no_double_casts_in_product_code() -> None:
    """🔴 Ни один продуктовый файл не подменяет тип ответа двойным кастом.

    Мутация проверки: вернуть `data as unknown as CalculatePlanResult`
    в `usePlan.ts` — тест обязан покраснеть.
    """
    offenders = []
    for path in _source_files():
        text = _strip_comments(path.read_text(encoding="utf-8"))
        for match in DOUBLE_CAST.finditer(text):
            line = text[: match.start()].count("\n") + 1
            offenders.append(f"{path.relative_to(REPO_ROOT)}:{line}")

    assert not offenders, (
        "Двойной каст выбрасывает сгенерированный тип и снимает сверку с контрактом: "
        + ", ".join(offenders)
        + ". Если тип действительно другой — чинить схему на бэкенде, а не глушить "
        "компилятор."
    )


def test_entity_types_reexport_generated() -> None:
    """Каждая сущность берёт типы из контракта, а не ведёт свои.

    Проверяется наличие импорта из сгенерированного клиента в `model/types.ts`.
    Рукописные вспомогательные интерфейсы допустимы (у части ответов схемы в
    контракте нет вовсе), но файл, не знающий про генератор ВООБЩЕ, — это
    признак типа, живущего своей жизнью.
    """
    entities = SRC / "entities"
    orphans = []
    for types_file in entities.glob("*/model/types.ts"):
        text = types_file.read_text(encoding="utf-8")
        if "@shared/api/generated" not in text:
            orphans.append(str(types_file.relative_to(REPO_ROOT)))

    assert not orphans, (
        "Типы сущности не связаны с контрактом: "
        + ", ".join(orphans)
        + ". Рукописный тип обещает то, что помнил автор, и молчит обо всём остальном."
    )
