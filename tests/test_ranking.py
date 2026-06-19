"""Тесты min-max нормализации и SAW-ранжирования (формулы ВКР §7-8)."""
from app.core.ranking import normalize_value, rank_alternatives


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
        # меняет выбор. Консерватор (вес ликвидности 0.45) выбирает высокую автономию;
        # агрессор (вес целей 0.40) — высокую обеспеченность целей.
        alts = [
            {"name": "liquidity", "Rt_new": 1000, "Lt_new": 6.0, "Dt_new": 0.2, "Si": 0.1},
            {"name": "goals", "Rt_new": 1000, "Lt_new": 1.0, "Dt_new": 0.2, "Si": 0.9},
        ]
        conservative = rank_alternatives([dict(a) for a in alts], risk_tolerance=1)
        aggressive = rank_alternatives([dict(a) for a in alts], risk_tolerance=5)
        assert conservative[0]["name"] == "liquidity"
        assert aggressive[0]["name"] == "goals"
