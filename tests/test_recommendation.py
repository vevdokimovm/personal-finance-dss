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


class TestExplainAlternativeDominantCriterion:
    """Батч 0.3, Волна 0: вклад критериев SAW в вердикт (карта качества,
    ось «объяснимость»). Аддитивно к существующему формату — новые поля,
    старые не убраны."""

    @staticmethod
    def _alt(weighted_scores=None, **overrides):
        alt = {
            "x_obligations": 5000, "x_reserve": 3000, "x_goals": 2000,
            "Rt_new": 1200, "Lt_new": 0.4, "Dt_new": 0.18,
        }
        if weighted_scores is not None:
            alt["weighted_scores"] = weighted_scores
        alt.update(overrides)
        return alt

    def test_dominant_criterion_is_max_weighted_score(self):
        alt = self._alt({"Rt": 0.05, "Lt": 0.20, "Dt": 0.03, "Si": 0.02})
        result = explain_alternative(
            alt, rt=1000, lt=0.35, dt=0.2,
            expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        assert result["dominant_criterion"] == "Lt"

    def test_dominant_criterion_none_without_weighted_scores(self):
        result = explain_alternative(
            self._alt(), rt=1000, lt=0.35, dt=0.2,
            expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        assert result["dominant_criterion"] is None

    def test_dominant_criterion_mentioned_in_insight(self):
        alt = self._alt({"Rt": 0.02, "Lt": 0.03, "Dt": 0.01, "Si": 0.25})
        result = explain_alternative(
            alt, rt=1000, lt=0.35, dt=0.2,
            expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        for token in ["Rt", "Lt", "Dt", "Si", "U(a)", "форм."]:
            assert token not in result["insight"]


class TestExplainAlternativeCounterfactual:
    """Батч 0.4, Волна 0: контрфактное объяснение — сравнение с реально
    посчитанным следующим по рангу вариантом (не гипотетический сценарий)."""

    @staticmethod
    def _alt(id_, utility, weighted_scores):
        return {
            "id": id_, "x_obligations": 5000, "x_reserve": 3000, "x_goals": 2000,
            "Rt_new": 1200, "Lt_new": 0.4, "Dt_new": 0.18,
            "utility": utility, "weighted_scores": weighted_scores,
        }

    def test_counterfactual_none_without_next_alt(self):
        result = explain_alternative(
            self._alt("a532", 0.7, {"Rt": 0.3, "Lt": 0.2, "Dt": 0.1, "Si": 0.1}),
            rt=1000, lt=0.35, dt=0.2, expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
        )
        assert result["counterfactual"] is None

    def test_counterfactual_available_with_next_alt(self):
        alt = self._alt("a532", 0.7, {"Rt": 0.30, "Lt": 0.20, "Dt": 0.10, "Si": 0.10})
        next_alt = self._alt("a542", 0.65, {"Rt": 0.28, "Lt": 0.15, "Dt": 0.12, "Si": 0.10})
        result = explain_alternative(
            alt, rt=1000, lt=0.35, dt=0.2, expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
            next_alt=next_alt,
        )
        cf = result["counterfactual"]
        assert cf["available"] is True
        assert cf["alternative_id"] == "a542"
        assert cf["utility_gap"] == round(0.7 - 0.65, 4)
        assert cf["dominant_criterion"] == "Lt"  # Lt дал наибольший разрыв в пользу alt

    def test_counterfactual_unavailable_without_scores(self):
        alt = {"id": "a532", "x_obligations": 5000, "x_reserve": 3000, "x_goals": 2000,
               "Rt_new": 1200, "Lt_new": 0.4, "Dt_new": 0.18}
        next_alt = {"id": "a542", "x_obligations": 4000, "x_reserve": 4000, "x_goals": 2000,
                    "Rt_new": 1100, "Lt_new": 0.5, "Dt_new": 0.18}
        result = explain_alternative(
            alt, rt=1000, lt=0.35, dt=0.2, expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
            next_alt=next_alt,
        )
        assert result["counterfactual"] == {"available": False}

    def test_counterfactual_text_has_no_jargon(self):
        alt = self._alt("a532", 0.7, {"Rt": 0.30, "Lt": 0.20, "Dt": 0.10, "Si": 0.10})
        next_alt = self._alt("a542", 0.65, {"Rt": 0.28, "Lt": 0.15, "Dt": 0.12, "Si": 0.10})
        result = explain_alternative(
            alt, rt=1000, lt=0.35, dt=0.2, expense_total=40000, obligation_payments=10000,
            goals_total=100000, risk_profile_label="Сбалансированный",
            next_alt=next_alt,
        )
        text = result["counterfactual"]["text"]
        assert isinstance(text, str) and text
        for token in ["Rt", "Lt", "Dt", "Si", "U(a)", "форм."]:
            assert token not in text
