from __future__ import annotations

import secrets
import string
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from app.core.categorization import classify_transaction
from app.core.money import to_money
from app.database.models import (
    Budget,
    Category,
    Event,
    Goal,
    GoalContribution,
    LiquidAsset,
    Obligation,
    ObligationPayment,
    Recommendation,
    Scenario,
    Transaction,
    UserPrefs,
)


def _owner_filter(query, model, user_id):
    """Фильтр изоляции по пользователю.

    user_id задан  → строки этого пользователя.
    user_id=None   → строки без владельца (анонимный/legacy-режим). После того как
                     первый зарегистрированный пользователь усыновил данные, аноним
                     перестаёт видеть чужие строки — это закрывает доступ к данным
                     других пользователей в multi-user-режиме.
    """
    if user_id is not None:
        return query.filter(model.user_id == user_id)
    return query.filter(model.user_id.is_(None))


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
    currency: str = "RUB",
    user_id: Optional[str] = None,
    autocommit: bool = True,
) -> Transaction:
    resolved_category = category or classify_transaction(description, mcc, type)
    transaction = Transaction(
        amount=to_money(amount),
        category=resolved_category,
        type=type,
        date=date,
        is_synced=is_synced,
        description=description,
        external_id=external_id,
        category_id=category_id,
        mcc=mcc,
        bank=bank,
        currency=currency,
        user_id=user_id,
        is_recurring=_is_recurring(db, description, type),
    )
    db.add(transaction)
    if autocommit:
        db.commit()
        db.refresh(transaction)
    return transaction


def bulk_create_transactions(
    db: Session,
    rows: list[dict],
    user_id: Optional[str] = None,
    bank: Optional[str] = None,
    currency: str = "RUB",
    batch_size: int = 1000,
) -> int:
    """Массовая вставка транзакций без поштучных запросов в БД.

    `create_transaction` зовёт `_is_recurring` (COUNT-запрос) на КАЖДУЮ строку —
    на выписке в 12k операций это десятки тысяч запросов и таймаут воркера. Здесь
    признак повторяемости (FR-13: ≥2 одинаковых описание+тип) считается ОДНИМ
    проходом в памяти (Counter по существующим + входящим), вставка — `bulk_insert_mappings`
    пачками. `rows` должны быть уже дедуплицированы вызывающим кодом.

    Каждая строка: {amount, type, date(datetime|isoformat), description?, mcc?, is_synced?}.
    """
    if not rows:
        return 0

    owner = Transaction.user_id == user_id if user_id else Transaction.user_id.is_(None)
    counts: Counter = Counter(
        (desc, typ)
        for desc, typ in db.query(Transaction.description, Transaction.type).filter(
            owner, Transaction.is_deleted == False  # noqa: E712
        )
    )
    for r in rows:
        counts[(r.get("description"), r["type"])] += 1

    now = datetime.utcnow()
    mappings: list[dict] = []
    inserted = 0

    def _flush() -> None:
        nonlocal inserted, mappings
        if mappings:
            db.bulk_insert_mappings(Transaction, mappings)
            db.commit()
            inserted += len(mappings)
            mappings = []

    for r in rows:
        desc = r.get("description")
        typ = r["type"]
        date = r["date"]
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        mappings.append({
            "amount": to_money(r["amount"]),
            "category": classify_transaction(desc, r.get("mcc"), typ),
            "type": typ,
            "date": date,
            "description": desc,
            "mcc": r.get("mcc"),
            "bank": bank,
            "currency": currency,
            "user_id": user_id,
            "is_synced": bool(r.get("is_synced", True)),
            "is_recurring": counts[(desc, typ)] >= 2,
            "is_deleted": False,
            "created_at": now,
        })
        if len(mappings) >= batch_size:
            _flush()
    _flush()
    return inserted


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


