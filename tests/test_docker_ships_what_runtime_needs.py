"""Образ содержит всё, что читается на рантайме (v8.45.0).

## Что проверяется

С v8.44.0 приложение читает файлы ВНЕ пакета `app/`: `GET /legal/documents/{slug}`
отдаёт содержимое `docs/legal/*.md` прямо с диска. Значит `.dockerignore` перестал быть
вопросом «что не тащить в образ» и стал вопросом «что приложение не сможет прочитать
в проде». Файл, исключённый по привычке (markdown — это же документация), даёт 503
на политике обработки ПДн — при том, что локально всё работает.

## 🔴 Первая редакция этого гейта СОЛГАЛА, и это записано намеренно

Гейт был написан с упрощённым разбором `.dockerignore` — совпадение проверялось в том
числе по ИМЕНИ файла. На такой семантике `*.md` «исключал» `docs/legal/privacy-policy.md`,
гейт покраснел на шести документах, и в `.dockerignore` было добавлено `!docs/legal/*.md`
как исправление несуществующего дефекта.

Настоящая семантика другая: Docker матчит паттерн против ПОЛНОГО пути через
`filepath.Match`, где `*` **не пересекает** `/`. Поэтому `*.md` исключает markdown только
в корне контекста, а `docs/legal/*.md` под него не попадал никогда. Проверено прямым
разбором обеих семантик, а не рассуждением.

Урок ровно тот же, что в соседнем разборе того же дня: **проверка отвечала на свой вопрос
точно, но вопрос был не тот.** Красное от неверной проверки опаснее отсутствия проверки —
оно ведёт к правке кода, которой не требовалось.

Ниже семантика воспроизведена корректно. Правило `!docs/legal/*.md` в `.dockerignore`
оставлено сознательно — не как исправление, а как явная страховка на случай, если
`*.md` когда-нибудь станет `**/*.md`.

## Почему проверка читает `.dockerignore`, а не собирает образ

Настоящая сборка — минуты и демон Docker, которого на машине разработки нет
(`command not found: docker`, проверено). Здесь тот же вопрос задан дёшево. 🔴 Это
ограничение, а не эквивалент: проверка сборкой остаётся долгом деплойного пайплайна.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCKERIGNORE = REPO_ROOT / ".dockerignore"


def _patterns() -> list[str]:
    lines = DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def _matches(pattern: str, path: str) -> bool:
    """Семантика Docker: `filepath.Match` против ПОЛНОГО пути.

    🔴 Ключевое отличие от `fnmatch`: `*` не пересекает `/`, поэтому `*.md` относится
    только к корню контекста, а не ко всем markdown в дереве. Именно на этом ошиблась
    первая редакция гейта (см. докстроку модуля). `**` пересекает разделитель.
    """
    clean = pattern.rstrip("/")
    regex = (
        re.escape(clean)
        .replace(r"\*\*", "\x00")   # `**` временно, чтобы не задеть его как два `*`
        .replace(r"\*", "[^/]*")
        .replace("\x00", ".*")
        .replace(r"\?", "[^/]")
    )
    if re.fullmatch(regex, path):
        return True
    # Правило-каталог исключает и всё, что под ним.
    return bool(re.fullmatch(regex, path.split("/")[0])) and "/" in path


def _is_excluded(rel_path: str) -> bool:
    """Исключён ли путь. Последнее совпавшее правило выигрывает — как в Docker."""
    excluded = False
    for pattern in _patterns():
        negated = pattern.startswith("!")
        if _matches(pattern[1:] if negated else pattern, rel_path):
            excluded = not negated
    return excluded


def _runtime_read_files() -> list[str]:
    """Файлы, которые приложение читает С ДИСКА во время работы.

    Список не выдуман: собирается из реестра юридических документов — единственного
    места, где рантайм обращается к файлам вне пакета `app/`.
    """
    from app.core.legal import LEGAL_DOCUMENTS

    return [doc["path"] for doc in LEGAL_DOCUMENTS.values()]


@pytest.mark.parametrize("rel_path", _runtime_read_files())
def test_runtime_files_are_not_excluded_from_image(rel_path) -> None:
    """🔴 Юридический текст обязан попасть в образ.

    Без него `/legal/documents/{slug}` отдаёт 503 на политике обработки ПДн — то есть
    в проде отсутствует документ, обязательный по 152-ФЗ, при том что локально всё
    работает.
    """
    assert not _is_excluded(rel_path), (
        f"{rel_path} исключён из образа .dockerignore, но читается на рантайме "
        f"(app/core/legal.py::LEGAL_DOCUMENTS). В контейнере эндпоинт вернёт 503."
    )


def test_runtime_files_exist_on_disk() -> None:
    """И сами файлы на месте: реестр не должен ссылаться в пустоту."""
    for rel_path in _runtime_read_files():
        assert (REPO_ROOT / rel_path).is_file(), rel_path


def test_frontend_build_is_in_the_image() -> None:
    """Сборка React попадает в образ отдельной стадией.

    `frontend/dist` в `.gitignore`, поэтому `COPY . .` его не приносит: без стадии
    сборки контейнер отдаёт старый Jinja-интерфейс, а весь фронт вехи 8 остаётся
    существовать только в dev.
    """
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "npm run build" in dockerfile, "Dockerfile не собирает фронт"
    assert "COPY --from=frontend" in dockerfile, (
        "сборка фронта не копируется в runtime-образ — стадия есть, результат не едет"
    )


def test_build_stage_copy_order() -> None:
    """`COPY --from=frontend` идёт ПОСЛЕ `COPY . .`.

    Обратный порядок молча затирает собранный фронт: в исходниках каталога `dist`
    нет, и второй слой кладёт поверх пустоту. Ошибка невидима при чтении — строки
    стоят рядом, — и видна только по итоговому образу.
    """
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert dockerfile.index("COPY . .") < dockerfile.index("COPY --from=frontend"), (
        "COPY . . идёт после копирования сборки фронта и затирает её"
    )
