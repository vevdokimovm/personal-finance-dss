from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Goal, LiquidAsset, Obligation, Transaction, UserPrefs


# ── Transactions ─────────────────────────────────────────────────────────
def create_transaction(
    db: Session,
    amount: float,
    category: str,
    type: str,
    date: datetime,
    is_synced: bool = False,
) -> Transaction:
    transaction = Transaction(
        amount=amount, category=category, type=type, date=date, is_synced=is_synced
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


# ── Obligations ──────────────────────────────────────────────────────────
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
        name=name, amount=amount, interest_rate=interest_rate,
        term=term, monthly_payment=monthly_payment,
        payment_day=payment_day, comment=comment,
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


# ── Goals ────────────────────────────────────────────────────────────────
def create_goal(
    db: Session,
    name: str,
    target_amount: float,
    current_amount: float,
    deadline: datetime,
    category: str = "material",
    comment: Optional[str] = None,
) -> Goal:
    goal = Goal(
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline,
        category=category,
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


# ── Liquid Assets ────────────────────────────────────────────────────────
def create_liquid_asset(
    db: Session,
    name: str = "Депозит",
    amount: float = 0.0,
    interest_rate: float = 0.0,
    type: str = "deposit",
    comment: Optional[str] = None,
) -> LiquidAsset:
    asset = LiquidAsset(
        name=name, amount=amount, interest_rate=interest_rate, type=type, comment=comment
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_liquid_assets(db: Session) -> list[LiquidAsset]:
    return db.query(LiquidAsset).order_by(LiquidAsset.id.desc()).all()


def delete_liquid_asset(db: Session, asset_id: int) -> Optional[LiquidAsset]:
    asset = db.get(LiquidAsset, asset_id)
    if asset is None:
        return None
    db.delete(asset)
    db.commit()
    return asset


# ── User Prefs (singleton, id=1) ─────────────────────────────────────────
def get_user_prefs(db: Session) -> UserPrefs:
    prefs = db.get(UserPrefs, 1)
    if prefs is None:
        prefs = UserPrefs(id=1)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


def update_user_prefs(
    db: Session,
    l_min: Optional[float] = None,
    risk_tolerance: Optional[int] = None,
    horizon: Optional[int] = None,
    r_bench: Optional[float] = None,
) -> UserPrefs:
    prefs = get_user_prefs(db)
    if l_min is not None:
        prefs.l_min = l_min
    if risk_tolerance is not None:
        prefs.risk_tolerance = risk_tolerance
    if horizon is not None:
        prefs.horizon = horizon
    if r_bench is not None:
        prefs.r_bench = r_bench
    db.commit()
    db.refresh(prefs)
    return prefs
