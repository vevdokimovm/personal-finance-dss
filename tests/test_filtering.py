"""Тесты фильтрации альтернатив по ограничениям (формула ВКР §18)."""
from app.core.filtering import filter_alternatives


class TestFiltering:
    def test_admissible_passes(self):
        accepted, rejected = filter_alternatives(
            [{"name": "ok", "Rt_new": 1000, "Lt_new": 0.5, "Dt_new": 0.2}]
        )
        assert len(accepted) == 1 and not rejected
        assert accepted[0]["is_admissible"] is True
        assert accepted[0]["violations"] == []

    def test_negative_rt_rejected(self):
        accepted, rejected = filter_alternatives(
            [{"name": "neg", "Rt_new": -100, "Lt_new": 0.5, "Dt_new": 0.2}]
        )
        assert not accepted and len(rejected) == 1
        assert rejected[0]["violations"]
        assert rejected[0]["is_admissible"] is False

    def test_negative_lt_rejected(self):
        accepted, rejected = filter_alternatives(
            [{"name": "low", "Rt_new": 1000, "Lt_new": -0.1, "Dt_new": 0.2}]
        )
        assert len(rejected) == 1

    def test_high_debt_rejected(self):
        accepted, rejected = filter_alternatives(
            [{"name": "debt", "Rt_new": 1000, "Lt_new": 0.5, "Dt_new": 0.5}]
        )
        assert len(rejected) == 1

    def test_custom_liquidity_threshold(self):
        # при lt_crit=0.30 альтернатива с Lt=0.1 отклоняется
        accepted, rejected = filter_alternatives(
            [{"name": "x", "Rt_new": 1000, "Lt_new": 0.1, "Dt_new": 0.2}],
            lt_crit=0.30,
        )
        assert len(rejected) == 1

    def test_mixed_split(self):
        alts = [
            {"name": "ok", "Rt_new": 1000, "Lt_new": 0.5, "Dt_new": 0.2},
            {"name": "bad", "Rt_new": -1, "Lt_new": 0.5, "Dt_new": 0.2},
        ]
        accepted, rejected = filter_alternatives(alts)
        assert len(accepted) == 1 and len(rejected) == 1
        assert accepted[0]["name"] == "ok"
