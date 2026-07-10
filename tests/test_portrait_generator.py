"""Тесты генератора синтетических портретов: регрессия v1 и калибровка v2.

Дефект v1 (подтверждён пятью независимыми расчётами): долги не связаны
с доходом (corr ~ 0.02), сроки кредитов аномально коротки → 80.8% сета
в дефиците, содержательная оценка модели строится на 17.5% портретов.

v2: долги через целевой ПДН (beta-распределение, калибровка по картине
ЦБ/НБКИ), тело кредита из аннуитета с реалистичным сроком 12–84 мес,
расходы от бюджета «после платежей», adversarial-слой граничных портретов.
v1 сохранён бит-в-бит: joined.csv (12 000 портретов экспертизы)
регенерируется только им.
"""
from __future__ import annotations

import math

from tools.portrait_testing.generator import (
    ADVERSARIAL_KINDS,
    EDGE_KINDS,
    EDGE_KINDS_V1,
    PortraitGenerator,
)

SEED = 20260702


def _rt(p: dict) -> float:
    payments = sum(o["monthly_payment"] for o in p["obligations"])
    return p["income_total"] - p["expense_total"] - payments


class TestV1Regression:
    """v1 обязан оставаться воспроизводимым: на нём построен эталон joined.csv."""

    def test_v1_pins_known_portraits(self):
        gen = PortraitGenerator(SEED, version=1)
        assert gen.generate(0)["kind"] == "zero_income"
        assert round(_rt(gen.generate(1)), 2) == 9295.54   # SP-00001
        assert round(_rt(gen.generate(0)), 2) == -178748.39  # SP-00000

    def test_v1_kind_cycle_unchanged(self):
        gen = PortraitGenerator(SEED, version=1)
        assert [gen.kind_for(i) for i in (0, 3, 6)] == [
            "zero_income", "zero_expenses", "deficit_cf"]
        assert len(EDGE_KINDS_V1) == 9


class TestV2Calibration:
    def test_default_version_is_v2(self):
        assert PortraitGenerator(SEED).version == 2

    def test_deterministic_per_index(self):
        a = PortraitGenerator(SEED).generate(17)
        b = PortraitGenerator(SEED).generate(17)
        assert a == b

    def test_adversarial_kinds_in_rotation(self):
        gen = PortraitGenerator(SEED)
        kinds = {gen.kind_for(i) for i in range(0, 3 * len(EDGE_KINDS), 3)}
        assert set(ADVERSARIAL_KINDS) <= kinds

    def test_deficit_share_is_sane(self):
        gen = PortraitGenerator(SEED)
        portraits = [gen.generate(i) for i in range(1500)]
        deficit = sum(1 for p in portraits if _rt(p) < 0)
        share = deficit / len(portraits)
        # у v1 здесь было ~0.81; допускаем реалистичный кризисный хвост
        assert 0.05 <= share <= 0.35, share

    def test_debt_correlates_with_income(self):
        gen = PortraitGenerator(SEED)
        xs, ys = [], []
        for i in range(1500):
            p = gen.generate(i)
            if p["kind"] != "plain" or not p["obligations"]:
                continue
            xs.append(p["income_total"])
            ys.append(sum(o["monthly_payment"] for o in p["obligations"]))
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
        sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
        corr = cov / (sx * sy)
        assert corr > 0.3, corr  # у v1 было ~0.02

    def test_pdn_distribution_realistic(self):
        gen = PortraitGenerator(SEED)
        pdns = []
        for i in range(1500):
            p = gen.generate(i)
            if p["kind"] != "plain" or not p["obligations"] or p["income_total"] <= 0:
                continue
            pdns.append(
                sum(o["monthly_payment"] for o in p["obligations"]) / p["income_total"]
            )
        pdns.sort()
        median = pdns[len(pdns) // 2]
        p90 = pdns[int(len(pdns) * 0.9)]
        assert 0.15 <= median <= 0.45, median
        assert p90 <= 0.70, p90

    def test_loan_terms_realistic(self):
        # тело кредита восстановимо из аннуитета: срок в коридоре 6–120 мес
        gen = PortraitGenerator(SEED)
        for i in range(600):
            p = gen.generate(i)
            if p["kind"] != "plain":
                continue
            for o in p["obligations"]:
                rate_m = o["interest_rate"] / 12
                a, pay = o["amount"], o["monthly_payment"]
                if pay <= 0 or rate_m <= 0:
                    continue
                if rate_m * a >= pay:  # платёж не покрывает даже проценты
                    raise AssertionError(f"портрет {i}: вечный кредит {o}")
                term = -math.log(1 - rate_m * a / pay) / math.log(1 + rate_m)
                assert 6 <= term <= 120, (i, term, o)

    def test_pdn_boundary_kind_near_gate(self):
        gen = PortraitGenerator(SEED)
        idx = next(i for i in range(0, 900, 3) if gen.kind_for(i) == "pdn_boundary")
        p = gen.generate(idx)
        pdn = sum(o["monthly_payment"] for o in p["obligations"]) / p["income_total"]
        assert 0.39 <= pdn <= 0.41

    def test_rate_at_bench_kind_exact(self):
        gen = PortraitGenerator(SEED)
        idx = next(i for i in range(0, 900, 3) if gen.kind_for(i) == "rate_at_bench")
        p = gen.generate(idx)
        assert p["obligations"]
        assert all(o["interest_rate"] == p["r_bench"] for o in p["obligations"])
