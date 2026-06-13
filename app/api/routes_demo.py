from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.models import Goal, Obligation, Transaction
from app.dependencies import get_db


router = APIRouter(tags=["Демо-данные"])


def _clear_all_data(db: Session) -> None:
    db.execute(delete(Transaction))
    db.execute(delete(Obligation))
    db.execute(delete(Goal))


@router.post("/demo/load", summary="Загрузить демо-данные")
def load_demo_data(db: Session = Depends(get_db)) -> dict[str, str]:
    _clear_all_data(db)

    now = datetime.utcnow()
    transactions = [
        Transaction(
            amount=145000,
            category="Заработная плата",
            type="income",
            date=now - timedelta(days=12),
        ),
        Transaction(
            amount=22000,
            category="Подработка",
            type="income",
            date=now - timedelta(days=5),
        ),
        Transaction(
            amount=18500,
            category="Продукты",
            type="expense",
            date=now - timedelta(days=10),
        ),
        Transaction(
            amount=6400,
            category="Транспорт",
            type="expense",
            date=now - timedelta(days=8),
        ),
        Transaction(
            amount=1900,
            category="Связь",
            type="expense",
            date=now - timedelta(days=6),
        ),
        Transaction(
            amount=9700,
            category="Досуг",
            type="expense",
            date=now - timedelta(days=3),
        ),
    ]

    obligations = [
        Obligation(
            name="Потребительский кредит",
            amount=280000,
            interest_rate=15.9,
            term=24,
            monthly_payment=23500,
            payment_day=12,
            comment="Ежемесячный платёж по кредиту на ремонт.",
        )
    ]

    goals = [
        Goal(
            name="Отпуск",
            target_amount=180000,
            current_amount=45000,
            deadline=now + timedelta(days=210),
            comment="Накопление на летний отпуск и билеты.",
        )
    ]

    db.add_all(transactions)
    db.add_all(obligations)
    db.add_all(goals)
    db.commit()

    return {"detail": "Демо-данные успешно загружены."}


@router.post("/demo/clear", summary="Очистить данные")
def clear_demo_data(db: Session = Depends(get_db)) -> dict[str, str]:
    _clear_all_data(db)
    db.commit()
    return {"detail": "Все данные удалены."}
