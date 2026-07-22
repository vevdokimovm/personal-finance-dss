"""Тесты сборщика joined раунда 4: confidence, разбор lump по назначению,
action-vector.

Новое против раунда 3:
  * колонка `confidence` 1-5 (обязательна, enum целых);
  * `lump_sum_plan` из jsonl раскладывается по направлениям (debt/reserve/
    goals+) — словари действий у каждого эксперта свои, нормализуются картой;
  * метрика action-vector: месячный сплит и разовые ходы сводятся в один
    вектор через горизонт H месяцев (закрывает дефект р.3 — месячная
    доминанта на stock-данных частично невалидна).
"""
from __future__ import annotations

import pytest

from tools.model_validation.build_joined_v4 import (
    ACTION_HORIZON_MONTHS,
    BudgetContext,
    LUMP_ACTION_MAP,
    action_vector,
    check_expert_row,
    lump_by_direction,
    parse_confidence,
    validate_id_sequence,
)


class TestValidateIdSequence:
    def test_exact_match_passes(self):
        validate_id_sequence("x", ["SP4-00000"], ["SP4-00000"])

    def test_mismatch_fails_loud_with_position(self):
        with pytest.raises(ValueError, match="строка 2"):
            validate_id_sequence("x", ["SP4-00000", "SP4-00002"],
                                 ["SP4-00000", "SP4-00001"])


class TestParseConfidence:
    def test_int_in_range(self):
        assert parse_confidence("x", 1, "3") == 3

    def test_float_string_truncated_to_int(self):
        assert parse_confidence("x", 1, "4.0") == 4

    def test_out_of_range_fails(self):
        with pytest.raises(ValueError, match="confidence"):
            parse_confidence("x", 1, "6")

    def test_missing_fails(self):
        with pytest.raises(ValueError, match="confidence"):
            parse_confidence("x", 1, "")


class TestCheckExpertRow:
    def _row(self, **kw):
        base = {"id": "SP4-00000", "status": "ok", "dom": "reserve",
                "res": "1000", "debt": "0", "goal": "0", "inv": "0",
                "lump": "0", "confidence": "4"}
        base.update(kw)
        return base

    def test_valid_row_within_budget(self):
        ctx = BudgetContext()
        nums, conf = check_expert_row("x", 0, self._row(), fcf=1500.0, ctx=ctx)
        assert conf == 4 and not ctx.violations and nums["res"] == 1000.0

    def test_budget_violation_recorded_not_raised(self):
        ctx = BudgetContext()
        check_expert_row("x", 0, self._row(res="2000"), fcf=1500.0, ctx=ctx)
        assert ctx.violations

    def test_invalid_row_shape_violation_recorded(self):
        ctx = BudgetContext()
        check_expert_row("x", 1, self._row(status="invalid", dom="debt"),
                         fcf=None, ctx=ctx)
        assert ctx.invalid_shape_violations


class TestLumpByDirection:
    def test_known_vocabularies_map_to_three_directions(self):
        plan = [{"kind": "repay_debt", "amount": 100},
                {"kind": "close_goal", "amount": 50},
                {"action": "deploy_surplus_risk_free", "amount": 25}]
        got = lump_by_direction(plan)
        assert got["debt"] == 100.0
        assert got["goals+"] == 75.0
        assert got["reserve"] == 0.0

    def test_unknown_action_raises_fail_loud(self):
        with pytest.raises(ValueError, match="неизвестное действие"):
            lump_by_direction([{"action": "teleport_money", "amount": 1}])

    def test_every_mapped_action_targets_valid_direction(self):
        assert set(LUMP_ACTION_MAP.values()) <= {"debt", "reserve", "goals+"}

    def test_empty_plan_is_zero_vector(self):
        assert lump_by_direction([]) == {"debt": 0.0, "reserve": 0.0,
                                         "goals+": 0.0}


class TestActionVector:
    def test_monthly_only_matches_monthly_dominance(self):
        vec, dom = action_vector(monthly={"debt": 0.0, "reserve": 500.0,
                                          "goals+": 100.0},
                                 lump={"debt": 0.0, "reserve": 0.0,
                                       "goals+": 0.0})
        assert dom == "reserve"
        assert vec["reserve"] == 500.0 * ACTION_HORIZON_MONTHS

    def test_lump_overturns_monthly_dominance(self):
        """Ключевой дефект р.3: месяц говорит goals+, а действие — debt."""
        vec, dom = action_vector(
            monthly={"debt": 0.0, "reserve": 0.0, "goals+": 24_380.0},
            lump={"debt": 1_225_223.0, "reserve": 0.0, "goals+": 0.0})
        assert dom == "debt"
        assert vec["debt"] > vec["goals+"]

    def test_all_zero_is_none(self):
        _, dom = action_vector(monthly={"debt": 0.0, "reserve": 0.0,
                                        "goals+": 0.0},
                               lump={"debt": 0.0, "reserve": 0.0,
                                     "goals+": 0.0})
        assert dom == "none"

    def test_tie_resolves_deterministically_by_priority(self):
        _, dom = action_vector(monthly={"debt": 1.0, "reserve": 1.0,
                                        "goals+": 0.0},
                               lump={"debt": 0.0, "reserve": 0.0,
                                     "goals+": 0.0})
        assert dom == "debt"
