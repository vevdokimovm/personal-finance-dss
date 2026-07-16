"""Acceptance gates for the FINPILOT portrait generator (pytest).

Why this exists
---------------
The generator produces the synthetic portraits the math model is tested against.
If the generator drifts, model tests keep passing while silently measuring bad
data. These gates assert the *dataset* meets spec BEFORE the model sees it, so in
CI a bad dataset fails the build loudly instead of causing phantom model failures
downstream. They also freeze audit findings P1..P9 as regression guards.

Two groups
----------
TestIntegrity          hard invariants; MUST pass on every version (data isn't broken).
TestPopulationRealism  quality gates encoding P1..P6 + methodology §3 acceptance tests;
                       these are the spec for v3 and are EXPECTED RED on v2 until the
                       generator is fixed. Each red test == one open generator defect.

Usage
-----
Point at the dataset via env var FINPILOT_DATASET_GLOB (defaults to the v2 files so
it runs out of the box). In CI, set it to the generator's fresh output.

    pytest test_generator_acceptance.py -v
"""

from __future__ import annotations

import glob
import gzip
import json
import math
import os
from dataclasses import dataclass, field

import numpy as np
import pytest
from scipy import stats

# --- tunable thresholds (calibrate to your target population / methodology) -----
MIN_RBENCH_DISTINCT = 50          # P3: benchmark must be ~continuous, not 5 buckets
MIN_GOAL_INCOME_CORR = 0.20       # P4: goals scaled to income (target ~ k * income)
KS_LOGNORMAL_ALPHA = 0.05         # P5: income marginal must not reject lognormal
POP_MAX_INCOME_TO_MEDIAN = 100.0  # P1: population layer free of absurd magnitudes
MAX_DEFICIT_SHARE = 0.15          # P8: sanity ceiling on monthly-deficit prevalence
MAX_PERPETUAL_LOAN_SHARE = 0.005  # §3#4: annuity consistency (perpetual/interest-only)
INCOME_EXPENSE_CORR_BAND = (0.40, 0.85)  # plausible richer-spends-more coupling
INTEREST_RATE_BAND = (0.0, 1.0)
REQUIRED_KEYS = {
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
}
DEFAULT_GLOB = "/mnt/user-data/uploads/expert_portraits_v2_part*.gz"


# --- loading --------------------------------------------------------------------
@dataclass
class Dataset:
    rows: list[dict]
    meta: dict = field(default_factory=dict)

    def has_kind(self) -> bool:
        return any("kind" in r for r in self.rows)

    def population(self) -> list[dict]:
        """The realistic-population layer: by `kind` if present, else all rows."""
        if self.has_kind():
            return [r for r in self.rows if r.get("kind") == "population"]
        return self.rows

    # derived arrays (population layer)
    def income(self) -> np.ndarray:
        return np.array([r["income_total"] for r in self.population()], float)

    def expense(self) -> np.ndarray:
        return np.array([r["expense_total"] for r in self.population()], float)

    def debt_service(self) -> np.ndarray:
        return np.array(
            [sum(o["monthly_payment"] for o in r["obligations"]) for r in self.population()],
            float,
        )

    def goal_gap(self) -> np.ndarray:
        return np.array(
            [sum(g["target_amount"] - g["current_amount"] for g in r["goals"])
             for r in self.population()],
            float,
        )


def _load(pattern: str) -> Dataset:
    rows: list[dict] = []
    meta: dict = {}
    for path in sorted(glob.glob(pattern)):
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if "id" not in obj and ("dataset_version" in obj or "seed" in obj):
                    meta.update(obj)  # methodology §4 metadata line
                else:
                    rows.append(obj)
    if not rows:
        pytest.skip(f"no portraits found at {pattern}")
    return Dataset(rows, meta)


@pytest.fixture(scope="session")
def ds() -> Dataset:
    return _load(os.environ.get("FINPILOT_DATASET_GLOB", DEFAULT_GLOB))


# --- group 1: hard invariants (must pass on any version) ------------------------
class TestIntegrity:
    def test_nonempty(self, ds: Dataset) -> None:
        assert len(ds.rows) > 0

    def test_unique_ids(self, ds: Dataset) -> None:
        ids = [r["id"] for r in ds.rows]
        assert len(ids) == len(set(ids)), "duplicate ids present"

    def test_required_keys_present(self, ds: Dataset) -> None:
        missing = [r.get("id", "?") for r in ds.rows if not REQUIRED_KEYS <= set(r)]
        assert not missing, f"{len(missing)} records missing required keys"

    def test_no_nan_or_none_in_money(self, ds: Dataset) -> None:
        bad = 0
        for r in ds.rows:
            vals = [r["income_total"], r["expense_total"], r["bliq"], r["r_bench"]]
            vals += [o["amount"] for o in r["obligations"]]
            vals += [o["monthly_payment"] for o in r["obligations"]]
            vals += [g["target_amount"] for g in r["goals"]]
            vals += [g["current_amount"] for g in r["goals"]]
            bad += sum(1 for v in vals if v is None or (isinstance(v, float) and math.isnan(v)))
        assert bad == 0, f"{bad} NaN/None money values"

    def test_no_negative_money(self, ds: Dataset) -> None:
        neg = 0
        for r in ds.rows:
            vals = [r["income_total"], r["expense_total"], r["bliq"]]
            vals += [o["amount"] for o in r["obligations"]]
            vals += [o["monthly_payment"] for o in r["obligations"]]
            vals += [g["target_amount"] for g in r["goals"]]
            neg += sum(1 for v in vals if v is not None and v < 0)
        assert neg == 0, f"{neg} negative money values"

    def test_interest_rate_band(self, ds: Dataset) -> None:
        lo, hi = INTEREST_RATE_BAND
        bad = [o["interest_rate"] for r in ds.rows for o in r["obligations"]
               if not (lo <= o["interest_rate"] <= hi)]
        assert not bad, f"{len(bad)} interest rates outside {INTEREST_RATE_BAND}"

    def test_risk_tolerance_domain(self, ds: Dataset) -> None:
        bad = [r["risk_tolerance"] for r in ds.rows if r["risk_tolerance"] not in {1, 2, 3, 4, 5}]
        assert not bad, "risk_tolerance outside 1..5"


