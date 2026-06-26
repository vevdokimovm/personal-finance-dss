"""
Property-based проверка инвариантов финансового ядра (hypothesis).

Зачем этот слой. Обычные unit-тесты проверяют ядро на нескольких заранее
подобранных входах. Property-based подход проверяет МАТЕМАТИЧЕСКИЕ ИНВАРИАНТЫ
модели на тысячах случайных входов: если где-то нарушится `Rt(a) ≥ 0`, ПДН
свалит за 0.40, сумма долей альтернативы перестанет равняться единице или
полезность вылезет за [0, 1] — hypothesis найдёт минимальный контрпример и
покажет его. Это ловит регрессии, которые точечные кейсы пропускают.

Инварианты сверены строго с каноном `docs/math_model_v3_0_0.md` (v3.0.0):
  §3   базовые показатели Rt, Lt (stock-based), Dt (ПДН), BLR
  §4.2 базовое ограничение распределения: x_d + x_r + x_g = R+_t, xi ≥ 0
  §4.3 дискретизация stars-and-bars, шаг 10% → |A| = 66
  §5   производные показатели альтернативы (Rt', Lt', Dt' реагируют на разные xi)
  §6   допустимость: жёсткие инварианты Rt' ≥ 0 и Dt' ≤ 0.40; Lt' ≥ L_min мягкий
  §7   min-max нормализация с защитой от вырожденности
  §8   SAW-свёртка U(a) ∈ [0, 1], a* = argmax U(a)
  §9   профили риска: веса в сумме = 1, монотонность по риску

Маркер `property` — чтобы CI мог запускать слой отдельно (`pytest -m property`).
"""
from __future__ import annotations

from datetime import datetime

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.avalanche import allocate_obligations_avalanche
from app.core.filtering import B_MIN, DT_MAX, filter_alternatives
from app.core.metrics import (
    calculate_blr,
    calculate_dt,
    calculate_lt,
    calculate_rt,
)
from app.core.ranking import RISK_PROFILES, normalize_value, rank_alternatives

pytestmark = pytest.mark.property

# Общий профиль hypothesis для ядра: deadline снят (первый прогон конвейера на
# 66 альтернативах может быть «медленным» по меркам hypothesis, но это не флак),
# умеренное число примеров — баланс покрытия и скорости в быстром CI-прогоне.
core_settings = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

TODAY = datetime(2026, 1, 1)

# ── Базовые стратегии входных данных ─────────────────────────────────────────
positive_money = st.floats(
    min_value=1.0, max_value=5_000_000.0, allow_nan=False, allow_infinity=False
)
nonneg_money = st.floats(
    min_value=0.0, max_value=5_000_000.0, allow_nan=False, allow_infinity=False
)
rate = st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False)
risk_profile = st.integers(min_value=1, max_value=5)
GOAL_CATEGORIES = ["income_growth", "safety", "material", "emotional"]


@st.composite
def obligations_list(draw: st.DrawFn) -> list[dict]:
    """Список кредитных обязательств с уникальными id и платежом ≤ остатка."""
    n = draw(st.integers(min_value=0, max_value=4))
    result = []
    for i in range(n):
        amount = draw(positive_money)
        payment = draw(
            st.floats(
                min_value=0.0,
                max_value=min(amount, 300_000.0),
                allow_nan=False,
                allow_infinity=False,
            )
        )
        result.append({
            "id": i,
            "name": f"loan{i}",
            "amount": round(amount, 2),
            "monthly_payment": round(payment, 2),
            "interest_rate": draw(rate),
        })
    return result


@st.composite
def goals_list(draw: st.DrawFn) -> list[dict]:
    """Список финансовых целей (deadline отсутствует → стабильная срочность)."""
    n = draw(st.integers(min_value=0, max_value=4))
    result = []
    for i in range(n):
        target = draw(positive_money)
        current = draw(
            st.floats(
                min_value=0.0, max_value=target, allow_nan=False, allow_infinity=False
            )
        )
        result.append({
            "id": i,
            "name": f"goal{i}",
            "target_amount": round(target, 2),
            "current_amount": round(current, 2),
            "deadline": None,
            "category": draw(st.sampled_from(GOAL_CATEGORIES)),
        })
    return result


