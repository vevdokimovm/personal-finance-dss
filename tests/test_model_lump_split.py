"""Разбор разового хода модели по направлениям (для метрики action-vector).

`model_lump` был одним числом — для сравнения с экспертами раунда 4 нужен
вектор: куда именно модель отправила деньги из накоплений.
"""
from __future__ import annotations

from tools.model_validation.expert_agreement import lump_split


class TestLumpSplit:
    def test_repay_debt_goes_to_debt(self):
        result = {"surplus_plan": {"moves": [
            {"type": "repay_debt", "amount": 100_000.0}]}}
        assert lump_split(result) == {"debt": 100_000.0, "reserve": 0.0,
                                      "goals+": 0.0}

    def test_fund_goal_and_invest_lump_go_to_goals_plus(self):
        result = {"surplus_plan": {"moves": [
            {"type": "fund_goal", "amount": 30_000.0},
            {"type": "invest_lump", "amount": 20_000.0}]}}
        assert lump_split(result)["goals+"] == 50_000.0

    def test_prealloc_goes_to_goals_plus(self):
        result = {"bliq_preallocation": {"bliq_used": 75_000.0}}
        assert lump_split(result)["goals+"] == 75_000.0

    def test_crisis_debt_closing_goes_to_debt(self):
        result = {"crisis_plan": {"actions": [
            {"type": "close_debts_from_liquidity", "bliq_used": 40_000.0}]}}
        assert lump_split(result)["debt"] == 40_000.0

    def test_empty_result_is_zero_vector(self):
        assert lump_split({}) == {"debt": 0.0, "reserve": 0.0, "goals+": 0.0}

    def test_sum_equals_legacy_model_lump(self):
        result = {
            "bliq_preallocation": {"bliq_used": 10.0},
            "surplus_plan": {"moves": [{"type": "repay_debt", "amount": 20.0},
                                       {"type": "invest_lump",
                                        "amount": 5.0}]},
            "crisis_plan": {"actions": [
                {"type": "close_debts_from_liquidity", "bliq_used": 7.0}]},
        }
        assert sum(lump_split(result).values()) == 42.0
