"""Тесты помесячного графика погашения долга — baseline vs накопительная лавина
(ADR-016, канон v3.8.0, §10.5)."""
from app.core.amortization import (
    MAX_HORIZON_MONTHS,
    _simulate,
    build_debt_amortization_schedule,
)
from app.core.avalanche import select_avalanche_targets


def _obligations():
    return [
        {"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.24},
        {"id": 2, "amount": 50000, "monthly_payment": 3000, "interest_rate": 0.08},
    ]


class TestDebtAmortizationSchedule:
    def test_basic_schedule_accelerated_faster(self):
        obls = [{"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.24}]
        summary = build_debt_amortization_schedule(obls, x_obl_monthly=3000, r_bench=0.14)
        assert summary is not None
        assert summary.accelerated_months < summary.baseline_months
        assert summary.interest_saved > 0
        assert summary.months_saved > 0
        assert summary.qualifying_debt_count == 1
        assert summary.horizon_capped is False
        assert summary.negative_amortization is False

    def test_accelerated_never_more_interest_than_baseline(self):
        for obls, extra, r_bench in (
            (_obligations(), 3000, 0.14),
            (_obligations(), 0.01, 0.14),
            ([{"id": 1, "amount": 300000, "monthly_payment": 8000, "interest_rate": 0.30}],
             10000, 0.14),
        ):
            summary = build_debt_amortization_schedule(obls, x_obl_monthly=extra, r_bench=r_bench)
            assert summary is not None
            assert summary.accelerated_total_interest <= summary.baseline_total_interest
            assert summary.accelerated_months <= summary.baseline_months

    def test_cascade_reallocation_after_payoff(self):
        # Долг 1 маленький и дорогой (закроется быстро), долг 2 большой и дешевле,
        # но всё ещё выше бенчмарка — оба таргеты. С каскадом освободившийся
        # платёж долга 1 должен ускорить долг 2 сильнее, чем без каскада.
        obligations = [
            {"id": 1, "amount": 20000, "monthly_payment": 5000, "interest_rate": 0.30},
            {"id": 2, "amount": 200000, "monthly_payment": 6000, "interest_rate": 0.20},
        ]
        target_order = [o["id"] for o in select_avalanche_targets(obligations, 0.14)]
        assert target_order == [1, 2]  # долг 1 дороже — приоритет

        months_cascade, _, _, _ = _simulate(
            obligations, target_order, extra_monthly=2000, cascade_freed=True,
            horizon_months=MAX_HORIZON_MONTHS,
        )
        months_no_cascade, _, _, _ = _simulate(
            obligations, target_order, extra_monthly=2000, cascade_freed=False,
            horizon_months=MAX_HORIZON_MONTHS,
        )
        assert months_cascade < months_no_cascade

    def test_term_zero_ignored_not_needed(self):
        # Реальные данные: term=0 (дефолт БД) и start_date отсутствует вовсе —
        # функция не должна их читать, срок погашения — выход, не вход.
        obls = [{"id": 1, "amount": 80000, "monthly_payment": 4000, "interest_rate": 0.20,
                 "term": 0}]
        summary = build_debt_amortization_schedule(obls, x_obl_monthly=2000, r_bench=0.14)
        assert summary is not None
        assert summary.baseline_months > 0

    def test_negative_amortization_terminates_and_flags(self):
        # monthly_payment (15000) <= месячные проценты (500000*0.48/12=20000):
        # тело баланса не убывает от минимального платежа — не должно повиснуть.
        obls = [{"id": 1, "amount": 500000, "monthly_payment": 15000, "interest_rate": 0.48}]
        summary = build_debt_amortization_schedule(obls, x_obl_monthly=100, r_bench=0.14)
        assert summary is not None
        assert summary.negative_amortization is True
        assert summary.horizon_capped is True
        assert summary.baseline_months == MAX_HORIZON_MONTHS

    def test_no_qualifying_debt_returns_none(self):
        obls = [{"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.08}]
        assert build_debt_amortization_schedule(obls, x_obl_monthly=3000, r_bench=0.14) is None

    def test_zero_extra_returns_none(self):
        summary = build_debt_amortization_schedule(_obligations(), x_obl_monthly=0, r_bench=0.14)
        assert summary is None

    def test_empty_obligations_returns_none(self):
        assert build_debt_amortization_schedule([], x_obl_monthly=3000, r_bench=0.14) is None

    def test_shared_target_selection_matches_avalanche(self):
        targets = select_avalanche_targets(_obligations(), 0.14)
        assert [o["id"] for o in targets] == [1]  # только id 1 (0.24 >= 0.14), по убыванию ставки

    def test_rounds_half_up_not_banker(self):
        # amount=100, rate=0.015 (1.5% годовых) → проценты за 1 месяц = 100*0.015/12 =
        # 0.125 ровно, точная граница копейки. Канон проекта — ROUND_HALF_UP (app/core/
        # money.py, скилл finpilot-money-format): 0.125 → 0.13. round() из stdlib на
        # точном float 0.125 применяет банковское round-half-to-even → 0.12 (неверно
        # по канону). Долг гасится за 1 месяц (monthly_payment=1000 >> amount+interest),
        # так что baseline_total_interest — это ровно эта одна начисленная сумма.
        obls = [{"id": 1, "amount": 100.0, "monthly_payment": 1000.0, "interest_rate": 0.015}]
        summary = build_debt_amortization_schedule(obls, x_obl_monthly=1.0, r_bench=0.01)
        assert summary is not None
        assert summary.baseline_months == 1
        assert summary.baseline_total_interest == 0.13
