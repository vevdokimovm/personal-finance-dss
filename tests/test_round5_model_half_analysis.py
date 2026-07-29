"""Тесты анализатора модельной половины раунда 5.

Проверяется ровно то, ради чего инструмент написан:
  * пропуски слоя D раскладываются по манифесту `expected_error` (иначе
    «600/625» не отличить от неизвестной течи валидатора);
  * `invalid` вне слоя D считается ложным срабатыванием;
  * метаморфические пары берутся ТОЛЬКО по `pair_relation` M*, а не по
    наличию `pair_id` (группы дублей id тоже носят pair_id и раньше
    засоряли метрику неполными парами);
  * жёсткие ожидания статуса: M2/M3/M4/M5 — статус неизменен, M1 —
    допустим только deficit -> ok;
  * семейства и доминанты собираются по ключу координатора.
"""
from __future__ import annotations

import pytest

from tools.model_validation.round5_model_half_analysis import analyse


def key_row(rid, layer="A", kind="population", family="", pair_id="",
            pair_role="", pair_relation="", expected_error=""):
    return {"id": rid, "layer": layer, "kind": kind, "family": family,
            "pair_id": pair_id, "pair_role": pair_role,
            "pair_relation": pair_relation, "expected_error": expected_error,
            "id_override": ""}


def outcome(rid, status="ok", dom="debt", xo=0.0, xr=0.0, xg=0.0,
            invest=0.0, rt=100.0, lt=2.0, invalid_reason="", lump=0.0):
    return {"id": rid, "kind": "", "risk": "3", "status": status,
            "rt": str(rt), "lt": str(lt), "dt": "0.1", "xo": str(xo),
            "xr": str(xr), "xg": str(xg), "invest": str(invest), "dom": dom,
            "dt_alert": "0", "crisis_severity": "", "crisis_actions": "",
            "invalid_reason": invalid_reason, "model_lump": str(lump),
            "model_lump_debt": "0", "model_lump_reserve": "0",
            "model_lump_goal": "0"}


class TestSizeContract:
    def test_size_mismatch_is_fail_loud(self):
        with pytest.raises(SystemExit):
            analyse([outcome("SP5-00000")],
                    [key_row("SP5-00000"), key_row("SP5-00001")])


class TestDefectLayer:
    def test_missed_defect_is_attributed_to_expected_error(self):
        keys = [key_row("SP5-00000", layer="D", kind="near_rate_above_cap",
                        expected_error="obligations.interest_rate:cap"),
                key_row("SP5-00001", layer="D", kind="negative_income",
                        expected_error="income_total:negative")]
        rows = [outcome("SP5-00000", status="ok"),
                outcome("SP5-00001", status="invalid",
                        invalid_reason="income_total отрицательное: -1")]
        d = analyse(rows, keys)["d_layer"]
        assert d["total"] == 2
        assert d["invalid"] == 1
        assert d["missed"] == 1
        assert d["missed_by_expected_error"] == {
            "obligations.interest_rate:cap": {"missed": 1, "total": 1}}

    def test_invalid_outside_defect_layer_is_false_positive(self):
        keys = [key_row("SP5-00000", layer="A")]
        rows = [outcome("SP5-00000", status="invalid")]
        d = analyse(rows, keys)["d_layer"]
        assert d["false_positives_on_valid"] == 1

    def test_reasons_are_grouped_by_prefix(self):
        keys = [key_row("SP5-00000", layer="D", expected_error="e"),
                key_row("SP5-00001", layer="D", expected_error="e")]
        rows = [outcome("SP5-00000", status="invalid",
                        invalid_reason="bliq отрицательное: -1"),
                outcome("SP5-00001", status="invalid",
                        invalid_reason="bliq отрицательное: -2")]
        assert analyse(rows, keys)["d_layer"]["reasons"] == {
            "bliq отрицательное": 2}


