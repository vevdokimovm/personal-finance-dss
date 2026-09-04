"""Статические guard-тесты фронтенда: UI не разъезжается с матмоделью.

Читают исходники фронта с диска и проверяют, что интерфейс не остался на семантике
предыдущей редакции модели. Класс дефекта: модель перевели на stock-based ликвидность
(v3.0.0), а подписи и пороги в UI остались flow-based — расчёт верный, объяснение
пользователю неверное, и расхождение не ловится ничем, потому что оба слоя «работают».

🔴 **Перенацелены на React в v8.47.0.** До этого читались `frontend/static/js/app.js`
и `frontend/templates/*.html` — Jinja-интерфейс, снесённый в том же батче. То есть
последние сорок с лишним версий эти проверки сторожили **не тот фронт**: React жил
своей жизнью и под guard не попадал вовсе (родня PIT-020 и PIT-022 — проверка была,
покрывала не то).

Проверяется наличие НОВОЙ семантики и отсутствие СТАРОЙ. Первое важнее: тест только
на отсутствие проходит и на пустом файле.
"""
from __future__ import annotations

from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"

# Экраны, где живёт семантика ликвидности и параметров расчёта.
METRICS = SRC / "widgets" / "metrics-grid"
PLAN_SETTINGS = SRC / "pages" / "planning" / "ui" / "PlanSettingsSection.tsx"

# Формулировки предыдущей редакции модели. Появление любой — регрессия объяснения.
STALE_PHRASES = (
    "21 вариант",
    "шаг 20%",
    "÷ Обязательные траты",
    "долю от обязательных трат",
    "Насколько свободно от обязательных платежей",
    "норма от 0.3",
)


def _tsx_sources() -> list[Path]:
    """Все исходники фронта, кроме сгенерированных и тестов.

    Сгенерированный клиент (`shared/api/generated`) исключён намеренно: его содержимое
    задаёт контракт бэкенда, и найденная там строка означала бы дефект схемы, а не UI.
    """
    return [
        p
        for p in SRC.rglob("*.tsx")
        if "generated" not in p.parts and not p.name.endswith(".test.tsx")
    ] + [
        p
        for p in SRC.rglob("*.ts")
        if "generated" not in p.parts and not p.name.endswith(".test.ts")
    ]


@pytest.fixture(scope="module")
def metrics_sources() -> str:
    return "\n".join(
        p.read_text(encoding="utf-8") for p in METRICS.rglob("*.tsx") if ".test." not in p.name
    )


class TestLiquidityIsStockBased:
    """Lt — месяцы автономии, а не доля от обязательных трат."""

    def test_liquidity_is_measured_in_months(self, metrics_sources: str) -> None:
        """Ликвидность выражена в МЕСЯЦАХ автономии, а не долей.

        🔴 Проверяется единица измерения, а не конкретное число. Первая редакция этого
        теста искала «2.5» — порог Greninger из Jinja-версии; React считает иначе
        и осознанно: там `RUNWAY_WARN_THRESHOLD = 1` со ссылкой на канон («отсев
        по ликвидности мягкий», `docs/math_model.md`), то есть предупреждение мягче,
        чем справочная норма. Тест на «2.5» требовал бы вернуть чужой порог —
        и был бы красным на исправном коде (родня PIT-021).

        Проверяется НАЛИЧИЕ: тест только на отсутствие старых формулировок прошёл бы
        и на экране, где про ликвидность не сказано вовсе.
        """
        assert "мес. автономии" in metrics_sources, (
            "ликвидность не выражена в месяцах автономии — UI мог вернуться "
            "к flow-семантике (доля от обязательных трат)"
        )

    def test_blr_is_distinguished_from_lt(self, metrics_sources: str) -> None:
        """Подушка (BLR) считает и цели — это другой показатель, чем запас Lt.

        Если их подписи совпадут, человек решит, что видит одно число дважды.
        """
        assert "включая цели" in metrics_sources


class TestPlanSettingsSemantics:
    def test_lmin_is_in_months(self) -> None:
        """`l_min` задаётся в месяцах расходов, а не долей."""
        text = PLAN_SETTINGS.read_text(encoding="utf-8")
        assert "мес" in text and "расход" in text.lower()

    def test_key_rate_source_is_offered(self) -> None:
        """Ставку можно взять у ЦБ, а не только вписать руками.

        Была в Jinja (`rbench-cbr`), в React — кнопка «Взять ключевую ставку ЦБ».
        """
        text = PLAN_SETTINGS.read_text(encoding="utf-8")
        assert "ключевую ставку" in text or "ключевая ставка" in text


class TestNoStaleModelSemanticsAnywhere:
    @pytest.mark.parametrize("phrase", STALE_PHRASES)
    def test_phrase_is_gone_from_frontend(self, phrase: str) -> None:
        """Формулировка предыдущей редакции модели не осталась ни в одном исходнике.

        🔴 Ищется по ВСЕМУ фронту, а не по списку файлов: экран могли перенести,
        переименовать или разделить — список устарел бы молча, а поиск по дереву нет.
        """
        offenders = [
            str(p.relative_to(SRC)) for p in _tsx_sources() if phrase in p.read_text("utf-8")
        ]
        assert not offenders, (
            f"устаревшая формулировка модели {phrase!r} в {offenders} — "
            f"UI объясняет пользователю то, чего расчёт больше не делает"
        )
