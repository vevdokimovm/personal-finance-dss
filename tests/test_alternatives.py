"""Тесты генерации (stars-and-bars) и оценки альтернатив (этап 4 ВКР)."""
import pytest

from app.core.alternatives import evaluate_alternative, generate_alternatives


class TestGenerate:
    def test_deficit_when_rt_nonpositive(self):
        alts = generate_alternatives(-100, 5000, 0)
        assert len(alts) == 1
        assert alts[0]["id"] == "deficit"

    def test_count_66_with_default_step_10(self):
        # дефолтный шаг 10% → C(12,2) = 66 дискретных распределений (тоньше советы)
        alts = generate_alternatives(10000, 5000, 50000)
        assert len(alts) == 66

    def test_count_21_with_step_20(self):
        # явный шаг 20% сохраняет прежнее число C(7,2) = 21
        alts = generate_alternatives(10000, 5000, 50000, step=0.20)
        assert len(alts) == 21

    def test_shares_sum_to_rt(self):
        alts = generate_alternatives(10000, 5000, 50000)
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

    def test_lt_is_stock_based_autonomy(self):
        # Lt_new = (Bliq + x_reserve) / расходы — месяцы автономии
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 12000, "x_goals": 0}
        result = evaluate_alternative(alt, 80000, 4000, [], [], 0.14, bliq=0.0)
        assert result["Lt_new"] == pytest.approx(3.0)  # 12000 / 4000

    def test_existing_bliq_counts_into_autonomy(self):
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 0, "x_goals": 0}
        result = evaluate_alternative(alt, 80000, 5000, [], [], 0.14, bliq=15000.0)
        assert result["Lt_new"] == pytest.approx(3.0)  # 15000 / 5000

    def test_reserve_lifts_liquidity_resource_unchanged(self):
        # Ортогонализация: при одинаковой досрочке (=0) резерв двигает ТОЛЬКО ликвидность,
        # ресурс Rt остаётся прежним. Это и есть развязка коллинеарности R/L.
        base = {"id": "a", "x_obligations": 0, "x_reserve": 0, "x_goals": 0}
        more_reserve = {"id": "b", "x_obligations": 0, "x_reserve": 20000, "x_goals": 0}
        r_base = evaluate_alternative(dict(base), 80000, 5000, [], [], 0.14, bliq=0.0)
        r_res = evaluate_alternative(dict(more_reserve), 80000, 5000, [], [], 0.14, bliq=0.0)
        assert r_res["Lt_new"] > r_base["Lt_new"]      # резерв поднял автономию
        assert r_res["Rt_new"] == r_base["Rt_new"]     # ресурс не изменился
