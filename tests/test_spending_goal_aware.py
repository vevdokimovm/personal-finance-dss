"""Тесты слоя 3-B: goal-aware советы (связь экономии с целями).

Чистая арифметика advisor'а на GoalRecord (без ORM): сколько раньше закроется
цель, если освобождённую экономию направить на её пополнение. База — наблюдаемый
темп пополнения; линейно, без процентов инструмента (консервативно).
"""
from app.core.spending_advice import GoalImpact, GoalRecord, SpendingAdvisor


class TestGoalImpact:
    def test_funded_goal_accelerated(self):
        # remaining 60000, темп 5000/мес → ETA 12; +5000 → ETA 6 → на 6 мес раньше
        g = GoalRecord(name="Машина", target_amount=100000, current_amount=40000,
                       months_to_deadline=24, monthly_contribution=5000, priority=1)
        impacts = SpendingAdvisor().analyze_goal_impact(5000, [g])
        car = impacts[0]
        assert car.eta_now == 12.0
        assert car.eta_boosted == 6.0
        assert car.months_earlier == 6.0
        assert car.on_track is True  # 12 <= 24

    def test_unfunded_goal_reaches_in_finite_time(self):
        # темп 0 → «раньше» не считаем; даём ETA при экономии: 60000/5000 = 12
        g = GoalRecord("Отпуск", 60000, 0, 12, 0.0, 0)
        v = SpendingAdvisor().analyze_goal_impact(5000, [g])[0]
        assert v.eta_now is None
        assert v.eta_boosted == 12.0
        assert v.months_earlier is None
        assert v.on_track is False

    def test_met_goal_skipped(self):
        g = GoalRecord("Готово", 50000, 50000, 12, 1000, 0)
        assert SpendingAdvisor().analyze_goal_impact(5000, [g]) == []

    def test_overfunded_goal_skipped(self):
        g = GoalRecord("Перевыполнено", 50000, 60000, 12, 1000, 0)
        assert SpendingAdvisor().analyze_goal_impact(5000, [g]) == []

    def test_no_saving_no_impact(self):
        g = GoalRecord("Машина", 100000, 40000, 24, 5000, 1)
        assert SpendingAdvisor().analyze_goal_impact(0, [g]) == []

    def test_negative_saving_no_impact(self):
        g = GoalRecord("Машина", 100000, 40000, 24, 5000, 1)
        assert SpendingAdvisor().analyze_goal_impact(-100, [g]) == []

    def test_not_on_track_when_pace_misses_deadline(self):
        # remaining 60000 при 1000/мес = 60 мес > дедлайн 12 → не в графике
        g = GoalRecord("Машина", 100000, 40000, 12, 1000, 0)
        v = SpendingAdvisor().analyze_goal_impact(5000, [g])[0]
        assert v.on_track is False
        assert v.eta_now == 60.0

    def test_sorted_by_priority(self):
        low = GoalRecord("Низкий", 100000, 0, 24, 2000, 0)
        high = GoalRecord("Высокий", 100000, 0, 24, 2000, 5)
        impacts = SpendingAdvisor().analyze_goal_impact(3000, [low, high])
        assert impacts[0].goal_name == "Высокий"

    def test_priority_tiebreak_by_deadline(self):
        far = GoalRecord("Дальняя", 100000, 0, 36, 2000, 0)
        near = GoalRecord("Близкая", 100000, 0, 6, 2000, 0)
        impacts = SpendingAdvisor().analyze_goal_impact(3000, [far, near])
        assert impacts[0].goal_name == "Близкая"

    def test_top_k(self):
        goals = [GoalRecord(f"G{i}", 100000, 0, 24, 1000, i) for i in range(5)]
        assert len(SpendingAdvisor().analyze_goal_impact(2000, goals, top_k=2)) == 2

    def test_message_mentions_goal_name(self):
        g = GoalRecord("Машина", 100000, 40000, 24, 5000, 1)
        msg = SpendingAdvisor().analyze_goal_impact(5000, [g])[0].message
        assert "Машина" in msg

    def test_remaining_computed(self):
        g = GoalRecord("Машина", 100000, 40000, 24, 5000, 1)
        v = SpendingAdvisor().analyze_goal_impact(5000, [g])[0]
        assert v.remaining == 60000.0

    def test_empty_goals(self):
        assert SpendingAdvisor().analyze_goal_impact(5000, []) == []

    def test_returns_goal_impact_type(self):
        g = GoalRecord("Машина", 100000, 40000, 24, 5000, 1)
        impacts = SpendingAdvisor().analyze_goal_impact(5000, [g])
        assert all(isinstance(i, GoalImpact) for i in impacts)
