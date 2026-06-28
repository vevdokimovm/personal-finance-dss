"""
Live-проверка доступности через axe-core (предрелизный тир `full`).

Чем отличается от `test_a11y_mechanical.py`. Механический тест парсит HTML и
проверяет инварианты разметки на статике. Этот — поднимает реальный браузер,
рендерит страницу со всем CSS/JS и прогоняет промышленный движок axe-core
(тот же, что Lighthouse/axe DevTools). Это ловит проблемы контраста, ARIA и
фокуса в РЕНДЕРЕ, а не только в исходнике.

Почему axe вендорится локально (tests/full/vendor/axe.min.js), а не грузится с
CDN. CSP приложения — `script-src 'self' 'unsafe-inline'`: внешний CDN
(cdnjs) браузер отвергает, поэтому загрузка `add_script_tag(url=...)` падала
ВСЕГДА (и в песочнице, и в CI) и тест молча скипался — то есть фактически не
работал. Inline-инъекция через `add_script_tag(content=...)` проходит по
`'unsafe-inline'` и не зависит от сети. Версия axe зафиксирована (4.12.1) для
воспроизводимости.

Покрытие: 14 публичных страниц × 2 темы (dark/light). Два уровня строгости:
  - critical  — недопустимы, ассерт валит прогон (жёсткий инвариант);
  - serious   — ratchet: известный долг зафиксирован в KNOWN_SERIOUS_RULES,
                ЛЮБОЕ новое serious-правило валит прогон (защита от регрессии).

Статус долга (v4.16.33, батч доступности):
  - `nested-interactive` — УСТРАНЁН (кнопка удаления вынесена из `<summary>` на /obligations,
    обёрнута в позиционированный контейнер; delete-делегирование через data-obligation-id цело,
    CRUD-E2E зелёный). В baseline его нет — повторное появление считается регрессией.
  - `color-contrast` — частично закрыт (новый токен `--c-accent-strong` для кнопок с белым текстом
    + снят `opacity` футера). Полный скан вскрыл, что остаток — СИСТЕМНЫЙ долг палитры (особенно
    light-тема: semantic-цвета, category-badges, ссылки, приглушённый текст массово ниже 4.5).
    Полная ревизия палитры под WCAG AA — отдельная крупная задача; до неё остаётся в baseline.

Тир `full`: гоняется перед релизом/тегом, нужен браузер.
"""
from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.full, pytest.mark.e2e]

# Вендорный axe-core (см. докстроку): инжектится контентом, обходя CSP.
_AXE_PATH = os.path.join(os.path.dirname(__file__), "vendor", "axe.min.js")

# Реальные публичные страницы (200). Битые пути прежней версии убраны: /login —
# страницы нет by design (вход через модалку), /legal — только /legal/{privacy,terms,consent}.
PAGES = [
    "/", "/dashboard", "/planning", "/transactions", "/obligations", "/goals",
    "/banks", "/validation", "/profile", "/contacts",
    "/legal/privacy", "/legal/terms", "/legal/consent",
    "/forgot-password",
]
THEMES = ["dark", "light"]

# Ratchet-baseline по доступности. ПУСТО: весь известный долг устранён.
#   nested-interactive — устранён в v4.16.33 (кнопка вынесена из <summary>).
#   color-contrast — устранён в v4.16.33–v4.16.35 (ревизия палитры под WCAG AA: accent-strong,
#     semantic -text токены во всех шаблонах/JS, text3, ссылки, badges, table-header). Полный скан
#     14 страниц × 2 темы даёт 0 (с заморозкой анимаций — см. _run_axe).
# Любое serious-нарушение теперь означает регрессию и валит прогон.
KNOWN_SERIOUS_RULES: set[str] = set()


def _load_axe() -> str:
    with open(_AXE_PATH, encoding="utf-8") as fh:
        return fh.read()


def _run_axe(page, url: str, theme: str) -> list[dict]:
    page.goto(url, wait_until="networkidle")
    # Тема хранится в localStorage под ключом finpilot-theme; применяется скриптом
    # в base.html при загрузке, поэтому ставим значение и перезагружаем.
    page.evaluate(f"localStorage.setItem('finpilot-theme', '{theme}')")
    page.reload(wait_until="networkidle")
    # Секции-карточки имеют fade-in анимацию (opacity 0->1). Если axe.run сработает
    # ДО её завершения, он замеряет контраст текста при opacity<1 (полупрозрачный
    # на фоне страницы) и выдаёт ЛОЖНЫЕ color-contrast нарушения. Замораживаем
    # анимации/переходы, чтобы opacity мгновенно встал в конечное значение (1).
    page.add_style_tag(content=(
        "*,*::before,*::after{animation-duration:0s!important;"
        "animation-delay:0s!important;transition-duration:0s!important;"
        "transition-delay:0s!important}"
    ))
    page.wait_for_timeout(300)
    page.add_script_tag(content=_load_axe())
    if not page.evaluate("typeof axe !== 'undefined'"):
        pytest.skip("axe-core не инициализировался (браузер/CSP)")
    results = page.evaluate(
        "async () => await axe.run(document, "
        "{runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa']}})"
    )
    return results.get("violations", [])


@pytest.mark.parametrize("path", PAGES)
@pytest.mark.parametrize("theme", THEMES)
def test_a11y_axe(page, base_url: str, path: str, theme: str):
    """Публичная страница в обеих темах: 0 critical (жёстко) + serious-ratchet (axe-core).

    Один прогон axe проверяет оба уровня, чтобы не поднимать браузер дважды.
    """
    violations = _run_axe(page, base_url + path, theme)

    critical = [v.get("id", "?") for v in violations if v.get("impact") == "critical"]
    assert not critical, (
        f"{path} [{theme}]: критические нарушения a11y: {', '.join(critical)}"
    )

    serious_rules = {v.get("id") for v in violations if v.get("impact") == "serious"}
    regressions = serious_rules - KNOWN_SERIOUS_RULES
    assert not regressions, (
        f"{path} [{theme}]: НОВЫЕ serious-нарушения (регрессия доступности): "
        f"{', '.join(sorted(regressions))}. Известный долг: {sorted(KNOWN_SERIOUS_RULES)}"
    )
