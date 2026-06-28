"""
Стресс-property финансового ядра (глубокий тир `deep`).

Те же инварианты мат-модели, что в `tests/test_core_properties.py`, но прогнанные
на ПОРЯДКИ большем числе случайных входов и с включённым поиском вырожденных
краёв. Быстрый прогон (`fast`) гоняет property на умеренном числе примеров —
этого хватает на каждый push; этот тир — для редкого глубокого прогона (вручную
или по расписанию), когда хочется выжать редкие контрпримеры.

Покрытие инвариантов (канон `docs/math_model_v3_0_0.md`):
  §3   формулы и границы базовых показателей Rt/Lt/Dt/BLR
  §4   |A| = 66, x_d + x_r + x_g = R+_t, xi ≥ 0, единственность вырожденной при дефиците
  §5   производные Rt'/Lt'/Dt' реагируют монотонно
  §6   жёсткие инварианты Rt' ≥ 0 и Dt' ≤ 0.40 на принятых; полнота и дизъюнктность фильтра
  §8   U(a) ∈ [0,1]; рекомендация = argmax и допустима; нормализация в [0,1]
  §11  avalanche: сохранность средств и неувеличение платежей
  Плюс — ДЕТЕРМИНИЗМ: повторный прогон конвейера на тех же входах даёт тот же результат.

Запуск: `pytest -m deep`. В быстрый прогон НЕ входит (см. addopts pytest.ini).
"""
from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.avalanche import allocate_obligations_avalanche
from app.core.filtering import B_MIN, DT_MAX, filter_alternatives
from app.core.metrics import calculate_blr, calculate_dt, calculate_lt, calculate_rt
from app.core.ranking import normalize_value, rank_alternatives

# Готовые стратегии и константы из основного property-файла — без дублирования.
from tests.test_core_properties import (
    TODAY,
    nonneg_money,
    obligations_list,
    positive_money,
    rate,
    scenario,
)

pytestmark = pytest.mark.deep

