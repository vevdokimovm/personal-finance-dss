"""Тесты прогнозирования: SES, Monte-Carlo, тренд (формулы ВКР §14, 35)."""
from app.core.forecast import (
    build_history_from_current,
    detect_trend,
    monte_carlo_intervals,
    ses_forecast,
)


class TestSES:
    def test_empty_history(self):
        assert ses_forecast([], horizon=3) == [0.0, 0.0, 0.0]

    def test_single_point(self):
        assert ses_forecast([500], horizon=2) == [500, 500]

    def test_smoothing(self):
        # s0=100; x=200 → 0.3*200 + 0.7*100 = 130
        assert ses_forecast([100, 200], alpha=0.3, horizon=1) == [130]

    def test_horizon_repeats(self):
        assert ses_forecast([100, 200], alpha=0.3, horizon=3) == [130, 130, 130]


class TestMonteCarlo:
    def test_intervals_ordered(self):
        intervals = monte_carlo_intervals([10000], horizon=1, seed=42)
        assert len(intervals) == 1
        i = intervals[0]
        assert i["p10"] <= i["p50"] <= i["p90"]

    def test_deterministic_with_seed(self):
        a = monte_carlo_intervals([5000, 5000], horizon=2, seed=7)
        b = monte_carlo_intervals([5000, 5000], horizon=2, seed=7)
        assert a == b

    def test_uncertainty_grows_with_horizon(self):
        intervals = monte_carlo_intervals([10000, 10000, 10000], horizon=3, seed=42)
        width1 = intervals[0]["p90"] - intervals[0]["p10"]
        width3 = intervals[2]["p90"] - intervals[2]["p10"]
        assert width3 > width1


class TestHistoryBuilder:
    def test_length(self):
        assert len(build_history_from_current(10000, periods=6)) == 6

    def test_nonpositive_value(self):
        assert build_history_from_current(0, periods=4) == [0, 0, 0, 0]


class TestTrend:
    def test_stable(self):
        assert detect_trend(100, [100]) == "stable"

    def test_improving(self):
        assert detect_trend(100, [200]) == "improving"

    def test_deteriorating(self):
        assert detect_trend(100, [50]) == "deteriorating"

    def test_empty_series(self):
        assert detect_trend(100, []) == "stable"
