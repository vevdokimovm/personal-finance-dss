"""Тесты генерации (stars-and-bars) и оценки альтернатив (этап 4 ВКР)."""
from app.core.alternatives import evaluate_alternative, generate_alternatives


class TestGenerate:
    def test_deficit_when_rt_nonpositive(self):
        alts = generate_alternatives(-100, 5000, 0)
        assert len(alts) == 1
        assert alts[0]["id"] == "deficit"

    def test_count_21_with_step_20(self):
        # число дискретных распределений = C(7,2) = 21
        alts = generate_alternatives(10000, 5000, 50000, step=0.20)
        assert len(alts) == 21

    def test_shares_sum_to_rt(self):
        alts = generate_alternatives(10000, 5000, 50000, step=0.20)
        for a in alts:
            total = a["x_obligations"] + a["x_reserve"] + a["x_goals"]
            assert abs(total - 10000) < 1.0


class TestEvaluate:
    def test_metrics_present(self):
        alt = {"id": "t", "x_obligations": 5000, "x_reserve": 0, "x_goals": 0}
        obls = [{"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.25}]
        result = evaluate_alternative(alt, 80000, 50000, obls, [], 0.14)
        assert "Rt_new" in result and "Lt_new" in result and "Dt_new" in result

    def test_prepayment_reduces_debt_load(self):
        # досрочка в дорогой кредит (ставка ≥ бенчмарк) снижает долговую нагрузку
        alt = {"id": "t", "x_obligations": 5000, "x_reserve": 0, "x_goals": 0}
        obls = [{"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.25}]
        result = evaluate_alternative(alt, 80000, 50000, obls, [], 0.14)
        assert result["Dt_new"] < 5000 / 80000
