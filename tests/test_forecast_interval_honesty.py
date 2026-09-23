"""Коридор прогноза обязан накрывать правду примерно в 80 % случаев (WORK_QUEUE P0 §2, ДК-15).

Замер Г43 по функции продукта `forecast_indicators`: коридор, заявленный как 80 %, накрывал
правду в 7–47 % случаев; у человека с нулевым балансом — **6,8 %**. Причина в самой формуле:
ширина берётся от величины показателя (`sigma_abs = |point| * sigma_h`), а не от разброса
собственного потока человека, растёт как sqrt(1 + 0.5h) — медленнее, чем растёт
неопределённость суммы потоков, — и одинакова для зарплатника и фрилансера.

Тесты ниже проверяют не формулу, а обещание: «80 %» должно быть правдой, и ширина должна
зависеть от разброса потока, а не от размера счёта.
"""
import random

from app.services.forecasting import forecast_indicators

HORIZON = 6
TOLERANCE = 0.12  # допуск к заявленным 80 %: ±12 п.п. при 300 портретах


def _coverage(portraits, horizon_index):
    hits = 0
    for income_history, expense_history, payment, balance, future in portraits:
        fc = forecast_indicators(
            balance=balance, rt=balance, lt=0, dt=0,
            income_total=income_history[-1], expense_total=expense_history[-1],
            obligation_payments=payment, horizon=HORIZON,
            income_history=list(income_history), expense_history=list(expense_history),
            obligation_history=[payment] * len(income_history), r_bench=0.0,
        )["forecast"][horizon_index]
        # Правда считается ПО ТОЙ ЖЕ формуле канона, что и прогноз: Rt = Bt + CF − P,
        # где Bt уже накопил поток. Двойной учёт последнего месяца — отдельный дефект
        # (ДК-22), и проверять здесь надо интервал, а не его.
        truth = balance + sum(future[: horizon_index + 1]) + future[horizon_index]
        if fc["Rt_p10"] <= truth <= fc["Rt_p90"]:
            hits += 1
    return hits / len(portraits)


def _make_portraits(n, balance_factor, seed):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        base = rng.uniform(40_000, 250_000)
        volatility = rng.choice([0.05, 0.15, 0.30])
        income = [base * (1 + rng.uniform(-volatility, volatility)) for _ in range(6 + HORIZON)]
        expense = [base * 0.6 * (1 + rng.uniform(-0.1, 0.1)) for _ in range(6 + HORIZON)]
        payment = base * rng.uniform(0.0, 0.2)
        net_future = [income[i] - expense[i] - payment for i in range(6, 6 + HORIZON)]
        out.append((income[:6], expense[:6], payment, base * balance_factor, net_future))
    return out


class TestCorridorKeepsItsPromise:
    def test_first_month_covers_about_eighty_percent(self):
        cov = _coverage(_make_portraits(300, balance_factor=1.0, seed=901), horizon_index=0)
        assert 0.80 - TOLERANCE <= cov <= 0.80 + TOLERANCE, f"покрытие первого месяца {cov:.1%}"

    def test_zero_balance_user_is_not_promised_certainty(self):
        """Человек без запаса — самый уязвимый; сейчас у него коридор схлопывается."""
        cov = _coverage(_make_portraits(300, balance_factor=0.0, seed=902), horizon_index=0)
        assert cov >= 0.80 - TOLERANCE, f"покрытие при нулевом балансе {cov:.1%}"


class TestWidthComesFromFlowNotFromBalance:
    def test_same_flow_different_balance_gives_similar_width(self):
        """Один и тот же поток и разброс: размер счёта не должен менять ширину коридора."""
        args = dict(rt=20_000, lt=3.0, dt=0.25, income_total=80_000, expense_total=50_000,
                    obligation_payments=10_000, horizon=3,
                    income_history=[80_000, 76_000, 84_000, 79_000, 81_000, 80_000],
                    expense_history=[50_000] * 6, obligation_history=[10_000] * 6, r_bench=0.0)
        poor = forecast_indicators(balance=0, **args)["forecast"][0]
        rich = forecast_indicators(balance=600_000, **args)["forecast"][0]
        width_poor = poor["Rt_p90"] - poor["Rt_p10"]
        width_rich = rich["Rt_p90"] - rich["Rt_p10"]
        assert width_poor > 0, "коридор не может быть нулевым"
        ratio = max(width_poor, width_rich) / max(min(width_poor, width_rich), 1e-9)
        assert ratio <= 1.5, f"ширина зависит от баланса: {width_poor:.0f} против {width_rich:.0f}"
