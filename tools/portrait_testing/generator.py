"""Генератор синтетических портретов пользователя для свипа мат-модели.

Детерминирован по (seed, index): каждый портрет воспроизводим независимо
от порядка генерации. ~треть портретов — граничные случаи (EDGE_KINDS).
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

EDGE_KINDS: tuple[str, ...] = (
    "zero_income",
    "zero_expenses",
    "deficit_cf",
    "overleveraged",
    "cheap_debts_only",
    "no_goals",
    "funded_goal",
    "huge_bliq",
    "many_goals",
)

R_BENCH_CHOICES: tuple[float, ...] = (0.10, 0.1281, 0.14, 0.1596, 0.20)


class PortraitGenerator:
    """Фабрика синтетических портретов: доходы/расходы/долги/цели/подушка."""

    def __init__(self, seed: int = 20260702) -> None:
        self.seed = seed

    def kind_for(self, index: int) -> str:
        if index % 3 == 0:
            return EDGE_KINDS[(index // 3) % len(EDGE_KINDS)]
        return "plain"

    def generate(self, index: int) -> dict[str, Any]:
        rng = random.Random(self.seed * 1_000_003 + index)
        kind = self.kind_for(index)
        today = date(2026, 7, 2)

        income = round(rng.lognormvariate(11.2, 0.5), 2)
        expenses = round(income * rng.uniform(0.35, 1.15), 2)

        obligations = self._gen_obligations(rng, income)
        goals = self._gen_goals(rng, today)
        bliq = round(expenses * rng.uniform(0.0, 12.0), 2)

        if kind == "zero_income":
            income = 0.0
        elif kind == "zero_expenses":
            expenses = 0.0
        elif kind == "deficit_cf":
            expenses = round(max(income, 1.0) * rng.uniform(1.05, 1.6), 2)
        elif kind == "overleveraged":
            obligations = self._gen_obligations(rng, income, min_count=1)
            target_pdn = rng.uniform(0.45, 0.9)
            payments = sum(o["monthly_payment"] for o in obligations)
            scale = (target_pdn * max(income, 1.0)) / payments if payments > 0 else 1.0
            for o in obligations:
                o["monthly_payment"] = round(o["monthly_payment"] * scale, 2)
        elif kind == "cheap_debts_only":
            obligations = self._gen_obligations(rng, income, min_count=1)
            for o in obligations:
                o["interest_rate"] = round(rng.uniform(0.01, 0.09), 4)
        elif kind == "no_goals":
            goals = []
        elif kind == "funded_goal":
            target = round(rng.uniform(50_000, 500_000), 2)
            goals = [{
                "id": 1, "name": "funded", "target_amount": target,
                "current_amount": round(target * rng.uniform(1.0, 1.2), 2),
                "deadline": today + timedelta(days=90),
            }]
        elif kind == "huge_bliq":
            bliq = round(max(expenses, 10_000.0) * rng.uniform(24.0, 60.0), 2)
        elif kind == "many_goals":
            goals = self._gen_goals(rng, today, count=8)

        return {
            "index": index,
            "kind": kind,
            "income_total": income,
            "expense_total": expenses,
            "obligations": obligations,
            "goals": goals,
            "bliq": bliq,
            "r_bench": rng.choice(R_BENCH_CHOICES),
            "risk_tolerance": rng.randint(1, 5),
            "l_min": 0.0,
        }

    def _gen_obligations(
        self, rng: random.Random, income: float, min_count: int = 0
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for i in range(rng.randint(min_count, 4)):
            principal = round(rng.uniform(30_000, 3_000_000), 2)
            items.append({
                "id": i + 1,
                "name": f"loan_{i + 1}",
                "amount": principal,
                "interest_rate": round(rng.uniform(0.03, 0.35), 4),
                "monthly_payment": round(principal * rng.uniform(0.02, 0.06), 2),
            })
        return items

    def _gen_goals(
        self, rng: random.Random, today: date, count: int | None = None
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for i in range(count if count is not None else rng.randint(0, 4)):
            target = round(rng.uniform(50_000, 2_000_000), 2)
            deadline = (
                today + timedelta(days=30 * rng.randint(3, 60))
                if rng.random() > 0.25 else None
            )
            items.append({
                "id": i + 1,
                "name": f"goal_{i + 1}",
                "target_amount": target,
                "current_amount": round(rng.uniform(0, target * 0.9), 2),
                "deadline": deadline,
            })
        return items