@st.composite
def scenario(draw: st.DrawFn) -> dict:
    """
    Полный финансовый срез пользователя. Денежные знаменатели (доход, расходы)
    строго положительны — это область применимости модели (§3: It, Σej > 0).
    """
    income = round(draw(positive_money), 2)
    expense = round(draw(positive_money), 2)
    obligations = draw(obligations_list())
    goals = draw(goals_list())
    obligation_payments = round(sum(o["monthly_payment"] for o in obligations), 2)
    goals_total = round(sum(g["target_amount"] - g["current_amount"] for g in goals), 2)
    rt = round(income - expense - obligation_payments, 2)
    return {
        "income_total": income,
        "expense_total": expense,
        "obligations": obligations,
        "goals": goals,
        "obligation_payments": obligation_payments,
        "goals_total": goals_total,
        "bliq": round(draw(nonneg_money), 2),
        "balance": round(draw(nonneg_money), 2),
        "r_bench": draw(rate),
        "risk": draw(risk_profile),
        "rt": rt,
    }


def _evaluate_all(s: dict) -> list[dict]:
    """Сгенерировать множество A и пересчитать показатели каждой альтернативы."""
    alts = generate_alternatives(s["rt"], s["obligation_payments"], s["goals_total"])
    return [
        evaluate_alternative(
            alt,
            s["income_total"],
            s["expense_total"],
            s["obligations"],
            s["goals"],
            s["r_bench"],
            s["bliq"],
            TODAY,
        )
        for alt in alts
    ]


# ── §4: генерация множества альтернатив ──────────────────────────────────────
class TestAlternativesGeneration:
    @core_settings
    @given(rt=positive_money, payments=positive_money, goals_total=positive_money)
    def test_full_set_is_66(self, rt: float, payments: float, goals_total: float):
        """При rt>0 и наличии и долгов, и целей множество A = ровно 66 (§4.3)."""
        alts = generate_alternatives(rt, payments, goals_total)
        assert len(alts) == 66

    @core_settings
    @given(rt=positive_money, payments=nonneg_money, goals_total=nonneg_money)
    def test_count_at_most_66(self, rt: float, payments: float, goals_total: float):
        """|A| ≤ 66 при любых входах (канон §1: |A| ≤ 66)."""
        alts = generate_alternatives(rt, payments, goals_total)
        assert 1 <= len(alts) <= 66

    @core_settings
    @given(rt=positive_money, payments=positive_money, goals_total=positive_money)
    def test_components_sum_to_rt(self, rt: float, payments: float, goals_total: float):
        """x_d + x_r + x_g = R+_t для каждой альтернативы (§4.2), доли в сумме = 1."""
        for alt in generate_alternatives(rt, payments, goals_total):
            s = alt["x_obligations"] + alt["x_reserve"] + alt["x_goals"]
            assert abs(s - rt) <= 0.02, (alt["id"], s, rt)

    @core_settings
    @given(rt=positive_money, payments=nonneg_money, goals_total=nonneg_money)
    def test_components_nonnegative(self, rt: float, payments: float, goals_total: float):
        """xi ≥ 0 для каждой компоненты каждой альтернативы (§4.2 / §6)."""
        for alt in generate_alternatives(rt, payments, goals_total):
            assert alt["x_obligations"] >= 0
            assert alt["x_reserve"] >= 0
            assert alt["x_goals"] >= 0

    @core_settings
    @given(
        rt=st.floats(min_value=-1e6, max_value=0.0, allow_nan=False, allow_infinity=False),
        payments=nonneg_money,
        goals_total=nonneg_money,
    )
    def test_deficit_is_single(self, rt: float, payments: float, goals_total: float):
        """rt ≤ 0 → одна «дефицитная» альтернатива, распределять нечего (§4.3)."""
        alts = generate_alternatives(rt, payments, goals_total)
        assert len(alts) == 1
        assert alts[0]["id"] == "deficit"
        assert alts[0]["x_obligations"] == 0
        assert alts[0]["x_reserve"] == 0
        assert alts[0]["x_goals"] == 0


