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


class TestDtGateNonWorsening:
    """G3 (модель v3.1.0): гейт «план не увеличивает ПДН» вместо «текущий ПДН <= 0.40».

    ПДН — андеррайтинговая метрика для выдачи НОВОГО кредита. Пользователь с
    ПДН 0.88 и положительным потоком должен получать план (лавина только
    снижает нагрузку), а не пустой экран — иначе система отказывает в помощи
    самой уязвимой группе (198 портретов экспертизы)."""

    def test_high_current_dt_plans_pass(self):
        # текущий ПДН 0.88 (кейс SP-00003): планы с Dt' <= текущего допустимы
        alts = [
            {"name": "avalanche", "Rt_new": 5000, "Lt_new": 0.0, "Dt_new": 0.70},
            {"name": "keep", "Rt_new": 14737, "Lt_new": 0.0, "Dt_new": 0.88},
        ]
        accepted, rejected = filter_alternatives(alts, dt_current=0.88)
        assert len(accepted) == 2 and not rejected

    def test_plan_increasing_dt_rejected(self):
        alts = [{"name": "worse", "Rt_new": 1000, "Lt_new": 0.0, "Dt_new": 0.95}]
        accepted, rejected = filter_alternatives(alts, dt_current=0.88)
        assert not accepted and len(rejected) == 1
        assert rejected[0]["violations"]

    def test_default_keeps_regulatory_gate(self):
        # без dt_current поведение прежнее: Dt' > 0.40 отсекается
        accepted, rejected = filter_alternatives(
            [{"name": "debt", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.5}],
            dt_current=0.30,
        )
        assert not accepted and len(rejected) == 1

    def test_below_regulatory_threshold_unaffected(self):
        # у здорового пользователя (ПДН 0.2) порог остаётся регуляторным 0.40
        accepted, _ = filter_alternatives(
            [{"name": "x", "Rt_new": 1000, "Lt_new": 3.0, "Dt_new": 0.35}],
            dt_current=0.20,
        )
        assert len(accepted) == 1
