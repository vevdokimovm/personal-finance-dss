"""Golden master движка планирования (характеризационные тесты).

Фиксируют ТЕКУЩИЙ выбор a* и распределение на наборе сценариев. Цель — гарантия,
что перевод денежных путей на Decimal не меняет управленческое решение:
- имя выбранной альтернативы, её доли и порядок топ-3 — строгие инварианты;
- денежные суммы допускают расхождение в пределах копейки (округление Decimal);
- безразмерная полезность U(a) (нормализация + веса SAW остаются float) не меняется.

run_planning детерминирован (Monte-Carlo прогноз сюда не входит), снапшоты стабильны.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.services.planning import run_planning

TODAY = datetime(2026, 6, 20)

SCENARIOS = [
    (
        "expensive_debt_balanced",
        dict(
            income_total=120000, expense_total=70000,
            obligations=[{"id": 1, "amount": 300000, "interest_rate": 0.20, "monthly_payment": 15000, "term": 24}],  # noqa: E501
            goals=[{"id": 1, "target_amount": 300000, "current_amount": 50000, "category": "safety", "deadline": datetime(2027, 6, 1), "name": "Подушка"}],  # noqa: E501
            bliq=40000, risk_tolerance=3,
        ),
        # v3.4.0 (ADR-006): подушка 0.57 мес < floor 2.0 — весь поток месяца
        # достраивает стартовый резерв, лавина ждёт заполнения floor.
        dict(
            best_name="Всё в резерв",
            x=(0.0, 35000.0, 0.0),
            utility=0.3,
            ind_rt_lt_dt=(35000.0, 0.5714, 0.125),
            top3=["Всё в резерв", "Акцент: резерв (10/90/0)", "Акцент: резерв (0/90/10)"],
        ),
    ),
    (
        "no_debt_aggressive",
        dict(
            income_total=100000, expense_total=50000,
            obligations=[],
            goals=[{"id": 1, "target_amount": 500000, "current_amount": 0, "category": "income_growth", "deadline": datetime(2028, 1, 1), "name": "Обучение"}],  # noqa: E501
            bliq=20000, risk_tolerance=5,
        ),
        # v3.4.0 (ADR-006): подушка 0.4 мес << floor 2.0 — и агрессивный профиль
        # сначала строит стартовый резерв целиком, цель ждёт floor.
        dict(
            best_name="Всё в резерв",
            x=(0.0, 50000.0, 0.0),
            utility=0.6,
            ind_rt_lt_dt=(50000, 0.4, 0.0),
            top3=["Всё в резерв", "Акцент: резерв (0/90/10)", "Акцент: резерв (0/80/20)"],
        ),
    ),
    (
        "cheap_debt_redirect",
        dict(
            income_total=150000, expense_total=80000,
            obligations=[{"id": 1, "amount": 2000000, "interest_rate": 0.085, "monthly_payment": 25000, "term": 120}],  # noqa: E501
            goals=[{"id": 1, "target_amount": 400000, "current_amount": 100000, "category": "material", "deadline": datetime(2027, 12, 1), "name": "Машина"}],  # noqa: E501
            bliq=60000, risk_tolerance=3,
        ),
        dict(
            best_name="Всё в резерв",
            x=(0.0, 45000.0, 0.0),
            utility=0.8,
            ind_rt_lt_dt=(45000.0, 0.75, 0.1667),
            top3=["Всё в резерв", "Акцент: резерв (0/90/10)", "Акцент: резерв (0/80/20)"],
        ),
    ),
    (
        "conservative_debt",
        dict(
            income_total=90000, expense_total=55000,
            obligations=[{"id": 1, "amount": 400000, "interest_rate": 0.18, "monthly_payment": 12000, "term": 36}],  # noqa: E501
            goals=[{"id": 1, "target_amount": 200000, "current_amount": 20000, "category": "safety", "deadline": datetime(2027, 3, 1), "name": "Резерв"}],  # noqa: E501
            bliq=15000, risk_tolerance=1,
        ),
        # v3.1.0 (G6): floor недостижим (0.69 мес максимум) — приоритет
        # максимальному заполнению стартовой ликвидности.
        dict(
            best_name="Всё в резерв",
            x=(0.0, 23000.0, 0.0),
            utility=0.45,
            ind_rt_lt_dt=(23000.0, 0.2727, 0.1333),
            top3=["Всё в резерв", "Акцент: резерв (10/90/0)", "Акцент: резерв (0/90/10)"],
        ),
    ),
    (
        "high_dti",
        dict(
            income_total=100000, expense_total=45000,
            obligations=[{"id": 1, "amount": 800000, "interest_rate": 0.22, "monthly_payment": 35000, "term": 30}],  # noqa: E501
            goals=[{"id": 1, "target_amount": 150000, "current_amount": 10000, "category": "emotional", "deadline": datetime(2027, 9, 1), "name": "Отпуск"}],  # noqa: E501
            bliq=10000, risk_tolerance=3,
        ),
        # v3.1.0 (G6): подушка 0.22 мес — floor лексикографически выше лавины;
        # максимум заполнения = «всё в резерв» (0.67 мес).
        dict(
            best_name="Всё в резерв",
            x=(0.0, 20000.0, 0.0),
            utility=0.3,
            ind_rt_lt_dt=(20000.0, 0.2222, 0.35),
            top3=["Всё в резерв", "Акцент: резерв (10/90/0)", "Акцент: резерв (0/90/10)"],
        ),
    ),
]


@pytest.mark.parametrize("name,inputs,expected", SCENARIOS, ids=[s[0] for s in SCENARIOS])
def test_engine_decision_snapshot(name, inputs, expected) -> None:
    res = run_planning(today=TODAY, **inputs)
    best = res["best"]
    assert best is not None

    # Управленческое решение — строгий инвариант рефактора.
    assert best["name"] == expected["best_name"]
    x = (best["x_obligations"], best["x_reserve"], best["x_goals"])
    assert x == pytest.approx(expected["x"], abs=0.01)
    assert [a["name"] for a in res["top3"]] == expected["top3"]

    # Безразмерная полезность не меняется (нормализация и веса SAW остаются float).
    assert best["utility"] == pytest.approx(expected["utility"], abs=1e-6)

    # Базовые денежные показатели — допуск в копейку под будущее Decimal-округление.
    ind = res["indicators"]
    assert (ind["Rt"], ind["Lt"], ind["Dt"]) == pytest.approx(expected["ind_rt_lt_dt"], abs=0.01)
