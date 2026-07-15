"""Тесты взвешенной обеспеченности целей Si (формулы ВКР §15-16)."""
from datetime import datetime

from app.core.goals_priority import calculate_goals_si


class TestGoalsSi:
    def test_no_goals(self):
        si, alloc = calculate_goals_si(10000, [])
        assert si == 0.0 and alloc == {}

    def test_no_money(self):
        goals = [{"id": 1, "target_amount": 50000, "current_amount": 0,
                  "deadline": "2027-01-01", "category": "material"}]
        si, alloc = calculate_goals_si(0, goals)
        assert si == 0.0 and alloc == {}

    def test_allocation_by_category_weight(self):
        # при равной срочности income_growth (вес 3) получает втрое больше material (вес 1)
        today = datetime(2026, 1, 1)
        goals = [
            {"id": 1, "target_amount": 100000, "current_amount": 0,
             "deadline": "2027-06-01", "category": "income_growth"},
            {"id": 2, "target_amount": 100000, "current_amount": 0,
             "deadline": "2027-06-01", "category": "material"},
        ]
        si, alloc = calculate_goals_si(4000, goals, today=today)
        assert alloc[1] == 3000.0
        assert alloc[2] == 1000.0

    def test_si_in_unit_range(self):
        today = datetime(2026, 1, 1)
        goals = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "deadline": "2027-06-01", "category": "material"}]
        si, _ = calculate_goals_si(5000, goals, today=today)
        assert 0.0 <= si <= 1.0

    def test_allocation_capped_at_remaining(self):
        # денег больше, чем нужно цели → направляем только остаток
        today = datetime(2026, 1, 1)
        goals = [{"id": 1, "target_amount": 10000, "current_amount": 8000,
                  "deadline": "2027-06-01", "category": "material"}]
        _, alloc = calculate_goals_si(50000, goals, today=today)
        assert alloc[1] == 2000.0

    def test_completed_goal_excluded(self):
        # уже накопленная цель не участвует
        today = datetime(2026, 1, 1)
        goals = [{"id": 1, "target_amount": 10000, "current_amount": 10000,
                  "deadline": "2027-06-01", "category": "material"}]
        si, alloc = calculate_goals_si(5000, goals, today=today)
        assert alloc == {}
