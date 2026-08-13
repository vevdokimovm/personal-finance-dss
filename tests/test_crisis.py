"""Тесты кризисного модуля (модель v3.1.0, дефект G2 независимой экспертизы).

При Rt < 0 модель обязана выдавать план действий, а не пустой объект:
закрытие кредита из ликвидности (если разворачивает поток при сохранении
floor-резерва), размер сокращения расходов до нуля дефицита, потолок трат,
заморозка целей, реструктуризация приоритетного кредита, запас хода.
"""
from __future__ import annotations

from datetime import datetime

from app.core.crisis import build_crisis_plan
from app.services.planning import run_planning

TODAY = datetime(2026, 7, 2, 12, 0, 0)


def _plan(**kwargs):
    defaults = dict(
        income_total=50_000.0,
        expense_total=60_000.0,
        obligations=[],
        goals=[],
        bliq=0.0,
        today=TODAY,
    )
    defaults.update(kwargs)
    return build_crisis_plan(**defaults)


class TestCrisisBasics:
    def test_positive_flow_returns_none(self):
        assert _plan(income_total=100_000, expense_total=40_000) is None

    def test_deficit_produces_actions(self):
        plan = _plan()
        assert plan is not None
        assert plan["deficit"] == 10_000.0
        assert len(plan["actions"]) >= 1
        assert plan["severity"] in (
            "recoverable_from_liquidity", "cut_required", "critical"
        )
        assert isinstance(plan["summary"], str) and plan["summary"]

    def test_runway_months(self):
        plan = _plan(bliq=30_000.0)  # дефицит 10к, подушка на 3 месяца дефицита
        assert plan["runway_months"] == 3.0

    def test_expense_cut_to_zero_deficit(self):
        plan = _plan()
        cut = next(a for a in plan["actions"] if a["type"] == "cut_expenses")
        assert cut["amount"] == 10_000.0
        # потолок трат: сколько можно тратить на жизнь, не углубляя долг
        assert plan["max_affordable_expenses"] == 50_000.0

    def test_goals_frozen_in_deficit(self):
        plan = _plan(goals=[
            {"id": 1, "name": "Отпуск", "target_amount": 100_000, "current_amount": 10_000},
        ])
        freeze = next(a for a in plan["actions"] if a["type"] == "freeze_goals")
        assert "Отпуск" in freeze["goals"]

    def test_zero_income_is_critical(self):
        plan = _plan(income_total=0.0, expense_total=40_000.0, bliq=100_000.0)
        assert plan["severity"] == "critical"


