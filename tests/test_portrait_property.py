"""Портретные property-тесты мат-модели (fast-подмножество свипа вехи 7)."""
from __future__ import annotations

import json

from app.core.ranking import RISK_PROFILES
from tools.portrait_testing.generator import EDGE_KINDS, PortraitGenerator
from tools.portrait_testing.invariants import (
    check_forecast_functions,
    check_result,
    check_static_profiles,
)
from tools.portrait_testing.runner import SweepRunner, run_one

SEED = 20260702


def test_static_profile_invariants() -> None:
    assert check_static_profiles() == []
    plateau = [RISK_PROFILES[r]["w_goals"] for r in (2, 3)]
    assert plateau[0] == plateau[1] == 0.20  # плато — сравнение нестрогое по канону


def test_forecast_invariants() -> None:
    assert check_forecast_functions() == []


def test_sweep_small_is_clean() -> None:
    stats = SweepRunner(n=25, seed=SEED, determinism_every=10).run()
    assert stats["crashes"] == [], stats["crashes"]
    assert stats["violations"] == [], stats["violations"][:5]


def test_determinism_on_sample() -> None:
    gen = PortraitGenerator(SEED)
    for i in (1, 7, 13):
        p = gen.generate(i)
        a = json.dumps(run_one(p), sort_keys=True, default=str)
        b = json.dumps(run_one(p), sort_keys=True, default=str)
        assert a == b


def test_deficit_budget_single_alternative() -> None:
    gen = PortraitGenerator(SEED)
    idx = next(i for i in range(0, 600, 3) if gen.kind_for(i) == "deficit_cf")
    portrait = gen.generate(idx)
    result = run_one(portrait)
    payments = sum(o["monthly_payment"] for o in portrait["obligations"])
    rt = portrait["income_total"] - portrait["expense_total"] - payments
    if rt <= 0:
        assert result["alternatives_total"] == 1  # fail-loud: «Дефицитный бюджет»
    assert check_result(portrait, result) == []


def test_overleveraged_fails_loud_not_crash() -> None:
    gen = PortraitGenerator(SEED)
    idx = next(i for i in range(0, 600, 3) if gen.kind_for(i) == "overleveraged")
    portrait = gen.generate(idx)
    result = run_one(portrait)
    assert check_result(portrait, result) == []
    if result["admissible_count"] == 0:
        assert result["best"] is None  # система отказывает громко, а не молчит


def test_edge_kinds_all_covered_without_crash() -> None:
    gen = PortraitGenerator(SEED)
    seen: set[str] = set()
    i = 0
    while seen != set(EDGE_KINDS) and i < 900:
        if gen.kind_for(i) != "plain":
            portrait = gen.generate(i)
            seen.add(portrait["kind"])
            assert check_result(portrait, run_one(portrait)) == []
        i += 3
    assert seen == set(EDGE_KINDS)