class TestMetamorphic:
    def _pair(self, relation, base_status="ok", twin_status="ok",
              base_dom="debt", twin_dom="debt"):
        keys = [key_row("SP5-00000", layer="E", kind="metamorphic",
                        pair_id="E5-0000", pair_role="base",
                        pair_relation=relation),
                key_row("SP5-00001", layer="E", kind="metamorphic",
                        pair_id="E5-0000", pair_role="twin",
                        pair_relation=relation)]
        rows = [outcome("SP5-00000", status=base_status, dom=base_dom,
                        xo=100.0, rt=100.0),
                outcome("SP5-00001", status=twin_status, dom=twin_dom,
                        xo=100.0, rt=100.0)]
        return analyse(rows, keys)["metamorphic"][relation]

    def test_stable_status_is_not_a_violation(self):
        assert self._pair("M4_bliq")["status_violations"] == []

    def test_status_regression_is_a_violation(self):
        slot = self._pair("M4_bliq", base_status="ok", twin_status="deficit")
        assert len(slot["status_violations"]) == 1

    def test_income_growth_may_lift_deficit_to_ok(self):
        slot = self._pair("M1_income", base_status="deficit",
                          twin_status="ok")
        assert slot["status_violations"] == []

    def test_income_growth_may_not_drop_ok_to_deficit(self):
        slot = self._pair("M1_income", base_status="ok",
                          twin_status="deficit")
        assert len(slot["status_violations"]) == 1

    def test_dominant_flip_counted_but_not_a_violation(self):
        slot = self._pair("M2_rate_single", base_dom="reserve",
                          twin_dom="debt")
        assert slot["dom_flips"] == 1
        assert slot["status_violations"] == []

    def test_duplicate_id_groups_are_not_metamorphic_pairs(self):
        keys = [key_row("SP5-00000", layer="C", kind="duplicate_id_valid_pair",
                        family="integrity_edges", pair_id="DUP-0000"),
                key_row("SP5-00001", layer="C", kind="duplicate_id_valid_pair",
                        family="integrity_edges", pair_id="DUP-0000")]
        rows = [outcome("SP5-00000"), outcome("SP5-00001")]
        assert analyse(rows, keys)["metamorphic"] == {}

    def test_scaling_by_ten_gives_l1_of_nine_rt(self):
        keys = [key_row("SP5-00000", layer="E", pair_id="E5-0001",
                        pair_role="base", pair_relation="M5_scale"),
                key_row("SP5-00001", layer="E", pair_id="E5-0001",
                        pair_role="twin", pair_relation="M5_scale")]
        rows = [outcome("SP5-00000", xo=100.0, rt=100.0),
                outcome("SP5-00001", xo=1000.0, rt=1000.0)]
        slot = analyse(rows, keys)["metamorphic"]["M5_scale"]
        assert slot["l1_rel_median"] == pytest.approx(9.0)


class TestFamiliesAndLump:
    def test_family_status_and_dominants(self):
        keys = [key_row("SP5-00000", layer="C", family="floor_edge"),
                key_row("SP5-00001", layer="C", family="floor_edge"),
                key_row("SP5-00002", layer="A")]
        rows = [outcome("SP5-00000", status="ok", dom="reserve"),
                outcome("SP5-00001", status="deficit", dom="none"),
                outcome("SP5-00002", status="ok", dom="debt")]
        fam = analyse(rows, keys)["families"]
        assert set(fam) == {"floor_edge"}
        assert fam["floor_edge"]["n"] == 2
        assert fam["floor_edge"]["dom_ok"] == {"reserve": 1}

    def test_lump_share_counts_only_positive_moves(self):
        keys = [key_row("SP5-00000"), key_row("SP5-00001")]
        rows = [outcome("SP5-00000", lump=0.0),
                outcome("SP5-00001", lump=500.0)]
        assert analyse(rows, keys)["lump"]["share_pct"] == pytest.approx(50.0)
