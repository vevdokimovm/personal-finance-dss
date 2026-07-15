"""Тесты детерминированного назначения варианта A/B (P3.5, ядро)."""
from __future__ import annotations

from app.core.experiments import assign_variant

FIFTY_FIFTY = [("control", 50), ("treatment", 50)]


class TestAssignVariant:
    def test_stable_for_same_subject(self):
        # одно и то же назначение при повторных вызовах
        first = assign_variant("exp1", "user-42", FIFTY_FIFTY)
        for _ in range(20):
            assert assign_variant("exp1", "user-42", FIFTY_FIFTY) == first
        assert first in {"control", "treatment"}

    def test_different_experiments_independent(self):
        # один subject в разных экспериментах распределяется независимо (хеш включает ключ)
        a = [assign_variant(f"exp-{i}", "user-42", FIFTY_FIFTY) for i in range(50)]
        assert set(a) == {"control", "treatment"}  # не залип в один вариант на всех экспериментах

    def test_distribution_matches_weights(self):
        # на большой выборке доли близки к весам
        counts = {"control": 0, "treatment": 0}
        n = 4000
        for i in range(n):
            counts[assign_variant("exp-dist", f"user-{i}", FIFTY_FIFTY)] += 1
        assert abs(counts["control"] / n - 0.5) < 0.05

    def test_weighted_split_respected(self):
        counts = {"a": 0, "b": 0}
        n = 4000
        for i in range(n):
            counts[assign_variant("exp-w", f"u-{i}", [("a", 90), ("b", 10)])] += 1
        assert abs(counts["a"] / n - 0.9) < 0.05

    def test_full_weight_always_wins(self):
        for i in range(100):
            assert assign_variant("exp-f", f"u-{i}", [("only", 100), ("never", 0)]) == "only"

    def test_no_subject_returns_none(self):
        assert assign_variant("exp", None, FIFTY_FIFTY) is None
        assert assign_variant("exp", "", FIFTY_FIFTY) is None

    def test_no_variants_or_zero_weights_returns_none(self):
        assert assign_variant("exp", "u", []) is None
        assert assign_variant("exp", "u", [("x", 0), ("y", 0)]) is None
