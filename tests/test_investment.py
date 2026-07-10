"""Тесты инвестиционного транша (модель v3.1.0, дефект G5 экспертизы — минимум).

Терминальный сток модели был «вечная подушка»: на портретах «нет целей +
подушка полна» модель клала 91.9% в резерв, эксперты — 91.3–95.8% в инвестиции
по риск-профилю. Минимум для продукта (консенсус всех четырёх): поток резерва
сверх целевого Lt* — это инвестиционный транш с инструментальной полкой
(депозит / облигации / акции) по профилю риска; вклады — с нотой о лимите АСВ.
"""
from __future__ import annotations

from datetime import datetime

from app.core.investment import EQUITY_SHARE_BY_PROFILE, annotate_investment_tranche
from app.services.planning import run_planning

TODAY = datetime(2026, 7, 2, 12, 0, 0)


class TestAnnotate:
    def test_full_tranche_when_cushion_at_target(self):
        # подушка 8 мес >= цели 4.5 — весь резервный поток становится траншем
        alt = {"x_reserve": 30_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.5, risk_tolerance=3,
        )
        tr = alt["investment_tranche"]
        assert tr is not None
        assert tr["amount"] == 30_000.0
        assert tr["cushion_part"] == 0.0

    def test_no_tranche_below_target(self):
        alt = {"x_reserve": 30_000.0}
        annotate_investment_tranche(
            alt, bliq=100_000.0, expense_total=50_000.0,  # 2 мес < цели
            lt_target=4.5, risk_tolerance=3,
        )
        assert alt["investment_tranche"] is None

    def test_partial_tranche_splits_cushion_first(self):
        # до цели не хватает 25к — они идут в подушку, остальное в транш
        alt = {"x_reserve": 60_000.0}
        annotate_investment_tranche(
            alt, bliq=200_000.0, expense_total=50_000.0,  # 4 мес, цель 4.5
            lt_target=4.5, risk_tolerance=3,
        )
        tr = alt["investment_tranche"]
        assert tr["cushion_part"] == 25_000.0
        assert tr["amount"] == 35_000.0

    def test_split_sums_to_amount_and_profile_shares(self):
        for risk, equity_share in EQUITY_SHARE_BY_PROFILE.items():
            alt = {"x_reserve": 100_000.0}
            annotate_investment_tranche(
                alt, bliq=500_000.0, expense_total=50_000.0,
                lt_target=4.0, risk_tolerance=risk,
            )
            tr = alt["investment_tranche"]
            split = tr["split"]
            assert abs(sum(split.values()) - tr["amount"]) < 0.02
            assert abs(split["equity"] - tr["amount"] * equity_share) < 0.02
            if equity_share == 0.0:
                assert split["equity"] == 0.0

    def test_profile_equity_shares_monotone(self):
        vals = [EQUITY_SHARE_BY_PROFILE[r] for r in sorted(EQUITY_SHARE_BY_PROFILE)]
        assert vals == sorted(vals)
        assert vals[0] == 0.0 and vals[-1] == 0.8

    def test_deposit_insurance_note_present(self):
        alt = {"x_reserve": 50_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.0, risk_tolerance=2,
        )
        assert "АСВ" in alt["investment_tranche"]["note"]


class TestPlanningIntegration:
    def test_terminal_sink_becomes_investment(self):
        # нет целей, подушка 10 мес: раньше «всё в вечный резерв» — теперь
        # резервный поток размечен как инвестиционный транш по профилю
        result = run_planning(
            income_total=150_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=500_000.0,
            r_bench=0.14, risk_tolerance=4, today=TODAY,
        )
        best = result["best"]
        tr = best["investment_tranche"]
        assert tr is not None and tr["amount"] > 0
        assert tr["cushion_part"] == 0.0
        assert best["x_reserve"] == tr["amount"] + tr["cushion_part"]

    def test_no_tranche_when_building_cushion(self):
        result = run_planning(
            income_total=80_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=0.0,
            r_bench=0.14, risk_tolerance=1, today=TODAY,
        )
        best = result["best"]
        assert best["x_reserve"] > 0
        assert best.get("investment_tranche") is None

    def test_explanation_mentions_investment(self):
        result = run_planning(
            income_total=150_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=500_000.0,
            r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        gains = " ".join(result["best"]["explanation"]["gains"])
        assert "инвестиц" in gains.lower()