# --- group 2: population-realism gates (encode P1..P6; expected RED on v2) -------
class TestPopulationRealism:
    def test_kind_labels_present(self, ds: Dataset) -> None:
        # P2: need a layer flag to separate population / boundary / adversarial.
        assert ds.has_kind(), "P2: field `kind` absent — cannot stratify or filter layers"

    def test_dataset_version_present(self, ds: Dataset) -> None:
        # P2/§4: version + seed must be recorded to make iterations comparable.
        has = "dataset_version" in ds.meta or all("dataset_version" in r for r in ds.rows)
        assert has, "P2/§4: dataset_version/seed metadata missing"

    def test_rbench_is_continuous(self, ds: Dataset) -> None:
        # P3: spread = rate - r_bench is a primary branching axis; 5 buckets is too coarse.
        distinct = len({round(r["r_bench"], 6) for r in ds.rows})
        assert distinct >= MIN_RBENCH_DISTINCT, \
            f"P3: r_bench has {distinct} distinct values (< {MIN_RBENCH_DISTINCT})"

    def test_goals_scaled_to_income(self, ds: Dataset) -> None:
        # P4: methodology requires target ~ k * annual income.
        inc, gap = ds.income(), ds.goal_gap()
        mask = (inc > 0) & (gap != 0)
        if mask.sum() < 30:
            pytest.skip("not enough goal-bearing portraits")
        r = float(stats.spearmanr(inc[mask], gap[mask]).correlation)
        assert r >= MIN_GOAL_INCOME_CORR, \
            f"P4: corr(goal_gap, income)={r:.3f} (< {MIN_GOAL_INCOME_CORR}) — goals decoupled"

    def test_income_marginal_lognormal(self, ds: Dataset) -> None:
        # P5 / §3#1: KS against the target marginal must not reject (p > alpha).
        inc = ds.income()
        inc = inc[inc > 0]
        assert len(inc) >= 100, "too few incomes to test"
        shape, loc, scale = stats.lognorm.fit(inc, floc=0)
        p = float(stats.kstest(inc, "lognorm", args=(shape, loc, scale)).pvalue)
        assert p > KS_LOGNORMAL_ALPHA, \
            f"P5: income rejects lognormal (KS p={p:.3g} <= {KS_LOGNORMAL_ALPHA})"

    def test_population_free_of_extreme_magnitudes(self, ds: Dataset) -> None:
        # P1: extreme (1e9-1e10) portraits must live in a flagged boundary layer,
        # not pollute the population layer where aggregates are computed.
        inc = ds.income()
        inc = inc[inc > 0]
        ratio = float(inc.max() / np.median(inc))
        assert ratio <= POP_MAX_INCOME_TO_MEDIAN, \
            f"P1: population max/median income = {ratio:.0f}x (> {POP_MAX_INCOME_TO_MEDIAN}) — extremes not isolated"

    def test_validity_layer_present(self, ds: Dataset) -> None:
        # P6: need flagged malformed records to test reject-garbage behavior.
        if not ds.has_kind():
            pytest.fail("P6: no `kind` field — validity/adversarial layer cannot exist")
        kinds = {r.get("kind") for r in ds.rows}
        assert kinds & {"adversarial", "validity", "invalid"}, \
            "P6: no adversarial/validity layer present"

    def test_deficit_share_sane(self, ds: Dataset) -> None:
        # P8: monthly-deficit prevalence inflated by pooled zero-income/unserviceable edges.
        inc, exp, dsv = ds.income(), ds.expense(), ds.debt_service()
        fcf = inc - exp - dsv
        share = float((fcf < 0).mean())
        assert share <= MAX_DEFICIT_SHARE, \
            f"P8: deficit share = {share:.1%} (> {MAX_DEFICIT_SHARE:.0%}) on population layer"

    def test_annuity_consistency(self, ds: Dataset) -> None:
        # §3#4: outside layers C/D, loans must amortize (payment > monthly interest).
        loans = [o for r in ds.population() for o in r["obligations"]]
        if not loans:
            pytest.skip("no loans")
        perpetual = sum(1 for o in loans
                        if o["monthly_payment"] <= o["amount"] * o["interest_rate"] / 12 + 1e-6)
        share = perpetual / len(loans)
        assert share <= MAX_PERPETUAL_LOAN_SHARE, \
            f"§3#4: {share:.1%} perpetual/interest-only loans (> {MAX_PERPETUAL_LOAN_SHARE:.1%})"

    def test_income_expense_coupling(self, ds: Dataset) -> None:
        # §3#2: realistic positive coupling (richer clients spend more).
        inc, exp = ds.income(), ds.expense()
        mask = (inc > 0) & (exp > 0)
        r = float(stats.spearmanr(inc[mask], exp[mask]).correlation)
        lo, hi = INCOME_EXPENSE_CORR_BAND
        assert lo <= r <= hi, f"corr(income, expense)={r:.3f} outside {INCOME_EXPENSE_CORR_BAND}"
