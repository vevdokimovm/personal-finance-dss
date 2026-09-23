"""Прогноз не изобретает тренд там, где его нет в данных (WORK_QUEUE P0 §1, ДК-37).

Замер Г43 (`docs/research/raw/statistical_forecasting_methods_2026-09-17.md`): точечный
прогноз продуктом — демпфированный Holt с зашитыми константами — оказался худшим из 14
методов на всех длинах истории. Ошибка суммы за шесть месяцев: 0.606 против 0.205 у среднего
при трёх точках истории, 0.319 против 0.180 при шести, 0.227 против 0.144 при двенадцати;
парный бутстрэп даёт разницу +0.135 доли дохода, 95 % CI [+0.106, +0.165] — 43 % всей ошибки.
Механизм: при трёх точках `holt_forecast` берёт тренд как разницу первых двух наблюдений,
и одна случайная разница становится трендом на полгода.

Канон §15 при этом описывает SES α = 0.3 — код разошёлся с каноном в худшую сторону.
Тесты ниже фиксируют канонное поведение и запрещают регресс к выдуманному тренду.
"""
import random

from app.core.forecast import choose_point_forecast, ses_forecast


class TestNoTrendFromNoise:
    def test_three_noisy_points_give_flat_forecast(self):
        """Три точки вокруг одного уровня — прогноз плоский, без наклона."""
        history = [100_000.0, 96_000.0, 104_000.0]
        out = choose_point_forecast(history, horizon=6)
        assert len(set(round(v, 2) for v in out)) == 1

    def test_first_two_points_do_not_become_a_trend(self):
        """Случайная разница первых двух наблюдений не должна задавать наклон на полгода."""
        rising_start = choose_point_forecast([80_000.0, 120_000.0, 100_000.0], horizon=6)
        falling_start = choose_point_forecast([120_000.0, 80_000.0, 100_000.0], horizon=6)
        assert rising_start[-1] == rising_start[0]
        assert falling_start[-1] == falling_start[0]

    def test_matches_canon_ses(self):
        """Точечный прогноз продукта совпадает с SES α = 0.3 канона §15."""
        history = [90_000.0, 110_000.0, 95_000.0, 105_000.0]
        assert choose_point_forecast(history, horizon=4) == ses_forecast(history, horizon=4)


class TestErrorNotWorseThanMean:
    """Регрессия против замера Г43: ошибка суммы за шесть месяцев не хуже среднего по истории.

    Ряды — шум вокруг уровня и уровень со сдвигом; именно на них зашитый Holt проигрывал
    в разы. Сравнение с простым средним — нижняя планка, а не идеал.
    """

    HORIZON = 6

    def _error(self, method, history, future):
        forecast = method(history)
        scale = sum(history) / len(history)
        return abs(sum(forecast) - sum(future)) / self.HORIZON / scale

    def test_not_worse_than_mean_on_noisy_levels(self):
        rng = random.Random(4307)
        product_errors, mean_errors = [], []
        for _ in range(200):
            base = rng.uniform(40_000, 250_000)
            series = [base * (1 + rng.uniform(-0.2, 0.2)) for _ in range(9)]
            history, future = series[:3], series[3:]
            product_errors.append(self._error(
                lambda h: choose_point_forecast(h, horizon=self.HORIZON), history, future))
            mean_errors.append(self._error(
                lambda h: [sum(h) / len(h)] * self.HORIZON, history, future))
        product = sum(product_errors) / len(product_errors)
        mean = sum(mean_errors) / len(mean_errors)
        assert product <= mean * 1.10, f"прогноз продукта {product:.3f} против среднего {mean:.3f}"
