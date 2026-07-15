"""Адаптер реального ядра СППР под контракт FinanceEngine (INFRA-15, REFACTOR-04).

Оборачивает `app.services.planning.run_planning` (SAW + Avalanche + Monte-Carlo)
так, чтобы оно удовлетворяло Protocol `FinanceEngine`. Логика ядра не меняется
(KEEP-01..05) — здесь только маппинг:

    FinancialSnapshot (Decimal, enum)  →  входные словари ядра (float, int 1..5)
    результат run_planning             →  Recommendation (Decimal)

Мультивалюта: снимок может нести разные валюты на объектах; перед прогоном всё
приводится к snapshot.base_currency переданным конвертером (FR-19). Если
конвертер не задан, предполагается, что снимок уже в одной валюте.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from app.ingestion.contracts import FinanceEngine  # noqa: F401  (документирует контракт)
from app.ingestion.models import (
    Allocation,
    FinancialSnapshot,
    Recommendation,
    RiskProfile,
)
from app.services.currency import CurrencyConverter
from app.services.planning import run_planning
from app.utils.time import utcnow


class CoreFinanceEngine:
    """Реальный движок СППР как FinanceEngine. Реализует analyze(snapshot, profile)."""

    def __init__(self, converter: Optional[CurrencyConverter] = None) -> None:
        self._converter = converter

    def analyze(
        self, snapshot: FinancialSnapshot, profile: RiskProfile
    ) -> Recommendation:
        base = snapshot.base_currency

        income_total, expense_total = self._sum_flows(snapshot, base)
        obligations = self._map_debts(snapshot, base)
        goals = self._map_goals(snapshot, base)
        bliq = self._sum_liquid(snapshot, base)

        result = run_planning(
            income_total=income_total,
            expense_total=expense_total,
            obligations=obligations,
            goals=goals,
            bliq=bliq,
            r_bench=float(snapshot.r_bench),
            risk_tolerance=int(profile),
            l_min=float(snapshot.l_min),
            today=utcnow(),
        )

        return self._to_recommendation(result, base)

    # ── Маппинг snapshot → вход ядра ─────────────────────────────────
    def _amount(self, value: Decimal, currency: str, base: str) -> float:
        if self._converter is not None and currency != base:
            return float(self._converter.convert(value, currency, base))
        return float(value)

    def _sum_flows(self, snapshot: FinancialSnapshot, base: str) -> tuple[float, float]:
        income = 0.0
        expense = 0.0
        for txn in snapshot.transactions:
            amount = self._amount(txn.amount, txn.currency, base)
            if int(txn.type) == 1:  # INCOME
                income += amount
            else:
                expense += amount
        return round(income, 2), round(expense, 2)

    def _sum_liquid(self, snapshot: FinancialSnapshot, base: str) -> float:
        return round(
            sum(
                self._amount(acc.balance, acc.currency, base)
                for acc in snapshot.accounts
                if acc.is_liquid
            ),
            2,
        )

    def _map_debts(self, snapshot: FinancialSnapshot, base: str) -> list[dict]:
        return [
            {
                "id": debt.debt_id,
                "name": debt.name,
                "amount": self._amount(debt.balance, debt.currency, base),
                "monthly_payment": self._amount(debt.monthly_payment, debt.currency, base),
                "interest_rate": float(debt.interest_rate),
                "term": debt.term_months,
            }
            for debt in snapshot.debts
        ]

    def _map_goals(self, snapshot: FinancialSnapshot, base: str) -> list[dict]:
        return [
            {
                "id": goal.goal_id,
                "name": goal.name,
                "target_amount": self._amount(goal.target_amount, goal.currency, base),
                "current_amount": self._amount(goal.current_amount, goal.currency, base),
                "deadline": goal.deadline,
                "category": goal.category,
            }
            for goal in snapshot.goals
        ]

    # ── Маппинг результат ядра → Recommendation ──────────────────────
    def _to_recommendation(self, result: dict, base: str) -> Recommendation:
        indicators = result.get("indicators", {})
        best = result.get("best") or {}

        allocation = Allocation(
            to_debt=_dec(best.get("x_obligations", 0)),
            to_reserve=_dec(best.get("x_reserve", 0)),
            to_goals=_dec(best.get("x_goals", 0)),
        )
        explanation = best.get("explanation") or {}
        reasoning = explanation.get("summary") if isinstance(explanation, dict) else ""

        return Recommendation(
            allocation=allocation,
            rt=_dec(indicators.get("Rt", 0)),
            lt=_dec(indicators.get("Lt", 0)),
            dt=_dec(indicators.get("Dt", 0)),
            blr=_dec(indicators.get("BLR", 0)),
            u_score=_dec(best.get("utility", 0)),
            currency=base,
            reasoning=reasoning or "",
            alternatives_total=int(result.get("alternatives_total", 0)),
            alternatives_accepted=int(result.get("admissible_count", 0)),
        )


def _dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")