# ── §3: базовые финансовые показатели ────────────────────────────────────────
class TestMetricsInvariants:
    @core_settings
    @given(reserve=nonneg_money, expense=positive_money)
    def test_lt_nonneg_and_formula(self, reserve: float, expense: float):
        """Lt = Bliq/Σej, stock-based, ≥ 0 при подушке ≥ 0 (§3.3)."""
        lt = calculate_lt(reserve, expense)
        assert lt >= 0.0
        assert lt == pytest.approx(reserve / expense)

    @core_settings
    @given(payments=nonneg_money, income=positive_money)
    def test_dt_nonneg_and_formula(self, payments: float, income: float):
        """Dt = ΣP/It (ПДН) ≥ 0 (§3.4)."""
        dt = calculate_dt(payments, income)
        assert dt >= 0.0
        assert dt == pytest.approx(payments / income)

    @core_settings
    @given(rt=nonneg_money, payments=nonneg_money)
    def test_rt_definition(self, rt: float, payments: float):
        """Rt = CFt − ΣP: ресурс падает ровно на величину платежей (§3.2)."""
        assert calculate_rt(rt, payments) == pytest.approx(rt - payments)

    @core_settings
    @given(balance=nonneg_money, bliq=nonneg_money, expense=positive_money)
    def test_blr_ge_lt(self, balance: float, bliq: float, expense: float):
        """BLR ⊇ Lt: общий запас не меньше чистой подушки при balance ≥ 0 (§3.5)."""
        blr = calculate_blr(balance, bliq, expense)
        lt = calculate_lt(bliq, expense)
        assert blr >= lt - 1e-9

    @core_settings
    @given(reserve=nonneg_money, payments=nonneg_money, income=positive_money)
    def test_zero_expense_is_safe(self, reserve: float, payments: float, income: float):
        """Σej = 0 → Lt и BLR возвращают 0.0, без деления на ноль (§7 защита)."""
        assert calculate_lt(reserve, 0.0) == 0.0
        assert calculate_blr(reserve, payments, 0.0) == 0.0

    @core_settings
    @given(payments=nonneg_money)
    def test_zero_income_is_safe(self, payments: float):
        """It = 0 → Dt возвращает 0.0, без деления на ноль (§7 защита)."""
        assert calculate_dt(payments, 0.0) == 0.0


# ── §5: производные показатели альтернативы ──────────────────────────────────
class TestAlternativeEvaluation:
    @core_settings
    @given(s=scenario())
    def test_lt_new_reacts_to_reserve(self, s: dict):
        """Lt'(a) = (Bliq + x_r)/Σej ≥ Bliq/Σej и ≥ 0 (§5.2, реагирует на резерв)."""
        base_lt = s["bliq"] / s["expense_total"]
        for alt in _evaluate_all(s):
            assert alt["Lt_new"] >= 0.0
            assert alt["Lt_new"] >= base_lt - 2e-4

    @core_settings
    @given(s=scenario())
    def test_rt_new_ge_baseline(self, s: dict):
        """Rt'(a) ≥ Rt: досрочка только высвобождает поток, не уводит вниз (§5.1)."""
        for alt in _evaluate_all(s):
            assert alt["Rt_new"] >= s["rt"] - 0.02

    @core_settings
    @given(s=scenario())
    def test_dt_new_le_baseline(self, s: dict):
        """Dt'(a) ≤ Dt: досрочка только снижает платёж, значит и ПДН (§5.3)."""
        base_dt = s["obligation_payments"] / s["income_total"]
        for alt in _evaluate_all(s):
            assert alt["Dt_new"] <= base_dt + 2e-4

    @core_settings
    @given(s=scenario())
    def test_avalanche_value_conservation(self, s: dict):
        """x_obl_effective + x_obl_unused = x_obligations: средства не исчезают (§11)."""
        for alt in _evaluate_all(s):
            total = alt["x_obl_effective"] + alt["x_obl_unused"]
            assert total == pytest.approx(alt["x_obligations"], abs=0.02)

    @core_settings
    @given(
        x_obl=nonneg_money,
        obligations=obligations_list(),
        r_bench=rate,
    )
    def test_avalanche_payment_never_grows(
        self, x_obl: float, obligations: list[dict], r_bench: float
    ):
        """Платёж по каждому кредиту после досрочки не больше исходного (§11)."""
        old_by_id = {o["id"]: o for o in obligations}
        _, new_obls, _ = allocate_obligations_avalanche(x_obl, obligations, r_bench)
        for o in new_obls:
            old = old_by_id[o["id"]]
            assert float(o["monthly_payment"]) <= float(old["monthly_payment"]) + 1e-6
            assert float(o["amount"]) <= float(old["amount"]) + 1e-6


# ── §6: допустимость (жёсткие инварианты безопасности) ───────────────────────
class TestFilteringInvariants:
    @core_settings
    @given(s=scenario())
    def test_accepted_satisfy_hard_gate(self, s: dict):
        """Каждая принятая альтернатива: Rt' ≥ 0 и Dt' ≤ 0.40 (§6 жёсткие)."""
        accepted, _ = filter_alternatives(_evaluate_all(s))
        for alt in accepted:
            assert alt["Rt_new"] >= B_MIN
            assert alt["Dt_new"] <= DT_MAX

    @core_settings
    @given(s=scenario())
    def test_partition_is_total(self, s: dict):
        """accepted ∪ rejected = A, без потерь и пересечений (полнота фильтра)."""
        alts = _evaluate_all(s)
        accepted, rejected = filter_alternatives(alts)
        assert len(accepted) + len(rejected) == len(alts)
        acc_ids = {id(a) for a in accepted}
        rej_ids = {id(a) for a in rejected}
        assert acc_ids.isdisjoint(rej_ids)

    @core_settings
    @given(s=scenario())
    def test_default_liquidity_never_rejects(self, s: dict):
        """При L_min=0 допустимость = (Rt'≥0 и Dt'≤0.40); ликвидность не отсевает (§6)."""
        for alt in _evaluate_all(s):
            single, _ = filter_alternatives([alt])
            is_admissible = bool(single)
            expected = alt["Rt_new"] >= B_MIN and alt["Dt_new"] <= DT_MAX
            assert is_admissible == expected


