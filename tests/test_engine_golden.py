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
            obligations=[{"id": 1, "amount": 300000, "interest_rate": 0.20, "monthly_payment": 15000, "term": 24}],
            goals=[{"id": 1, "target_amount": 300000, "current_amount": 50000, "category": "safety", "deadline": datetime(2027, 6, 1), "name": "Подушка"}],
            bliq=40000, risk_tolerance=3,
        ),
        dict(
            best_name="Всё на погашение долга",
            x=(35000.0, 0.0, 0.0),
            utility=0.5,
            ind_rt_lt_dt=(35000.0, 0.5714, 0.125),
            top3=["Всё на погашение долга", "Акцент: обязательства (90/10/0)", "Акцент: обязательства (90/0/10)"],
        ),
    ),
    (
        "no_debt_aggressive",
        dict(
            income_total=100000, expense_total=50000,
            obligations=[],
            goals=[{"id": 1, "target_amount": 500000, "current_amount": 0, "category": "income_growth", "deadline": datetime(2028, 1, 1), "name": "Обучение"}],
            bliq=20000, risk_tolerance=5,
        ),
        dict(
            best_name="Всё на цели",
            x=(0.0, 0.0, 50000.0),
            utility=0.9,
            ind_rt_lt_dt=(50000, 0.4, 0.0),
            top3=["Всё на цели", "Акцент: цели (0/10/90)", "Акцент: цели (0/20/80)"],
        ),
    ),
    (
        "cheap_debt_redirect",
        dict(
            income_total=150000, expense_total=80000,
            obligations=[{"id": 1, "amount": 2000000, "interest_rate": 0.085, "monthly_payment": 25000, "term": 120}],
            goals=[{"id": 1, "target_amount": 400000, "current_amount": 100000, "category": "material", "deadline": datetime(2027, 12, 1), "name": "Машина"}],
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
            obligations=[{"id": 1, "amount": 400000, "interest_rate": 0.18, "monthly_payment": 12000, "term": 36}],
            goals=[{"id": 1, "target_amount": 200000, "current_amount": 20000, "category": "safety", "deadline": datetime(2027, 3, 1), "name": "Резерв"}],
            bliq=15000, risk_tolerance=1,
        ),
        dict(
            best_name="Акцент: обязательства (90/10/0)",
            x=(20700.0, 2300.0, 0.0),
            utility=0.452,
            ind_rt_lt_dt=(23000.0, 0.2727, 0.1333),
            top3=["Акцент: обязательства (90/10/0)", "Акцент: обязательства (60/40/0)", "Акцент: резерв (30/70/0)"],
        ),
    ),
    (
        "high_dti",
        dict(
            income_total=100000, expense_total=45000,
            obligations=[{"id": 1, "amount": 800000, "interest_rate": 0.22, "monthly_payment": 35000, "term": 30}],
            goals=[{"id": 1, "target_amount": 150000, "current_amount": 10000, "category": "emotional", "deadline": datetime(2027, 9, 1), "name": "Отпуск"}],
            bliq=10000, risk_tolerance=3,
        ),
        dict(
            best_name="Всё на погашение долга",
            x=(20000.0, 0.0, 0.0),
            utility=0.5,
            ind_rt_lt_dt=(20000.0, 0.2222, 0.35),
            top3=["Всё на погашение долга", "Акцент: обязательства (90/10/0)", "Акцент: обязательства (90/0/10)"],
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
