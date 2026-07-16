"""Тесты min-max нормализации и SAW-ранжирования (формулы ВКР §7-8)."""
from app.core.ranking import RISK_PROFILES, normalize_value, rank_alternatives


class TestNormalize:
    def test_basic(self):
        assert normalize_value(5, 0, 10) == 0.5

    def test_minimize_inverts(self):
        # для критерия «меньше — лучше» (долговая нагрузка)
        assert normalize_value(2, 0, 10, minimize=True) == 0.8

    def test_equal_bounds_returns_one(self):
        assert normalize_value(5, 5, 5) == 1.0

    def test_edges(self):
        assert normalize_value(0, 0, 10) == 0.0
        assert normalize_value(10, 0, 10) == 1.0


class TestRanking:
    @staticmethod
    def _alts():
        return [
            {"name": "A", "Rt_new": 1000, "Lt_new": 0.5, "Dt_new": 0.20, "Si": 0.3},
            {"name": "B", "Rt_new": 2000, "Lt_new": 0.6, "Dt_new": 0.15, "Si": 0.5},
            {"name": "C", "Rt_new": 500, "Lt_new": 0.4, "Dt_new": 0.30, "Si": 0.1},
        ]

    def test_empty(self):
        assert rank_alternatives([]) == []

    def test_exactly_one_recommended(self):
        ranked = rank_alternatives(self._alts(), risk_tolerance=3)
        assert sum(1 for a in ranked if a.get("is_recommended")) == 1

    def test_utility_in_unit_range(self):
        ranked = rank_alternatives(self._alts(), risk_tolerance=3)
        assert all(0.0 <= a["utility"] <= 1.0 for a in ranked)

    def test_sorted_descending(self):
        ranked = rank_alternatives(self._alts(), risk_tolerance=3)
        utils = [a["utility"] for a in ranked]
        assert utils == sorted(utils, reverse=True)

    def test_best_is_first(self):
        ranked = rank_alternatives(self._alts(), risk_tolerance=3)
        assert ranked[0].get("is_recommended") is True

    def test_dominant_alternative_wins(self):
        # B доминирует по всем критериям → должна победить при любом профиле
        ranked = rank_alternatives(self._alts(), risk_tolerance=1)
        assert ranked[0]["name"] == "B"

    def test_single_alternative_no_crash(self):
        # единственная альтернатива: min==max по всем критериям → нет деления на ноль
        ranked = rank_alternatives(
            [{"name": "solo", "Rt_new": 1000, "Lt_new": 2.0, "Dt_new": 0.2, "Si": 0.5}]
        )
        assert len(ranked) == 1 and ranked[0]["is_recommended"] is True
        assert 0.0 <= ranked[0]["utility"] <= 1.0

    def test_all_equal_debt_no_crash(self):
        # пользователь без долгов: у всех Dt_new одинаков → нормализация не падает
        alts = [
            {"name": "A", "Rt_new": 1000, "Lt_new": 2.0, "Dt_new": 0.0, "Si": 0.3},
            {"name": "B", "Rt_new": 2000, "Lt_new": 4.0, "Dt_new": 0.0, "Si": 0.6},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=3)
        assert all(0.0 <= a["utility"] <= 1.0 for a in ranked)

    def test_profile_changes_choice(self):
        # Главный эффект refined-модели: с ортогональными критериями профиль реально
        # меняет выбор. Оба варианта дают >= 2 мес (floor v3.4.0 удовлетворён, решает
        # SAW): консерватор (вес ликвидности 0.45) берёт высокую автономию;
        # агрессор (вес целей 0.40) — высокую обеспеченность целей.
        alts = [
            {"name": "liquidity", "Rt_new": 1000, "Lt_new": 6.0, "Dt_new": 0.2, "Si": 0.1},
            {"name": "goals", "Rt_new": 1000, "Lt_new": 2.2, "Dt_new": 0.2, "Si": 0.9},
        ]
        conservative = rank_alternatives([dict(a) for a in alts], risk_tolerance=1)
        aggressive = rank_alternatives([dict(a) for a in alts], risk_tolerance=5)
        assert conservative[0]["name"] == "liquidity"
        assert aggressive[0]["name"] == "goals"


