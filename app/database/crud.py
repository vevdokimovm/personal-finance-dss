from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.categorization import classify_transaction
from app.database.models import (
    Budget,
    Category,
    Goal,
    GoalContribution,
    LiquidAsset,
    Obligation,
    ObligationPayment,
    Scenario,
    Transaction,
    UserPrefs,
)


# ── Categories (DATA-04) ─────────────────────────────────────────────────
def create_category(db: Session, name: str, type: str = "expense", is_system: bool = False) -> Category:
    category = Category(name=name, type=type, is_system=is_system)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session, type: Optional[str] = None) -> list[Category]:
    query = db.query(Category)
    if type is not None:
        query = query.filter(Category.type == type)
    return query.order_by(Category.name.asc()).all()


def get_or_create_category(db: Session, name: str, type: str = "expense") -> Category:
    existing = db.query(Category).filter(Category.name == name, Category.type == type).first()
    if existing is not None:
        return existing
    return create_category(db, name=name, type=type, is_system=False)


# ── Transactions ─────────────────────────────────────────────────────────
def create_transaction(
    db: Session,
    amount: float,
    type: str,
    date: datetime,
    category: Optional[str] = None,
    is_synced: bool = False,
    description: Optional[str] = None,
    external_id: Optional[str] = None,
    category_id: Optional[int] = None,
    mcc: Optional[str] = None,
    bank: Optional[str] = None,
) -> Transaction:
    resolved_category = category or classify_transaction(description, mcc, type)
    transaction = Transaction(
        amount=amount,
        category=resolved_category,
        type=type,
        date=date,
        is_synced=is_synced,
        description=description,
        external_id=external_id,
        category_id=category_id,
        mcc=mcc,
        bank=bank,
        is_recurring=_is_recurring(db, description, type),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def _is_recurring(db: Session, description: Optional[str], txn_type: str) -> bool:
    """Помечает операцию повторяющейся, если уже есть ≥2 таких же (FR-13)."""
    if not description:
        return False
    count = (
        db.query(Transaction)
        .filter(
            Transaction.description == description,
            Transaction.type == txn_type,
            Transaction.is_deleted == False,  # noqa: E712
        )
        .count()
    )
    return count >= 2


def get_spending_by_category(db: Session, days: int = 30, top_n: int = 5) -> dict:
    """Разрез расходов по категориям и топ-мерчанты за период (FR-14)."""
    since = datetime.now() - timedelta(days=days)
    base_filter = (
        Transaction.type == "expense",
        Transaction.is_deleted == False,  # noqa: E712
        Transaction.date >= since,
    )

    cat_rows = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("cnt"),
        )
        .filter(*base_filter)
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    categories = [
        {"category": row.category, "total": round(row.total or 0.0, 2), "count": row.cnt}
        for row in cat_rows
    ]

    merchant_rows = (
        db.query(
            Transaction.description,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("cnt"),
        )
        .filter(*base_filter, Transaction.description.isnot(None))
        .group_by(Transaction.description)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(top_n)
        .all()
    )
    top_merchants = [
        {"merchant": row.description, "total": round(row.total or 0.0, 2), "count": row.cnt}
        for row in merchant_rows
    ]

    total_expense = round(sum(c["total"] for c in categories), 2)
    return {
        "categories": categories,
        "top_merchants": top_merchants,
        "total_expense": total_expense,
        "period_days": days,
    }


def get_budgets(db: Session) -> list[Budget]:
    return db.query(Budget).order_by(Budget.category).all()


def create_budget(db: Session, category: str, limit_amount: float) -> Budget:
    """Создаёт бюджет; при существующей категории — обновляет лимит (FR-22)."""
    existing = db.query(Budget).filter(Budget.category == category).first()
    if existing is not None:
        existing.limit_amount = limit_amount
        db.commit()
        db.refresh(existing)
        return existing
    budget = Budget(category=category, limit_amount=limit_amount)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int) -> bool:
    budget = db.get(Budget, budget_id)
    if budget is None:
        return False
    db.delete(budget)
    db.commit()
    return True


def save_scenario(
    db: Session,
    name: str,
    parameters: dict,
    result: dict,
    parent_recommendation_id: Optional[int] = None,
    description: Optional[str] = None,
) -> Scenario:
    """Сохраняет снимок сценария что-если (LOG-06)."""
    scenario = Scenario(
        name=name,
        description=description,
        parameters_json=parameters,
        result_json=result,
        parent_recommendation_id=parent_recommendation_id,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


def get_scenarios(db: Session, limit: int = 20) -> list[Scenario]:
    return db.query(Scenario).order_by(Scenario.created_at.desc()).limit(limit).all()


def get_budget_status(db: Session, days: int = 30) -> list[dict]:
    """План-факт по категорийным бюджетам за период (FR-22)."""
    since = datetime.now() - timedelta(days=days)
    statuses = []
    for b in db.query(Budget).order_by(Budget.category).all():
        spent = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.type == "expense",
                Transaction.is_deleted == False,  # noqa: E712
                Transaction.category == b.category,
                Transaction.date >= since,
            )
            .scalar()
        ) or 0.0
        pct = round(spent / b.limit_amount * 100, 1) if b.limit_amount > 0 else 0.0
        statuses.append({
            "id": b.id,
            "category": b.category,
            "limit_amount": round(b.limit_amount, 2),
            "spent": round(spent, 2),
            "pct": pct,
            "over": spent > b.limit_amount,
        })
    return statuses


