"""Статические guard-тесты фронтенда.

Браузерных кликов тут нет (для них нужен Playwright). Эти тесты читают исходники
фронта с диска и проверяют, что UI не разъезжается с математической моделью бэка:
после перевода ликвидности на stock-based (refined-модель v3.0.0) во фронте не должно
остаться старой flow-семантики Lt (норма-доля 0.30, «доля от обязательных трат») и
устаревшего числа альтернатив. Именно этот класс рассинхрона ловят тесты.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
APP_JS = FRONTEND / "static" / "js" / "app.js"
DASHBOARD = FRONTEND / "templates" / "dashboard.html"
PLANNING = FRONTEND / "templates" / "planning.html"
TEMPLATES_DIR = FRONTEND / "templates"


@pytest.fixture(scope="module")
def app_js() -> str:
    return APP_JS.read_text(encoding="utf-8")


class TestAppJsNoStaleSemantics:
    def test_no_hardcoded_alternative_count(self, app_js: str) -> None:
        # Число альтернатив изменилось (21 → 66) и может меняться дальше — оно не
        # должно быть зашито в UI-текст.
        assert "21 вариант" not in app_js
        assert "шаг 20%" not in app_js

    def test_no_old_flow_liquidity_formula(self, app_js: str) -> None:
        # Старая формула Lt = свободные / обязательные траты
        assert "÷ Обязательные траты (расходы + кредиты)" not in app_js
        assert "долю от обязательных трат составляют свободные" not in app_js

    def test_lt_uses_month_thresholds(self, app_js: str) -> None:
        # Цвет/вердикт ликвидности — по месяцам автономии (норма Greninger 2.5–6),
        # а не по доле 0.3.
        assert "Lt >= 2.5" in app_js
        assert "Lt >= 0.3 ?" not in app_js

    def test_lt_popup_is_stock_based(self, app_js: str) -> None:
        # Новый разбор Lt: ликвидная подушка ÷ месячные расходы
        assert "Ликвидная подушка" in app_js
        assert "Месячные расходы" in app_js


class TestDashboardTemplate:
    def test_lt_card_months_norm(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "норма 2.5" in html
        assert "норма от 0.3" not in html

    def test_lt_card_no_flow_caption(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "Насколько свободно от обязательных платежей" not in html

    def test_blr_distinct_from_lt(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "включая цели" in html


class TestPlanningTemplate:
    def test_lmin_in_months(self) -> None:
        html = PLANNING.read_text(encoding="utf-8")
        assert "мес. расходов" in html

    def test_rbench_source_buttons(self) -> None:
        html = PLANNING.read_text(encoding="utf-8")
        assert "rbench-cbr" in html
        assert "rbench-from-asset" in html


class TestAllTemplatesConsistent:
    def test_no_flow_liquidity_caption_anywhere(self) -> None:
        # Ни в одном шаблоне (включая легаси) не осталось старой flow-подписи Lt
        for tpl in TEMPLATES_DIR.glob("*.html"):
            text = tpl.read_text(encoding="utf-8")
            assert "Насколько свободно от обязательных платежей" not in text, tpl.name
