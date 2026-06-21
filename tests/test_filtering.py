"""Тесты фильтрации альтернатив по ограничениям допустимости (refined model v2.2).

Жёсткие инварианты: Rt' ≥ 0 (не в минус), Dt' ≤ 0.40 (ПДН).
Порог ликвидности l_min = минимум месяцев автономии, по умолчанию 0 (выключен) —
ликвидность работает как критерий полезности, а не как фильтр, чтобы не выбрасывать
пользователей с тонким бюджетом.
"""
from app.core.filtering import filter_alternatives


class TestFiltering:
    def test_admissible_passes(self):
        accepted, rejected = filter_alternatives(
            [{"name": "ok", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.2}]
        )
        assert len(accepted) == 1 and not rejected
        assert accepted[0]["is_admissible"] is True
        assert accepted[0]["violations"] == []

    def test_negative_rt_rejected(self):
        accepted, rejected = filter_alternatives(
            [{"name": "neg", "Rt_new": -100, "Lt_new": 3.0, "Dt_new": 0.2}]
        )
        assert not accepted and len(rejected) == 1
        assert rejected[0]["violations"]
        assert rejected[0]["is_admissible"] is False

    def test_high_debt_rejected(self):
        accepted, rejected = filter_alternatives(
            [{"name": "debt", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.5}]
        )
        assert len(rejected) == 1

    def test_liquidity_off_by_default(self):
        # по умолчанию l_min=0 → даже нулевая автономия не отсевается (мягкий критерий)
        accepted, rejected = filter_alternatives(
            [{"name": "x", "Rt_new": 1000, "Lt_new": 0.0, "Dt_new": 0.2}]
        )
        assert len(accepted) == 1 and not rejected

    def test_custom_autonomy_threshold(self):
        # при l_min=2.5 план с автономией 1 мес отсекается, с 3 мес проходит
        alts = [
            {"name": "thin", "Rt_new": 1000, "Lt_new": 1.0, "Dt_new": 0.2},
            {"name": "safe", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.2},
        ]
        accepted, rejected = filter_alternatives(alts, l_min=2.5)
        assert len(accepted) == 1 and accepted[0]["name"] == "safe"
        assert len(rejected) == 1 and rejected[0]["name"] == "thin"

    def test_mixed_split(self):
        alts = [
            {"name": "ok", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.2},
            {"name": "bad", "Rt_new": -1, "Lt_new": 3.0, "Dt_new": 0.2},
        ]
        accepted, rejected = filter_alternatives(alts)
        assert len(accepted) == 1 and len(rejected) == 1
        assert accepted[0]["name"] == "ok"
