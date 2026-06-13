from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class Obligation(Base):
    __tablename__ = "obligations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        default="Обязательство",
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    term: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_payment: Mapped[float] = mapped_column(Float, nullable=False)
    payment_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
