"""Тесты подготовки входных данных (этап 1 pipeline ВКР)."""
from app.core.preprocessing import is_active_goal, prepare_data


class TestIsActiveGoal:
    def test_active(self):
        assert is_active_goal({"target_amount": 1000, "current_amount": 500}) is True

    def test_completed(self):
        assert is_active_goal({"target_amount": 1000, "current_amount": 1000}) is False

    def test_overfunded(self):
        assert is_active_goal({"target_amount": 1000, "current_amount": 1500}) is False


class TestPrepareData:
    def test_structure(self):
        result = prepare_data([], [], [])
        assert set(result.keys()) == {
            "transactions", "obligations", "goals", "active_goals", "liquid_assets"
        }

    def test_none_liquid_assets(self):
        result = prepare_data([], [], [], None)
        assert result["liquid_assets"] == []

    def test_active_goals_filtered(self):
        goals = [
            {"target_amount": 1000, "current_amount": 500},
            {"target_amount": 1000, "current_amount": 1000},
        ]
        result = prepare_data([], [], goals)
        assert len(result["goals"]) == 2
        assert len(result["active_goals"]) == 1

    def test_invalid_type_becomes_expense(self):
        result = prepare_data([{"amount": 100, "type": "weird"}], [], [])
        assert result["transactions"][0]["type"] == "expense"

    def test_counts_preserved(self):
        result = prepare_data(
            [{"amount": 1, "type": "income"}],
            [{"monthly_payment": 100}],
            [],
        )
        assert len(result["transactions"]) == 1
        assert len(result["obligations"]) == 1
