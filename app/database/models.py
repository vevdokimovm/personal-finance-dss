from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint

from app.database.types import EncryptedString
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
    display_name: Mapped[Optional[str]] = mapped_column(EncryptedString, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    newsletter_opt_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Account lockout (P1.2): защита от перебора пароля.
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    referral_code: Mapped[Optional[str]] = mapped_column(
        String(12), nullable=True, unique=True, index=True
    )
    referred_by_code: Mapped[Optional[str]] = mapped_column(String(12), nullable=True, index=True)
    # Telegram-привязка (P3.6): chat_id привязанного бота, уникален (один чат — один аккаунт).
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, unique=True, index=True
    )
    # Монетизация (каркас): тариф и срок его действия. free по умолчанию; premium с
    # истёкшим plan_expires_at трактуется как free (см. services/subscription.py).
    plan_tier: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    plan_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


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
    # P3.7: общий скоуп. NULL = личная операция (дефолт). Задан → видна членам household.
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
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
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
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
    comment: Mapped[Optional[str]] = mapped_column(EncryptedString, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="material", index=True)
    # Ставка по инструменту, где копятся деньги цели (вклад/счёт), долей. 0 = без процентов.
    savings_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    # Конверты: ликвидный актив, где физически копятся деньги цели. NULL = не привязана.
    linked_asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("liquid_assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Жизненный цикл по ER (DATA-06).
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    achieved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(EncryptedString, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
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
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
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
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Депозит")
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=0.0)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="deposit")
    comment: Mapped[Optional[str]] = mapped_column(EncryptedString, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


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


class NotificationLog(Base):
    """Журнал отправленных уведомлений (P2.5) — дедупликация.

    dedup_key уникально описывает событие (например 'budget_overrun:Кафе:2026-06'),
    чтобы одно и то же не отправлялось повторно при периодических прогонах.
    """
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Notification(Base):
    """In-app уведомление (P2.3) — то, что пользователь видит в интерфейсе (колокольчик).

    Отличается от NotificationLog: тот — служебный дедуп-журнал отправленных ПИСЕМ,
    а это — само уведомление для показа в приложении (заголовок, текст, ссылка,
    флаг прочитано). Персональное (без household-оси): уведомления не расшариваются.
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )


class PlanSnapshot(Base):
    """Снапшот рассчитанного плана распределения (P2.6 — история плана).

    Сохраняет результат _compute_plan на момент времени: профиль риска, показатели
    Rt/Lt/Dt/BLR, выбранную (лучшую) альтернативу и полный топ-3 (JSON) для детального
    просмотра. Soft-delete — как у остальных пользовательских сущностей.
    """

    __tablename__ = "plan_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    household_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("households.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    risk_profile: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    # показатели на момент расчёта (Dt — доля, не проценты, как в каноне)
    rt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    dt: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    blr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # выбранная (лучшая) альтернатива
    best_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    x_obligations: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    x_reserve: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    x_goals: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    utility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # полный топ-3 (JSON) — для детального просмотра истории
    top3: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class UserCategoryRule(Base):
    """Пользовательское правило категоризации (P2.7, обучение на правках).

    Когда пользователь вручную переназначает категорию операции, сохраняется правило
    (match_token -> category) для его user_id. Правило применяется к будущим импортам и
    ретроактивно к существующим совпадающим операциям. Детерминированно, без ML.
    `match_token` хранится уже нормализованным (см. normalize_match_key).
    """

    __tablename__ = "user_category_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    # Нормализованный токен-подстрока: операция матчится, если её описание его содержит.
    match_token: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="expense")
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("user_id", "match_token", "type", name="uq_user_category_rule"),
    )


class Experiment(Base):
    """A/B-эксперимент (P3.5). Управляется через админ-API: создать → running → stopped.

    Варианты хранятся JSON-списком `[{"name": str, "weight": int}, ...]`; назначение —
    детерминированным хешем (см. core/experiments.py) с фиксацией в ExperimentAssignment.
    `conversion_event` — тип события, по которому считается конверсия в результатах.
    """

    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    variants: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    conversion_event: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ExperimentAssignment(Base):
    """Зафиксированное назначение subject → вариант (P3.5).

    Лочит назначение при первом показе: даже если веса/варианты эксперимента потом изменят,
    уже назначенный subject остаётся в своём варианте (ноль контаминации выборки).
    subject_id — user_id (аутентифицирован) либо session_id (аноним).
    """

    __tablename__ = "experiment_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("experiments.id"), nullable=False, index=True
    )
    subject_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(64), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("experiment_id", "subject_id", name="uq_experiment_assignment"),
    )


# ── Household: совместный скоуп поверх персонального владения (P3.7) ───────
#
# Дизайн-инвариант: household — ДОПОЛНИТЕЛЬНЫЙ скоуп, а не замена user_id.
# Каждая доменная строка по-прежнему принадлежит автору (user_id); household_id
# опционален (NULL = личное, как до P3.7). Это держит FINPILOT персональным
# по умолчанию и аддитивным по отношению к семейному функционалу.


class Household(Base):
    """Совместное пространство (семья). owner_id — создатель и единственный, кто
    управляет членством/удалением на первой фазе."""

    __tablename__ = "households"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Семья")
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class HouseholdMembership(Base):
    """Членство пользователя в household с ролью. role: owner | member | viewer.

    owner — полный контроль (управление членством, удаление household, r/w общих
    данных); member — r/w общих данных, без управления членством; viewer —
    только чтение общих данных. Личными данными (household_id NULL) владелец
    распоряжается всегда сам, независимо от роли в household.
    """

    __tablename__ = "household_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("household_id", "user_id", name="uq_household_member"),
    )


class HouseholdInvite(Base):
    """Приглашение в household по токену. Живёт до accept/revoke/expiry.

    status: pending | accepted | revoked. Протухание определяется по expires_at
    (а не отдельным статусом), чтобы не требовать фонового джоба. Живая отправка
    письма приглашения — на стороне VPS (как SMTP P0.2); здесь генерируется токен
    и ссылка, само письмо в песочнице не уходит.
    """

    __tablename__ = "household_invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