# Глубокий профиль: много примеров, увеличенный размер данных, без дедлайна.
stress_settings = settings(
    max_examples=3000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
# Лёгкие инварианты (чистые формулы метрик) можно гонять ещё агрессивнее.
metric_settings = settings(
    max_examples=5000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _evaluate_all(s: dict) -> list[dict]:
    alts = generate_alternatives(s["rt"], s["obligation_payments"], s["goals_total"])
    return [
        evaluate_alternative(
            alt, s["income_total"], s["expense_total"],
            s["obligations"], s["goals"], s["r_bench"], s["bliq"], TODAY,
        )
        for alt in alts
    ]


# ── §6: жёсткие инварианты безопасности ──────────────────────────────────────
@stress_settings
@given(s=scenario())
def test_stress_hard_invariants_hold(s: dict):
    """Под стрессом: каждая принятая альтернатива держит Rt'≥0 и Dt'≤0.40 (§6)."""
    accepted, rejected = filter_alternatives(_evaluate_all(s))
    for alt in accepted:
        assert alt["Rt_new"] >= B_MIN
        assert alt["Dt_new"] <= DT_MAX


@stress_settings
@given(s=scenario())
def test_stress_partition_total_and_disjoint(s: dict):
    """Под стрессом: accepted ∪ rejected = A, без потерь и пересечений (полнота фильтра)."""
    alts = _evaluate_all(s)
    accepted, rejected = filter_alternatives(alts)
    assert len(accepted) + len(rejected) == len(alts)
    assert {id(a) for a in accepted}.isdisjoint({id(a) for a in rejected})


# ── §4: структура множества альтернатив ──────────────────────────────────────
@stress_settings
@given(s=scenario())
def test_stress_alternative_count_bounded(s: dict):
    """Под стрессом: |A| ≤ 66; полный набор = 66 только когда есть и долги, и цели (§4.3).

    Если обязательств или целей нет, соответствующее направление отсекается
    (нет смысла предлагать «погасить долг» без долгов) — комбинаций меньше 66.
    """
    alts = generate_alternatives(s["rt"], s["obligation_payments"], s["goals_total"])
    assert len(alts) <= 66
    if s["rt"] > 0 and s["obligation_payments"] > 0 and s["goals_total"] > 0:
        assert len(alts) == 66


@stress_settings
@given(s=scenario())
def test_stress_components_sum_and_nonneg(s: dict):
    """Под стрессом: x_d + x_r + x_g = R+_t и каждая доля ≥ 0 (§4.2)."""
    rt_pos = max(s["rt"], 0.0)
    for alt in _evaluate_all(s):
        parts = (alt["x_obligations"], alt["x_reserve"], alt["x_goals"])
        for x in parts:
            assert x >= -1e-6
        assert sum(parts) == pytest.approx(rt_pos, abs=0.02)


@stress_settings
@given(s=scenario())
def test_stress_deficit_is_single(s: dict):
    """Под стрессом: при дефиците (R+_t = 0) множество вырождается в одну альтернативу (§4.3)."""
    assume(s["rt"] <= 0.0)
    alts = generate_alternatives(s["rt"], s["obligation_payments"], s["goals_total"])
    assert len(alts) == 1
    only = alts[0]
    assert only["x_obligations"] == pytest.approx(0.0)
    assert only["x_reserve"] == pytest.approx(0.0)
    assert only["x_goals"] == pytest.approx(0.0)


# ── §5: производные показатели реагируют монотонно ───────────────────────────
@stress_settings
@given(s=scenario())
def test_stress_derived_metrics_react(s: dict):
    """Под стрессом: Rt'≥Rt, Dt'≤Dt, Lt'≥base — досрочка/резерв двигают метрики в нужную сторону (§5)."""
    base_lt = s["bliq"] / s["expense_total"]
    base_dt = s["obligation_payments"] / s["income_total"]
    for alt in _evaluate_all(s):
        assert alt["Rt_new"] >= s["rt"] - 0.02
        assert alt["Dt_new"] <= base_dt + 2e-4
        assert alt["Lt_new"] >= base_lt - 2e-4
        assert alt["Lt_new"] >= 0.0


# ── §11: Debt Avalanche ──────────────────────────────────────────────────────
@stress_settings
@given(s=scenario())
def test_stress_avalanche_value_conservation(s: dict):
    """Под стрессом: x_obl_effective + x_obl_unused = x_obligations — средства не исчезают (§11)."""
    for alt in _evaluate_all(s):
        total = alt["x_obl_effective"] + alt["x_obl_unused"]
        assert total == pytest.approx(alt["x_obligations"], abs=0.02)


@stress_settings
@given(x_obl=nonneg_money, obligations=obligations_list(), r_bench=rate)
def test_stress_avalanche_payment_never_grows(
    x_obl: float, obligations: list[dict], r_bench: float
):
    """Под стрессом: платёж и остаток по каждому кредиту после досрочки не растут (§11)."""
    old_by_id = {o["id"]: o for o in obligations}
    _, new_obls, _ = allocate_obligations_avalanche(x_obl, obligations, r_bench)
    for o in new_obls:
        old = old_by_id[o["id"]]
        assert float(o["monthly_payment"]) <= float(old["monthly_payment"]) + 1e-6
        assert float(o["amount"]) <= float(old["amount"]) + 1e-6


# ── §8: SAW-ранжирование ─────────────────────────────────────────────────────
@stress_settings
@given(s=scenario(), risk=st.integers(min_value=1, max_value=5))
def test_stress_utility_bounded_and_argmax(s: dict, risk: int):
    """Под стрессом: U(a) ∈ [0,1] и рекомендация = argmax при любом профиле (§8)."""
    ranked = rank_alternatives(_evaluate_all(s), risk)
    for alt in ranked:
        assert -1e-4 <= alt["utility"] <= 1.0 + 1e-4
    recommended = [a for a in ranked if a.get("is_recommended")]
    assert len(recommended) == 1
    assert recommended[0]["utility"] == pytest.approx(max(a["utility"] for a in ranked))


@stress_settings
@given(s=scenario(), risk=st.integers(min_value=1, max_value=5))
def test_stress_recommendation_is_admissible(s: dict, risk: int):
    """Под стрессом: рекомендация из допустимого набора сама проходит жёсткий гейт (§6+§8)."""
    accepted, _ = filter_alternatives(_evaluate_all(s))
    assume(len(accepted) > 0)
    ranked = rank_alternatives(accepted, risk)
    recommended = [a for a in ranked if a.get("is_recommended")]
    assert len(recommended) == 1
    rec = recommended[0]
    assert rec["Rt_new"] >= B_MIN
    assert rec["Dt_new"] <= DT_MAX


# ── Детерминизм: новый инвариант, которого нет в быстром слое ─────────────────
@stress_settings
@given(s=scenario(), risk=st.integers(min_value=1, max_value=5))
def test_stress_pipeline_is_deterministic(s: dict, risk: int):
    """Под стрессом: повторный прогон конвейера на тех же входах даёт идентичный результат.

    Ловит скрытую недетерминированность (нестабильный порядок, неучтённый рандом):
    одинаковый вход обязан давать одинаковые utility и распределение по позициям.
    """
    first = rank_alternatives(_evaluate_all(s), risk)
    second = rank_alternatives(_evaluate_all(s), risk)
    assert len(first) == len(second)
    for a, b in zip(first, second):
        assert a["utility"] == pytest.approx(b["utility"])
        assert a["x_obligations"] == pytest.approx(b["x_obligations"])
        assert a["x_reserve"] == pytest.approx(b["x_reserve"])
        assert a["x_goals"] == pytest.approx(b["x_goals"])
        assert bool(a.get("is_recommended")) == bool(b.get("is_recommended"))


# ── §3: чистые формулы базовых метрик (агрессивный прогон) ────────────────────
@metric_settings
@given(reserve=nonneg_money, expense=positive_money)
def test_stress_lt_formula(reserve: float, expense: float):
    """Под стрессом: Lt = Bliq/Σej, stock-based, ≥ 0 (§3.3)."""
    lt = calculate_lt(reserve, expense)
    assert lt >= 0.0
    assert lt == pytest.approx(reserve / expense)


@metric_settings
@given(payments=nonneg_money, income=positive_money)
def test_stress_dt_formula(payments: float, income: float):
    """Под стрессом: Dt = ΣP/It (ПДН) ≥ 0 (§3.4)."""
    dt = calculate_dt(payments, income)
    assert dt >= 0.0
    assert dt == pytest.approx(payments / income)


@metric_settings
@given(balance=nonneg_money, bliq=nonneg_money, expense=positive_money)
def test_stress_blr_ge_lt(balance: float, bliq: float, expense: float):
    """Под стрессом: BLR ⊇ Lt — общий запас не меньше чистой подушки (§3.5)."""
    assert calculate_blr(balance, bliq, expense) >= calculate_lt(bliq, expense) - 1e-9
    # Rt — определение: ресурс падает ровно на величину платежей (§3.2).
    assert calculate_rt(bliq, balance) == pytest.approx(bliq - balance)


@metric_settings
@given(
    value=st.floats(min_value=0.0, max_value=1e7, allow_nan=False, allow_infinity=False),
    lo=st.floats(min_value=0.0, max_value=1e7, allow_nan=False, allow_infinity=False),
    span=st.floats(min_value=1.0, max_value=1e7, allow_nan=False, allow_infinity=False),
)
def test_stress_normalize_bounded_and_complementary(value: float, lo: float, span: float):
    """Под стрессом: min-max ∈ [0,1]; maximize и minimize в сумме = 1 (§7)."""
    hi = lo + span
    v = min(max(value, lo), hi)  # значение внутри [lo, hi]
    up = normalize_value(v, lo, hi, minimize=False)
    down = normalize_value(v, lo, hi, minimize=True)
    assert 0.0 <= up <= 1.0
    assert 0.0 <= down <= 1.0
    assert up + down == pytest.approx(1.0)
