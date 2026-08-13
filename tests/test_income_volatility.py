"""ADR-015: floor резерва растёт с волатильностью дохода — зеркально G8 (токсичный долг
опускает floor), в обратную сторону. Красная линия: Rt/Dt/кризисный режим НЕ трогаются —
эти тесты проверяют только сдвиг floor, не сам поток.
"""
from __future__ import annotations

from app.core.ranking import (
    INCOME_VOLATILITY_THRESHOLD,
    RESERVE_FLOOR_MONTHS,
    TOXIC_FLOOR_MONTHS,
    effective_floor_months,
    income_cv,
)


class TestIncomeCv:
    def test_constant_income_is_zero_cv(self):
        assert income_cv([100_000.0] * 6) == 0.0

    def test_insufficient_months_is_none(self):
        # < 6 содержательных месяцев — недостаточно данных, тот же фолбэк-принцип,
        # что у choose_point_forecast для короткой истории (только порог строже).
        assert income_cv([100_000.0] * 5) is None

    def test_none_history_is_none(self):
        assert income_cv(None) is None

    def test_zero_months_excluded_from_denominator(self):
        # месяц без дохода (0) — не "маленький доход", а отсутствие данных за
        # этот бин (build_monthly_history так же трактует ведущие нули).
        history = [100_000.0, 100_000.0, 100_000.0, 100_000.0, 100_000.0, 100_000.0, 0.0]
        assert income_cv(history) == 0.0

    def test_volatile_income_cv_value(self):
        history = [50_000.0, 150_000.0, 50_000.0, 150_000.0, 50_000.0, 150_000.0]
        assert abs(income_cv(history) - 0.5) < 1e-9


class TestEffectiveFloorMonthsWithIncomeHistory:
    def _obl(self, rate):
        return {"amount": 100_000, "interest_rate": rate, "monthly_payment": 5_000}

    def test_no_history_keeps_base_floor(self):
        # обратная совместимость: старые вызовы без income_history не меняют поведение.
        assert effective_floor_months([], r_bench=0.14) == RESERVE_FLOOR_MONTHS

    def test_stable_income_keeps_base_floor(self):
        history = [100_000.0] * 6
        assert effective_floor_months(
            [], r_bench=0.14, income_history=history
        ) == RESERVE_FLOOR_MONTHS

    def test_exactly_at_threshold_keeps_base_floor(self):
        # CV ровно на пороге — без буста (строго больше, не >=).
        mean = 100_000.0
        dev = mean * INCOME_VOLATILITY_THRESHOLD
        history = [mean - dev, mean + dev] * 3
        assert abs(income_cv(history) - INCOME_VOLATILITY_THRESHOLD) < 1e-6
        assert effective_floor_months(
            [], r_bench=0.14, income_history=history
        ) == RESERVE_FLOOR_MONTHS

    def test_volatile_income_raises_floor(self):
        history = [50_000.0, 150_000.0, 50_000.0, 150_000.0, 50_000.0, 150_000.0]  # CV=0.5
        floor = effective_floor_months([], r_bench=0.14, income_history=history)
        assert floor == RESERVE_FLOOR_MONTHS + 0.2

    def test_extreme_volatility_caps_at_one_extra_month(self):
        history = [10_000.0, 10_000.0, 10_000.0, 10_000.0, 10_000.0, 550_000.0]  # CV ~2.0
        floor = effective_floor_months([], r_bench=0.14, income_history=history)
        assert floor == RESERVE_FLOOR_MONTHS + 1.0

    def test_toxic_debt_wins_over_volatile_income(self):
        # ADR-015: токсичный долг приоритетнее волатильности — лавина дороже
        # любой страховки, порядок приоритета не меняется волатильностью дохода.
        history = [10_000.0, 10_000.0, 10_000.0, 10_000.0, 10_000.0, 550_000.0]
        floor = effective_floor_months(
            [self._obl(0.60)], r_bench=0.14, income_history=history
        )
        assert floor == TOXIC_FLOOR_MONTHS
