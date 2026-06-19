"""Тесты базовых финансовых показателей (формулы ВКР §3)."""
import pytest

from app.core.metrics import (
    calculate_blr,
    calculate_cft,
    calculate_dt,
    calculate_expense_total,
    calculate_income_total,
    calculate_lt,
    calculate_rt,
    classify_blr,
    sum_obligation_payments,
)


class TestTotals:
    def test_income_total(self):
        tx = [
            {"amount": 100, "type": "income"},
            {"amount": 50, "type": "income"},
            {"amount": 30, "type": "expense"},
        ]
        assert calculate_income_total(tx) == 150

    def test_expense_total(self):
        tx = [
            {"amount": 100, "type": "income"},
            {"amount": 30, "type": "expense"},
            {"amount": 20, "type": "expense"},
        ]
        assert calculate_expense_total(tx) == 50

    def test_empty(self):
        assert calculate_income_total([]) == 0
        assert calculate_expense_total([]) == 0

    def test_obligation_payments(self):
        obls = [{"monthly_payment": 15000}, {"monthly_payment": 8000}]
        assert sum_obligation_payments(obls) == 23000


class TestCashFlow:
    def test_cft(self):
        tx = [{"amount": 1000, "type": "income"}, {"amount": 400, "type": "expense"}]
        assert calculate_cft(tx) == 600

    def test_rt(self):
        # Rt = CF − ΣP
        assert calculate_rt(600, 200) == 400

    def test_rt_negative(self):
        assert calculate_rt(100, 300) == -200


class TestLiquidity:
    def test_lt(self):
        # Lt = Rt / (E + ΣP) = 400 / (400 + 200)
        assert calculate_lt(400, 400, 200) == pytest.approx(0.6667, rel=1e-3)

    def test_lt_zero_denominator(self):
        assert calculate_lt(400, 0, 0) == 0.0


class TestDebt:
    def test_dt(self):
        # Dt = ΣP / I — ПДН 20%
        assert calculate_dt(200, 1000) == pytest.approx(0.2)

    def test_dt_zero_income(self):
        assert calculate_dt(200, 0) == 0.0


class TestBLR:
    def test_blr(self):
        # BLR = (B + Bliq) / E = (1000 + 2000) / 1000
        assert calculate_blr(1000, 2000, 1000) == 3.0

    def test_blr_zero_expense(self):
        assert calculate_blr(1000, 2000, 0) == 0.0

    @pytest.mark.parametrize("blr,level", [
        (0.5, "critical"),
        (1.5, "weak"),
        (3.0, "normal"),
        (7.0, "surplus"),
    ])
    def test_classify_blr_boundaries(self, blr, level):
        assert classify_blr(blr)["level"] == level
