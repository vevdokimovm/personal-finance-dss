from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Goal, Obligation, Transaction


def create_transaction(
    db: Session,
    amount: float,
    category: str,
    type: str,
    date: datetime,
    is_synced: bool = False,
) -> Transaction:
    transaction = Transaction(
        amount=amount,
        category=category,
        type=type,
        date=date,
        is_synced=is_synced,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transactions(db: Session) -> list[Transaction]:
    return db.query(Transaction).order_by(Transaction.date.desc()).all()


def delete_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        return None

    db.delete(transaction)
    db.commit()
    return transaction


def create_obligation(
    db: Session,
    name: str,
    amount: float,
    interest_rate: float,
    term: int,
    monthly_payment: float,
    payment_day: int,
    comment: Optional[str] = None,
) -> Obligation:
    obligation = Obligation(
        name=name,
        amount=amount,
        interest_rate=interest_rate,
        term=term,
        monthly_payment=monthly_payment,
        payment_day=payment_day,
        comment=comment,
    )
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


def get_obligations(db: Session) -> list[Obligation]:
    return db.query(Obligation).order_by(Obligation.id.desc()).all()


def delete_obligation(db: Session, obligation_id: int) -> Optional[Obligation]:
    obligation = db.get(Obligation, obligation_id)
    if obligation is None:
        return None

    db.delete(obligation)
    db.commit()
    return obligation


def create_goal(
    db: Session,
    name: str,
    target_amount: float,
    current_amount: float,
    deadline: datetime,
    comment: Optional[str] = None,
) -> Goal:
    goal = Goal(
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline,
        comment=comment,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goals(db: Session) -> list[Goal]:
    return db.query(Goal).order_by(Goal.deadline.asc()).all()


def delete_goal(db: Session, goal_id: int) -> Optional[Goal]:
    goal = db.get(Goal, goal_id)
    if goal is None:
        return None

    db.delete(goal)
    db.commit()
    return goal