def get_spending_by_category(
    db: Session, days: int = 30, top_n: int = 5, user_id: Optional[str] = None
) -> dict:
    """Разрез расходов по категориям и топ-мерчанты за период (FR-14)."""
    since = datetime.now() - timedelta(days=days)
    owner = Transaction.user_id == user_id if user_id is not None else Transaction.user_id.is_(None)
    base_filter = (
        Transaction.type == "expense",
        Transaction.is_deleted == False,  # noqa: E712
        Transaction.date >= since,
        owner,
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


def get_budgets(db: Session, user_id: Optional[str] = None) -> list[Budget]:
    query = _owner_filter(db.query(Budget), Budget, user_id)
    return query.order_by(Budget.category).all()


def create_budget(
    db: Session, category: str, limit_amount: float, user_id: Optional[str] = None
) -> Budget:
    """Создаёт бюджет; при существующей категории у того же владельца — обновляет лимит (FR-22)."""
    existing = _owner_filter(
        db.query(Budget).filter(Budget.category == category), Budget, user_id
    ).first()
    if existing is not None:
        existing.limit_amount = to_money(limit_amount)
        db.commit()
        db.refresh(existing)
        return existing
    budget = Budget(category=category, limit_amount=to_money(limit_amount), user_id=user_id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int, user_id: Optional[str] = None) -> bool:
    budget = db.get(Budget, budget_id)
    if budget is None or budget.user_id != user_id:
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
    user_id: Optional[str] = None,
) -> Scenario:
    """Сохраняет снимок сценария что-если (LOG-06)."""
    scenario = Scenario(
        name=name,
        description=description,
        parameters_json=parameters,
        result_json=result,
        parent_recommendation_id=parent_recommendation_id,
        user_id=user_id,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


def get_scenarios(db: Session, limit: int = 20, user_id: Optional[str] = None) -> list[Scenario]:
    query = _owner_filter(db.query(Scenario), Scenario, user_id)
    return query.order_by(Scenario.created_at.desc()).limit(limit).all()


def get_budget_status(db: Session, days: int = 30, user_id: Optional[str] = None) -> list[dict]:
    """План-факт по категорийным бюджетам за период (FR-22)."""
    since = datetime.now() - timedelta(days=days)
    owner = Transaction.user_id == user_id if user_id is not None else Transaction.user_id.is_(None)
    statuses = []
    for b in _owner_filter(db.query(Budget), Budget, user_id).order_by(Budget.category).all():
        spent = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.type == "expense",
                Transaction.is_deleted == False,  # noqa: E712
                Transaction.category == b.category,
                Transaction.date >= since,
                owner,
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


def get_transactions(db: Session, user_id: Optional[str] = None) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.is_deleted == False)  # noqa: E712
    query = _owner_filter(query, Transaction, user_id)
    return query.order_by(Transaction.date.desc()).all()


def delete_transaction(
    db: Session, transaction_id: int, user_id: Optional[str] = None
) -> Optional[Transaction]:
    """Мягкое удаление (BUG-03): запись сохраняется и может быть восстановлена."""
    transaction = db.get(Transaction, transaction_id)
    if transaction is None or transaction.is_deleted or transaction.user_id != user_id:
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
    currency: str = "RUB",
    user_id: Optional[str] = None,
) -> Obligation:
    obligation = Obligation(
        name=name,
        amount=to_money(amount),
        interest_rate=interest_rate,
        term=term,
        monthly_payment=to_money(monthly_payment),
        payment_day=payment_day,
        comment=comment,
        bank=bank,
        type=type,
        start_date=start_date or datetime.utcnow(),
        is_active=True,
        currency=currency,
        user_id=user_id,
    )
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


def get_obligations(
    db: Session, active_only: bool = False, user_id: Optional[str] = None
) -> list[Obligation]:
    query = db.query(Obligation).filter(Obligation.is_deleted.is_(False))
    if active_only:
        query = query.filter(Obligation.is_active.is_(True))
    query = _owner_filter(query, Obligation, user_id)
    return query.order_by(Obligation.id.desc()).all()


def delete_obligation(
    db: Session, obligation_id: int, user_id: Optional[str] = None
) -> Optional[Obligation]:
    """Мягкое удаление (P1.7): запись помечается удалённой и может быть восстановлена.
    История платежей сохраняется (привязана к записи) и возвращается при restore."""
    obligation = db.get(Obligation, obligation_id)
    if obligation is None or obligation.is_deleted or obligation.user_id != user_id:
        return None
    obligation.is_deleted = True
    obligation.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(obligation)
    return obligation


