"""Предзарегистрированная гипотеза раунда 4: токсичный долг пробивает floor.

Правило зарегистрировано ДО прогона (v6.15.0): долг считается
токсичным при ставке >= max(30%, r_bench + 15 п.п.); при его наличии floor
резерва опускается с 2.0 до TOXIC_FLOOR_MONTHS месяцев, потому что лавина по
ставке 40-290% съедает подушку быстрее, чем подушка страхует.
"""
from __future__ import annotations

from app.core.ranking import (
    RESERVE_FLOOR_MONTHS,
    TOXIC_FLOOR_MONTHS,
    effective_floor_months,
    rank_alternatives,
)


class TestEffectiveFloorMonths:
    def _obl(self, rate):
        return {"amount": 100_000, "interest_rate": rate,
                "monthly_payment": 5_000}

    def test_no_obligations_keeps_base_floor(self):
        assert effective_floor_months([], r_bench=0.14) == RESERVE_FLOOR_MONTHS

    def test_cheap_debt_keeps_base_floor(self):
        assert effective_floor_months([self._obl(0.18)],
                                      r_bench=0.14) == RESERVE_FLOOR_MONTHS

    def test_absolute_threshold_thirty_percent(self):
        """При низком бенчмарке решает абсолютный порог 30%."""
        assert effective_floor_months([self._obl(0.30)],
                                      r_bench=0.08) == TOXIC_FLOOR_MONTHS
        assert effective_floor_months([self._obl(0.2999)],
                                      r_bench=0.08) == RESERVE_FLOOR_MONTHS

    def test_spread_threshold_when_benchmark_high(self):
        """При бенчмарке 24% токсичность начинается с 39%, а не с 30%."""
        assert effective_floor_months([self._obl(0.35)],
                                      r_bench=0.24) == RESERVE_FLOOR_MONTHS
        assert effective_floor_months([self._obl(0.39)],
                                      r_bench=0.24) == TOXIC_FLOOR_MONTHS

    def test_repaid_debt_does_not_count(self):
        obl = self._obl(0.50)
        obl["amount"] = 0
        assert effective_floor_months([obl],
                                      r_bench=0.14) == RESERVE_FLOOR_MONTHS

    def test_one_toxic_among_cheap_is_enough(self):
        assert effective_floor_months(
            [self._obl(0.12), self._obl(0.60)],
            r_bench=0.14) == TOXIC_FLOOR_MONTHS


class TestRankAlternativesFloorOverride:
    def _alt(self, lt, utility_driver):
        return {"Rt_new": utility_driver, "Lt_new": lt, "Dt_new": 0.2,
                "Si": utility_driver, "x_obligations": 0.0,
                "x_reserve": 0.0, "goal_allocation": {}}

    def test_default_floor_is_base_constant(self):
        alts = [self._alt(1.5, 0.0), self._alt(1.0, 100.0)]
        ranked = rank_alternatives(alts, risk_tolerance=3)
        assert ranked[0]["Lt_new"] == 1.5  # floor важнее полезности

    def test_lowered_floor_lets_utility_win(self):
        alts = [self._alt(1.5, 0.0), self._alt(1.0, 100.0)]
        ranked = rank_alternatives(alts, risk_tolerance=3, floor_months=1.0)
        assert ranked[0]["Lt_new"] == 1.0  # обе набрали floor -> решает utility

    def test_floor_level_capped_by_given_floor(self):
        alts = [self._alt(5.0, 1.0)]
        ranked = rank_alternatives(alts, risk_tolerance=3, floor_months=1.0)
        assert ranked[0]["floor_level"] == 1.0
