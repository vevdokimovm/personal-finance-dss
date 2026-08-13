"""Тесты инвестиционного транша (модель v3.1.0, дефект G5 экспертизы — минимум).

Терминальный сток модели был «вечная подушка»: на портретах «нет целей +
подушка полна» модель клала 91.9% в резерв, эксперты — 91.3–95.8% в инвестиции
по риск-профилю. Минимум для продукта (консенсус всех четырёх): поток резерва
сверх целевого Lt* — это инвестиционный транш с инструментальной полкой
(депозит / облигации / акции) по профилю риска; вклады — с нотой о лимите АСВ.
"""
from __future__ import annotations

from datetime import datetime

from app.core.investment import (
    EQUITY_SHARE_BY_PROFILE,
    GROWTH_ILLUSTRATION_RATES,
    GROWTH_ILLUSTRATION_YEARS,
    annotate_investment_tranche,
    estimate_iis_deduction,
    project_compound_growth,
)
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

    def test_iis_note_present(self):
        # ADR-014, вариант B: нота про вычет ИИС рядом с нотой АСВ, механику
        # транша не меняет (то же самое разбиение депозит/облигации/акции).
        alt = {"x_reserve": 50_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.0, risk_tolerance=2,
        )
        assert "ИИС" in alt["investment_tranche"]["note"]

    def test_iis_type_a_personalized_note_and_estimate(self):
        # ADR-017: тип А — реальная цифра вычета в note + iis_deduction_estimate.
        alt = {"x_reserve": 50_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.0, risk_tolerance=2,
            iis_type="A", iis_contributed_this_year=0.0,
        )
        tr = alt["investment_tranche"]
        assert tr["iis_deduction_estimate"] == {
            "eligible_amount": 50_000.0, "deduction": 6_500.0,
        }
        assert "6" in tr["note"] and "500" in tr["note"]

    def test_iis_type_b_no_numeric_estimate(self):
        # ADR-017: тип Б/ИИС-3 — остаётся общая нота, никакой выдуманной цифры.
        from app.core.investment import DEPOSIT_INSURANCE_NOTE, IIS_NOTE

        alt = {"x_reserve": 50_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.0, risk_tolerance=2, iis_type="B",
        )
        tr = alt["investment_tranche"]
        assert tr["iis_deduction_estimate"] is None
        assert tr["note"] == f"{DEPOSIT_INSURANCE_NOTE} {IIS_NOTE}"


class TestEstimateIISDeduction:
    def test_type_a_under_limit(self):
        assert estimate_iis_deduction(100_000.0, "A") == {
            "eligible_amount": 100_000.0, "deduction": 13_000.0,
        }

    def test_type_a_over_limit_capped(self):
        result = estimate_iis_deduction(600_000.0, "A")
        assert result == {"eligible_amount": 400_000.0, "deduction": 52_000.0}

    def test_type_a_partial_limit_remaining(self):
        # уже внесено 380 000 в этом году — доступно ещё 20 000
        result = estimate_iis_deduction(100_000.0, "A", contributed_this_year=380_000.0)
        assert result == {"eligible_amount": 20_000.0, "deduction": 2_600.0}

    def test_type_a_limit_exhausted(self):
        result = estimate_iis_deduction(50_000.0, "A", contributed_this_year=400_000.0)
        assert result is None

    def test_type_a_limit_over_exhausted(self):
        # contributed сверх лимита (данные пользователя не проверяются) — не уходит в минус
        result = estimate_iis_deduction(50_000.0, "A", contributed_this_year=450_000.0)
        assert result is None

    def test_type_b_returns_none(self):
        assert estimate_iis_deduction(100_000.0, "B") is None

    def test_type_three_returns_none(self):
        assert estimate_iis_deduction(100_000.0, "three") is None

    def test_type_none_returns_none(self):
        assert estimate_iis_deduction(100_000.0, "none") is None

    def test_zero_amount_returns_none(self):
        assert estimate_iis_deduction(0.0, "A") is None


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

    def test_iis_status_does_not_affect_decision_adr_017(self):
        """Красная линия ADR-017: iis_type/iis_contributed_this_year влияют
        ТОЛЬКО на текст/диагностику investment_tranche, не на Rt/Dt/победителя.
        Тот же портрет с трёх разных статусов ИИС должен дать идентичное решение."""
        kwargs = dict(
            income_total=150_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=500_000.0,
            r_bench=0.14, risk_tolerance=4, today=TODAY,
        )
        baseline = run_planning(**kwargs)
        with_iis_a = run_planning(
            **kwargs, iis_type="A", iis_contributed_this_year=0.0,
        )
        with_iis_a_maxed = run_planning(
            **kwargs, iis_type="A", iis_contributed_this_year=1_000_000.0,
        )

        for other in (with_iis_a, with_iis_a_maxed):
            assert other["indicators"]["Rt"] == baseline["indicators"]["Rt"]
            assert other["indicators"]["Dt"] == baseline["indicators"]["Dt"]
            assert other["best"]["id"] == baseline["best"]["id"]
            assert other["best"]["utility"] == baseline["best"]["utility"]

        # но диагностика транша реально разная (иначе тест ничего не проверял бы)
        assert with_iis_a["best"]["investment_tranche"]["iis_deduction_estimate"] is not None
        assert with_iis_a_maxed["best"]["investment_tranche"]["iis_deduction_estimate"] is None


class TestProjectCompoundGrowth:
    def test_matches_compound_interest_formula(self):
        result = project_compound_growth(100_000.0, years=[10], rates=[0.08])
        assert result == [
            {"rate": 0.08, "years": 10, "future_value": round(100_000.0 * 1.08**10, 2)}
        ]

    def test_default_years_and_rates_used(self):
        result = project_compound_growth(100_000.0)
        assert len(result) == len(GROWTH_ILLUSTRATION_YEARS) * len(GROWTH_ILLUSTRATION_RATES)
        assert {r["years"] for r in result} == set(GROWTH_ILLUSTRATION_YEARS)
        assert {r["rate"] for r in result} == set(GROWTH_ILLUSTRATION_RATES)

    def test_higher_rate_gives_higher_value_same_years(self):
        result = project_compound_growth(100_000.0, years=[10], rates=[0.05, 0.12])
        by_rate = {r["rate"]: r["future_value"] for r in result}
        assert by_rate[0.12] > by_rate[0.05]

    def test_zero_amount_returns_none(self):
        assert project_compound_growth(0.0) is None

    def test_negative_amount_returns_none(self):
        assert project_compound_growth(-100.0) is None


class TestAnnotateGrowthIllustration:
    def test_growth_illustration_present_when_tranche_exists(self):
        alt = {"x_reserve": 50_000.0}
        annotate_investment_tranche(
            alt, bliq=400_000.0, expense_total=50_000.0,
            lt_target=4.0, risk_tolerance=2,
        )
        tr = alt["investment_tranche"]
        assert tr["growth_illustration"] is not None
        assert len(tr["growth_illustration"]) == (
            len(GROWTH_ILLUSTRATION_YEARS) * len(GROWTH_ILLUSTRATION_RATES)
        )

    def test_growth_illustration_absent_when_no_tranche(self):
        alt = {"x_reserve": 30_000.0}
        annotate_investment_tranche(
            alt, bliq=100_000.0, expense_total=50_000.0,  # 2 мес < цели — транша нет
            lt_target=4.5, risk_tolerance=3,
        )
        assert alt["investment_tranche"] is None