def restore_obligation(
    db: Session, obligation_id: int, user_id: Optional[str] = None
) -> Optional[Obligation]:
    """Восстановление мягко удалённого обязательства (P1.7)."""
    obligation = db.get(Obligation, obligation_id)
    if obligation is None or not obligation.is_deleted or obligation.user_id != user_id:
        return None
    obligation.is_deleted = False
    obligation.deleted_at = None
    db.commit()
    db.refresh(obligation)
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
        amount=to_money(amount),
        is_early=is_early,
        remaining_after=to_money(remaining_after),
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
    currency: str = "RUB",
    savings_rate: float = 0.0,
    linked_asset_id: Optional[int] = None,
    user_id: Optional[str] = None,
) -> Goal:
    goal = Goal(
        name=name,
        target_amount=to_money(target_amount),
        current_amount=to_money(current_amount),
        deadline=deadline,
        category=category,
        comment=comment,
        priority=priority,
        savings_rate=savings_rate,
        linked_asset_id=linked_asset_id,
        is_active=True,
        currency=currency,
        user_id=user_id,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    # Стартовое накопление фиксируем в истории (DATA-06).
    if current_amount and current_amount > 0:
        db.add(GoalContribution(goal_id=goal.id, amount=current_amount, source="initial"))
        db.commit()

    return goal


def get_goals(
    db: Session, active_only: bool = False, user_id: Optional[str] = None
) -> list[Goal]:
    query = db.query(Goal).filter(Goal.is_deleted.is_(False))
    if active_only:
        query = query.filter(Goal.is_active.is_(True))
    query = _owner_filter(query, Goal, user_id)
    return query.order_by(Goal.deadline.asc()).all()


def delete_goal(db: Session, goal_id: int, user_id: Optional[str] = None) -> Optional[Goal]:
    """Мягкое удаление (P1.7): цель помечается удалённой, история взносов сохраняется."""
    goal = db.get(Goal, goal_id)
    if goal is None or goal.is_deleted or goal.user_id != user_id:
        return None
    goal.is_deleted = True
    goal.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


def restore_goal(db: Session, goal_id: int, user_id: Optional[str] = None) -> Optional[Goal]:
    """Восстановление мягко удалённой цели (P1.7)."""
    goal = db.get(Goal, goal_id)
    if goal is None or not goal.is_deleted or goal.user_id != user_id:
        return None
    goal.is_deleted = False
    goal.deleted_at = None
    db.commit()
    db.refresh(goal)
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
        amount=to_money(amount),
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
    currency: str = "RUB",
    user_id: Optional[str] = None,
) -> LiquidAsset:
    asset = LiquidAsset(
        name=name, amount=to_money(amount), interest_rate=interest_rate, type=type,
        comment=comment, currency=currency, user_id=user_id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_liquid_assets(db: Session, user_id: Optional[str] = None) -> list[LiquidAsset]:
    query = db.query(LiquidAsset).filter(LiquidAsset.is_deleted.is_(False))
    query = _owner_filter(query, LiquidAsset, user_id)
    return query.order_by(LiquidAsset.id.desc()).all()


def delete_liquid_asset(
    db: Session, asset_id: int, user_id: Optional[str] = None
) -> Optional[LiquidAsset]:
    """Мягкое удаление (P1.7): актив помечается удалённым и может быть восстановлен."""
    asset = db.get(LiquidAsset, asset_id)
    if asset is None or asset.is_deleted or asset.user_id != user_id:
        return None
    asset.is_deleted = True
    asset.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)
    return asset


def restore_liquid_asset(
    db: Session, asset_id: int, user_id: Optional[str] = None
) -> Optional[LiquidAsset]:
    """Восстановление мягко удалённого ликвидного актива (P1.7)."""
    asset = db.get(LiquidAsset, asset_id)
    if asset is None or not asset.is_deleted or asset.user_id != user_id:
        return None
    asset.is_deleted = False
    asset.deleted_at = None
    db.commit()
    db.refresh(asset)
    return asset


# ── User Prefs (singleton, id=1) ─────────────────────────────────────────
def get_user_prefs(db: Session, user_id: Optional[str] = None) -> UserPrefs:
    """Параметры пользователя.

    user_id=None → legacy single-user (строка без владельца), как в v2.x.
    user_id задан → строка этого пользователя; создаётся при первом обращении.
    """
    if user_id is None:
        prefs = db.query(UserPrefs).filter(UserPrefs.user_id.is_(None)).first()
        if prefs is None:
            prefs = UserPrefs(user_id=None)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        return prefs

    prefs = db.query(UserPrefs).filter(UserPrefs.user_id == user_id).first()
    if prefs is None:
        prefs = UserPrefs(user_id=user_id)
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
    base_currency: Optional[str] = None,
    user_id: Optional[str] = None,
) -> UserPrefs:
    prefs = get_user_prefs(db, user_id=user_id)
    if l_min is not None:
        prefs.l_min = l_min
    if risk_tolerance is not None:
        prefs.risk_tolerance = risk_tolerance
    if horizon is not None:
        prefs.horizon = horizon
    if r_bench is not None:
        prefs.r_bench = r_bench
    if base_currency is not None:
        prefs.base_currency = base_currency
    db.commit()
    db.refresh(prefs)
    return prefs


# ── Users (DATA-03, INFRA-06) ────────────────────────────────────────────
from app.database.models import User  # noqa: E402


def generate_referral_code(db: Session, length: int = 8) -> str:
    """Генерирует уникальный реферальный код (заглавные буквы + цифры)."""
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(10):
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not db.query(User).filter(User.referral_code == code).first():
            return code
    raise RuntimeError("Не удалось сгенерировать уникальный реферальный код")


