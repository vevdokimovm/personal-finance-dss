"""Шапка README не отстаёт от версии (v9.0.0).

## Как обнаружилось

`preflight` сверяет версии в `VERSION`, `app/config.py`, `CHANGELOG.md`, журнале состояния
и **бейдже** README — и был чист, когда шапка `<!-- STATUS -->` показывала `v8.54.0`
при фактической `v9.0.0`. Две версии подряд обновляли бейдж и не трогали текст рядом
с ним: проверка смотрела на одну строку файла и молчала про соседнюю.

🔴 **Почему это не мелочь.** README — первое, что читает человек, открывший репозиторий,
и единственное, что видит публичное зеркало. Устаревшая шапка утверждает, что продукт
находится в состоянии, которого нет: «§8.2 закрыт» рядом с бейджем `9.0.0` — это
не пропущенное обновление, а два взаимоисключающих утверждения на одном экране.

Тот же класс, что PIT-029: обоснование отпало, а текст, стоявший на нём, остался
и стал враньём. Разница в том, что здесь его никто не читал внимательно — потому
что рядом стоял зелёный гейт.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
VERSION_FILE = REPO_ROOT / "VERSION"


def _status_block() -> str:
    text = README.read_text(encoding="utf-8")
    match = re.search(r"<!-- STATUS -->(.*?)<!-- /STATUS -->", text, re.DOTALL)
    assert match, "в README нет блока <!-- STATUS -->"
    return match.group(1)


def test_status_block_names_the_current_version() -> None:
    """🔴 Версия в шапке совпадает с `VERSION`.

    Мутация: откатить версию в шапке — падает здесь, а не через две версии
    в чужих руках.
    """
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    assert f"`v{version}`" in _status_block(), (
        f"шапка README не знает про v{version} — она описывает состояние, "
        "которого больше нет, и это первое, что читает человек"
    )


def test_status_block_is_not_empty() -> None:
    """Шапка объясняет состояние словами, а не только номером.

    Номер без объяснения не отвечает на вопрос «где продукт сейчас», ради
    которого блок и существует.
    """
    body = re.sub(r"[`>*\s]", "", _status_block())
    assert len(body) > 60, "шапка README свелась к номеру версии без объяснения"


def test_milestone_line_matches_version_series() -> None:
    """🔴 Строка «Вехи» не противоречит номеру версии.

    Версия `9.x` означает открытую веху 9. Утверждение «8 идёт» рядом с ней —
    два взаимоисключающих факта на одном экране, и читатель верит тому,
    что попалось первым.
    """
    major = VERSION_FILE.read_text(encoding="utf-8").strip().split(".")[0]
    text = README.read_text(encoding="utf-8")
    match = re.search(r"^\|\s*\*\*Вехи\*\*\s*\|(.+)$", text, re.MULTILINE)
    assert match, "в README нет строки «Вехи»"
    line = match.group(1)
    assert f"**{major} " in line or f"**{major}(" in line, (
        f"строка «Вехи» не называет веху {major} идущей, хотя версия — {major}.x: {line[:120]}"
    )
