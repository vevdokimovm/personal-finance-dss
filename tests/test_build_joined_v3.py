"""Тесты сборщика joined раунда 3 (позиционный контракт, enum с invalid)."""
from __future__ import annotations

import pytest

from tools.model_validation.build_joined_v3 import (
    BudgetContext,
    check_expert_row,
    validate_id_sequence,
)


class TestValidateIdSequence:
    def test_exact_match_passes(self):
        validate_id_sequence("x", ["SP3-00000", "SP3-00001"],
                             ["SP3-00000", "SP3-00001"])

    def test_mismatch_fails_loud_with_position(self):
        with pytest.raises(ValueError, match="строка 2"):
            validate_id_sequence("x", ["SP3-00000", "SP3-00002"],
                                 ["SP3-00000", "SP3-00001"])

    def test_length_mismatch_fails(self):
        with pytest.raises(ValueError, match="строк"):
            validate_id_sequence("x", ["SP3-00000"],
                                 ["SP3-00000", "SP3-00001"])


class TestCheckExpertRow:
    def _row(self, **kw):
        base = {"id": "SP3-00000", "status": "ok", "dom": "reserve",
                "res": "1000", "debt": "0", "goal": "0", "inv": "0", "lump": "0"}
        base.update(kw)
        return base

    def test_valid_ok_row_within_budget(self):
        ctx = BudgetContext()
        check_expert_row("x", 0, self._row(), fcf=1500.0, ctx=ctx)
        assert not ctx.violations

    def test_budget_violation_recorded_not_raised(self):
        ctx = BudgetContext()
        check_expert_row("x", 0, self._row(res="2000"), fcf=1500.0, ctx=ctx)
        assert ctx.violations and ctx.violations[0][0] == "x"

    def test_bad_enum_fails_loud(self):
        with pytest.raises(ValueError, match="status"):
            check_expert_row("x", 0, self._row(status="borked"),
                             fcf=1.0, ctx=BudgetContext())

    def test_invalid_row_must_be_none_and_zeros(self):
        ctx = BudgetContext()
        check_expert_row(
            "x", 0, self._row(status="invalid", dom="none",
                              res="0", lump="0"), fcf=None, ctx=ctx)
        assert not ctx.invalid_shape_violations
        check_expert_row(
            "x", 1, self._row(status="invalid", dom="debt", res="5"),
            fcf=None, ctx=ctx)
        assert ctx.invalid_shape_violations

    def test_nonnumeric_amount_fails_loud(self):
        with pytest.raises(ValueError, match="не число"):
            check_expert_row("x", 0, self._row(res="abc"),
                             fcf=1.0, ctx=BudgetContext())


class TestModelOutcomeR3:
    """R3-F1 (граница нуля) + model_lump для lump-стенда раунда 3."""

    def _portrait(self, **kw):
        base = {
            "income_total": 50_000.0, "expense_total": 20_000.0,
            "obligations": [], "goals": [], "bliq": 300_000.0,
            "r_bench": 0.15, "risk_tolerance": 3, "l_min": 0.0,
        }
        base.update(kw)
        return base

    def test_tiny_negative_flow_is_not_deficit(self):
        from tools.model_validation.expert_agreement import model_outcome
        o = model_outcome(self._portrait(expense_total=50_000.003))
        assert o["status"] != "deficit", "полкопейки не делают кризис (R3-F1)"

    def test_real_deficit_still_fires(self):
        from tools.model_validation.expert_agreement import model_outcome
        o = model_outcome(self._portrait(expense_total=50_000.05))
        assert o["status"] == "deficit"

    def test_model_lump_aggregates_stock_moves(self):
        from tools.model_validation.expert_agreement import model_outcome
        # излишек сверх целевой подушки => surplus-ходы; близкая цель =>
        # преаллокация из bliq; всё это - разовые ходы из накоплений
        p = self._portrait(
            bliq=1_000_000.0,
            goals=[{"id": 1, "name": "Отпуск", "target_amount": 60_000.0,
                    "current_amount": 55_000.0, "deadline": None}],
        )
        o = model_outcome(p)
        assert "model_lump" in o and o["model_lump"] > 0
