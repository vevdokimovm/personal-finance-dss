"""Тесты слоя 3-A: временные паттерны трат (temporal, мат-модель v3.0.0).

Проверяют робастный наклон (Theil-Sen), исключение текущего (неполного) месяца
из тренда, корректный учёт пропущенных месяцев через порядковый номер месяца,
порог значимости тренда (flat не показываем) и устойчивость к нехватке истории.
"""
import pytest

from app.core.spending_advice import ExpenseRecord, SpendingAdvisor, TemporalPattern


def _series(category: str, totals_by_period: dict[str, float]) -> list[ExpenseRecord]:
    """Одна операция на период, сумма = месячный итог."""
    return [
        ExpenseRecord(category=category, amount=total, period=period)
        for period, total in totals_by_period.items()
    ]


class TestTheilSen:
    def test_clean_linear_slope(self):
        # равномерный рост на 1000 за шаг → наклон 1000
        points = [(0, 1000), (1, 2000), (2, 3000), (3, 4000)]
        assert SpendingAdvisor.theil_sen(points) == pytest.approx(1000.0)

    def test_robust_to_middle_outlier(self):
        # выброс 50000 в середине: OLS дал бы ~5700, Theil-Sen устойчив → 1000
        points = [(0, 1000), (1, 2000), (2, 50000), (3, 4000)]
        assert SpendingAdvisor.theil_sen(points) == pytest.approx(1000.0)

    def test_negative_slope(self):
        points = [(0, 4000), (1, 3000), (2, 2000), (3, 1000)]
        assert SpendingAdvisor.theil_sen(points) == pytest.approx(-1000.0)

    def test_single_point_no_slope(self):
        assert SpendingAdvisor.theil_sen([(0, 1000)]) == 0.0


class TestTemporalPatterns:
    def test_rising_trend_detected(self):
        # прошлые 01..04 растут на 1000/мес; 05 — текущий, в тренд не входит
        records = _series("Кафе и рестораны",
                          {"2026-01": 1000, "2026-02": 2000, "2026-03": 3000, "2026-04": 4000, "2026-05": 9999})  # noqa: E501
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-05")
        cafe = next(p for p in patterns if p.category == "Кафе и рестораны")
        assert cafe.direction == "rising"
        assert cafe.slope_abs == pytest.approx(1000.0)
        assert cafe.months_observed == 4
        # baseline = median(1000,2000,3000,4000) = 2500 → 1000/2500 = 40%
        assert cafe.baseline == 2500.0
        assert cafe.slope_pct == pytest.approx(40.0)

    def test_current_period_excluded_from_slope(self):
        # дикий текущий месяц не должен влиять на наклон тренда
        records = _series("Покупки",
                          {"2026-01": 1000, "2026-02": 2000, "2026-03": 3000, "2026-04": 4000, "2026-05": 999999})  # noqa: E501
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-05")
        buy = next(p for p in patterns if p.category == "Покупки")
        assert buy.slope_abs == pytest.approx(1000.0)

    def test_robust_slope_ignores_spike(self):
        # всплеск 50000 в одном из прошлых месяцев не разносит тренд
        records = _series("Развлечения",
                          {"2026-01": 1000, "2026-02": 2000, "2026-03": 50000, "2026-04": 4000, "2026-05": 5000})  # noqa: E501
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-05")
        ent = next(p for p in patterns if p.category == "Развлечения")
        assert ent.slope_abs == pytest.approx(1000.0)
        assert ent.direction == "rising"

    def test_gap_months_use_calendar_distance(self):
        # пропуск марта/апреля: 01,02,05 — расстояние по календарю, не по позиции
        records = _series("Покупки",
                          {"2026-01": 1000, "2026-02": 2000, "2026-05": 5000, "2026-06": 7000})
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-06")
        buy = next(p for p in patterns if p.category == "Покупки")
        # наклоны 01→02, 02→05, 01→05 все = 1000/мес → median 1000
        assert buy.slope_abs == pytest.approx(1000.0)

    def test_falling_trend(self):
        records = _series("Кафе и рестораны",
                          {"2026-01": 4000, "2026-02": 3000, "2026-03": 2000, "2026-04": 1000, "2026-05": 900})  # noqa: E501
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-05")
        cafe = next(p for p in patterns if p.category == "Кафе и рестораны")
        assert cafe.direction == "falling"
        assert cafe.slope_abs < 0

    def test_flat_trend_not_reported(self):
        # шум в пределах ~0.3%/мес → ниже порога 5% → не показываем
        records = _series("Покупки",
                          {"2026-01": 1000, "2026-02": 1050, "2026-03": 980, "2026-04": 1010, "2026-05": 1000})  # noqa: E501
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-05")
        assert all(p.category != "Покупки" for p in patterns)

    def test_insufficient_history_not_reported(self):
        # только 2 прошлых месяца (< min_months=3) → тренд не считаем
        records = _series("Покупки", {"2026-01": 1000, "2026-02": 5000, "2026-03": 9000})
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-03")
        assert all(p.category != "Покупки" for p in patterns)

    def test_sorted_by_absolute_ruble_impact(self):
        records = (
            _series("Кафе и рестораны", {"2026-01": 1000,
                    "2026-02": 2000, "2026-03": 3000, "2026-04": 4000})
            + _series("Развлечения", {"2026-01": 100, "2026-02": 1100,
                      "2026-03": 2100, "2026-04": 3100})
            + _series("Покупки", {"2026-01": 5000, "2026-02": 5000,
                      "2026-03": 5000, "2026-04": 5000})
        )
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-04")
        # «Развлечения» растут на 1000/мес тоже, но проверяем сортировку по |₽|
        impacts = [abs(p.slope_abs) for p in patterns]
        assert impacts == sorted(impacts, reverse=True)

    def test_top_k_limit(self):
        records = (
            _series("Кафе и рестораны", {"2026-01": 1000,
                    "2026-02": 2000, "2026-03": 3000, "2026-04": 4000})
            + _series("Развлечения", {"2026-01": 500, "2026-02": 1500,
                      "2026-03": 2500, "2026-04": 3500})
            + _series("Покупки", {"2026-01": 200, "2026-02": 1200,
                      "2026-03": 2200, "2026-04": 3200})
            + _series("Подписки и сервисы", {"2026-01": 100,
                      "2026-02": 600, "2026-03": 1100, "2026-04": 1600})
        )
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-04", top_k=2)
        assert len(patterns) == 2

    def test_message_mentions_category_and_percent(self):
        records = _series("Кафе и рестораны",
                          {"2026-01": 1000, "2026-02": 2000, "2026-03": 3000, "2026-04": 4000})
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-04")
        msg = patterns[0].message
        assert "Кафе и рестораны" in msg
        assert "%" in msg

    def test_empty_input(self):
        assert SpendingAdvisor().analyze_trends([], current_period="2026-04") == []

    def test_returns_temporal_pattern_type(self):
        records = _series("Кафе и рестораны",
                          {"2026-01": 1000, "2026-02": 2000, "2026-03": 3000, "2026-04": 4000})
        patterns = SpendingAdvisor().analyze_trends(records, current_period="2026-04")
        assert all(isinstance(p, TemporalPattern) for p in patterns)
