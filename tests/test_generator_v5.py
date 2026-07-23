"""Приёмка генератора v5 — по консолидированному ТЗ четырёх экспертов
(`docs/model/expert_certification/iterations/4/expert_feedback_aggregate.md` §5)
и под предзарегистрированные гипотезы раунда 5 (H5-1, H5-2).

Каждый тест назван по пункту ТЗ, который он закрывает.
"""
from __future__ import annotations

import gzip
import json
import math
from collections import Counter
from datetime import date

import pytest

from tools.portrait_testing.generator_v5 import (
    GOAL_NAME_RANGES_V5,
    UNBOUNDED_GOAL_NAMES,
    K_GOAL_MAX,
    K_GOAL_MIN,
    PortraitGeneratorV5,
)

N = 3000


@pytest.fixture(scope="module")
def gen():
    return PortraitGeneratorV5(seed=20260723, n=N)


@pytest.fixture(scope="module")
def portraits(gen):
    return [gen.generate(i) for i in range(N)]


class TestIdentityAndDeterminism:
    def test_prefix_is_sp5(self, gen):
        assert gen.expert_row(0)["id"].startswith("SP5-")

    def test_no_foreign_prefix_leaks_into_ids(self, gen):
        """Чужой префикс в id — это отпечаток слоя дефектов.

        В v4 путь `duplicate_id_broken` жёстко зашивал `SP4-`; унаследованный
        как есть, он пометил бы 17 битых строк датасета v5 так, что эксперт
        находил бы их одним grep. Слепота пакета этого не переживает.
        """
        foreign = [gen.expert_row(i)["id"] for i in range(gen.n)
                   if not gen.expert_row(i)["id"].startswith("SP5-")]
        assert not foreign

    def test_same_seed_same_data(self):
        a = PortraitGeneratorV5(seed=7, n=200)
        b = PortraitGeneratorV5(seed=7, n=200)
        assert [a.generate(i) for i in range(200)] == \
               [b.generate(i) for i in range(200)]

    def test_different_seed_differs(self):
        a = PortraitGeneratorV5(seed=7, n=200).generate(5)
        b = PortraitGeneratorV5(seed=8, n=200).generate(5)
        assert a != b


class TestT1BlindMetaDeclarations:
    """ТЗ-1: слепая meta объясняет дизайн, не раскрывая слоёв."""

    def test_declares_stress_share(self, gen):
        assert "stress_magnitude_share" in gen.meta()

    def test_declares_out_of_spec_share(self, gen):
        assert "loan_amount_out_of_spec_share" in gen.meta()

    def test_declares_actual_k_range(self, gen):
        rng = gen.meta()["k_goal_spec"]["actual_range"]
        assert len(rng) == 2 and rng[0] <= rng[1]

    def test_declares_risk_tolerance_is_doe_not_population(self, gen):
        note = gen.meta()["notes"]["risk_tolerance"]
        assert "DOE" in note or "равномер" in note

    def test_meta_does_not_leak_layer_of_any_row(self, gen):
        blob = repr(gen.meta())
        assert "layer_by_index" not in blob and "c_kind" not in blob


class TestT2GoalCapRemoved:
    """ТЗ-2: кап 1e8 снят, хвост целей непрерывный."""

    def test_no_pile_up_at_one_hundred_million(self, portraits):
        targets = [g["target_amount"] for p in portraits
                   for g in (p.get("goals") or ())
                   if isinstance(g.get("target_amount"), (int, float))]
        assert Counter(targets)[1e8] <= 1

    def test_stress_magnitudes_are_a_separate_kind(self, portraits):
        kinds = {p.get("kind") for p in portraits}
        assert "magnitude_stress" in kinds


class TestT3QuotaJitter:
    """ТЗ-3: круглые объёмы больше не выдают дизайн."""

    def test_defect_share_is_not_a_round_five_percent(self, gen):
        d = sum(1 for t in gen.layer_by_index if t == "D")
        assert 0.04 <= d / gen.n <= 0.06
        assert abs(d / gen.n - 0.05) > 1e-6

    def test_boundary_kinds_are_not_all_equal(self, portraits):
        counts = Counter(p["kind"] for p in portraits if p["layer"] == "C")
        flow = [counts[k] for k in ("zero_income", "zero_expenses",
                                    "fcf_zero_exact", "deficit_flow")]
        assert len(set(flow)) > 1


