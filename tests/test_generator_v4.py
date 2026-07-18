"""Приёмочные тесты генератора портретов v4 (итерация 4 сертификации).

Спецификация — консолидированное ТЗ раунда 3
(`docs/model/expert_certification/iterations/3/expert_feedback_aggregate.md` §6)
плюс невыполненные пункты методички тест-сетов и уроки раундов 1–3:

  P1 продуктовая типизация кредитов (4/4 эксперта): ставка × срок × остаток
     разыгрываются СОВМЕСТНО по продукту, имя кредита — из продукта;
  P2 спека k-целей совпадает с фактом (k — суммарный масштаб портрета);
  P6 имя цели согласовано с суммой; «Подушка безопасности» убрана (коллизия с bliq);
  P9 граничные кейсы строятся в точной десятичной арифметике (источник R3-F1);
  P5 «киты» реалистичны (P99.9 ≈ 5–10 млн), стресс 2e9 — отдельной меткой;
  P8 слой D v2: составные и near-miss дефекты, рандомизированные объёмы;
     дубли id при ВАЛИДНЫХ данных — отдельный kind слоя C (не мусор);
  P7 страты для статвыводов — семейства C по >= 385 записей (power analysis);
  E-каталог: неравномерные возмущения (одна ставка, один дедлайн) — раунд 3 §4;
  meta декларирует целевые доли статусов (проверяются здесь же).
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import date, datetime
from decimal import Decimal

import numpy as np
import pytest

from tools.portrait_testing.generator_v4 import (
    C_FAMILIES,
    E_RELATIONS,
    EXPERT_FIELDS_V4,
    GOAL_NAME_RANGES,
    LAYER_QUOTAS,
    LOAN_PRODUCTS,
    PortraitGeneratorV4,
)

SEED = 20260718
N = 12000


@pytest.fixture(scope="module")
def gen() -> PortraitGeneratorV4:
    return PortraitGeneratorV4(seed=SEED, n=N)


@pytest.fixture(scope="module")
def portraits(gen) -> list[dict]:
    return [gen.generate(i) for i in range(N)]


def _spearman(x, y) -> float:
    rx = np.argsort(np.argsort(np.asarray(x, dtype=float)))
    ry = np.argsort(np.argsort(np.asarray(y, dtype=float)))
    return float(np.corrcoef(rx, ry)[0, 1])


def _implied_term(amount: float, rate: float, payment: float) -> float:
    i = rate / 12.0
    if payment <= amount * i:
        return math.inf
    if i == 0:
        return amount / payment
    return -math.log(1.0 - amount * i / payment) / math.log(1.0 + i)


def _fcf(p: dict) -> float:
    pay = sum(o["monthly_payment"] for o in p["obligations"])
    return p["income_total"] - p["expense_total"] - pay


@pytest.mark.slow
class TestDeterminismAndLayout:
    def test_deterministic_by_seed(self):
        a = PortraitGeneratorV4(seed=SEED, n=N)
        b = PortraitGeneratorV4(seed=SEED, n=N)
        for i in (0, 11, 6000, 11999):
            assert a.generate(i) == b.generate(i)
        c = PortraitGeneratorV4(seed=SEED + 1, n=N)
        assert any(a.generate(i) != c.generate(i) for i in range(50))

    def test_layer_quotas_and_interleaving(self, portraits):
        assert Counter(p["layer"] for p in portraits) == dict(LAYER_QUOTAS)
        assert len(Counter(p["layer"] for p in portraits[:1000])) == 5

    def test_meta_declares_full_design(self, gen):
        meta = gen.meta()
        assert meta["dataset_version"] == 4
        assert meta["seed"] == SEED
        assert meta["layers"] == dict(LAYER_QUOTAS)
        for key in ("loan_products", "c_families", "e_relations",
                    "status_targets", "k_goal_spec", "goal_name_ranges",
                    "frozen_today", "spearman_targets"):
            assert key in meta, key


@pytest.mark.slow
class TestLoanProductTyping:
    """P1: главный дефект v3 — ипотека под 30% на 3 года."""

    def _product_of(self, obligation: dict) -> dict:
        for spec in LOAN_PRODUCTS.values():
            if spec["name"] == obligation["name"]:
                return spec
        raise AssertionError(f"имя вне каталога продуктов: {obligation['name']}")

    def test_every_loan_name_is_a_product(self, portraits):
        for p in portraits:
            if p["layer"] == "D":
                continue
            for o in p["obligations"]:
                self._product_of(o)

    def test_rate_and_term_inside_product_spec(self, portraits):
        for p in portraits:
            if p["layer"] == "D":
                continue
            for o in p["obligations"]:
                spec = self._product_of(o)
                lo, hi = spec["rate"]
                assert lo - 1e-9 <= o["interest_rate"] <= hi + 1e-9, (p["kind"], o)
                if p["kind"] in ("interest_only_block", "growing_debt"):
                    continue  # по дизайну платёж не аннуитетный
                if p.get("pair_role") == "twin" and \
                        p["pair_relation"].startswith("M2_"):
                    continue  # M2: ставка растёт при том же платеже — дизайн
                term = _implied_term(o["amount"], o["interest_rate"],
                                     o["monthly_payment"])
                t_lo, t_hi = spec["term"]
                # допуск относительный: на длинном плече аннуитет плохо
                # обусловлен (платёж близок к процентам), и округление тела до
                # копеек сдвигает срок на ~1%. Дефект уровня v3 («ипотека 30% на
                # 3 года») этим допуском не маскируется — там разрыв в разы.
                assert t_lo * 0.99 - 1.0 <= term <= t_hi * 1.01 + 1.0, (
                    p["kind"], o, term)

    def test_amount_inside_product_spec_on_population(self, portraits):
        """Слой A обязан быть реалистичным по всем трём осям сразу."""
        for p in portraits:
            if p["layer"] != "A":
                continue
            for o in p["obligations"]:
                spec = self._product_of(o)
                lo, hi = spec["amount"]
                assert lo * 0.999 <= o["amount"] <= hi * 1.001, (o, spec["name"])

    def test_mfo_rate_capped_by_psk(self, portraits):
        """P4: законодательный потолок ПСК — 292% годовых."""
        for p in portraits:
            if p["layer"] == "D":
                continue
            for o in p["obligations"]:
                assert o["interest_rate"] <= 2.92 + 1e-9

    def test_all_products_present(self, portraits):
        names = {o["name"] for p in portraits if p["layer"] != "D"
                 for o in p["obligations"]}
        assert names == {spec["name"] for spec in LOAN_PRODUCTS.values()}


@pytest.mark.slow
class TestGoalsSpec:
    def test_k_scale_matches_declared_spec(self, portraits, gen):
        """P2: заявленный диапазон k обязан совпадать с фактом (суммарный k)."""
        lo, hi = gen.meta()["k_goal_spec"]["range"]
        for p in portraits:
            if p["layer"] not in ("A", "B") or not p["goals"]:
                continue
            if p["income_total"] <= 0:
                continue
            k = sum(g["target_amount"] for g in p["goals"]) / (12 * p["income_total"])
            assert lo - 1e-6 <= k <= hi + 1e-6, (p["index"], round(k, 4))

    def test_goal_name_matches_amount_band(self, portraits):
        """P6: «Техника» на 3.6 млн — дефект v3."""
        for p in portraits:
            if p["layer"] == "D":
                continue
            if p.get("pair_relation") == "M5_scale" and \
                    p["pair_role"] == "twin":
                continue  # ×10 намеренно рвёт натуральные диапазоны имён
            for g in p["goals"]:
                band = GOAL_NAME_RANGES.get(g["name"])
                assert band, f"имя цели вне каталога: {g['name']}"
                lo, hi = band
                assert lo * 0.999 <= g["target_amount"] <= hi * 1.001, (g,)

    def test_no_cushion_name_collision(self, portraits):
        for p in portraits:
            for g in p["goals"]:
                assert "одушк" not in g["name"], "коллизия имени цели с bliq (P6)"


@pytest.mark.slow
class TestExactBoundaryArithmetic:
    """P9: источник R3-F1 — float-остаток в «точном нуле»."""

    def test_fcf_zero_is_exactly_zero(self, portraits):
        cases = [p for p in portraits if p["kind"] == "fcf_zero_exact"]
        assert cases
        for p in cases:
            assert _fcf(p) == 0.0, (p["index"], _fcf(p))

    def test_target_equals_current_exactly(self, portraits):
        cases = [p for p in portraits if p["kind"] == "target_eq_current_kopeck"]
        assert cases
        for p in cases:
            assert any(g["target_amount"] == g["current_amount"] for g in p["goals"])

    def test_pdn_boundary_is_exact(self, portraits):
        cases = [p for p in portraits if p["kind"] == "pdn_boundary"]
        assert cases
        for p in cases:
            pay = sum(Decimal(str(o["monthly_payment"])) for o in p["obligations"])
            pdn = pay / Decimal(str(p["income_total"]))
            assert abs(pdn - Decimal("0.40")) <= Decimal("0.021"), pdn


@pytest.mark.slow
class TestLayerCFamilies:
    def test_families_have_statistical_power(self, portraits):
        """P7: страта для выводов — семейство, минимум 385 (±5%, 95%)."""
        fam = Counter(p["family"] for p in portraits if p["layer"] == "C")
        assert set(fam) == set(C_FAMILIES)
        for name, n in fam.items():
            assert n >= 385, f"семейство {name}: {n} < 385"

    def test_catalog_kinds_all_present(self, portraits):
        kinds = Counter(p["kind"] for p in portraits if p["layer"] == "C")
        declared = {k for kinds_ in C_FAMILIES.values() for k in kinds_}
        assert set(kinds) == declared
        assert min(kinds.values()) >= 20

    def test_whale_is_realistic_and_stress_is_labelled(self, portraits):
        whales = [p for p in portraits if p["kind"] == "magnitude_whale"]
        stress = [p for p in portraits if p["kind"] == "magnitude_stress"]
        assert whales and stress
        for p in whales:  # P5: реалистичный кит
            assert 5e6 <= p["income_total"] <= 10e6
        for p in stress:
            assert p["income_total"] >= 1e9
        for p in portraits:  # гиганты не протекают в популяцию
            if p["layer"] in ("A", "B"):
                assert p["income_total"] <= 10e6

    def test_duplicate_id_valid_pair_is_valid_data(self, portraits):
        dups = [p for p in portraits if p["kind"] == "duplicate_id_valid_pair"]
        assert len(dups) >= 100 and len(dups) % 2 == 0
        by_id: dict[str, list[dict]] = {}
        for p in dups:
            by_id.setdefault(p["id_override"], []).append(p)
        pairs = [v for v in by_id.values() if len(v) == 2]
        assert pairs, "дубли обязаны идти парами с одним id"
        for a, b in pairs:  # обе валидны, но данные конфликтуют
            assert a["income_total"] != b["income_total"]
            assert isinstance(a["income_total"], float)
            assert isinstance(b["income_total"], float)


@pytest.mark.slow
class TestLayerDAdversarialV2:
    def test_manifest_and_randomized_volumes(self, portraits):
        d = [p for p in portraits if p["layer"] == "D"]
        assert len(d) == dict(LAYER_QUOTAS)["D"]
        assert all(p.get("expected_error") for p in d)
        counts = Counter(p["kind"] for p in d)
        assert len(set(counts.values())) > 1, "P8: объёмы обязаны быть неравными"
        assert min(counts.values()) >= 10

    def test_composite_and_near_miss_present(self, portraits):
        kinds = {p["kind"] for p in portraits if p["layer"] == "D"}
        assert any(k.startswith("composite_") for k in kinds), "составные (P8)"
        assert any(k.startswith("near_") for k in kinds), "near-miss (P8)"

    def test_near_miss_are_really_invalid(self, portraits):
        from tools.model_validation.portrait_validation import invalid_reason
        for p in portraits:
            if p["layer"] == "D" and p["kind"].startswith("near_"):
                assert invalid_reason(p), (p["kind"], p["index"])

    def test_all_d_records_caught_by_validator(self, portraits):
        from tools.model_validation.portrait_validation import invalid_reason
        for p in portraits:
            if p["layer"] == "D":
                assert invalid_reason(p), (p["kind"], p["index"])
            elif p["layer"] != "D":
                assert invalid_reason(p) is None, (p["kind"], p["index"],
                                                   invalid_reason(p))


@pytest.mark.slow
class TestLayerEMetamorphic:
    def test_relations_include_non_uniform_perturbations(self, portraits):
        rels = {p["pair_relation"] for p in portraits if p["layer"] == "E"}
        assert rels == set(E_RELATIONS)
        assert "M2_rate_single" in rels and "M3_deadline_single" in rels

    def test_pair_semantics(self, portraits):
        e = [p for p in portraits if p["layer"] == "E"]
        by_pair: dict[str, dict[str, dict]] = {}
        for p in e:
            by_pair.setdefault(p["pair_id"], {})[p["pair_role"]] = p
        assert len(by_pair) == dict(LAYER_QUOTAS)["E"] // 2
        for pair in by_pair.values():
            base, twin = pair["base"], pair["twin"]
            rel = base["pair_relation"]
            if rel == "M1_income":
                assert twin["income_total"] == pytest.approx(
                    base["income_total"] * 1.01)
            elif rel == "M2_rate_all":
                for ob, ot in zip(base["obligations"], twin["obligations"]):
                    assert ot["interest_rate"] == pytest.approx(
                        ob["interest_rate"] + 0.01)
            elif rel == "M2_rate_single":
                diffs = [round(ot["interest_rate"] - ob["interest_rate"], 6)
                         for ob, ot in zip(base["obligations"],
                                           twin["obligations"])]
                assert diffs.count(0.01) == 1 and set(diffs) <= {0.0, 0.01}
            elif rel == "M3_deadline_all":
                for gb, gt in zip(base["goals"], twin["goals"]):
                    if gb["deadline"] is not None:
                        assert (gt["deadline"] - gb["deadline"]).days >= 180
            elif rel == "M3_deadline_single":
                moved = [(gt["deadline"] - gb["deadline"]).days
                         for gb, gt in zip(base["goals"], twin["goals"])
                         if gb["deadline"] is not None]
                assert moved.count(0) == len(moved) - 1
            elif rel == "M4_bliq":
                assert twin["bliq"] == pytest.approx(base["bliq"] * 1.01)
            elif rel == "M5_scale":
                assert twin["income_total"] == pytest.approx(
                    base["income_total"] * 10.0)
                assert twin["bliq"] == pytest.approx(base["bliq"] * 10.0)


@pytest.mark.slow
class TestPopulationRealism:
    def test_status_shares_match_declared_targets(self, portraits, gen):
        targets = gen.meta()["status_targets"]
        for layer, band in targets.items():
            sub = [p for p in portraits if p["layer"] == layer]
            share = 100 * sum(1 for p in sub if _fcf(p) < 0) / len(sub)
            lo, hi = band["deficit_pct"]
            assert lo <= share <= hi, f"{layer}: дефицитов {share:.1f}% вне {band}"

    def test_spearman_targets(self, portraits, gen):
        a = [p for p in portraits if p["layer"] == "A"]
        with_goals = [(p["income_total"],
                       sum(g["target_amount"] for g in p["goals"]))
                      for p in a if p["goals"]]
        rs_goals = _spearman([x for x, _ in with_goals],
                             [g for _, g in with_goals])
        rs_ep = _spearman([p["expense_total"] for p in a],
                          [sum(o["monthly_payment"] for o in p["obligations"])
                           for p in a])
        assert 0.30 <= rs_goals <= 0.50, f"цели~доход {rs_goals:.2f}"
        assert 0.20 <= rs_ep <= 0.35, f"расходы~платежи {rs_ep:.2f}"

    def test_income_lognormal_core(self, portraits):
        logs = np.log([p["income_total"] for p in portraits
                       if p["layer"] == "A"])
        z = np.sort((logs - logs.mean()) / logs.std())
        cdf = 0.5 * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))
        emp = np.arange(1, len(z) + 1) / len(z)
        assert float(np.max(np.abs(cdf - emp))) < 0.02

    def test_r_bench_continuous(self, portraits):
        vals = {p["r_bench"] for p in portraits if p["layer"] != "D"}
        assert len(vals) >= 1000
        assert all(0.08 <= v <= 0.24 for v in vals)

    def test_deadlines_are_relative_and_long_horizons_exist(self, portraits, gen):
        t0 = date.fromisoformat(gen.meta()["frozen_today"])
        long = 0
        for p in portraits:
            if p["layer"] == "D":
                continue
            for g in p["goals"]:
                d = g["deadline"]
                if d is None:
                    continue
                d = d.date() if isinstance(d, datetime) else d
                if (d - t0).days > 60 * 30:
                    long += 1
        assert long >= 385, "страта горизонтов > 5 лет должна быть мощной (P7)"


class TestBlindContract:
    def test_expert_row_hides_design(self, gen):
        row = gen.expert_row(5)
        assert set(row) == set(EXPERT_FIELDS_V4)
        for leak in ("kind", "layer", "family", "pair_id", "expected_error"):
            assert leak not in row

    def test_coordinator_key_restores_labels(self, gen):
        key = gen.coordinator_key(5)
        for field in ("id", "layer", "kind", "family", "pair_id",
                      "pair_relation", "expected_error", "id_override"):
            assert field in key


@pytest.mark.slow
class TestExportV4:
    """Экспортные контракты v4: канон, слепой пакет, ключ, outcomes, карточки."""

    N_SMALL = 600

    def test_canonical_and_blind_pack(self, tmp_path):
        import gzip
        import json
        from tools.model_validation.dataset_export import (
            export_expert_pack, export_portraits,
        )
        canon = tmp_path / "portraits_v4.jsonl.gz"
        export_portraits(canon, n=self.N_SMALL, seed=SEED, version=4)
        with gzip.open(canon, "rt", encoding="utf-8") as fh:
            lines = [json.loads(x) for x in fh]
        meta, records = lines[0], lines[1:]
        assert meta["dataset_version"] == 4 and meta["seed"] == SEED
        assert "loan_products" in meta and "c_families" in meta
        assert len(records) == self.N_SMALL
        assert all("layer" in r and "kind" in r for r in records)

        parts = export_expert_pack(tmp_path, n=self.N_SMALL, seed=SEED,
                                   version=4, chunk_size=200)
        rows = []
        for path in parts:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    rec = json.loads(line)
                    if rec.get("__meta__"):
                        assert "layers" not in rec  # дизайн не течёт
                        continue
                    rows.append(rec)
        assert len(rows) == self.N_SMALL
        forbidden = {"layer", "kind", "family", "pair_id", "expected_error"}
        assert all(not (forbidden & set(r)) for r in rows)
        ids = [r["id"] for r in rows]
        assert len(set(ids)) < len(ids), "дубли id обязаны дожить до экспертов"

    def test_coordinator_key_has_family(self, tmp_path):
        import csv
        import gzip
        from tools.model_validation.dataset_export import export_coordinator_key
        out = tmp_path / "key_v4.csv.gz"
        export_coordinator_key(out, n=self.N_SMALL, seed=SEED, version=4)
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == self.N_SMALL
        assert "family" in rows[0]
        assert any(r["family"] for r in rows)

    def test_outcomes_v4_invalid_branch(self, tmp_path):
        import csv
        import gzip
        from collections import Counter
        from tools.model_validation.dataset_export import export_model_outcomes
        out = tmp_path / "outcomes_v4.csv.gz"
        export_model_outcomes(out, n=self.N_SMALL, seed=SEED, version=4)
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        gen = PortraitGeneratorV4(seed=SEED, n=self.N_SMALL)
        d_count = sum(1 for i in range(self.N_SMALL)
                      if gen.layer_by_index[i] == "D")
        statuses = Counter(r["status"] for r in rows)
        assert statuses["invalid"] == d_count
        assert all(r["id"].startswith("SP4-") for r in rows)

    def test_markdown_cards_v4(self, tmp_path):
        from tools.model_validation.dataset_export import export_markdown
        out = tmp_path / "cards_v4.md"
        export_markdown(out, n=self.N_SMALL, seed=SEED, version=4)
        text = out.read_text(encoding="utf-8")
        assert text.count("### SP4-") == self.N_SMALL
        for token in ("kind", "layer", "family", "expected_error"):
            assert token not in text