def get_transactions(db: Session) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.is_deleted == False)  # noqa: E712
        .order_by(Transaction.date.desc())
        .all()
    )


def delete_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Мягкое удаление (BUG-03): запись сохраняется и может быть восстановлена."""
    transaction = db.get(Transaction, transaction_id)
    if transaction is None or transaction.is_deleted:
        return None
    transaction.is_deleted = True
    transaction.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)
    return transaction


def restore_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Восстановление мягко удалённой транзакции (BUG-03)."""
    transaction = db.get(Transaction, transaction_id)
    if transaction is None or not transaction.is_deleted:
        return None
    transaction.is_deleted = False
    transaction.deleted_at = None
    db.commit()
    db.refresh(transaction)
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
    bank: Optional[str] = None,
    type: str = "other",
    start_date: Optional[datetime] = None,
) -> Obligation:
    obligation = Obligation(
        name=name,
        amount=amount,
        interest_rate=interest_rate,
        term=term,
        monthly_payment=monthly_payment,
        payment_day=payment_day,
        comment=comment,
        bank=bank,
        type=type,
        start_date=start_date or datetime.utcnow(),
        is_active=True,
    )
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


def get_obligations(db: Session, active_only: bool = False) -> list[Obligation]:
    query = db.query(Obligation)
    if active_only:
        query = query.filter(Obligation.is_active.is_(True))
    return query.order_by(Obligation.id.desc()).all()


def delete_obligation(db: Session, obligation_id: int) -> Optional[Obligation]:
    obligation = db.get(Obligation, obligation_id)
    if obligation is None:
        return None
    db.delete(obligation)
    db.commit()
    return obligation


def close_obligation(db: Session, obligation_id: int) -> Optional[Obligation]:
    obligation = db.get(Obligation, obligation_id)
    if obligation is None:
        return None
    obligation.is_active = False
    obligation.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(obligation)
    return obligation


def record_obligation_payment(
    db: Session,
    obligation_id: int,
    amount: float,
    is_early: bool = False,
    remaining_after: float = 0.0,
    payment_date: Optional[datetime] = None,
) -> ObligationPayment:
    payment = ObligationPayment(
        obligation_id=obligation_id,
        amount=amount,
        is_early=is_early,
        remaining_after=remaining_after,
        payment_date=payment_date or datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_obligation_payments(db: Session, obligation_id: int) -> list[ObligationPayment]:
    return (
        db.query(ObligationPayment)
        .filter(ObligationPayment.obligation_id == obligation_id)
        .order_by(ObligationPayment.payment_date.asc())
        .all()
    )


# ── Goals ────────────────────────────────────────────────────────────────
def create_goal(
    db: Session,
    name: str,
    target_amount: float,
    current_amount: float,
    deadline: datetime,
    category: str = "material",
    comment: Optional[str] = None,
    priority: int = 0,
) -> Goal:
    goal = Goal(
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline,
        category=category,
        comment=comment,
        priority=priority,
        is_active=True,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    # Стартовое накопление фиксируем в истории (DATA-06).
    if current_amount and current_amount > 0:
        db.add(GoalContribution(goal_id=goal.id, amount=current_amount, source="initial"))
        db.commit()

    return goal


def get_goals(db: Session, active_only: bool = False) -> list[Goal]:
    query = db.query(Goal)
    if active_only:
        query = query.filter(Goal.is_active.is_(True))
    return query.order_by(Goal.deadline.asc()).all()


def delete_goal(db: Session, goal_id: int) -> Optional[Goal]:
    goal = db.get(Goal, goal_id)
    if goal is None:
        return None
    db.delete(goal)
    db.commit()
    return goal


def achieve_goal(db: Session, goal_id: int) -> Optional[Goal]:
    goal = db.get(Goal, goal_id)
    if goal is None:
        return None
    goal.is_active = False
    goal.achieved_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


def record_goal_contribution(
    db: Session,
    goal_id: int,
    amount: float,
    source: str = "manual",
    contribution_date: Optional[datetime] = None,
) -> GoalContribution:
    contribution = GoalContribution(
        goal_id=goal_id,
        amount=amount,
        source=source,
        contribution_date=contribution_date or datetime.utcnow(),
    )
    db.add(contribution)
    db.commit()
    db.refresh(contribution)
    return contribution


def get_goal_contributions(db: Session, goal_id: int) -> list[GoalContribution]:
    return (
        db.query(GoalContribution)
        .filter(GoalContribution.goal_id == goal_id)
        .order_by(GoalContribution.contribution_date.asc())
        .all()
    )


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