class TestReserveSaturation:
    """G1 (модель v3.1.0): полезность резерва насыщается на целевом Lt*(risk).

    Выше целевой подушки прирост ликвидности не даёт полезности — модель
    перестаёт бесконечно копить резерв и финансирует цели, как консенсус
    четырёх независимых экспертов (коридор 3–6 месяцев)."""

    def test_lt_targets_present_and_in_corridor(self):
        for r, p in RISK_PROFILES.items():
            assert 3.0 <= p["lt_target"] <= 6.0, r

    def test_lt_targets_non_increasing_with_risk(self):
        vals = [RISK_PROFILES[r]["lt_target"] for r in sorted(RISK_PROFILES)]
        assert vals == sorted(vals, reverse=True)
        assert vals[0] == 6.0 and vals[-1] == 3.0

    def test_above_target_liquidity_is_neutral(self):
        # Подушка уже 11 мес (кейс SP-00002): «ещё в резерв» и «в цели» дают
        # одинаковый насыщенный Lt → выигрывают цели, а не бесконечная подушка.
        alts = [
            {"name": "more_reserve", "Rt_new": 0, "Lt_new": 12.6, "Dt_new": 0.0, "Si": 0.0},
            {"name": "fund_goals", "Rt_new": 0, "Lt_new": 11.4, "Dt_new": 0.0, "Si": 0.7},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=3)
        assert ranked[0]["name"] == "fund_goals"

    def test_conservative_also_saturates(self):
        # даже профиль 1 (w_lt=0.45) не копит выше своей цели 6 мес
        alts = [
            {"name": "more_reserve", "Rt_new": 0, "Lt_new": 9.0, "Dt_new": 0.0, "Si": 0.0},
            {"name": "fund_goals", "Rt_new": 0, "Lt_new": 7.0, "Dt_new": 0.0, "Si": 0.5},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=1)
        assert ranked[0]["name"] == "fund_goals"

    def test_below_target_liquidity_still_discriminates(self):
        # ниже цели прежняя механика сохраняется: консерватор строит подушку
        alts = [
            {"name": "reserve", "Rt_new": 0, "Lt_new": 3.0, "Dt_new": 0.0, "Si": 0.0},
            {"name": "goals", "Rt_new": 0, "Lt_new": 1.2, "Dt_new": 0.0, "Si": 0.6},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=1)
        assert ranked[0]["name"] == "reserve"


class TestReserveFloor:
    """G6 (модель v3.1.0): стартовый месяц ликвидности не отменяется риск-профилем.

    Кейс SP-00299: риск 5, Lt=0.32 — модель клала всё в цель при консенсусе
    «сначала резерв». Floor = 1 месяц burn лексикографически приоритетнее SAW."""

    def test_floor_beats_goals_even_for_aggressive(self):
        alts = [
            {"name": "all_goals", "Rt_new": 0, "Lt_new": 0.32, "Dt_new": 0.0, "Si": 1.0},
            {"name": "fill_floor", "Rt_new": 0, "Lt_new": 1.1, "Dt_new": 0.0, "Si": 0.2},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=5)
        assert ranked[0]["name"] == "fill_floor"

    def test_partial_fill_preferred_when_floor_unreachable(self):
        # если до floor (2 мес, v3.4.0) не дотянуться — приоритет ближайшему к нему
        alts = [
            {"name": "zero", "Rt_new": 0, "Lt_new": 0.1, "Dt_new": 0.0, "Si": 1.0},
            {"name": "closer", "Rt_new": 0, "Lt_new": 0.6, "Dt_new": 0.0, "Si": 0.3},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=5)
        assert ranked[0]["name"] == "closer"

    def test_above_floor_saw_decides(self):
        # оба варианта дают >= 2 мес — floor v3.4.0 удовлетворён, решает SAW
        # (агрессор → цели)
        alts = [
            {"name": "reserve", "Rt_new": 0, "Lt_new": 4.0, "Dt_new": 0.0, "Si": 0.1},
            {"name": "goals", "Rt_new": 0, "Lt_new": 2.2, "Dt_new": 0.0, "Si": 0.9},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=5)
        assert ranked[0]["name"] == "goals"

    def test_utility_field_stays_in_unit_range(self):
        alts = [
            {"name": "a", "Rt_new": 0, "Lt_new": 0.2, "Dt_new": 0.0, "Si": 0.9},
            {"name": "b", "Rt_new": 0, "Lt_new": 1.5, "Dt_new": 0.0, "Si": 0.1},
        ]
        ranked = rank_alternatives(alts, risk_tolerance=4)
        assert all(0.0 <= a["utility"] <= 1.0 for a in ranked)