class TestCloseDebtsFromLiquidity:
    """Балансовый ход: закрытие кредита из подушки разворачивает поток (кейс SP-00044)."""

    CASE = dict(
        income_total=90_000.0,
        expense_total=89_000.0,
        obligations=[{
            "id": 1, "name": "loan_1", "amount": 500_000.0,
            "interest_rate": 0.24, "monthly_payment": 28_000.0,
        }],
        bliq=736_000.0,
    )

    def test_flow_flips_positive(self):
        plan = _plan(**self.CASE)  # Rt = 90к − 89к − 28к = −27к
        act = next(a for a in plan["actions"]
                   if a["type"] == "close_debts_from_liquidity")
        assert act["new_rt"] >= 0
        assert plan["severity"] == "recoverable_from_liquidity"
        step = act["steps"][0]
        assert step["name"] == "loan_1" and step["closed"] is True
        assert act["bliq_used"] == 500_000.0

    def test_floor_reserve_preserved(self):
        plan = _plan(**self.CASE)
        act = next(a for a in plan["actions"]
                   if a["type"] == "close_debts_from_liquidity")
        # после хода подушка не ниже 2 месяцев расходов (v3.4.0, ADR-006)
        assert act["bliq_remaining"] >= 178_000.0 - 0.01

    def test_not_offered_when_it_breaks_floor(self):
        # после floor 2 мес (178к) доступно 342к — на разворот потока не хватает
        thin = dict(self.CASE, bliq=520_000.0)
        plan = _plan(**thin)
        assert not any(a["type"] == "close_debts_from_liquidity"
                       for a in plan["actions"])
        assert plan["severity"] == "cut_required"

    def test_partial_paydown_when_liquidity_tight(self):
        # на полный кредит не хватает (доступно 490к из 500к при floor
        # v3.4.0 = 2 мес × 89к = 178к), но платёж пропорционален остатку:
        # чтобы вернуть 27к потока при P/A = 28к/500к, достаточно погасить
        # ~482к — кредит гасится частично, поток развёрнут
        case = dict(self.CASE, bliq=668_000.0)
        plan = _plan(**case)
        act = next(a for a in plan["actions"]
                   if a["type"] == "close_debts_from_liquidity")
        assert act["new_rt"] >= 0
        assert act["bliq_used"] < 500_000.0
        assert act["steps"][0]["closed"] is False
        assert act["bliq_remaining"] >= 178_000.0 - 0.01  # floor 2 мес не тронут

    def test_most_efficient_loan_first(self):
        # эффективность = платёж на рубль погашения; loan_b возвращает поток вдвое дешевле
        case = dict(
            income_total=50_000.0,
            expense_total=40_000.0,
            obligations=[
                {"id": 1, "name": "loan_a", "amount": 400_000.0,
                 "interest_rate": 0.30, "monthly_payment": 12_000.0},
                {"id": 2, "name": "loan_b", "amount": 100_000.0,
                 "interest_rate": 0.20, "monthly_payment": 6_000.0},
            ],
            bliq=300_000.0,
        )
        plan = _plan(**case)  # дефицит 8к; floor 40к; доступно 260к
        act = next(a for a in plan["actions"]
                   if a["type"] == "close_debts_from_liquidity")
        assert act["steps"][0]["name"] == "loan_b"
        assert act["steps"][0]["closed"] is True  # b закрыт целиком (100к <= 260к)
        assert act["new_rt"] >= 0


class TestRestructuring:
    def test_priority_is_most_expensive_loan(self):
        plan = _plan(
            income_total=40_000.0,
            expense_total=30_000.0,
            obligations=[
                {"id": 1, "name": "cheap", "amount": 300_000.0,
                 "interest_rate": 0.08, "monthly_payment": 8_000.0},
                {"id": 2, "name": "expensive", "amount": 200_000.0,
                 "interest_rate": 0.32, "monthly_payment": 7_000.0},
            ],
            bliq=0.0,
        )
        rest = next(a for a in plan["actions"] if a["type"] == "restructure_debt")
        assert rest["loan"] == "expensive"
        assert rest["interest_rate"] == 0.32


