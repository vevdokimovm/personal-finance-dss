"""Тесты взвешенной обеспеченности целей Si (формулы ВКР §15-16)."""
from datetime import datetime, timedelta

from app.core.goals_priority import (
    GOAL_INFLATION_HORIZON_MONTHS,
    GOAL_INFLATION_RATE,
    calculate_goals_si,
    goals_allocation_breakdown,
    inflated_target_amount,
)


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

    def test_si_lower_for_long_horizon_due_to_inflation(self):
        # урочность одинакова (обе >= 12 мес, u_s насыщается на 1.0) — разница
        # чисто от инфляционной индексации цели дальше 36 месяцев (батч 0.1)
        today = datetime(2026, 1, 1)
        short = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "deadline": datetime(2027, 1, 1), "category": "material"}]
        long_ = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "deadline": datetime(2036, 1, 1), "category": "material"}]
        si_short, _ = calculate_goals_si(50000, short, today=today)
        si_long, _ = calculate_goals_si(50000, long_, today=today)
        assert si_long < si_short


class TestGoalInflationIndexing:
    """Батч 0.1, Волна 0 (v3.6.0): индексация целей с горизонтом > ~3 лет —
    единственная систематическая (не спорная) ошибка карты качества модели."""

    def test_within_horizon_unchanged(self):
        today = datetime(2026, 1, 1)
        result = inflated_target_amount(100000.0, datetime(2028, 1, 1), today)  # 24 мес
        assert result == 100000.0

    def test_exactly_at_horizon_unchanged(self):
        # _months_left считает дни/30 (не календарные месяцы) — 1080 дней
        # ровно даёт 36.0 мес по формуле кода, а не календарные «через 3 года»
        today = datetime(2026, 1, 1)
        deadline = today + timedelta(days=1080)
        assert inflated_target_amount(100000.0, deadline, today) == 100000.0

    def test_beyond_horizon_indexed(self):
        today = datetime(2026, 1, 1)
        deadline = datetime(2031, 1, 1)
        months = (deadline - today).days / 30.0
        years = months / 12.0
        result = inflated_target_amount(100000.0, deadline, today)
        expected = 100000.0 * (1.0 + GOAL_INFLATION_RATE) ** years
        assert abs(result - expected) < 1.0

    def test_open_ended_unchanged(self):
        today = datetime(2026, 1, 1)
        assert inflated_target_amount(100000.0, None, today) == 100000.0

    def test_default_horizon_is_36_months(self):
        assert GOAL_INFLATION_HORIZON_MONTHS == 36.0

    def test_goals_allocation_breakdown_indexes_long_horizon_goal(self):
        today = datetime(2026, 1, 1)
        goals = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "deadline": datetime(2036, 1, 1), "category": "material"}]  # 10 лет
        breakdown = goals_allocation_breakdown(50000, goals, today=today)
        assert breakdown[0]["remaining"] > 100000.0

    def test_goals_allocation_breakdown_does_not_index_short_horizon_goal(self):
        today = datetime(2026, 1, 1)
        goals = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "deadline": datetime(2027, 1, 1), "category": "material"}]  # 1 год
        breakdown = goals_allocation_breakdown(50000, goals, today=today)
        assert breakdown[0]["remaining"] == 100000.0
