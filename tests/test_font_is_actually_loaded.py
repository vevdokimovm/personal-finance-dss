"""Шрифт из токена обязан реально загружаться (v8.39.0).

🔴 `--font-body: "Manrope", …` был объявлен в `tokens.css` и НЕ загружался ниоткуда:
ни `@font-face`, ни `<link>`, ни пакета в зависимостях. Весь SPA рендерился системным
шрифтом, то есть дизайн-система обещала гарнитуру, которой в продукте не существовало.
Найдено design-critic ещё в v8.10.0 и прожило до v8.39.0 — двадцать восемь версий.

Класс дефекта тот же, что у мёртвой ссылки `/join` и у непрочитанного `?ref=`: объявление
есть, механизма за ним нет, и глазами это не видно — макет выглядит прилично на любом
шрифте, а на машине разработчика Manrope может быть установлен системно.

Гейт проверяет ровно связь «объявлено → загружается», а не конкретную гарнитуру:
поменяется шрифт — тест продолжит работать, если новый действительно подключён.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
TOKENS = FRONTEND / "src" / "app" / "styles" / "tokens.css"
PACKAGE_JSON = FRONTEND / "package.json"
SRC = FRONTEND / "src"

# Гарнитуры, которые есть у пользователя и так: их загружать не нужно и нельзя.
SYSTEM_FAMILIES = {
    "segoe ui",
    "system-ui",
    "sans-serif",
    "serif",
    "monospace",
    "ui-monospace",
    "-apple-system",
    "blinkmacsystemfont",
    "roboto",
    "helvetica neue",
    "arial",
    "menlo",
    "consolas",
    "sfmono-regular",
    "liberation mono",
    "courier new",
    "ui-sans-serif",
}


# Комментарии из проверки вырезаются. 🔴 Первая редакция гейта этого не делала и была
# слепа: в исходниках упоминались и `manrope`, и `fonts.googleapis.com` — оба в
# КОММЕНТАРИЯХ, объясняющих, почему шрифт грузится самохостом. Двух слов в прозе хватило,
# чтобы проверка сочла шрифт доставленным. Поймано мутацией: удаление пакета из
# зависимостей гейт не заметил. Гейт, удовлетворяемый комментарием, хуже отсутствующего.
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _code_only(text: str) -> str:
    text = _BLOCK_COMMENT.sub(" ", text)
    text = _LINE_COMMENT.sub(" ", text)
    return _HTML_COMMENT.sub(" ", text).lower()


def _custom_families() -> set[str]:
    """Все НЕ системные гарнитуры, названные в токенах шрифта."""
    text = TOKENS.read_text(encoding="utf-8")
    families: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"\s*--font-[a-z-]+:\s*(.+);", line)
        if not match:
            continue
        for raw in match.group(1).split(","):
            name = raw.strip().strip('"').strip("'").lower()
            if name and name not in SYSTEM_FAMILIES and not name.startswith("var("):
                families.add(name)
    return families


def _self_hosted(family: str) -> bool:
    """Пакет самохоста в зависимостях — имя пакета, а не упоминание в тексте."""
    package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    slug = family.replace(" ", "-")
    return any(slug in name.lower() for name in deps)


def _has_font_face(family: str) -> bool:
    """Собственный `@font-face`, объявляющий именно эту гарнитуру."""
    for path in SRC.rglob("*.css"):
        code = _code_only(path.read_text(encoding="utf-8"))
        for block in re.findall(r"@font-face\s*\{[^}]*\}", code):
            if re.search(rf"font-family\s*:\s*['\"]?{re.escape(family)}", block):
                return True
    return False


def _external_link(family: str) -> bool:
    """`<link href=...fonts.googleapis.com...family=...>` в разметке, а не в тексте."""
    index_html = FRONTEND / "index.html"
    if not index_html.exists():
        return False
    code = _code_only(index_html.read_text(encoding="utf-8"))
    slug = family.replace(" ", "+")
    return bool(re.search(rf"href=[^>]*fonts\.googleapis\.com[^>]*{re.escape(slug)}", code))


def test_tokens_declare_at_least_one_font() -> None:
    """Канарейка: если токены шрифта исчезнут, тест ниже станет пустым и зелёным."""
    assert "--font-body" in TOKENS.read_text(encoding="utf-8")


@pytest.mark.parametrize("family", sorted(_custom_families()))
def test_declared_font_is_really_delivered(family: str) -> None:
    """Каждая объявленная нестандартная гарнитура обязана иметь способ доставки.

    Годится любой из трёх: пакет самохоста в зависимостях, собственный `@font-face`,
    внешний `<link>`. Не годится — объявление в токене и упоминание в комментарии.
    """
    delivered = _self_hosted(family) or _has_font_face(family) or _external_link(family)
    assert delivered, (
        f"Шрифт «{family}» объявлен в токенах, но нигде не загружается: нет ни пакета "
        f"самохоста в зависимостях, ни @font-face, ни <link>. Интерфейс будет рисоваться "
        f"системным шрифтом, а дизайн-система — обещать гарнитуру, которой нет."
    )
