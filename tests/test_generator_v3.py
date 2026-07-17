"""Приёмочные тесты генератора портретов v3 (слои A–E).

Спецификация — консолидированное ТЗ четырёх экспертов раунда 2:
`docs/model/expert_certification/iterations/2/expert_feedback_aggregate.md` §6
+ архитектура слоёв из `docs/model/expert_certification/iteration_protocol.md`.

v3 — независимая генерация с нуля (не мутация v2): гауссова копула (слой A),
LHS по нормализованным осям (B), детерминированный каталог граничных кейсов (C),
adversarial-мусор с манифестом (D), метаморфические пары с pair_id (E).
Общего с v2 — только схема полей экспертного пакета.
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pytest

from tools.portrait_testing.generator_v3 import (
    EXPERT_FIELDS_V3,
    LAYER_QUOTAS,
    PortraitGeneratorV3,
)

SEED = 20260716
N = 12000


@pytest.fixture(scope="module")
def gen() -> PortraitGeneratorV3:
    return PortraitGeneratorV3(seed=SEED, n=N)


@pytest.fixture(scope="module")
def portraits(gen) -> list[dict]:
    return [gen.generate(i) for i in range(N)]


def _spearman(x: list[float], y: list[float]) -> float:
    rx = np.argsort(np.argsort(np.asarray(x, dtype=float)))
    ry = np.argsort(np.argsort(np.asarray(y, dtype=float)))
    return float(np.corrcoef(rx, ry)[0, 1])


def _implied_term_months(amount: float, rate: float, payment: float) -> float:
    i = rate / 12.0
    if payment <= amount * i:
        return math.inf
    if i == 0:
        return amount / payment
    return -math.log(1.0 - amount * i / payment) / math.log(1.0 + i)


class TestDeterminismAndLayout:
    def test_deterministic_by_seed(self):
        a = PortraitGeneratorV3(seed=SEED, n=N)
        b = PortraitGeneratorV3(seed=SEED, n=N)
        for i in (0, 7, 4999, 11999):
            assert a.generate(i) == b.generate(i)
        c = PortraitGeneratorV3(seed=SEED + 1, n=N)
        assert any(a.generate(i) != c.generate(i) for i in range(50))

    def test_layer_quotas_exact(self, portraits):
        counts = Counter(p["layer"] for p in portraits)
        assert counts == dict(LAYER_QUOTAS)

    def test_meta_declares_design(self, gen):
        meta = gen.meta()
        assert meta["dataset_version"] == 3
        assert meta["seed"] == SEED
        assert meta["layers"] == dict(LAYER_QUOTAS)
        assert "spearman_targets" in meta and "frozen_today" in meta

    def test_layers_interleaved_not_blocked(self, portraits):
        """Слой не должен читаться по позиции id (слепота экспертов)."""
        first_1000 = Counter(p["layer"] for p in portraits[:1000])
        assert len(first_1000) == 5


class TestContinuousBenchmark:
    def test_r_bench_continuous_band(self, portraits):
        vals = {p["r_bench"] for p in portraits if p["layer"] != "D"}
        assert len(vals) >= 1000, "бенчмарк обязан быть непрерывным (D1)"
        assert all(0.08 <= v <= 0.24 for v in vals)

    def test_rate_eq_bench_exact_cases(self, portraits):
        exact = [
            p for p in portraits
            if p["kind"] == "rate_eq_bench_exact"
            and any(o["interest_rate"] == p["r_bench"] for o in p["obligations"])
        ]
        assert len(exact) >= 50


class TestLayerA:
    def test_spearman_targets_within_tolerance(self, portraits, gen):
        a = [p for p in portraits if p["layer"] == "A"]
        inc = [p["income_total"] for p in a]
        goals_sum = [sum(g["target_amount"] for g in p["goals"]) for p in a]
        pay = [sum(o["monthly_payment"] for o in p["obligations"]) for p in a]
        exp = [p["expense_total"] for p in a]
        with_goals = [(i, g) for i, g in zip(inc, goals_sum) if g > 0]
        rs_goals = _spearman([x for x, _ in with_goals], [g for _, g in with_goals])
        rs_ep = _spearman(exp, pay)
        assert 0.30 <= rs_goals <= 0.50, f"цели↔доход {rs_goals:.2f} вне ТЗ (D4)"
        assert 0.20 <= rs_ep <= 0.35, f"расходы↔платежи {rs_ep:.2f} вне ТЗ (D10)"

    def test_income_lognormal_core(self, portraits):
        a = [p for p in portraits if p["layer"] == "A"]
        logs = np.log([p["income_total"] for p in a])
        mu, sigma = float(np.mean(logs)), float(np.std(logs))
        z = np.sort((logs - mu) / sigma)
        cdf = 0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2)))
        emp = (np.arange(1, len(z) + 1)) / len(z)
        d = float(np.max(np.abs(cdf - emp)))
        assert d < 0.02, f"KS D={d:.3f}: маргинал слоя A не лог-нормален (P2/P5)"

    def test_income_tail_not_clamped(self, portraits):
        a = [p["income_total"] for p in portraits if p["layer"] == "A"]
        assert max(a) > 1_000_000, "хвост дохода обрезан (D11)"
        band = sum(1 for x in a if 300_000 <= x <= 1_000_000)
        assert band > 30, "полоса 300 тыс–1 млн пуста (D11)"

    def test_annuity_consistency_outside_cd(self, portraits):
        for p in portraits:
            if p["layer"] not in ("A", "B", "E"):
                continue
            if p["layer"] == "E" and p["pair_role"] != "base":
                continue  # твины наследуют базу + контролируемую дельту (M2)
            for o in p["obligations"]:
                term = _implied_term_months(
                    o["amount"], o["interest_rate"], o["monthly_payment"]
                )
                assert 6.0 - 0.01 <= term <= 360.0 + 0.01, (p["index"], o, term)


class TestLayerBAndGoals:
    def test_n_goals_axis_has_no_hole(self, portraits):
        levels = Counter(len(p["goals"]) for p in portraits if p["layer"] == "B")
        for level in range(9):
            assert levels.get(level, 0) >= 100, f"дыра n_goals={level} (D6)"

    def test_deadline_horizons_beyond_60_months(self, portraits, gen):
        today = gen.meta()["frozen_today"]
        t0 = date.fromisoformat(today[:10])
        long = 0
        for p in portraits:
            if p["layer"] == "D":
                continue
            for g in p["goals"]:
                if g["deadline"] is None:
                    continue
                d = g["deadline"]
                d = d.date() if isinstance(d, datetime) else d
                if (d - t0).days > 60 * 30:
                    long += 1
        assert long >= 300, "страта дедлайнов > 60 мес пуста (D8)"


class TestLayerCCatalog:
    def _kinds(self, portraits, kind):
        return [p for p in portraits if p["kind"] == kind]

    def test_catalog_holes_closed(self, portraits, gen):
        today = date.fromisoformat(gen.meta()["frozen_today"][:10])
        eq = self._kinds(portraits, "target_eq_current_kopeck")
        assert eq and all(
            any(g["target_amount"] == g["current_amount"] for g in p["goals"])
            for p in eq
        )
        bz = self._kinds(portraits, "bliq_zero")
        assert bz and all(p["bliq"] == 0.0 for p in bz)
        fz = self._kinds(portraits, "fcf_zero_exact")
        for p in fz:
            fcf = (p["income_total"] - p["expense_total"]
                   - sum(o["monthly_payment"] for o in p["obligations"]))
            assert abs(fcf) < 1e-6
        dt = self._kinds(portraits, "deadline_today_exact")
        assert dt
        for p in dt:
            dates = [g["deadline"] for g in p["goals"] if g["deadline"] is not None]
            dates = [(d.date() if isinstance(d, datetime) else d) for d in dates]
            assert today in dates
        deep = self._kinds(portraits, "deadline_deep_overdue")
        assert deep
        for p in deep:
            dates = [g["deadline"] for g in p["goals"] if g["deadline"] is not None]
            dates = [(d.date() if isinstance(d, datetime) else d) for d in dates]
            assert any(90 <= (today - d).days <= 730 for d in dates)
        eight = self._kinds(portraits, "eight_goals_same_deadline")
        assert eight
        for p in eight:
            assert len(p["goals"]) == 8
            assert len({g["deadline"] for g in p["goals"]}) == 1

    def test_interest_only_and_growing_are_explicit(self, portraits):
        io = self._kinds(portraits, "interest_only_block")
        gr = self._kinds(portraits, "growing_debt")
        assert len(io) >= 40 and len(gr) >= 40

    def test_toxic_mfo_thin_cushion_present(self, portraits):
        tox = self._kinds(portraits, "toxic_mfo_thin_cushion")
        assert tox
        for p in tox:
            assert any(o["interest_rate"] >= 0.35 for o in p["obligations"])

    def test_magnitude_stratum_isolated_and_capped(self, portraits):
        mag = self._kinds(portraits, "magnitude_1e9")
        assert 60 <= len(mag) <= 200, "магнитудная страта с заявленной долей (D5)"
        for p in mag:
            assert p["income_total"] <= 2e9
        for p in portraits:
            if p["layer"] in ("A", "B"):
                assert p["income_total"] < 5e7, "гиганты вне страты (D5)"


class TestLayerDAdversarial:
    def test_every_d_record_declares_expected_error(self, portraits):
        d = [p for p in portraits if p["layer"] == "D"]
        assert len(d) == dict(LAYER_QUOTAS)["D"]
        assert all(p.get("expected_error") for p in d)

    def test_d_actually_malformed(self, portraits):
        d = [p for p in portraits if p["layer"] == "D"]
        broken = 0
        for p in d:
            ok = True
            if p.get("id_override"):
                ok = False  # дубль id — дефект уровня экспорта, битость по манифесту
            try:
                if p.get("income_total") is None or float(p["income_total"]) < 0:
                    ok = False
                for o in p["obligations"]:
                    if float(o["amount"]) < 0 or float(o["interest_rate"]) < 0:
                        ok = False
                    if float(o["interest_rate"]) > 3.0:
                        ok = False
                for g in p["goals"]:
                    if g["deadline"] is not None and not isinstance(
                        g["deadline"], (date, datetime)
                    ):
                        date.fromisoformat(str(g["deadline"]))
            except (TypeError, ValueError, KeyError):
                ok = False
            broken += not ok
        assert broken == len(d), "каждая D-запись обязана быть реально битой"

    def test_duplicate_id_kind_exists(self, portraits):
        dups = [p for p in portraits if p["kind"] == "duplicate_id"]
        assert dups and all(p.get("id_override") for p in dups)


class TestLayerEMetamorphic:
    def test_pairs_manifest_and_relations(self, portraits, gen):
        e = [p for p in portraits if p["layer"] == "E"]
        assert len(e) == dict(LAYER_QUOTAS)["E"]
        by_pair: dict[str, dict[str, dict]] = {}
        for p in e:
            by_pair.setdefault(p["pair_id"], {})[p["pair_role"]] = p
        assert len(by_pair) == dict(LAYER_QUOTAS)["E"] // 2
        rel_counts = Counter()
        for pid, pair in by_pair.items():
            base, twin = pair["base"], pair["twin"]
            rel = base["pair_relation"]
            rel_counts[rel] += 1
            if rel == "M1_income":
                assert twin["income_total"] == pytest.approx(
                    base["income_total"] * 1.01)
                assert twin["bliq"] == base["bliq"]
            elif rel == "M2_rate":
                for ob, ot in zip(base["obligations"], twin["obligations"]):
                    assert ot["interest_rate"] == pytest.approx(
                        ob["interest_rate"] + 0.01)
            elif rel == "M3_deadline":
                pairs = zip(base["goals"], twin["goals"])
                moved = 0
                for gb, gt in pairs:
                    if gb["deadline"] is None:
                        assert gt["deadline"] is None
                    else:
                        moved += 1
                        db, dt_ = gb["deadline"], gt["deadline"]
                        assert (dt_ - db).days >= 180
                assert moved >= 1
            elif rel == "M4_bliq":
                assert twin["bliq"] == pytest.approx(base["bliq"] * 1.01)
                assert twin["income_total"] == base["income_total"]
            elif rel == "M5_scale":
                k = twin["income_total"] / max(base["income_total"], 1e-9)
                assert k == pytest.approx(10.0)
                assert twin["bliq"] == pytest.approx(base["bliq"] * 10.0)
        assert set(rel_counts) == {
            "M1_income", "M2_rate", "M3_deadline", "M4_bliq", "M5_scale"}


class TestBlindExportContract:
    def test_expert_projection_hides_labels(self, gen):
        row = gen.expert_row(3)
        assert set(row.keys()) == set(EXPERT_FIELDS_V3)
        assert "kind" not in row and "layer" not in row


class TestExportV3:
    """Экспортные контракты v3: канон с метками, слепой пакет, ключ координатора."""

    N_SMALL = 600

    @pytest.fixture()
    def exported(self, tmp_path):
        from tools.model_validation.dataset_export import (
            export_coordinator_key,
            export_expert_pack,
            export_portraits,
        )
        canon = tmp_path / "portraits_v3_test.jsonl.gz"
        export_portraits(canon, n=self.N_SMALL, seed=SEED, version=3)
        parts = export_expert_pack(
            tmp_path, n=self.N_SMALL, seed=SEED, version=3, chunk_size=200)
        key = tmp_path / "portraits_v3_coordinator_key.csv.gz"
        export_coordinator_key(key, n=self.N_SMALL, seed=SEED)
        return canon, parts, key

    def test_canonical_has_meta_and_labels(self, exported):
        import gzip
        import json
        canon, _, _ = exported
        with gzip.open(canon, "rt", encoding="utf-8") as fh:
            lines = [json.loads(line) for line in fh]
        meta, records = lines[0], lines[1:]
        assert meta.get("__meta__") is True and meta["dataset_version"] == 3
        assert meta["seed"] == SEED and "layers" in meta
        assert len(records) == self.N_SMALL
        assert all("layer" in r and "kind" in r for r in records)
        assert any(r["layer"] == "E" and r.get("pair_id") for r in records)

    def test_blind_pack_hides_labels_and_keeps_duplicates(self, exported):
        import gzip
        import json
        _, parts, _ = exported
        rows = []
        for path in parts:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    rec = json.loads(line)
                    if rec.get("__meta__"):
                        assert "layers" not in rec, "конфиг слоёв — утечка дизайна"
                        continue
                    rows.append(rec)
        assert len(rows) == self.N_SMALL
        forbidden = {"layer", "kind", "pair_id", "pair_role",
                     "pair_relation", "expected_error", "index", "l_min"}
        assert all(not (forbidden & set(r)) for r in rows)
        ids = [r["id"] for r in rows]
        assert len(set(ids)) < len(ids), "дубли id обязаны дожить до экспертов"

    def test_coordinator_key_restores_blindness(self, exported):
        import csv
        import gzip
        _, _, key = exported
        with gzip.open(key, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == self.N_SMALL
        assert {"id", "layer", "kind", "pair_id", "pair_relation",
                "expected_error", "id_override"} <= set(rows[0])
        assert sum(1 for r in rows if r["layer"] == "E") > 0
        assert sum(1 for r in rows if r["expected_error"]) > 0

    def test_outcomes_v3_with_invalid_branch(self, tmp_path):
        import csv
        import gzip
        from collections import Counter
        from tools.model_validation.dataset_export import export_model_outcomes
        out = tmp_path / "outcomes_v3.csv.gz"
        n = export_model_outcomes(out, n=self.N_SMALL, seed=SEED, version=3)
        assert n == self.N_SMALL
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == self.N_SMALL
        statuses = Counter(r["status"] for r in rows)
        assert set(statuses) <= {"ok", "deficit", "invalid", "no_admissible_plan"}
        gen = PortraitGeneratorV3(seed=SEED, n=self.N_SMALL)
        d_count = sum(1 for i in range(self.N_SMALL)
                      if gen.layer_by_index[i] == "D")
        # слой D битый по построению => ровно он и должен стать invalid
        assert statuses["invalid"] == d_count
        for r in rows:
            if r["status"] == "invalid":
                assert r["dom"] == "none"
                assert r["xo"] == r["xr"] == r["xg"] == "0.0"
                assert r["invalid_reason"]
            else:
                assert r["invalid_reason"] == ""

    def test_markdown_v3_renders_blind_cards(self, tmp_path):
        from tools.model_validation.dataset_export import export_markdown
        out = tmp_path / "cards.md"
        n = export_markdown(out, n=self.N_SMALL, seed=SEED, version=3)
        text = out.read_text(encoding="utf-8")
        assert n == self.N_SMALL
        # одна карточка на входную строку; дубли id — с повторённым id
        assert text.count("### SP3-") == self.N_SMALL
        ids = [line.split(" · ")[0] for line in text.splitlines()
               if line.startswith("### SP3-")]
        assert len(set(ids)) < self.N_SMALL  # дубли id дожили до карточек
        for token in ("kind", "layer", "pair_id", "expected_error"):
            assert token not in text, f"утечка метки {token}"
        assert "некорректн" in text  # шапка предупреждает про слой сырой выгрузки


class TestPortraitValidator:
    def test_valid_portrait_passes(self):
        from tools.model_validation.portrait_validation import invalid_reason
        gen = PortraitGeneratorV3(seed=SEED, n=1200)
        checked = 0
        for i in range(1200):
            p = gen.generate(i)
            if p["layer"] == "D":
                continue
            assert invalid_reason(p) is None, (p["index"], invalid_reason(p))
            checked += 1
        assert checked > 1000

    def test_every_d_kind_caught_with_reason(self):
        from tools.model_validation.portrait_validation import invalid_reason
        gen = PortraitGeneratorV3(seed=SEED, n=N)
        seen: dict[str, str] = {}
        for i in range(N):
            if gen.layer_by_index[i] != "D":
                continue
            p = gen.generate(i)
            reason = invalid_reason(p)
            assert reason, f"D-запись не поймана: {p['kind']} (index {i})"
            seen.setdefault(p["kind"], reason)
        assert len(seen) == 12, sorted(seen)

    def test_borderline_values_are_valid(self):
        # бриф: «пограничные, но читаемые — НЕ дефект»
        from tools.model_validation.portrait_validation import invalid_reason
        gen = PortraitGeneratorV3(seed=SEED, n=1200)
        base = next(gen.generate(i) for i in range(1200)
                    if gen.layer_by_index[i] == "A" and gen.generate(i)["obligations"])
        base["obligations"][0]["interest_rate"] = 0.59
        base["income_total"] = 1.9e9
        assert invalid_reason(base) is None
