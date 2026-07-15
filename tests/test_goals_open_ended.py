"""
Бессрочные цели: `deadline = NULL` (ROADMAP §6.3).

Канон допускает цель без срока («коплю фоном, дедлайна нет»), а колонка
`goals.deadline` была NOT NULL. Тесты фиксируют семантику по всем слоям:

  ЯДРО      срочность u_s = 1.0 (нейтральная, без ускорения); в разбивке
            months_left = None; бессрочная цель не «близкая» (не закрывается
            разово из Bliq) и не получает дедлайновый транш из излишка;
            полка инструмента — длинный горизонт.
  БД        колонка nullable; бессрочные в списке идут ПОСЛЕ срочных
            (`NULLS LAST` — SQLite по умолчанию ставит NULL первыми, PG — последними,
            поэтому порядок задан явно; тест держит матрицу SQLite/PG).
  API       POST без `deadline` → 201, в ответе `deadline: null`.
  ПОТРЕБИТЕЛИ  spending-advice не падает и не считает бессрочную «отстающей»;
            напоминания о дедлайне её пропускают; план строится end-to-end.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.core.goals_priority import (
    goals_allocation_breakdown,
    calculate_goals_si,
    preallocate_from_bliq,
)
from app.core.investment import instrument_for_horizon
from app.core.spending_advice import GoalRecord, SpendingAdvisor
from app.core.surplus import build_surplus_plan
from app.database.crud import create_goal, get_goals
from app.database.db import engine
from app.services.planning import run_planning

NOW = datetime(2026, 7, 12)


def _goal(gid, deadline, target=100_000.0, current=0.0, category="material"):
    return {
        "id": gid, "name": f"goal-{gid}", "target_amount": target,
        "current_amount": current, "deadline": deadline, "category": category,
    }


class TestCoreUrgency:
    """Бессрочная цель не ускоряется: u_s = 1.0."""

    def test_breakdown_open_ended_has_neutral_urgency_and_no_months(self):
        rows = goals_allocation_breakdown(10_000.0, [_goal(1, None)], today=NOW)
        assert len(rows) == 1
        assert rows[0]["urgency"] == 1.0
        assert rows[0]["months_left"] is None

    def test_open_ended_gets_less_than_urgent_goal(self):
        goals = [_goal(1, None), _goal(2, NOW + timedelta(days=90))]
        _, alloc = calculate_goals_si(30_000.0, goals, today=NOW)
        assert alloc[2] > alloc[1]

    def test_open_ended_equals_far_dated_goal(self):
        """Дедлайн через 12 мес даёт ту же срочность (12/12 = 1) — доли равны."""
        goals = [_goal(1, None), _goal(2, NOW + timedelta(days=365))]
        _, alloc = calculate_goals_si(30_000.0, goals, today=NOW)
        assert abs(alloc[1] - alloc[2]) < 1.0


class TestCoreBliqAndSurplus:
    """Бессрочная цель не «близкая» и не дедлайновая: разовых ходов не получает."""

    def test_open_ended_goal_is_never_near(self):
        bliq_left, closed, active = preallocate_from_bliq(
            1_000_000.0, [_goal(1, None, target=10_000.0)], today=NOW
        )
        assert closed == []
        assert bliq_left == 1_000_000.0
        assert len(active) == 1

    def test_surplus_skips_open_ended_goal(self):
        plan = build_surplus_plan(
            bliq=500_000.0, expense_total=50_000.0, obligations=[],
            goals=[_goal(1, None)], r_bench=0.14, risk_tolerance=3,
            lt_target=3.0, today=NOW,
        )
        assert plan is not None
        assert all(m["type"] != "fund_goal" for m in plan["moves"])

    def test_instrument_for_open_ended_is_long_horizon(self):
        assert "от 3 лет" in instrument_for_horizon(None)


class TestDatabaseNullable:
    """Колонка nullable + порядок NULLS LAST (матрица SQLite/PostgreSQL)."""

    def test_deadline_column_is_nullable(self, db_session):
        cols = {c["name"]: c for c in inspect(engine).get_columns("goals")}
        assert cols["deadline"]["nullable"] is True

    def test_create_goal_without_deadline(self, db_session):
        goal = create_goal(
            db_session, name="Бессрочная", target_amount=100_000, current_amount=0,
            deadline=None,
        )
        assert goal.deadline is None

    def test_open_ended_goals_sorted_last(self, db_session):
        create_goal(db_session, name="Бессрочная", target_amount=100_000,
                    current_amount=0, deadline=None)
        create_goal(db_session, name="Срочная", target_amount=50_000,
                    current_amount=0, deadline=NOW + timedelta(days=30))
        names = [g.name for g in get_goals(db_session)]
        assert names == ["Срочная", "Бессрочная"]


class TestApi:
    def test_post_goal_without_deadline(self, client: TestClient):
        created = client.post("/api/goals", json={
            "name": "Финансовая независимость", "target_amount": 5_000_000,
            "current_amount": 100_000, "category": "safety",
        })
        assert created.status_code == 201
        assert created.json()["deadline"] is None

        listed = client.get("/api/goals").json()
        assert listed[0]["deadline"] is None

    def test_post_goal_with_explicit_null_deadline(self, client: TestClient):
        created = client.post("/api/goals", json={
            "name": "Подушка мечты", "target_amount": 300_000,
            "current_amount": 0, "deadline": None,
        })
        assert created.status_code == 201


class TestConsumers:
    """Потребители дедлайна не падают и трактуют «без срока» осмысленно."""

    def test_spending_advice_handles_open_ended(self):
        advisor = SpendingAdvisor()
        impacts = advisor.analyze_goal_impact(
            saving=5_000.0,
            goals=[
                GoalRecord(name="Бессрочная", target_amount=100_000.0,
                           current_amount=10_000.0, months_to_deadline=None,
                           monthly_contribution=5_000.0),
                GoalRecord(name="Срочная", target_amount=50_000.0,
                           current_amount=10_000.0, months_to_deadline=6.0,
                           monthly_contribution=1_000.0),
            ],
        )
        by_name = {i.goal_name: i for i in impacts}
        assert by_name["Бессрочная"].months_to_deadline is None
        # без срока отставания быть не может, пока есть темп пополнения
        assert by_name["Бессрочная"].on_track is True
        # срочная при 1к/мес и остатке 40к за 6 мес не успевает
        assert by_name["Срочная"].on_track is False

    def test_notifications_skip_open_ended(self, db_session):
        from app.services.notifications import goals_near_deadline

        create_goal(db_session, name="Бессрочная", target_amount=100_000,
                    current_amount=0, deadline=None, user_id=None)
        assert goals_near_deadline(db_session, None) == []

    def test_planning_runs_with_open_ended_goal(self):
        """Подушка насыщена (Lt = 12 мес) → ресурс доходит до целей, разбивка не пуста."""
        res = run_planning(
            income_total=80_000, expense_total=50_000,
            obligations=[], goals=[_goal(1, None, target=300_000)],
            bliq=600_000, r_bench=0.14, risk_tolerance=3,
        )
        assert res["best"] is not None
        goals_alt = next(
            (a for a in res["ranked"] if a["x_goals"] > 0 and a["goal_breakdown"]), None
        )
        assert goals_alt is not None
        assert goals_alt["goal_breakdown"][0]["months_left"] is None
        assert goals_alt["goal_breakdown"][0]["urgency"] == 1.0