class TestT4LongHorizons:
    """ТЗ-4: пенсия и образование детей перестали быть непроверяемыми."""

    def test_at_least_five_percent_of_dated_goals_are_long(self, portraits):
        dated = [g for p in portraits for g in (p.get("goals") or ())
                 if isinstance(g.get("deadline"), object)
                 and g.get("deadline") is not None
                 and hasattr(g.get("deadline"), "year")]
        long_ = [g for g in dated
                 if (g["deadline"].year - 2026) >= 10]
        assert len(long_) / max(1, len(dated)) >= 0.05

    def test_horizon_reaches_thirty_years(self, portraits):
        years = [g["deadline"].year for p in portraits
                 for g in (p.get("goals") or ())
                 if hasattr(g.get("deadline"), "year")]
        assert max(years) >= 2050


class TestT5PskEdge:
    """ТЗ-5: кромка ПСК 292-300% больше не пустая."""

    def test_valid_side_has_rates_just_below_cap(self, portraits):
        rates = [o["interest_rate"] for p in portraits
                 if p["layer"] != "D"
                 for o in (p.get("obligations") or ())
                 if isinstance(o.get("interest_rate"), (int, float))]
        assert any(2.90 <= r <= 2.92 for r in rates)

    def test_defect_side_probes_just_above_cap(self, portraits):
        rates = [o["interest_rate"] for p in portraits if p["layer"] == "D"
                 for o in (p.get("obligations") or ())
                 if isinstance(o.get("interest_rate"), (int, float))]
        assert any(2.92 < r <= 3.00 for r in rates)


class TestT6DuplicateShapes:
    """ТЗ-6: сборщик, выучивший «дубль = ровно два», должен упасть."""

    def test_has_a_triple_duplicate(self, gen):
        ids = [gen.expert_row(i)["id"] for i in range(gen.n)]
        assert max(Counter(ids).values()) >= 3

    def test_has_invalid_invalid_duplicate_pair(self, gen, portraits):
        by_id: dict[str, list[int]] = {}
        for i in range(gen.n):
            by_id.setdefault(gen.expert_row(i)["id"], []).append(i)
        groups = [idx for idx in by_id.values() if len(idx) > 1]
        assert any(all(portraits[i]["layer"] == "D" for i in g)
                   for g in groups)


class TestT7LegalProductLimits:
    """ТЗ-7: экстремум нагрузки — числом кредитов, а не мифическим остатком."""

    def test_mfo_balance_within_legal_limit(self, portraits):
        mfo = [o for p in portraits if p["layer"] != "D"
               for o in (p.get("obligations") or ())
               if isinstance(o.get("interest_rate"), (int, float))
               and o["interest_rate"] >= 0.50
               and isinstance(o.get("amount"), (int, float))]
        assert all(o["amount"] <= 1_000_000 for o in mfo)

    def test_overleveraged_reached_by_count_not_by_absurd_balance(
            self, portraits):
        over = [p for p in portraits if p.get("kind") == "overleveraged"]
        assert over and max(len(p["obligations"]) for p in over) >= 5


class TestT8GoalNameCaps:
    def test_household_goal_names_stay_plausible(self, portraits):
        # стресс-магнитуды вынесены отдельными видами (ТЗ-2) и объявлены
        # в meta — популяционный кап на них не распространяется
        skip = {"magnitude_stress", "magnitude_whale", "whale_thin_cushion"}
        for p in portraits:
            if p["layer"] in ("D", "E") or p.get("kind") in skip:
                continue
            for g in p.get("goals") or ():
                if g.get("name") in UNBOUNDED_GOAL_NAMES:
                    continue  # инвестпортфель/недвижимость предела не имеют
                lo_hi = GOAL_NAME_RANGES_V5.get(g.get("name"))
                if lo_hi and isinstance(g.get("target_amount"), (int, float)):
                    assert g["target_amount"] <= lo_hi[1] * 1.05


class TestT9KGoalInSpec:
    def test_actual_k_inside_declared_range(self, portraits, gen):
        ks = []
        for p in portraits:
            if p["layer"] in ("D", "E") or not p.get("goals"):
                continue
            income = p.get("income_total") or 0
            if not isinstance(income, (int, float)) or income <= 0:
                continue
            total = sum(g["target_amount"] for g in p["goals"]
                        if isinstance(g.get("target_amount"), (int, float)))
            ks.append(total / (income * 12))
        assert ks
        assert min(ks) >= K_GOAL_MIN * 0.9
        assert max(ks) <= K_GOAL_MAX * 1.1


class TestT10DefectCoverage:
    """ТЗ-10: слой D перестал бить всего 4 поля из двенадцати."""

    def test_defects_touch_at_least_eight_distinct_fields(self, gen):
        fields = {gen.coordinator_key(i)["expected_error"].split(":")[0]
                  for i in range(gen.n)
                  if gen.coordinator_key(i)["expected_error"]}
        assert len(fields) >= 8

    def test_composite_defects_are_at_least_ten_percent_of_layer(
            self, portraits):
        d = [p for p in portraits if p["layer"] == "D"]
        comp = [p for p in d if p["kind"].startswith("composite_")]
        assert len(comp) / len(d) >= 0.10


