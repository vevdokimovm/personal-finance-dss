"""Юр-элементы фронта существуют и подключены (L5, L6, L7 — v8.40.0).

Гейт против самого дорогого класса ошибок этого проекта: **элемент объявлен, но
не доезжает до страницы**. За вахту он встретился четырежды — мёртвый роут `/join`,
непрочитанный `?ref=`, шрифт из токена без загрузки, недостижимая роль «наблюдатель».
Юридический контур — худшее место для повторения: отсутствие cookie-баннера или ссылки
на политику это не «страница поехала», а нарушение, за которое штрафуют.

Проверяется СВЯЗЬ, а не текст: виджет существует И подключён в корневом layout. Текст
и разметку проверяют юнит- и браузерные тесты (`CookieBanner.test.tsx`,
`LegalFooter.test.tsx`, `e2e/legal.spec.ts`) — здесь только «не пропало».

🔴 Комментарии вырезаются перед проверкой. Урок гейта шрифта (v8.39.0): первая редакция
искала подстроки, находила их в комментариях, объясняющих реализацию, и была зелёной
на сломанном состоянии.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
ROOT_ROUTE = FRONTEND / "src" / "routes" / "__root.tsx"
PLANNING_PAGE = FRONTEND / "src" / "pages" / "planning" / "PlanningPage.tsx"

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)


def _code_only(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", text))


@pytest.mark.parametrize(
    "widget,requirement",
    [
        ("CookieBanner", "L6 — баннер выбора cookie"),
        ("LegalFooter", "L7 — ссылки на юридические документы"),
    ],
)
def test_widget_is_mounted_in_root_layout(widget: str, requirement: str) -> None:
    """Виджет подключён именно в КОРНЕ — то есть на каждой странице, включая гостевые.

    До входа оферту и политику читают чаще, чем после: подключение в отдельных экранах
    оставило бы гостя без них, а требование распространяется на весь сайт.
    """
    code = _code_only(ROOT_ROUTE)
    assert f"<{widget} />" in code, (
        f"{widget} не смонтирован в __root.tsx — требование «{requirement}» "
        "не выполняется на страницах, где виджета нет"
    )
    assert re.search(rf"import\s*\{{\s*{widget}\s*\}}", code), (
        f"{widget} используется, но не импортирован в __root.tsx"
    )


def test_cookie_banner_offers_both_choices() -> None:
    """Раздельный выбор — суть требования L6.

    Одна кнопка «Ок» согласием не является: у человека должна быть возможность
    отказаться, и отказ должен стоить ровно одного клика, как и согласие.
    """
    code = _code_only(FRONTEND / "src" / "widgets" / "cookie-banner" / "CookieBanner.tsx")
    assert '"all"' in code and '"necessary"' in code, (
        "у баннера нет раздельного выбора: остался один вариант, а это не согласие"
    )


def test_cookie_choice_is_bound_to_policy_version() -> None:
    """Согласие даётся на КОНКРЕТНУЮ редакцию, перенос на новую — нарушение."""
    code = _code_only(FRONTEND / "src" / "widgets" / "cookie-banner" / "cookieConsent.ts")
    assert "version" in code, "выбор не привязан к редакции политики"


def test_disclaimer_comes_from_the_response() -> None:
    """Дисклеймер 39-ФЗ берётся из ответа, а не перепечатан во фронте (L5).

    Перепечатанный юридический текст расходится с каноном молча и ровно тогда, когда
    канон меняют. Здесь проверяется, что экран читает поле, а не хранит копию.
    """
    code = _code_only(PLANNING_PAGE)
    assert "plan.disclaimer" in code, (
        "экран рекомендаций не показывает дисклеймер из ответа — либо его нет вовсе, "
        "либо текст перепечатан во фронте и разойдётся с каноном"
    )
    assert "не является инвестиционным советником" not in code, (
        "юридический текст перепечатан в компоненте: он обязан приходить полем ответа"
    )
