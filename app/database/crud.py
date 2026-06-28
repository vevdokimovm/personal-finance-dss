from __future__ import annotations

import secrets
import string
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from app.core.categorization import (
    MIN_MATCH_TOKEN_LEN,
    classify_transaction,
    classify_with_rules,
    normalize_match_key,
)
from app.core.money import to_money
from app.database.models import (
    Budget,
    Category,
    Event,
    Goal,
    GoalContribution,
    Household,
    HouseholdInvite,
    HouseholdMembership,
    LiquidAsset,
    Obligation,
    ObligationPayment,
    PlanSnapshot,
    Recommendation,
    Scenario,
    Transaction,
    UserCategoryRule,
    UserPrefs,
)


def _household_ids_for(session, user_id) -> tuple:
    """household_id всех домохозяйств пользователя.

    Кешируется на время жизни сессии (= время HTTP-запроса, т.к. get_db выдаёт
    сессию на запрос) в session.info, чтобы множественные вызовы _owner_filter в
    одном запросе не порождали N+1 SELECT по household_memberships.
    """
    if user_id is None:
        return ()
    cache = session.info.setdefault("_household_ids_cache", {})
    if user_id not in cache:
        rows = (
            session.query(HouseholdMembership.household_id)
            .filter(HouseholdMembership.user_id == user_id)
            .all()
        )
        cache[user_id] = tuple(r[0] for r in rows)
    return cache[user_id]


def _owner_filter(query, model, user_id):
    """Фильтр изоляции: персональное владение + (опционально) household-скоуп (P3.7).

    user_id=None    → строки без владельца (анонимный/legacy-режим) — как раньше.
    user_id задан:
      • модель без household_id            → только свои строки (поведение до P3.7);
      • модель с household_id, нет семей    → только свои строки (household-ось пуста,
                                              дизъюнкция вырождается — байт-в-байт
                                              прежнее поведение, ничего не сломано);
      • модель с household_id, есть семьи   → свои строки ∪ общие строки его семей.

    Личное (household_id IS NULL) видно только автору всегда: общее условие
    `user_id == me` ловит свои личные строки, а `household_id IN (...)` — только
    те, что явно положены в общий котёл.
    """
    if user_id is None:
        return query.filter(model.user_id.is_(None))
    if hasattr(model, "household_id"):
        household_ids = _household_ids_for(query.session, user_id)
        if household_ids:
            return query.filter(
                (model.user_id == user_id) | (model.household_id.in_(household_ids))
            )
    return query.filter(model.user_id == user_id)


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
    household_id: Optional[int] = None,
    autocommit: bool = True,
) -> Transaction:
    if category:
        resolved_category = category
    else:
        rules = get_user_category_rules(db, user_id, type)
        resolved_category = classify_with_rules(description, mcc, type, rules)
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
        household_id=household_id,
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

    # P2.7: пользовательские правила категоризации — один запрос на весь батч (без N+1).
    rules_by_type = _user_rules_by_type(db, user_id)

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
            "category": classify_with_rules(desc, r.get("mcc"), typ, rules_by_type.get(typ, ())),
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
    db: Session,
    category: str,
    limit_amount: float,
    user_id: Optional[str] = None,
    household_id: Optional[int] = None,
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
    budget = Budget(
        category=category,
        limit_amount=to_money(limit_amount),
        user_id=user_id,
        household_id=household_id,
    )
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


# ── Обучение категоризации: пользовательские правила (P2.7) ───────────────
def get_user_category_rules(
    db: Session, user_id: Optional[str], txn_type: Optional[str] = None
) -> list[tuple[str, str]]:
    """`[(match_token, category)]` правил пользователя для классификации (новые сверху).

    Опционально фильтрует по типу операции. Возвращает лёгкие кортежи, а не ORM-объекты —
    ровно то, что ждёт `classify_with_rules`.
    """
    query = _owner_filter(
        db.query(UserCategoryRule.match_token, UserCategoryRule.category),
        UserCategoryRule,
        user_id,
    )
    if txn_type is not None:
        query = query.filter(UserCategoryRule.type == txn_type)
    query = query.order_by(UserCategoryRule.updated_at.desc())
    return [(row.match_token, row.category) for row in query]


