"""Каноническая provider-agnostic модель данных (DATA-07, KEEP-07).

`FinancialSnapshot` — контракт между любым источником данных (ручной ввод,
Plaid, CSV-импорт, B2B-партнёр) и движком СППР. Источник обязан отдать снимок
в этих терминах; движок принимает его, ничего не зная о происхождении.

Деньги — `Decimal` (точность, DATA-08). Профиль риска — enum 1..5, совпадает
с RISK_PROFILES ядра. Валюта несётся на каждом денежном объекте (FR-19).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Optional


class RiskProfile(IntEnum):
    """Совпадает с ключами RISK_PROFILES в app.core.ranking."""
    CONSERVATIVE = 1
    MODERATELY_CONSERVATIVE = 2
    BALANCED = 3
    MODERATELY_AGGRESSIVE = 4
    AGGRESSIVE = 5


class TransactionType(IntEnum):
    INCOME = 1
    EXPENSE = 2


@dataclass(frozen=True)
class Account:
    """Денежный счёт. is_liquid=True → попадает в Bliq (накопит./депозит/кэш)."""
    account_id: str
    name: str
    balance: Decimal
    currency: str = "RUB"
    is_liquid: bool = False
    interest_rate: Decimal = Decimal("0")


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    amount: Decimal
    type: TransactionType
    date: datetime
    currency: str = "RUB"
    description: Optional[str] = None
    mcc: Optional[str] = None
    category: Optional[str] = None


@dataclass(frozen=True)
class Debt:
    debt_id: str
    name: str
    balance: Decimal
    monthly_payment: Decimal
    interest_rate: Decimal
    term_months: int = 0
    currency: str = "RUB"


@dataclass(frozen=True)
class Goal:
    goal_id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    deadline: datetime
    category: str = "material"
    currency: str = "RUB"


@dataclass(frozen=True)
class FinancialSnapshot:
    """Полный снимок финансов пользователя в канонических терминах."""
    base_currency: str = "RUB"
    risk_profile: RiskProfile = RiskProfile.BALANCED
    accounts: list[Account] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    debts: list[Debt] = field(default_factory=list)
    goals: list[Goal] = field(default_factory=list)
    l_min: Decimal = Decimal("0.0")
    r_bench: Decimal = Decimal("0.14")
    horizon_months: int = 12


@dataclass(frozen=True)
class Allocation:
    """Рекомендованное распределение свободного ресурса a* = (x_d, x_r, x_g)."""
    to_debt: Decimal
    to_reserve: Decimal
    to_goals: Decimal


@dataclass(frozen=True)
class Recommendation:
    """Результат анализа — provider-agnostic ответ движка."""
    allocation: Allocation
    rt: Decimal
    lt: Decimal
    dt: Decimal
    blr: Decimal
    u_score: Decimal
    currency: str = "RUB"
    reasoning: str = ""
    alternatives_total: int = 0
    alternatives_accepted: int = 0