def get_user_by_referral_code(db: Session, code: str) -> Optional[User]:
    return db.query(User).filter(User.referral_code == code).first()


def count_referrals(db: Session, code: str) -> int:
    """Сколько пользователей пришло по этому реферальному коду."""
    return db.query(User).filter(User.referred_by_code == code).count()


def ensure_referral_code(db: Session, user: User) -> str:
    """Лениво присваивает код пользователю без него (legacy-аккаунты до P3.2)."""
    if not user.referral_code:
        user.referral_code = generate_referral_code(db)
        db.commit()
        db.refresh(user)
    return user.referral_code


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    display_name: Optional[str] = None,
    newsletter_opt_in: bool = False,
    consent_at: Optional[datetime] = None,
    referred_by_code: Optional[str] = None,
) -> User:
    user = User(
        email=email.lower().strip(),
        password_hash=password_hash,
        display_name=display_name,
        newsletter_opt_in=newsletter_opt_in,
        consent_at=consent_at or datetime.utcnow(),
        referral_code=generate_referral_code(db),
        referred_by_code=referred_by_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)


def update_user_profile(
    db: Session, user_id: str, display_name: Optional[str] = None
) -> Optional[User]:
    """Обновление данных профиля (пока имя)."""
    user = db.get(User, user_id)
    if user is None:
        return None
    if display_name is not None:
        user.display_name = display_name.strip() or None
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: str, password_hash: str) -> Optional[User]:
    user = db.get(User, user_id)
    if user is None:
        return None
    user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user


def mark_email_verified(db: Session, user_id: str) -> Optional[User]:
    user = db.get(User, user_id)
    if user is None:
        return None
    user.email_verified = True
    db.commit()
    db.refresh(user)
    return user


def register_failed_login(
    db: Session, user: User, max_attempts: int, lockout_minutes: int
) -> User:
    """Учитывает неудачную попытку входа. При достижении лимита — блокирует
    аккаунт на lockout_minutes (P1.2, защита от перебора пароля)."""
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= max_attempts:
        user.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
    db.commit()
    db.refresh(user)
    return user


def reset_failed_logins(db: Session, user: User) -> User:
    """Сбрасывает счётчик и снимает блокировку после успешного входа."""
    if user.failed_login_attempts or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
        db.refresh(user)
    return user


def delete_user(db: Session, user_id: str) -> bool:
    """Полное удаление аккаунта со всеми данными пользователя (152-ФЗ)."""
    user = db.get(User, user_id)
    if user is None:
        return False
    # История привязана к целям/обязательствам пользователя — на PostgreSQL её
    # нужно удалить до родительских строк, иначе FK заблокирует удаление.
    goal_ids = [row[0] for row in db.query(Goal.id).filter(Goal.user_id == user_id)]
    obl_ids = [row[0] for row in db.query(Obligation.id).filter(Obligation.user_id == user_id)]
    if goal_ids:
        db.execute(delete(GoalContribution).where(GoalContribution.goal_id.in_(goal_ids)))
    if obl_ids:
        db.execute(delete(ObligationPayment).where(ObligationPayment.obligation_id.in_(obl_ids)))
    # Основные сущности пользователя.
    for model in (*_OWNED_MODELS, UserPrefs):
        db.execute(delete(model).where(model.user_id == user_id))
    # Аналитика и рекомендации — тоже персональные данные (право на удаление).
    db.execute(delete(Event).where(Event.user_id == user_id))
    db.execute(delete(Recommendation).where(Recommendation.user_id == user_id))
    db.delete(user)
    db.commit()
    return True


def count_users(db: Session) -> int:
    return db.query(User).count()


_OWNED_MODELS = (Transaction, Obligation, Goal, LiquidAsset, Budget, Scenario)


def adopt_orphan_rows(db: Session, user_id: str) -> int:
    """Усыновление осиротевших строк первым пользователем (single→multi).

    Все записи без владельца (user_id IS NULL), созданные в анонимном режиме,
    привязываются к user_id. Также legacy-настройки (user_prefs.user_id IS NULL)
    переносятся на нового владельца. Возвращает число затронутых строк.
    """
    affected = 0
    for model in _OWNED_MODELS:
        rows = db.query(model).filter(model.user_id.is_(None)).all()
        for row in rows:
            row.user_id = user_id
            affected += 1
    legacy_prefs = db.query(UserPrefs).filter(UserPrefs.user_id.is_(None)).first()
    if legacy_prefs is not None and db.query(UserPrefs).filter(UserPrefs.user_id == user_id).first() is None:
        legacy_prefs.user_id = user_id
        affected += 1
    db.commit()
    return affected