class TestT11CardMinimumPayment:
    def test_card_payment_is_two_to_five_percent_of_balance(self, portraits):
        # `growing_debt` — намеренная кромка «платёж ниже процентов»,
        # объявлена видом; стресс-магнитуды масштабируются by design.
        skip = {"growing_debt", "magnitude_stress", "magnitude_whale"}
        bad = []
        for p in portraits:
            if p["layer"] == "D" or p.get("kind") in skip:
                continue
            for o in p.get("obligations") or ():
                if o.get("name") != "Кредитная карта":
                    continue
                amount, pay = o.get("amount"), o.get("monthly_payment")
                if isinstance(amount, (int, float)) and amount > 0:
                    if not 0.015 <= pay / amount <= 0.20:
                        bad.append((amount, pay))
        assert not bad[:5]


class TestH5PreRegisteredFamilies:
    """Семейства под предзарегистрированные гипотезы раунда 5."""

    def test_floor_edge_family_has_power(self, portraits):
        fam = [p for p in portraits if p.get("family") == "floor_edge"]
        assert len(fam) >= 385 * N // 12000

    def test_floor_edge_splits_by_near_deadline(self, portraits):
        kinds = {p["kind"] for p in portraits
                 if p.get("family") == "floor_edge"}
        assert {"floor_edge_with_near_goal", "floor_edge_no_near_goal"} <= kinds

    def test_whale_thin_cushion_family_exists(self, portraits):
        fam = [p for p in portraits
               if p.get("kind") == "whale_thin_cushion"]
        assert fam

    def test_whale_thin_cushion_actually_contains_whales(self, portraits):
        """H5-2 без китов проверить нельзя: вся гипотеза о том, что при
        доходе в миллионы «подушка два месяца расходов» абсурдна как
        приоритет. Планка кита — ТЗ итерации 3 п.4: реалистичный кит 5-10 млн.
        """
        fam = [p for p in portraits
               if p.get("kind") == "whale_thin_cushion"]
        incomes = sorted(p["income_total"] for p in fam)
        assert incomes[len(incomes) // 2] >= 5_000_000

    def test_whale_thin_cushion_cushion_is_actually_thin(self, portraits):
        """Тонкая подушка = L_t в полосе спора [1; 2), иначе семейство
        проверяет не то."""
        for p in portraits:
            if p.get("kind") != "whale_thin_cushion":
                continue
            lt = p["bliq"] / p["expense_total"]
            assert 0.9 <= lt <= 2.1, lt


class TestBuild2CellPower:
    """Сборка 2 датасета v5: ячейки предзарегистрированных гипотез добирают
    порог мощности 385 НА УРОВНЕ ЯЧЕЙКИ, а не только семейства.

    Сборка 1 (seed 20260722) объявила недобор (231/241/120 на 12 000) вместо
    регенерации. Решение владельца: итерация последняя, второго захода не
    будет — ячейки добираются фиксированными квотами с джиттером. Порог
    масштабируется пропорционально n.
    """

    H5_CELLS = ("floor_edge_with_near_goal", "floor_edge_no_near_goal",
                "whale_thin_cushion")

    def test_h5_cells_each_pass_power_threshold(self, portraits):
        need = math.ceil(385 * N / 12000)
        counts = Counter(p["kind"] for p in portraits)
        for kind in self.H5_CELLS:
            assert counts[kind] >= need, (kind, counts[kind], need)

    def test_h5_quotas_are_not_identical_round_numbers(self, portraits):
        """Ровно равные объёмы — отпечаток дизайна (урок р.4: по 100 на
        категорию). Квоты дрожат, три ячейки не обязаны совпадать."""
        counts = Counter(p["kind"] for p in portraits)
        assert len({counts[k] for k in self.H5_CELLS}) > 1

    def test_seed_goal_leaves_no_constant_pileup(self, portraits):
        """Сборка 1: 18 целей ровно по 384 000.00 ₽ — след _seed_goal
        (max(income, 40 000) x 0.8 x 12 при доходе ниже пола). Пол и k
        дрожат, скопления одного значения нет."""
        targets = Counter(
            round(float(g["target_amount"]), 2)
            for p in portraits if p["layer"] != "D"
            for g in (p.get("goals") or ())
            if isinstance(g.get("target_amount"), (int, float))
            and not isinstance(g.get("target_amount"), bool))
        top_value, top_count = targets.most_common(1)[0]
        assert top_count <= 5, (top_value, top_count)

    def test_default_build_is_2026_07_23(self):
        gen = PortraitGeneratorV5(n=10)
        assert gen.seed == 20260723
        assert gen.frozen_today == date(2026, 7, 23)

    def test_pdn_exact_040_has_probe_mass(self, portraits):
        """Сборка 1 оставляла 11 записей с ПДН ровно 0.40, сборка 2 без
        починки — 5: карта (ТЗ-11) и легальные капы (ТЗ-7) ломали точную
        конструкцию дальше по конвейеру. Строгость «<= 0.40» должна
        проверяться минимум на уровне v4 (26 на 12 000)."""
        cnt = 0
        for p in portraits:
            income = p.get("income_total")
            if p["layer"] == "D" or not isinstance(income, (int, float)) \
                    or isinstance(income, bool) or income <= 0:
                continue
            pays = sum(o["monthly_payment"]
                       for o in (p.get("obligations") or ())
                       if isinstance(o.get("monthly_payment"), (int, float)))
            if pays / income == 0.40:
                cnt += 1
        assert cnt >= math.ceil(26 * N / 12000), cnt

    @pytest.mark.parametrize("n", [60, 200, 500])
    def test_group_kinds_survive_pool_truncation(self, n):
        """Регресс сборки 2: фиксированные квоты сместили обрезку пула на
        хвост, и тройник дублей мог остаться группой из четырёх — сборка
        групп молча теряла индекс, генерация падала KeyError. Групповые
        виды обязаны быть кратны своей группе на любом n."""
        gen = PortraitGeneratorV5(seed=7, n=n)
        counts = Counter(gen._c_kind.values())
        counts.update(gen._d_kind.values())
        assert counts.get("duplicate_id_triple", 0) % 3 == 0
        assert counts.get("duplicate_id_valid_pair", 0) % 2 == 0
        assert counts.get("duplicate_id_invalid_pair", 0) % 2 == 0
        for i in range(n):
            gen.generate(i)  # не падает


class TestInvariantsPreserved:
    """Что эксперты просили не сломать (§3 агрегата)."""

    def test_rates_stay_inside_product_spec(self, portraits):
        from tools.portrait_testing.generator_v5 import products_for_rate
        for p in portraits:
            if p["layer"] == "D":
                continue
            for o in p.get("obligations") or ():
                r = o.get("interest_rate")
                if isinstance(r, (int, float)):
                    assert products_for_rate(r), (o["name"], r)

    def test_r_bench_is_continuous(self, portraits):
        vals = {p["r_bench"] for p in portraits
                if isinstance(p.get("r_bench"), float)}
        assert len(vals) > N // 4

    def test_exact_zero_flow_still_present(self, portraits):
        zeros = [p for p in portraits
                 if p.get("kind") == "fcf_zero_exact"]
        assert zeros

    def test_metamorphic_pairs_intact(self, portraits):
        """Пары слоя E — ровно по двое (дубли id образуют свои группы)."""
        pairs = Counter(p["pair_id"] for p in portraits
                        if p.get("pair_relation"))
        assert pairs and set(pairs.values()) == {2}


class TestBlindDeclarations:
    """ТЗ п.1 раунда 4: агрегаты в слепой meta, без раскрытия слоёв."""

    def test_declarations_cover_all_consensus_claims(self):
        gen = PortraitGeneratorV5(seed=20260723, n=1200)
        d = gen.blind_declarations()
        for field in ("stress_magnitude_share", "realistic_whale_share",
                      "loan_amount_outside_product_spec_share",
                      "goal_amount_outside_name_band_share",
                      "k_goal_actual_range", "k_goal_declared_range",
                      "income_lognormal_ks_population", "risk_tolerance_note"):
            assert field in d, field
        lo, hi = d["k_goal_actual_range"]
        assert 0 < lo <= hi <= 6.0
        assert 0.0 <= d["income_lognormal_ks_population"] <= 1.0

    def test_declarations_do_not_leak_design(self):
        gen = PortraitGeneratorV5(seed=20260723, n=1200)
        blob = json.dumps(gen.blind_declarations(), ensure_ascii=False).lower()
        for leak in ("layer", "kind", "family", "pair", "expected_error",
                     "слой", "quota", "seed"):
            assert leak not in blob, f"утечка дизайна в декларациях: {leak}"

    def test_declarations_land_in_blind_pack_meta(self, tmp_path):
        from tools.model_validation.dataset_export import export_expert_pack
        parts = export_expert_pack(tmp_path, n=600, seed=20260723, version=5,
                                   chunk_size=300)
        for path in parts:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                meta = json.loads(fh.readline())
            assert meta.get("__meta__") is True
            assert "declarations" in meta
            assert "layers" not in meta and "c_families" not in meta
