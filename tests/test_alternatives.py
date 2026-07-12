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


class TestGoalRemainderReroute:
    """G7-остаток (ADR-009): нераспределённый остаток целевого бакета уходит в резерв.

    Каскад освоения свободного ресурса: долг → (остаток) цели → (остаток) резерв.
    Резерв — конечный сток: деньги, которые не влезли ни в долг, ни в цели, не
    испаряются из плана, а поднимают ликвидную подушку (Lt'). До ADR-009 остаток
    целевого бакета терялся: не шёл ни в цели (кэп по потребности), ни в резерв.
    """

    def test_saturated_goal_overflow_goes_to_reserve(self):
        # Цель нуждается в 5 000, а в бакет целей направлено 20 000 → 15 000 не
        # влезли и должны уйти в резерв, подняв автономию.
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 0, "x_goals": 20000}
        goals = [{"id": 1, "target_amount": 5000, "current_amount": 0,
                  "category": "material", "deadline": None}]
        r = evaluate_alternative(alt, 80000, 4000, [], goals, 0.14, bliq=0.0)
        assert r["x_goals_unused"] == pytest.approx(15000.0)
        assert r["x_reserve_effective"] == pytest.approx(15000.0)
        assert r["Lt_new"] == pytest.approx(15000.0 / 4000.0)  # 3.75 мес автономии

    def test_no_overflow_when_goals_absorb_everything(self):
        # Цель ёмкая (нужно 100 000) → все 5 000 осваиваются, остатка нет,
        # эффективный резерв равен номинальному.
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 0, "x_goals": 5000}
        goals = [{"id": 1, "target_amount": 100000, "current_amount": 0,
                  "category": "material", "deadline": None}]
        r = evaluate_alternative(alt, 80000, 4000, [], goals, 0.14, bliq=0.0)
        assert r["x_goals_unused"] == pytest.approx(0.0)
        assert r["x_reserve_effective"] == pytest.approx(0.0)
        assert r["Lt_new"] == pytest.approx(0.0)

    def test_reserve_effective_adds_nominal_and_overflow(self):
        # Номинальный резерв 6 000 + переток 15 000 = эффективный 21 000.
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 6000, "x_goals": 20000}
        goals = [{"id": 1, "target_amount": 5000, "current_amount": 0,
                  "category": "material", "deadline": None}]
        r = evaluate_alternative(alt, 80000, 3000, [], goals, 0.14, bliq=0.0)
        assert r["x_goals_unused"] == pytest.approx(15000.0)
        assert r["x_reserve_effective"] == pytest.approx(21000.0)
        assert r["Lt_new"] == pytest.approx(21000.0 / 3000.0)  # 7.0 мес

    def test_debt_unused_cascades_through_goals_into_reserve(self):
        # Полный каскад: дешёвый долг (10% < r_bench 14%) не гасится → 10 000
        # уходят в цели; цель ёмкостью 4 000 их не вмещает (3 000 своих + 10 000) →
        # 9 000 перетекают в резерв.
        alt = {"id": "t", "x_obligations": 10000, "x_reserve": 0, "x_goals": 3000}
        obls = [{"id": 1, "amount": 50000, "monthly_payment": 2000, "interest_rate": 0.10}]
        goals = [{"id": 1, "target_amount": 4000, "current_amount": 0,
                  "category": "material", "deadline": None}]
        r = evaluate_alternative(alt, 80000, 3000, obls, goals, 0.14, bliq=0.0)
        assert r["x_obl_unused"] == pytest.approx(10000.0)   # дешёвый долг пропущен
        assert r["x_goals_unused"] == pytest.approx(9000.0)  # переток целей → резерв
        assert r["x_reserve_effective"] == pytest.approx(9000.0)
        assert r["Lt_new"] == pytest.approx(3.0)             # 9000 / 3000

    def test_no_money_leaks_conservation(self):
        # Инвариант сохранения: долг(эфф.) + цели(развёрнуто) + резерв(эфф.) == R+.
        # До ADR-009 остаток целевого бакета испарялся и сумма была меньше R+.
        alt = {"id": "t", "x_obligations": 0, "x_reserve": 2000, "x_goals": 18000}
        goals = [{"id": 1, "target_amount": 3000, "current_amount": 0,
                  "category": "material", "deadline": None}]
        r = evaluate_alternative(alt, 80000, 4000, [], goals, 0.14, bliq=0.0)
        deployed_goals = sum(float(v) for v in r["goal_allocation"].values())
        conserved = r["x_obl_effective"] + deployed_goals + r["x_reserve_effective"]
        nominal = alt["x_obligations"] + alt["x_reserve"] + alt["x_goals"]
        assert conserved == pytest.approx(nominal)  # ничего не потеряно
