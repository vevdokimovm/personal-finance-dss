from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_synced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Obligation(Base):
    __tablename__ = "obligations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, default="Обязательство")
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    term: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_payment: Mapped[float] = mapped_column(Float, nullable=False)
    payment_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    # Категория цели для взвешенной приоритизации (форм. 9 ВКР)
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="material",
        index=True,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class LiquidAsset(Base):
    """Независимая ликвидная позиция Bliq: депозиты, накопит. счета, кэш."""
    __tablename__ = "liquid_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Депозит")
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="deposit",
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class UserPrefs(Base):
    """Параметры пользователя U = (Lmin, R, H, r_bench) из ВКР, форм. 7."""
    __tablename__ = "user_prefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    l_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_tolerance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    horizon: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    # Альтернативная доходность накоплений (OCR) — порог для Avalanche
    r_bench: Mapped[float] = mapped_column(Float, nullable=False, default=0.14)
