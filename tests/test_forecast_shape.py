"""
Контракт формы прогноза (ROADMAP §6.3, разрешение «почему всегда прямая»).

Разбор: `docs/reports/investigations/forecast_straight_line_investigation.md`.

Прогноз v3.3.0 БОЛЬШЕ НЕ прямая с одинаковой дельтой:
  - точечный доход/расход — демпфированный Holt по РЕАЛЬНОЙ истории (наклон по данным);
  - баланс капитализируется по r_bench ⇒ траектория выпуклая, приращения РАЗНЫЕ.
Тесты фиксируют это, чтобы регресс к плоской линии/константной дельте был замечен.
"""
from app.core.forecast import choose_point_forecast, holt_forecast, monthly_rate, ses_forecast
from app.services.forecasting import build_monthly_history, forecast_indicators

FLAT = dict(balance=100_000, rt=20_000, lt=3.0, dt=0.25,
            income_total=80_000, expense_total=50_000, obligation_payments=10_000)


def _deltas(xs):
    return [round(xs[i + 1] - xs[i], 2) for i in range(len(xs) - 1)]


class TestForecastIsCurvedNotConstantDelta:
    def test_compounding_makes_deltas_non_constant(self):
        """При r_bench>0 приращения баланса РАЗНЫЕ — не «одна и та же дельта»."""
        rt = [f["Rt"] for f in forecast_indicators(**FLAT, r_bench=0.14)["forecast"]]
        d1 = _deltas(rt)
        assert len(set(round(x) for x in d1)) > 1  # дельты различаются

    def test_trajectory_is_convex_under_positive_rate(self):
        """Капитализация при положительном потоке даёт выпуклость: вторые разности > 0."""
        rt = [f["Rt"] for f in forecast_indicators(**FLAT, r_bench=0.14)["forecast"]]
        d1 = _deltas(rt)
        second = _deltas(d1)
        assert all(s > 0 for s in second)  # ускоряющийся рост

    def test_zero_rate_flat_history_reduces_to_linear(self):
        """Контроль источника кривизны: r_bench=0 + ЯВНО плоская история ⇒ снова
        прямая (одинаковая дельта). Значит нелинейность даёт именно капитализация."""
        rt = [f["Rt"] for f in forecast_indicators(
            balance=100_000, rt=20_000, lt=3.0, dt=0.25,
            income_total=80_000, expense_total=50_000, obligation_payments=10_000,
            income_history=[80_000] * 6, expense_history=[50_000] * 6,
            obligation_history=[10_000] * 6, r_bench=0.0,
        )["forecast"]]
        second = _deltas(_deltas(rt))
        assert all(abs(s) <= 0.02 for s in second)  # линейно с точностью до копеек


class TestHoltUsesRealTrend:
    def test_rising_history_yields_rising_income_forecast(self):
        """Растущая реальная история ⇒ наклонный (не плоский) прогноз дохода."""
        rising = [50_000 * (1.08 ** i) for i in range(6)]
        fc = forecast_indicators(
            balance=100_000, rt=5_000, lt=2.0, dt=0.24,
            income_total=rising[-1], expense_total=45_000, obligation_payments=12_000,
            income_history=rising, expense_history=[45_000] * 6, r_bench=0.14,
        )["forecast"]
        income = [f["income"] for f in fc]
        assert income[-1] > income[0]                 # прогноз растёт вслед за историей
        assert len(set(round(x) for x in income)) > 1  # не константа

    def test_falling_history_yields_falling_income_forecast(self):
        falling = [80_000 * (0.95 ** i) for i in range(6)]
        out = choose_point_forecast(falling, horizon=6)
        assert out[-1] < out[0]

    def test_damped_trend_stays_bounded_and_non_negative(self):
        """Демпфирование не даёт тренду улетать; денежный прогноз ≥ 0."""
        rising = [10_000 * (1.5 ** i) for i in range(4)]  # агрессивный рост
        out = holt_forecast(rising, horizon=24)
        assert all(v >= 0 for v in out)
        # затухание: последний шаг меньше первого шага прогноза
        step_first = out[1] - out[0]
        step_last = out[-1] - out[-2]
        assert step_last <= step_first + 1e-6


class TestFallbacksAndHelpers:
    def test_ses_fallback_for_short_history(self):
        """<3 наблюдений ⇒ SES-фолбэк (плоско)."""
        out = choose_point_forecast([100_000, 105_000], horizon=6)
        assert len(set(out)) == 1

    def test_monthly_rate_matches_annual_compounding(self):
        r = monthly_rate(0.14)
        assert abs((1 + r) ** 12 - 1.14) < 1e-9

    def test_build_monthly_history_rolling_bins(self):
        """Скользящие 30-дневные корзины относительно now, старые → свежие."""
        import datetime

        now = datetime.datetime(2026, 7, 11)

        class T:
            def __init__(self, days_ago, a, t):
                self.date = now - datetime.timedelta(days=days_ago)
                self.amount = a
                self.type = t

        txs = [T(5, 60_000, "income"), T(40, 50_000, "income"),
               T(5, 41_000, "expense"), T(40, 40_000, "expense")]
        h = build_monthly_history(txs, months=8, now=now)
        assert h["income"][-1] == 60_000.0   # текущие 30 дней — последний элемент
        assert h["income"][-2] == 50_000.0   # предыдущий месяц
        assert h["expense"][-1] == 41_000.0
        assert h["months"] == 2


class TestMonteCarloBandStillProportional:
    def test_band_grows_for_healthy_growing_balance(self):
        """Для растущего положительного баланса коридор p90−p10 расширяется."""
        fc = forecast_indicators(**FLAT, r_bench=0.14)["forecast"]
        widths = [f["Rt_p90"] - f["Rt_p10"] for f in fc]
        assert widths[-1] > widths[0]