def _user_rules_by_type(db: Session, user_id: Optional[str]) -> dict[str, list[tuple[str, str]]]:
    """Все правила пользователя, сгруппированные по типу операции — для bulk-импорта без N+1."""
    query = _owner_filter(
        db.query(
            UserCategoryRule.match_token,
            UserCategoryRule.category,
            UserCategoryRule.type,
        ),
        UserCategoryRule,
        user_id,
    ).order_by(UserCategoryRule.updated_at.desc())
    grouped: dict[str, list[tuple[str, str]]] = {}
    for token, category, typ in query:
        grouped.setdefault(typ, []).append((token, category))
    return grouped


def get_category_rules(db: Session, user_id: Optional[str]) -> list[UserCategoryRule]:
    """Полные ORM-объекты правил пользователя для API (список/удаление), новые сверху."""
    return (
        _owner_filter(db.query(UserCategoryRule), UserCategoryRule, user_id)
        .order_by(UserCategoryRule.updated_at.desc())
        .all()
    )


def upsert_category_rule(
    db: Session,
    user_id: Optional[str],
    match_token: str,
    category: str,
    txn_type: str = "expense",
    category_id: Optional[int] = None,
) -> UserCategoryRule:
    """Создаёт или обновляет правило по ключу `(user_id, normalized_token, type)`.

    Токен нормализуется перед записью, поэтому UNIQUE-ограничение реально дедуплицирует
    правила одного мерчанта вне зависимости от регистра/пробелов.
    """
    token = normalize_match_key(match_token)
    rule = _owner_filter(
        db.query(UserCategoryRule), UserCategoryRule, user_id
    ).filter(
        UserCategoryRule.match_token == token,
        UserCategoryRule.type == txn_type,
    ).first()
    if rule is not None:
        rule.category = category
        rule.category_id = category_id
        rule.updated_at = datetime.utcnow()
    else:
        rule = UserCategoryRule(
            user_id=user_id,
            match_token=token,
            type=txn_type,
            category=category,
            category_id=category_id,
        )
        db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def set_transaction_category(
    db: Session,
    transaction_id: int,
    category: str,
    user_id: Optional[str] = None,
    category_id: Optional[int] = None,
) -> Optional[Transaction]:
    """Переназначает категорию конкретной операции (с проверкой владельца). None — если не найдена."""
    transaction = _owner_filter(
        db.query(Transaction), Transaction, user_id
    ).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False,  # noqa: E712
    ).first()
    if transaction is None:
        return None
    transaction.category = category
    transaction.category_id = (
        category_id
        if category_id is not None
        else category_id_for(db, category, transaction.type)
    )
    db.commit()
    db.refresh(transaction)
    return transaction


def apply_category_rule(
    db: Session,
    user_id: Optional[str],
    match_token: str,
    category: str,
    txn_type: str = "expense",
    exclude_id: Optional[int] = None,
) -> int:
    """Ретроактивно применяет правило ко всем совпадающим операциям пользователя.

    Совпадение — нормализованный токен содержится в нормализованном описании операции (тот же
    критерий, что в `classify_with_rules`). Подстроковый матч с нормализацией нельзя выразить
    переносимо в SQL, поэтому грузим операции пользователя одним запросом и фильтруем в Python —
    приемлемо даже для тысяч строк (один SELECT + батч UPDATE). Возвращает число изменённых.
    """
    token = normalize_match_key(match_token)
    if len(token) < MIN_MATCH_TOKEN_LEN:
        return 0
    transactions = _owner_filter(
        db.query(Transaction), Transaction, user_id
    ).filter(
        Transaction.is_deleted == False,  # noqa: E712
        Transaction.type == txn_type,
    ).all()
    changed = 0
    for transaction in transactions:
        if transaction.id == exclude_id:
            continue
        if token in normalize_match_key(transaction.description) and transaction.category != category:
            transaction.category = category
            if category_id_value := category_id_for(db, category, txn_type):
                transaction.category_id = category_id_value
            changed += 1
    if changed:
        db.commit()
    return changed