class TestHighInterestCreditCardCase:
    """Живой кейс из ROADMAP §6.3: кредитка Т-Банк, долг 100к+, минималка ~6к,
    доход 20к стабильно (+ до 25к донорство ситуативно)."""

    CARD = {"id": 1, "name": "Кредитка Т-Банк", "amount": 100_000.0,
            "interest_rate": 0.399, "monthly_payment": 6_000.0}

    def test_stable_income_only_deficit_advice(self):
        # только стабильный доход: 20к − 16к − 6к = −2к/мес
        plan = build_crisis_plan(
            income_total=20_000.0, expense_total=16_000.0,
            obligations=[dict(self.CARD)], goals=[], bliq=4_000.0, today=TODAY,
        )
        assert plan["deficit"] == 2_000.0
        # сколько можно тратить на жизнь, чтобы не углублять долг
        assert plan["max_affordable_expenses"] == 14_000.0
        assert plan["runway_months"] == 2.0
        cut = next(a for a in plan["actions"] if a["type"] == "cut_expenses")
        assert cut["amount"] == 2_000.0
        rest = next(a for a in plan["actions"] if a["type"] == "restructure_debt")
        assert rest["loan"] == "Кредитка Т-Банк"

    def test_with_donor_income_avalanche_attacks_card(self):
        # со ситуативным доходом поток положительный — обычный план; подушка
        # сделана (Lt = 80к/16к = 5 мес > цели 4.5 и floor 2.0 v3.4.0) → SAW
        # отдаёт поток лавине в кредитку
        result = run_planning(
            income_total=45_000.0, expense_total=16_000.0,
            obligations=[dict(self.CARD)], goals=[], bliq=80_000.0,
            r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        assert result["crisis_plan"] is None
        best = result["best"]
        assert best is not None
        assert best["x_obl_effective"] > 0
        names = [o["name"] for o in best["avalanche_detail"]["passed"]]
        assert "Кредитка Т-Банк" in names


class TestPlanningIntegration:
    def test_crisis_plan_attached_on_deficit(self):
        result = run_planning(
            income_total=30_000.0, expense_total=45_000.0,
            obligations=[], goals=[], bliq=90_000.0,
            r_bench=0.14, risk_tolerance=2, today=TODAY,
        )
        assert result["alternatives_total"] == 1  # fail-loud ветка сохраняется
        plan = result["crisis_plan"]
        assert plan is not None and plan["actions"]

    def test_no_crisis_plan_on_positive_flow(self):
        result = run_planning(
            income_total=100_000.0, expense_total=40_000.0,
            obligations=[], goals=[], bliq=0.0,
            r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        assert result["crisis_plan"] is None

    def test_crisis_plan_ignores_income_history_adr_015(self):
        """Красная линия ADR-015: волатильность/уровень исторического дохода
        НЕ подавляет и не смягчает кризисный режим — это факт о текущем месяце
        (income_total), а не об истории. Портрет: этот месяц дефицитный, но
        историческое среднее ВЫШЕ текущего дохода (выглядело бы "стабильно
        хорошо" по среднему) — кризисный план обязан сработать всё равно,
        инвариант I12 не должен зависеть от income_history ни при каких его
        значениях."""
        history_looks_fine = [80_000.0] * 8  # среднее заметно выше текущего дохода
        result = run_planning(
            income_total=30_000.0, expense_total=45_000.0,
            obligations=[], goals=[], bliq=90_000.0,
            r_bench=0.14, risk_tolerance=2, today=TODAY,
            income_history=history_looks_fine,
        )
        plan = result["crisis_plan"]
        assert plan is not None and plan["actions"]
        assert result["indicators"]["Rt"] < 0

    def test_crisis_plan_unaffected_by_debt_schedule_adr_016(self):
        """Красная линия ADR-016: график погашения (даже с большой
        потенциальной экономией на процентах) НЕ влияет на Rt/Dt/crisis_plan —
        считается строго ПОСЛЕ ранжирования, чисто диагностически. Долг с
        высокой ставкой даёт заметную экономию при досрочке — если бы график
        как-то протекал в решение, это был бы незавалидированный пятый
        критерий SAW."""
        obligations = [
            {"id": 1, "amount": 500_000, "interest_rate": 0.35, "monthly_payment": 20_000},
        ]
        result = run_planning(
            income_total=30_000.0, expense_total=45_000.0,
            obligations=obligations, goals=[], bliq=90_000.0,
            r_bench=0.14, risk_tolerance=2, today=TODAY,
        )
        plan = result["crisis_plan"]
        assert plan is not None and plan["actions"]
        assert result["indicators"]["Rt"] < 0

    def test_bliq_preallocation_suppressed_in_deficit(self):
        # в дефиците цели заморожены — этап 4.0 не тратит подушку на близкие цели
        result = run_planning(
            income_total=30_000.0, expense_total=45_000.0,
            obligations=[],
            goals=[{"id": 1, "name": "близкая", "target_amount": 20_000.0,
                    "current_amount": 15_000.0,
                    "deadline": datetime(2026, 8, 1)}],
            bliq=200_000.0, r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        assert result["bliq_preallocation"]["bliq_used"] == 0.0
