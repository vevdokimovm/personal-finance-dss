"""Тесты сборщика joined раунда 5.

Контракт наследован от раунда 4 без изменений — это условие сравнимости
раундов, поэтому тесты проверяют именно НЕизменность контракта плюс то
новое, что появилось в раунде 5: словари разовых ходов четырёх экспертов.
"""
from __future__ import annotations

import pytest

from tools.model_validation.build_joined_v4 import (
    LUMP_ACTION_MAP as MAP_V4,
    action_vector as action_vector_v4,
)
from tools.model_validation.build_joined_v5 import (
    ACTION_HORIZON_MONTHS,
    BudgetContext,
    LUMP_ACTION_MAP,
    action_vector,
    check_expert_row,
    lump_by_direction,
    validate_id_sequence,
)


class TestContractUnchanged:
    def test_horizon_matches_round_four(self):
        assert ACTION_HORIZON_MONTHS == 12.0

    def test_v4_vocabulary_is_a_subset(self):
        assert set(MAP_V4) <= set(LUMP_ACTION_MAP)

    def test_action_vector_identical_to_round_four(self):
        monthly = {"debt": 100.0, "reserve": 50.0, "goals+": 0.0}
        lump = {"debt": 0.0, "reserve": 900.0, "goals+": 0.0}
        assert action_vector(monthly, lump) == action_vector_v4(monthly, lump)


class TestRoundFiveVocabularies:
    @pytest.mark.parametrize("action", [
        "close_debt_to_free_payment", "close_expensive_debt",
        "close_toxic_debt", "prepay_expensive_debt", "prepay_toxic_debt",
        "prepay_debt_partial", "pay_down_debt_from_savings",
    ])
    def test_debt_actions(self, action):
        assert lump_by_direction([{"action": action, "amount": 10}])["debt"] == 10

    @pytest.mark.parametrize("action", [
        "deploy_surplus_to_investments", "fund_goal_from_savings",
        "top_up_goal", "invest_surplus", "fund_goal",
    ])
    def test_goal_actions(self, action):
        vec = lump_by_direction([{"action": action, "amount": 7}])
        assert vec["goals+"] == 7

    def test_unknown_action_fails_loud(self):
        with pytest.raises(ValueError, match="неизвестное действие"):
            lump_by_direction([{"action": "buy_crypto", "amount": 1}])


class TestAcceptance:
    def test_id_sequence_position_reported(self):
        with pytest.raises(ValueError, match="строка 2"):
            validate_id_sequence("v", ["SP5-00000", "SP5-00002"],
                                 ["SP5-00000", "SP5-00001"])

    def test_budget_overspend_recorded(self):
        ctx = BudgetContext()
        row = {"status": "ok", "dom": "debt", "res": "0", "debt": "500",
               "goal": "0", "inv": "0", "lump": "0", "confidence": "3"}
        check_expert_row("v", 1, row, fcf=100.0, ctx=ctx)
        assert len(ctx.violations) == 1

    def test_invalid_must_be_zeroed(self):
        ctx = BudgetContext()
        row = {"status": "invalid", "dom": "debt", "res": "0", "debt": "5",
               "goal": "0", "inv": "0", "lump": "0", "confidence": "1"}
        check_expert_row("v", 1, row, fcf=None, ctx=ctx)
        assert len(ctx.invalid_shape_violations) == 1
