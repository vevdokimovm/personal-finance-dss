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

    # ── Доходы ──────────────────────────────────────────────────
    transactions = [
        Transaction(amount=145000, category="Заработная плата",  type="income",  date=now - timedelta(days=14)),
        Transaction(amount=22000,  category="Подработка",         type="income",  date=now - timedelta(days=5)),
        Transaction(amount=8500,   category="Дивиденды",          type="income",  date=now - timedelta(days=2)),
        # ── Расходы ─────────────────────────────────────────────
        Transaction(amount=19500,  category="Продукты",           type="expense", date=now - timedelta(days=12)),
        Transaction(amount=7200,   category="Транспорт",          type="expense", date=now - timedelta(days=10)),
        Transaction(amount=5800,   category="Коммунальные услуги", type="expense", date=now - timedelta(days=9)),
        Transaction(amount=2100,   category="Связь",              type="expense", date=now - timedelta(days=7)),
        Transaction(amount=8400,   category="Досуг и рестораны",  type="expense", date=now - timedelta(days=4)),
        Transaction(amount=4300,   category="Одежда",             type="expense", date=now - timedelta(days=3)),
        Transaction(amount=3200,   category="Здоровье",           type="expense", date=now - timedelta(days=1)),
    ]

    # ── Обязательства ───────────────────────────────────────────
    obligations = [
        Obligation(
            name="Потребительский кредит",
            amount=320000,
            interest_rate=16.5,
            term=24,
            monthly_payment=16500,
            payment_day=10,
            comment="Кредит на ремонт квартиры.",
        ),
        Obligation(
            name="Автокредит",
            amount=850000,
            interest_rate=12.9,
            term=48,
            monthly_payment=23800,
            payment_day=15,
            comment="Автомобиль в кредит.",
        ),
        Obligation(
            name="Рассрочка на технику",
            amount=65000,
            interest_rate=0.0,
            term=12,
            monthly_payment=5500,
            payment_day=20,
            comment="Беспроцентная рассрочка на ноутбук.",
        ),
    ]

    # ── Цели ────────────────────────────────────────────────────
    goals = [
        Goal(
            name="Отпуск (Европа)",
            target_amount=180000,
            current_amount=52000,
            deadline=now + timedelta(days=210),
            comment="Летний отпуск: перелёт, отель, экскурсии.",
        ),
        Goal(
            name="Подушка безопасности",
            target_amount=300000,
            current_amount=85000,
            deadline=now + timedelta(days=365),
            comment="Резервный фонд на 3–4 месяца расходов.",
        ),
        Goal(
            name="Первоначальный взнос (ипотека)",
            target_amount=1200000,
            current_amount=310000,
            deadline=now + timedelta(days=730),
            comment="Накопление на первоначальный взнос по ипотеке.",
        ),
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