def category_id_for(db: Session, category: str, txn_type: str) -> Optional[int]:
    """id системной категории по имени+типу, если такая есть (для консистентности FK). Иначе None."""
    row = (
        db.query(Category.id)
        .filter(Category.name == category, Category.type == txn_type)
        .first()
    )
    return row.id if row is not None else None


def delete_category_rule(db: Session, rule_id: int, user_id: Optional[str] = None) -> bool:
    """Удаляет правило пользователя по id (с проверкой владельца). False — если не найдено."""
    rule = _owner_filter(
        db.query(UserCategoryRule), UserCategoryRule, user_id
    ).filter(UserCategoryRule.id == rule_id).first()
    if rule is None:
        return False
    db.delete(rule)
    db.commit()
    return True


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
    household_id: Optional[int] = None,
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
        household_id=household_id,
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
    household_id: Optional[int] = None,
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
        household_id=household_id,
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
    household_id: Optional[int] = None,
) -> LiquidAsset:
    asset = LiquidAsset(
        name=name, amount=to_money(amount), interest_rate=interest_rate, type=type,
        comment=comment, currency=currency, user_id=user_id, household_id=household_id,
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


# ── История планов (P2.6) ─────────────────────────────────────────────────
def create_plan_snapshot(
    db: Session,
    result: dict,
    user_id: Optional[str] = None,
    note: Optional[str] = None,
) -> PlanSnapshot:
    """Сохраняет снапшот результата _compute_plan в историю."""
    ind = result.get("indicators", {}) or {}
    top3 = result.get("top3", []) or []
    best = top3[0] if top3 else {}

    def _f(v) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    snap = PlanSnapshot(
        user_id=user_id,
        risk_profile=str(result.get("risk_profile", "")),
        rt=_f(ind.get("Rt")),
        lt=_f(ind.get("Lt")),
        dt=_f(ind.get("Dt")),
        blr=_f(ind.get("BLR")),
        best_name=str(best.get("name", "")),
        x_obligations=_f(best.get("x_obligations")),
        x_reserve=_f(best.get("x_reserve")),
        x_goals=_f(best.get("x_goals")),
        utility=_f(best.get("utility")),
        top3=top3 or None,
        note=(note or None),
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def get_plan_snapshots(
    db: Session, user_id: Optional[str] = None, limit: int = 50
) -> list[PlanSnapshot]:
    owner = PlanSnapshot.user_id == user_id if user_id else PlanSnapshot.user_id.is_(None)
    return (
        db.query(PlanSnapshot)
        .filter(owner, PlanSnapshot.is_deleted == False)  # noqa: E712
        .order_by(PlanSnapshot.created_at.desc(), PlanSnapshot.id.desc())
        .limit(limit)
        .all()
    )


def get_plan_snapshot(
    db: Session, snapshot_id: int, user_id: Optional[str] = None
) -> Optional[PlanSnapshot]:
    owner = PlanSnapshot.user_id == user_id if user_id else PlanSnapshot.user_id.is_(None)
    return (
        db.query(PlanSnapshot)
        .filter(
            PlanSnapshot.id == snapshot_id, owner, PlanSnapshot.is_deleted == False  # noqa: E712
        )
        .first()
    )


def soft_delete_plan_snapshot(
    db: Session, snapshot_id: int, user_id: Optional[str] = None
) -> bool:
    snap = get_plan_snapshot(db, snapshot_id, user_id)
    if snap is None:
        return False
    snap.is_deleted = True
    snap.deleted_at = datetime.utcnow()
    db.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════
# Household (P3.7) — совместный скоуп поверх персонального владения.
#
# Инвариант прав: owner — полный контроль (членство, удаление household, r/w
# общих данных); member — r/w общих данных; viewer — только чтение общих данных.
# Личные данные (household_id IS NULL) к ролям отношения не имеют — ими владелец
# распоряжается сам через обычный user_id-скоуп.
# ══════════════════════════════════════════════════════════════════════════

HOUSEHOLD_ROLES = ("owner", "member", "viewer")
_HOUSEHOLD_WRITE_ROLES = ("owner", "member")
_INVITE_TTL_HOURS = 24 * 7


def get_user_household_ids(db: Session, user_id: Optional[str]) -> list[int]:
    """Список household_id, где пользователь состоит. Пусто для гостя/без семей."""
    if user_id is None:
        return []
    rows = (
        db.query(HouseholdMembership.household_id)
        .filter(HouseholdMembership.user_id == user_id)
        .all()
    )
    return [r[0] for r in rows]


def get_membership(
    db: Session, household_id: int, user_id: Optional[str]
) -> Optional[HouseholdMembership]:
    if user_id is None:
        return None
    return (
        db.query(HouseholdMembership)
        .filter(
            HouseholdMembership.household_id == household_id,
            HouseholdMembership.user_id == user_id,
        )
        .first()
    )


def get_household_role(db: Session, household_id: int, user_id: Optional[str]) -> Optional[str]:
    membership = get_membership(db, household_id, user_id)
    return membership.role if membership is not None else None


def is_household_member(db: Session, household_id: int, user_id: Optional[str]) -> bool:
    return get_membership(db, household_id, user_id) is not None


def can_write_household(db: Session, household_id: int, user_id: Optional[str]) -> bool:
    """Право записи общих данных: член household с ролью owner/member (не viewer)."""
    role = get_household_role(db, household_id, user_id)
    return role in _HOUSEHOLD_WRITE_ROLES


def create_household(db: Session, user_id: str, name: str) -> Household:
    """Создаёт household и делает создателя его owner-членом (одной транзакцией)."""
    household = Household(name=name, owner_id=user_id)
    db.add(household)
    db.flush()  # нужен household.id для членства
    db.add(HouseholdMembership(household_id=household.id, user_id=user_id, role="owner"))
    db.commit()
    db.refresh(household)
    return household


def get_household(db: Session, household_id: int) -> Optional[Household]:
    return db.get(Household, household_id)


def get_user_households(db: Session, user_id: Optional[str]) -> list[Household]:
    if user_id is None:
        return []
    return (
        db.query(Household)
        .join(HouseholdMembership, HouseholdMembership.household_id == Household.id)
        .filter(HouseholdMembership.user_id == user_id)
        .order_by(Household.created_at.asc())
        .all()
    )


def household_member_count(db: Session, household_id: int) -> int:
    return (
        db.query(func.count(HouseholdMembership.id))
        .filter(HouseholdMembership.household_id == household_id)
        .scalar()
        or 0
    )


def get_household_members(db: Session, household_id: int) -> list[HouseholdMembership]:
    return (
        db.query(HouseholdMembership)
        .filter(HouseholdMembership.household_id == household_id)
        .order_by(HouseholdMembership.joined_at.asc())
        .all()
    )


def rename_household(db: Session, household_id: int, name: str) -> Optional[Household]:
    household = db.get(Household, household_id)
    if household is None:
        return None
    household.name = name
    db.commit()
    db.refresh(household)
    return household


# Доменные таблицы, в которых строки возвращаются авторам при роспуске household.
_HOUSEHOLD_SCOPED_MODELS = (
    Transaction,
    Obligation,
    Goal,
    Budget,
    Scenario,
    LiquidAsset,
    PlanSnapshot,
)


def delete_household(db: Session, household_id: int) -> bool:
    """Распускает household. Общие строки возвращаются авторам (household_id → NULL),
    членства и приглашения удаляются. Данные не теряются и не повисают обезличенными
    (152-ФЗ). Обнуление household_id делается явно — не полагаемся на FK ON DELETE
    SET NULL, т.к. на SQLite enforcement FK по умолчанию выключен.
    """
    household = db.get(Household, household_id)
    if household is None:
        return False
    for model in _HOUSEHOLD_SCOPED_MODELS:
        db.query(model).filter(model.household_id == household_id).update(
            {model.household_id: None}, synchronize_session=False
        )
    db.query(HouseholdInvite).filter(
        HouseholdInvite.household_id == household_id
    ).delete(synchronize_session=False)
    db.query(HouseholdMembership).filter(
        HouseholdMembership.household_id == household_id
    ).delete(synchronize_session=False)
    db.delete(household)
    db.commit()
    return True


def remove_member(db: Session, household_id: int, user_id: str) -> bool:
    """Удаляет члена из household. Owner так удалить нельзя (только распуск household)."""
    membership = get_membership(db, household_id, user_id)
    if membership is None or membership.role == "owner":
        return False
    db.delete(membership)
    db.commit()
    return True


def leave_household(db: Session, household_id: int, user_id: str) -> bool:
    """Выход члена из household. Owner выйти не может (нужно распустить household
    или передать владение — передача вне первой фазы)."""
    return remove_member(db, household_id, user_id)


def create_invite(
    db: Session,
    household_id: int,
    created_by: str,
    role: str = "member",
    email: Optional[str] = None,
    ttl_hours: int = _INVITE_TTL_HOURS,
) -> HouseholdInvite:
    invite = HouseholdInvite(
        household_id=household_id,
        token=secrets.token_urlsafe(32),
        email=email,
        role=role,
        status="pending",
        created_by=created_by,
        expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def get_household_invites(
    db: Session, household_id: int, pending_only: bool = False
) -> list[HouseholdInvite]:
    query = db.query(HouseholdInvite).filter(HouseholdInvite.household_id == household_id)
    if pending_only:
        query = query.filter(HouseholdInvite.status == "pending")
    return query.order_by(HouseholdInvite.created_at.desc()).all()


def get_invite_by_id(db: Session, invite_id: int) -> Optional[HouseholdInvite]:
    return db.get(HouseholdInvite, invite_id)


def get_invite_by_token(db: Session, token: str) -> Optional[HouseholdInvite]:
    return (
        db.query(HouseholdInvite).filter(HouseholdInvite.token == token).first()
    )


def revoke_invite(db: Session, invite_id: int) -> Optional[HouseholdInvite]:
    invite = db.get(HouseholdInvite, invite_id)
    if invite is None:
        return None
    invite.status = "revoked"
    db.commit()
    db.refresh(invite)
    return invite


def accept_invite(
    db: Session, token: str, user_id: str
) -> tuple[Optional[HouseholdMembership], Optional[str]]:
    """Принимает приглашение. Возвращает (membership, None) при успехе либо
    (None, code) с кодом причины отказа: 'invalid' | 'expired'.

    Идемпотентно для уже состоящего пользователя: помечает приглашение принятым и
    возвращает существующее членство (без дублей — спасает UNIQUE).
    """
    invite = get_invite_by_token(db, token)
    if invite is None or invite.status != "pending":
        return None, "invalid"
    if invite.expires_at < datetime.utcnow():
        invite.status = "expired"
        db.commit()
        return None, "expired"

    existing = get_membership(db, invite.household_id, user_id)
    if existing is not None:
        invite.status = "accepted"
        invite.accepted_by = user_id
        invite.accepted_at = datetime.utcnow()
        db.commit()
        return existing, None

    membership = HouseholdMembership(
        household_id=invite.household_id, user_id=user_id, role=invite.role
    )
    db.add(membership)
    invite.status = "accepted"
    invite.accepted_by = user_id
    invite.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(membership)
    return membership, None
