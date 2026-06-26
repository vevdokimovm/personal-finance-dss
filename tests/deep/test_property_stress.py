"""
Стресс-property финансового ядра (глубокий тир `deep`).

Те же инварианты мат-модели, что в `tests/test_core_properties.py`, но прогнанные
на ПОРЯДКИ большем числе случайных входов и с включённым поиском вырожденных
краёв. Быстрый прогон (`fast`) гоняет property на умеренном числе примеров —
этого хватает на каждый push; этот тир — для редкого глубокого прогона (вручную
или по расписанию), когда хочется выжать редкие контрпримеры.

Запуск: `pytest -m deep`. В быстрый прогон НЕ входит (см. addopts pytest.ini).
"""
from __future__ import annotations

from datetime import datetime

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.filtering import B_MIN, DT_MAX, filter_alternatives
from app.core.ranking import rank_alternatives

# Импортируем готовые стратегии из основного property-файла, чтобы не дублировать.
from tests.test_core_properties import TODAY, scenario

pytestmark = pytest.mark.deep

# Глубокий профиль: много примеров, увеличенный размер данных, без дедлайна.
stress_settings = settings(
    max_examples=2000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
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


@stress_settings
@given(s=scenario())
def test_stress_hard_invariants_hold(s: dict):
    """Под стрессом: каждая принятая альтернатива держит Rt'≥0 и Dt'≤0.40 (§6)."""
    alts = _evaluate_all(s)
    accepted, rejected = filter_alternatives(alts)
    assert len(accepted) + len(rejected) == len(alts)
    for alt in accepted:
        assert alt["Rt_new"] >= B_MIN
        assert alt["Dt_new"] <= DT_MAX


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
