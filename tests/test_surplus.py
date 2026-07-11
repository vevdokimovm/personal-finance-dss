"""Тесты слоя управления накопленным запасом (модель v3.2.0, дефект G4).

Экспертиза: «эксперты развернули 0.5–1 млрд ₽ излишков разовыми ходами, модель —
14 млн через узкий этап 4.0». Излишек = Bliq сверх ЦЕЛЕВОЙ подушки Lt*·Σe.
Порядок разворачивания (консенсус): дорогие долги (Avalanche, ставка >= r_bench)
→ разовые взносы в дедлайновые цели (с инструментом по горизонту — полный G5)
→ разовый инвестиционный транш по профильной полке. Месячную решётку слой
не трогает — это отдельный план разовых ходов, как кризисный модуль.
"""
from __future__ import annotations

from datetime import datetime

from app.core.surplus import build_surplus_plan
from app.services.planning import run_planning

TODAY = datetime(2026, 7, 2, 12, 0, 0)


def _plan(**kwargs):
    defaults = dict(
        bliq=500_000.0,
        expense_total=50_000.0,
        obligations=[],
        goals=[],
        r_bench=0.14,
        risk_tolerance=3,   # lt_target 4.5 -> целевая подушка 225к
        lt_target=4.5,
        today=TODAY,
    )
    defaults.update(kwargs)
    return build_surplus_plan(**defaults)


class TestDeployable:
    def test_no_plan_when_cushion_below_target(self):
        assert _plan(bliq=200_000.0) is None  # 4 мес < цели 4.5

    def test_no_plan_when_expenses_zero(self):
        assert _plan(expense_total=0.0) is None  # подушка не определена

    def test_deployable_is_excess_over_target(self):
        plan = _plan()  # 500к − 225к = 275к
        assert plan["deployable"] == 275_000.0
        assert plan["reserve_target"] == 225_000.0

    def test_cushion_never_broken(self):
        plan = _plan()
        assert plan["bliq_after"] >= plan["reserve_target"] - 0.01
        moved = sum(m["amount"] for m in plan["moves"])
        assert abs(moved - plan["deployable"]) < 0.01  # излишек развёрнут целиком


class TestRepayDebts:
    def test_expensive_debt_repaid_avalanche_order(self):
        plan = _plan(obligations=[
            {"id": 1, "name": "cheap", "amount": 100_000.0,
             "interest_rate": 0.06, "monthly_payment": 4_000.0},
            {"id": 2, "name": "mid", "amount": 150_000.0,
             "interest_rate": 0.20, "monthly_payment": 6_000.0},
            {"id": 3, "name": "hot", "amount": 80_000.0,
             "interest_rate": 0.35, "monthly_payment": 5_000.0},
        ])
        repays = [m for m in plan["moves"] if m["type"] == "repay_debt"]
        assert [m["name"] for m in repays] == ["hot", "mid"]  # дорогие, по ставке
        assert all(m["closed"] for m in repays)               # 275к хватает на оба
        assert not any(m["name"] == "cheap" for m in repays)  # 6% < r_bench: не гасим

    def test_partial_repay_when_excess_small(self):
        plan = _plan(bliq=280_000.0, obligations=[  # излишек 55к
            {"id": 1, "name": "hot", "amount": 200_000.0,
             "interest_rate": 0.30, "monthly_payment": 8_000.0},
        ])
        repay = next(m for m in plan["moves"] if m["type"] == "repay_debt")
        assert repay["amount"] == 55_000.0 and repay["closed"] is False
        assert repay["payment_freed"] == 2_200.0  # пропорциональная модель платежа


class TestFundGoals:
    GOALS = [
        {"id": 1, "name": "бессрочная", "target_amount": 300_000.0,
         "current_amount": 0.0, "deadline": None},
        {"id": 2, "name": "отпуск", "target_amount": 120_000.0,
         "current_amount": 20_000.0, "deadline": datetime(2026, 12, 1)},
        {"id": 3, "name": "первый взнос", "target_amount": 1_000_000.0,
         "current_amount": 900_000.0, "deadline": datetime(2027, 2, 1)},
    ]

    def test_deadline_goals_funded_nearest_first(self):
        plan = _plan(goals=[dict(g) for g in self.GOALS])
        funds = [m for m in plan["moves"] if m["type"] == "fund_goal"]
        assert [m["name"] for m in funds] == ["отпуск", "первый взнос"]
        assert funds[0]["amount"] == 100_000.0 and funds[0]["closed"] is True
        assert funds[1]["amount"] == 100_000.0 and funds[1]["closed"] is True
        assert not any(m["name"] == "бессрочная" for m in funds)  # питается потоком

    def test_goal_instrument_by_horizon(self):
        # полный G5: до дедлайна < 12 мес — только депозит/накопительный
        plan = _plan(goals=[dict(g) for g in self.GOALS])
        funds = {m["name"]: m for m in plan["moves"] if m["type"] == "fund_goal"}
        assert "депозит" in funds["отпуск"]["instrument"].lower()


class TestInvestLump:
    def test_remainder_goes_to_invest_with_profile_shelf(self):
        plan = _plan(risk_tolerance=5, lt_target=3.0)  # цель 150к, излишек 350к
        lump = next(m for m in plan["moves"] if m["type"] == "invest_lump")
        assert lump["amount"] == 350_000.0
        assert abs(lump["split"]["equity"] - 350_000.0 * 0.8) < 0.02
        assert "АСВ" in lump["note"]

    def test_order_debts_then_goals_then_invest(self):
        plan = _plan(
            obligations=[{"id": 1, "name": "hot", "amount": 50_000.0,
                          "interest_rate": 0.30, "monthly_payment": 3_000.0}],
            goals=[{"id": 1, "name": "цель", "target_amount": 60_000.0,
                    "current_amount": 0.0, "deadline": datetime(2027, 1, 1)}],
        )
        types = [m["type"] for m in plan["moves"]]
        assert types == ["repay_debt", "fund_goal", "invest_lump"]


class TestPlanningIntegration:
    def test_surplus_plan_attached_when_excess(self):
        result = run_planning(
            income_total=100_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=500_000.0,
            r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        sp = result["surplus_plan"]
        assert sp is not None and sp["deployable"] > 0

    def test_no_surplus_plan_in_deficit(self):
        # в дефиците запасом распоряжается кризисный модуль
        result = run_planning(
            income_total=30_000.0, expense_total=45_000.0,
            obligations=[], goals=[], bliq=500_000.0,
            r_bench=0.14, risk_tolerance=3, today=TODAY,
        )
        assert result["surplus_plan"] is None
        assert result["crisis_plan"] is not None

    def test_no_surplus_plan_when_no_excess(self):
        result = run_planning(
            income_total=100_000.0, expense_total=50_000.0,
            obligations=[], goals=[], bliq=100_000.0,
            r_bench=0.14, risk_tolerance=1, today=TODAY,
        )
        assert result["surplus_plan"] is None
