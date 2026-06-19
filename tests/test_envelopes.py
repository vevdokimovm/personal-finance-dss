"""Тесты ядра «конвертов» — связи цель↔ликвидный актив (вариант B).

Ключевой инвариант: деньги не учитываются дважды. Привязанный к цели актив
участвует только через цель (в Sn), свободный — только в Bliq (подушка).
Тесты написаны до реализации (TDD).
"""
import pytest

from app.core.envelopes import (
    apply_envelopes,
    assets_index,
    effective_goal_values,
    free_assets,
    linked_asset_ids,
)


def _goal(gid, current, rate=0.0, linked=None, target=100000):
    return {"id": gid, "name": f"goal{gid}", "target_amount": target,
            "current_amount": current, "savings_rate": rate,
            "linked_asset_id": linked, "category": "material"}


def _asset(aid, amount, rate=0.14):
    return {"id": aid, "name": f"asset{aid}", "amount": amount,
            "interest_rate": rate, "type": "deposit"}


class TestLinkage:
    def test_linked_ids_empty_when_no_links(self):
        goals = [_goal(1, 100), _goal(2, 200)]
        assert linked_asset_ids(goals) == set()

    def test_linked_ids_collected(self):
        goals = [_goal(1, 100, linked=10), _goal(2, 200, linked=11), _goal(3, 0)]
        assert linked_asset_ids(goals) == {10, 11}

    def test_free_assets_excludes_linked(self):
        assets = [_asset(10, 50000), _asset(11, 30000), _asset(12, 80000)]
        goals = [_goal(1, 0, linked=10)]
        free = free_assets(assets, goals)
        free_ids = {a["id"] for a in free}
        assert free_ids == {11, 12}

    def test_free_assets_all_when_no_links(self):
        assets = [_asset(10, 50000), _asset(11, 30000)]
        free = free_assets(assets, [_goal(1, 100)])
        assert len(free) == 2


class TestEffectiveGoalValues:
    def test_unlinked_goal_keeps_own_values(self):
        goal = _goal(1, 35000, rate=0.0)
        current, rate = effective_goal_values(goal, {})
        assert current == 35000
        assert rate == 0.0

    def test_linked_goal_takes_asset_values(self):
        goal = _goal(1, 0, linked=10)
        idx = assets_index([_asset(10, 42000, rate=0.16)])
        current, rate = effective_goal_values(goal, idx)
        assert current == 42000
        assert rate == 0.16

    def test_linked_to_missing_asset_falls_back(self):
        # привязка к несуществующему активу — безопасный fallback на свои значения
        goal = _goal(1, 5000, rate=0.05, linked=999)
        current, rate = effective_goal_values(goal, {})
        assert current == 5000
        assert rate == 0.05


class TestApplyEnvelopes:
    def test_linked_goal_projects_asset_amount(self):
        goals = [_goal(1, 0, linked=10), _goal(2, 7000, rate=0.0)]
        assets = [_asset(10, 42000, rate=0.16), _asset(11, 50000)]
        eff_goals, free = apply_envelopes(goals, assets)
        g1 = next(g for g in eff_goals if g["id"] == 1)
        g2 = next(g for g in eff_goals if g["id"] == 2)
        assert g1["current_amount"] == 42000
        assert g1["savings_rate"] == 0.16
        assert g2["current_amount"] == 7000  # непривязанная не меняется
        assert {a["id"] for a in free} == {11}

    def test_no_double_counting_invariant(self):
        # деньги в активах не теряются и не задваиваются:
        # свободный резерв + накопления привязанных целей = сумма всех активов
        assets = [_asset(10, 42000), _asset(11, 30000), _asset(12, 80000)]
        goals = [_goal(1, 0, linked=10), _goal(2, 0, linked=12)]
        eff_goals, free = apply_envelopes(goals, assets)
        free_sum = sum(a["amount"] for a in free)
        linked_goal_sum = sum(g["current_amount"] for g in eff_goals if g["linked_asset_id"])
        assert free_sum + linked_goal_sum == 42000 + 30000 + 80000

    def test_backward_compatible_no_links(self):
        # без привязок — цели и активы неизменны, Bliq = все активы
        goals = [_goal(1, 10000), _goal(2, 20000)]
        assets = [_asset(10, 50000), _asset(11, 30000)]
        eff_goals, free = apply_envelopes(goals, assets)
        assert [g["current_amount"] for g in eff_goals] == [10000, 20000]
        assert sum(a["amount"] for a in free) == 80000

    def test_empty_inputs(self):
        eff_goals, free = apply_envelopes([], [])
        assert eff_goals == []
        assert free == []
