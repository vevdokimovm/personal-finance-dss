from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Category(Base):
    """Справочник категорий (DATA-04). type: income | expense."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="expense")
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class User(Base):
    """Пользователь системы (DATA-03, INFRA-06). PK — uuid в строке (кросс-СУБД)."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class FxRate(Base):
    """Курс валюты к USD-пивоту (FR-19). convert(A→B) = amount · rate(A)/rate(B)."""
    __tablename__ = "fx_rates"

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    rate_to_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ManualSnapshot(Base):
    """Персистентное хранилище ручного FinancialSnapshot (INFRA-18)."""
    __tablename__ = "manual_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PlaidToken(Base):
    """Plaid access_token, шифрованный «в покое» Fernet (INFRA-17, NFR-06)."""
    __tablename__ = "plaid_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    # Денормализованное имя категории — fallback и совместимость со старым кодом.
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # FK на справочник (DATA-04); заполняется движком категоризации (FR-13, Сессия 5).
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    # Сырьё для категоризатора и merchant-аналитики — больше не склеивается в category.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    mcc: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_synced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Источник-банк импортированной операции (tinkoff/sber/...), NULL для ручных.
    bank: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Obligation(Base):
    __tablename__ = "obligations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, default="Обязательство")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    term: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_payment: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    payment_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Жизненный цикл + атрибуты по ER (DATA-06, DATA-09).
    bank: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="material", index=True)
    # Жизненный цикл по ER (DATA-06).
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    achieved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    limit_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    parent_recommendation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recommendations.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class LiquidAsset(Base):
    """Независимая ликвидная позиция Bliq: депозиты, накопит. счета, кэш."""
    __tablename__ = "liquid_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Депозит")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="deposit")
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ObligationPayment(Base):
    """История платежей по обязательству (DATA-06)."""
    __tablename__ = "obligation_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    obligation_id: Mapped[int] = mapped_column(
        ForeignKey("obligations.id"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    is_early: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remaining_after: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0)


class GoalContribution(Base):
    """История пополнений цели (DATA-06). source: manual | initial | sync."""
    __tablename__ = "goal_contributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    contribution_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")


class UserPrefs(Base):
    """Параметры пользователя U = (Lmin, R, H, r_bench, base_currency).

    v3.0.0: одна строка на пользователя (user_id unique FK, DATA-03);
    base_currency — валюта расчётов движка (FR-19).
    """
    __tablename__ = "user_prefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, unique=True, index=True
    )
    l_min: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.0"))
    risk_tolerance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    horizon: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    r_bench: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=Decimal("0.14"))
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Event(Base):
    """Единая событийная модель продуктовой аналитики (LOG-01).

    user_id NULL-able: в single-user релизе v2.1.0 пользователь один,
    колонка готова к мультипользовательскому v3.0.0 без миграции схемы.
    """
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    app_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )


class Recommendation(Base):
    """Снимок каждой сгенерированной рекомендации (LOG-02).

    Главный аналитический актив: полная история советов СППР для анализа
    динамики финансового здоровья, качества рекомендаций и accept-rate.
    """
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    income_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expense_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    obligation_payments_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    balance_bt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bliq: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    rt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    dt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    blr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    optimal_x_obl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    optimal_x_res: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    optimal_x_goals: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    u_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    alternatives_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    alternatives_accepted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reasoning_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