# ── §7–§8: нормализация и SAW-свёртка полезности ─────────────────────────────
class TestRankingInvariants:
    @core_settings
    @given(s=scenario(), risk=risk_profile)
    def test_utility_in_unit_interval(self, s: dict, risk: int):
        """U(a) ∈ [0, 1] для каждой альтернативы при любом профиле (§8)."""
        for alt in rank_alternatives(_evaluate_all(s), risk):
            assert -1e-4 <= alt["utility"] <= 1.0 + 1e-4

    @core_settings
    @given(s=scenario(), risk=risk_profile)
    def test_recommended_is_argmax(self, s: dict, risk: int):
        """Рекомендованная альтернатива = argmax U(a) (§8)."""
        ranked = rank_alternatives(_evaluate_all(s), risk)
        recommended = [a for a in ranked if a.get("is_recommended")]
        assert len(recommended) == 1
        best_utility = max(a["utility"] for a in ranked)
        assert recommended[0]["utility"] == pytest.approx(best_utility)

    @core_settings
    @given(
        value=st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False),
        lo=st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False),
        span=st.floats(min_value=1.0, max_value=1e6, allow_nan=False, allow_infinity=False),
    )
    def test_normalize_in_range_and_complementary(
        self, value: float, lo: float, span: float
    ):
        """min-max ∈ [0,1]; maximize и minimize в сумме = 1 при vmax>vmin (§7)."""
        hi = lo + span
        v = min(max(value, lo), hi)  # значение внутри [lo, hi]
        up = normalize_value(v, lo, hi, minimize=False)
        down = normalize_value(v, lo, hi, minimize=True)
        assert 0.0 <= up <= 1.0
        assert 0.0 <= down <= 1.0
        assert up + down == pytest.approx(1.0)

    @core_settings
    @given(
        value=st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False),
        point=st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False),
    )
    def test_normalize_degenerate_returns_one(self, value: float, point: float):
        """vmax = vmin (нет разброса критерия) → нормировка = 1.0, не делит на ноль (§7)."""
        assert normalize_value(value, point, point) == 1.0


# ── §9: профили риска ────────────────────────────────────────────────────────
class TestRiskProfiles:
    def test_exactly_five_profiles(self):
        """Ровно 5 профилей риска с ключами 1..5 (§9)."""
        assert sorted(RISK_PROFILES.keys()) == [1, 2, 3, 4, 5]

    def test_weights_sum_to_one(self):
        """Веса каждого профиля в сумме = 1.00 (§8: Σwi = 1)."""
        for r, profile in RISK_PROFILES.items():
            total = profile["w_rt"] + profile["w_lt"] + profile["w_dt"] + profile["w_goals"]
            assert total == pytest.approx(1.0), (r, total)

    def test_weight_monotonicity_by_risk(self):
        """Монотонность по риску 1→5: ликвидность строго ↓, цели и ресурс ↗ (§9).

        Канон §9 даёт ликвидность строго убывающей (0.45→0.10), а цели и ресурс —
        неубывающими с плато (цели 0.10,0.20,0.20,0.30,0.40; ресурс
        0.20,0.20,0.25,0.30,0.35), т.е. растут по краям, но не строго на каждом шаге.
        """
        order = [RISK_PROFILES[r] for r in range(1, 6)]
        w_lt = [p["w_lt"] for p in order]
        w_goals = [p["w_goals"] for p in order]
        w_rt = [p["w_rt"] for p in order]
        # ликвидность убывает строго на каждом шаге
        assert all(w_lt[i] > w_lt[i + 1] for i in range(4)), w_lt
        # цели и ресурс не убывают (плато допустимо) и растут от консерватора к агрессору
        assert all(w_goals[i] <= w_goals[i + 1] for i in range(4)), w_goals
        assert w_goals[0] < w_goals[-1], w_goals
        assert all(w_rt[i] <= w_rt[i + 1] for i in range(4)), w_rt
        assert w_rt[0] < w_rt[-1], w_rt
