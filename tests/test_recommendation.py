"""Тесты текстовых рекомендаций и объяснений (FR-01: язык без формул)."""
from app.core.recommendation import build_recommendation_text, explain_alternative


class TestRecommendationText:
    def test_returns_string(self):
        text = build_recommendation_text(
            rt=5000, lt=0.5, dt=0.1, has_active_goals=False,
            expense_total=30000, obligation_payments=0,
        )
        assert isinstance(text, str)

    def test_high_debt_mentioned(self):
        text = build_recommendation_text(
            rt=1000, lt=0.3, dt=0.5, has_active_goals=False,
            expense_total=50000, obligation_payments=40000,
        )
        assert "40%" in text or "кредит" in text.lower()

    def test_no_formula_jargon(self):
        text = build_recommendation_text(
            rt=5000, lt=0.5, dt=0.1, has_active_goals=True,
            expense_total=30000, obligation_payments=5000,
        )
        for token in ["Rt", "Lt", "U(a)", "форм."]:
            assert token not in text


class TestExplainAlternative:
    @staticmethod
    def _alt():
        return {
            "x_obligations": 5000, "x_reserve": 3000, "x_goals": 2000,
            "Rt_new": 1200, "Lt_new": 0.4, "Dt_new": 0.18,
        }

    def test_return_structure(self):
        result = explain_alternative(
            self._alt(), rt=1000, lt=0.35, dt=0.2,
            expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        assert {"gains", "costs", "insight", "delta"} <= set(result.keys())
        assert isinstance(result["gains"], list)
        assert isinstance(result["insight"], str)

    def test_no_jargon_in_explanation(self):
        result = explain_alternative(
            self._alt(), rt=1000, lt=0.35, dt=0.2,
            expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        # только пользовательский текст; delta — служебные числовые поля
        blob = " ".join(result["gains"] + result["costs"]) + " " + result["insight"]
        for token in ["Rt", "Lt", "U(a)", "Avalanche", "форм."]:
            assert token not in blob
