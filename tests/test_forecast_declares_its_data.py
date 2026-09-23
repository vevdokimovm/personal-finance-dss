"""Прогноз честно говорит, на чём он построен (WORK_QUEUE P0 §3, ДК-15).

Когда истории нет или в ней меньше двух точек, сервис достраивает ряд синтетикой
(`build_history_from_current`). Сам по себе фолбэк допустим — без него прогноза не было бы
вовсе, — но пользователь и фронтенд узнать об этом не могли: в контракте ответа не было
ни одного поля, отличающего расчёт по реальной истории от расчёта по выдуманной.

Плюс поле `method` описывало метод, которого в коде уже нет: «демпфированный Holt»
и «1000 случайных сценариев». Описание метода, разошедшееся с методом, хуже отсутствующего —
оно выглядит как факт.
"""
from app.services.forecasting import forecast_indicators

BASE = dict(balance=100_000, rt=20_000, lt=3.0, dt=0.25,
            income_total=80_000, expense_total=50_000, obligation_payments=10_000,
            horizon=3, r_bench=0.0)


class TestSyntheticHistoryIsDeclared:
    def test_no_history_is_marked_synthetic(self):
        out = forecast_indicators(**BASE)
        quality = out["data_quality"]
        assert quality["synthetic"] is True
        assert quality["history_months"] == 0
        assert quality["note"]

    def test_real_history_is_not_marked_synthetic(self):
        out = forecast_indicators(
            **BASE,
            income_history=[80_000, 78_000, 82_000, 79_000, 81_000, 80_000],
            expense_history=[50_000] * 6, obligation_history=[10_000] * 6)
        quality = out["data_quality"]
        assert quality["synthetic"] is False
        assert quality["history_months"] == 6

    def test_partial_history_counts_what_there_is(self):
        """Одна точка — это тоже «истории нет»: ряд всё равно достраивается синтетикой."""
        out = forecast_indicators(**BASE, income_history=[80_000],
                                  expense_history=[50_000], obligation_history=[10_000])
        assert out["data_quality"]["synthetic"] is True
        assert out["data_quality"]["history_months"] == 1


class TestMethodDescriptionMatchesTheMethod:
    def test_point_method_is_not_holt(self):
        text = forecast_indicators(**BASE)["method"]["point"]
        assert "Holt" not in text and "холт" not in text.lower()
        assert "SES" in text

    def test_interval_method_is_not_monte_carlo(self):
        text = forecast_indicators(**BASE)["method"]["interval"]
        assert "сценар" not in text.lower(), "Монте-Карло в коридоре больше не используется"
        assert "80" in text
