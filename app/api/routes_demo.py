"""
Демо-данные FINPILOT — шесть типовых пользовательских профилей из ВКР.

Кейсы соответствуют портретам:
  1. Анна (Москва, маркетолог) — пограничный, оптимизация долга
  2. Дмитрий (СПб, IT senior) — здоровый, акцент на цели
  3. Михаил (Казань, мастерская) — критический, структурный диагноз
  4. Игорь (НН, junior) — старт карьеры, без долгов
  5. Ольга (Тула, библиотекарь) — микс-стратегия
  6. Виктор (ЕКБ, инженер) — пред-пенсионный, ликвидная позиция

Категории целей (форм. 9 ВКР):
  income_growth — рост дохода (w=3.0)
  safety        — безопасность     (w=2.0)
  material      — материальная цель (w=1.0)
  emotional     — эмоциональная цель (w=0.5)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.models import Goal, LiquidAsset, Obligation, Transaction
from app.dependencies import get_current_user_id, get_db

router = APIRouter(tags=["Демо-данные"])


def _clear_all(db: Session, user_id: str | None = None) -> None:
    """Очистка данных пользователя. user_id=None → строки анонимного режима."""
    for model in (Transaction, Obligation, Goal, LiquidAsset):
        stmt = delete(model)
        if user_id is not None:
            stmt = stmt.where(model.user_id == user_id)
        else:
            stmt = stmt.where(model.user_id.is_(None))
        db.execute(stmt)


def _make_income(amount: float, category: str, days_ago: int = 7) -> Transaction:
    return Transaction(
        amount=amount, category=category, type="income",
        date=datetime.utcnow() - timedelta(days=days_ago),
    )


def _make_expense(amount: float, category: str, days_ago: int = 7) -> Transaction:
    return Transaction(
        amount=amount, category=category, type="expense",
        date=datetime.utcnow() - timedelta(days=days_ago),
    )


# ─── Шесть кейсов ─────────────────────────────────────────────────────────

def case_anna() -> dict[str, list[Any]]:
    """Кейс 1 · Анна Петрова, 36, маркетолог, Москва (пограничный)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(180000, "Заработная плата (маркетолог)", 14),
            _make_expense(34000, "Продукты", 12),
            _make_expense(11000, "Транспорт", 10),
            _make_expense(9500, "ЖКХ", 8),
            _make_expense(2500, "Связь", 6),
            _make_expense(13000, "Развлечения и досуг", 4),
            _make_expense(8000, "Одежда", 2),
        ],
        "obligations": [
            Obligation(name="Ипотека · Сбер", amount=3070000, interest_rate=0.085,
                       term=96, monthly_payment=32000, payment_day=10,
                       comment="Покупка квартиры 8 лет назад"),
            Obligation(name="Автокредит · ВТБ", amount=518000, interest_rate=0.129,
                       term=28, monthly_payment=18500, payment_day=15,
                       comment="Семейный автомобиль"),
            Obligation(name="Курсы дочери · Тинькофф", amount=120000, interest_rate=0.0,
                       term=10, monthly_payment=12000, payment_day=20,
                       comment="Подготовка к ОГЭ, рассрочка 0%"),
        ],
        "goals": [
            Goal(name="Отпуск в Турцию", target_amount=180000, current_amount=35000,
                 deadline=now + timedelta(days=270), category="emotional"),
            Goal(name="Подушка безопасности", target_amount=468000, current_amount=80000,
                 deadline=now + timedelta(days=600), category="safety"),
            Goal(name="Взнос на квартиру дочери", target_amount=1200000, current_amount=150000,
                 deadline=now + timedelta(days=1080), category="material"),
        ],
        "liquid_assets": [],
    }


def case_dmitriy() -> dict[str, list[Any]]:
    """Кейс 2 · Дмитрий Соколов, 28, IT-разработчик, СПб (здоровый)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(230000, "Заработная плата (senior backend)", 14),
            _make_income(50000, "Фриланс (зарубежные проекты)", 7),
            _make_expense(40000, "Продукты и доставка", 12),
            _make_expense(12000, "IT-подписки и коворкинг", 10),
            _make_expense(15000, "Развлечения и досуг", 8),
            _make_expense(13000, "ЖКХ и связь", 6),
            _make_expense(15000, "Спорт и здоровье", 4),
        ],
        "obligations": [
            Obligation(name="Льготная IT-ипотека · Сбер", amount=10800000, interest_rate=0.055,
                       term=240, monthly_payment=45000, payment_day=10,
                       comment="Студия на Васильевском острове"),
        ],
        "goals": [
            Goal(name="Подушка безопасности", target_amount=285000, current_amount=120000,
                 deadline=now + timedelta(days=240), category="safety"),
            Goal(name="Машина", target_amount=1200000, current_amount=350000,
                 deadline=now + timedelta(days=395), category="material"),
            Goal(name="Инвест-квартира — взнос", target_amount=3500000, current_amount=800000,
                 deadline=now + timedelta(days=820), category="material"),
        ],
        "liquid_assets": [],
    }


def case_mikhail() -> dict[str, list[Any]]:
    """Кейс 3 · Михаил Кузнецов, 45, владелец мастерской, Казань (критический)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(150000, "Доход от мастерской", 14),
            _make_expense(30000, "Продукты и быт", 12),
            _make_expense(10000, "Лекарства для матери", 10),
            _make_expense(15000, "Школа дочери, занятия", 8),
            _make_expense(12000, "ЖКХ и связь", 6),
            _make_expense(13000, "Транспорт", 4),
        ],
        "obligations": [
            Obligation(name="Оборудование · Альфа", amount=504000, interest_rate=0.185,
                       term=18, monthly_payment=28000, payment_day=5,
                       comment="Деревообрабатывающий станок"),
            Obligation(name="Бизнес-кредит · Сбер", amount=528000, interest_rate=0.165,
                       term=24, monthly_payment=22000, payment_day=10,
                       comment="Кассовый разрыв, оборотные средства"),
            Obligation(name="Автокредит · Тинькофф", amount=540000, interest_rate=0.149,
                       term=36, monthly_payment=15000, payment_day=15,
                       comment="Служебная машина для развоза"),
            Obligation(name="Рассрочка · ВТБ", amount=48000, interest_rate=0.0,
                       term=6, monthly_payment=8000, payment_day=20,
                       comment="Ноутбук для учёта, рассрочка 0%"),
        ],
        "goals": [
            Goal(name="Резерв на налоги", target_amount=180000, current_amount=20000,
                 deadline=now + timedelta(days=120), category="safety"),
            Goal(name="Расширение производства", target_amount=950000, current_amount=100000,
                 deadline=now + timedelta(days=400), category="income_growth"),
        ],
        "liquid_assets": [],
    }


def case_igor() -> dict[str, list[Any]]:
    """Кейс 4 · Игорь Лебедев, 25, junior backend, Нижний Новгород (старт)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(95000, "Заработная плата (junior backend)", 14),
            _make_expense(20000, "Аренда комнаты", 12),
            _make_expense(15000, "Продукты", 10),
            _make_expense(6000, "Транспорт и связь", 8),
            _make_expense(8000, "IT-подписки и курсы", 6),
            _make_expense(6000, "Досуг", 4),
        ],
        "obligations": [],
        "goals": [
            Goal(name="Подушка безопасности", target_amount=165000, current_amount=15000,
                 deadline=now + timedelta(days=240), category="safety"),
            Goal(name="Курсы повышения квалификации", target_amount=80000, current_amount=0,
                 deadline=now + timedelta(days=120), category="income_growth"),
            Goal(name="Взнос на ипотеку (студия)", target_amount=1000000, current_amount=0,
                 deadline=now + timedelta(days=820), category="material"),
        ],
        "liquid_assets": [],
    }


def case_olga() -> dict[str, list[Any]]:
    """Кейс 5 · Ольга Морозова, 38, библиотекарь, мать-одиночка, Тула (микс)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(75000, "Заработная плата (библиотекарь)", 14),
            _make_income(12000, "Алименты", 10),
            _make_expense(25000, "Аренда квартиры", 12),
            _make_expense(18000, "Продукты", 10),
            _make_expense(5000, "Школа и кружок дочери", 8),
            _make_expense(6000, "Транспорт и связь", 6),
            _make_expense(4000, "Быт и одежда", 4),
        ],
        "obligations": [
            Obligation(name="Кредит наличными · Совкомбанк", amount=300000, interest_rate=0.199,
                       term=24, monthly_payment=12500, payment_day=15,
                       comment="Закрытие совместных долгов после развода"),
        ],
        "goals": [
            Goal(name="Подушка безопасности", target_amount=174000, current_amount=35000,
                 deadline=now + timedelta(days=240), category="safety"),
            Goal(name="Курсы Python (переход в IT)", target_amount=95000, current_amount=5000,
                 deadline=now + timedelta(days=30), category="income_growth"),
            Goal(name="Поездка к морю с дочерью", target_amount=80000, current_amount=0,
                 deadline=now + timedelta(days=60), category="emotional"),
        ],
        "liquid_assets": [],
    }


def case_viktor() -> dict[str, list[Any]]:
    """Кейс 6 · Виктор Соловьёв, 58, главный инженер, Екатеринбург (пред-пенсионный)."""
    now = datetime.utcnow()
    return {
        "transactions": [
            _make_income(145000, "Заработная плата + надбавки", 14),
            _make_expense(15000, "Продукты", 12),
            _make_expense(8000, "ЖКХ", 10),
            _make_expense(10000, "Лекарства жене", 8),
            _make_expense(10000, "Помощь дочери и внуку", 6),
            _make_expense(8000, "Транспорт и дача", 4),
            _make_expense(14000, "Связь, быт, прочее", 2),
        ],
        "obligations": [],
        "goals": [
            Goal(name="Внуку Мише на образование", target_amount=600000, current_amount=120000,
                 deadline=now + timedelta(days=1550), category="material"),
            Goal(name="Капремонт квартиры", target_amount=350000, current_amount=200000,
                 deadline=now + timedelta(days=70), category="material"),
            Goal(name="Поездка с женой в Сочи", target_amount=120000, current_amount=0,
                 deadline=now + timedelta(days=60), category="emotional"),
            Goal(name="Резерв на лечение", target_amount=300000, current_amount=150000,
                 deadline=now + timedelta(days=600), category="safety"),
        ],
        "liquid_assets": [
            LiquidAsset(name="Депозит (накопления за 8 лет)", amount=850000,
                        interest_rate=0.145, type="deposit",
                        comment="Накоплено после закрытия всех ипотек"),
        ],
    }


CASES = {
    "anna":     case_anna,
    "dmitriy":  case_dmitriy,
    "mikhail":  case_mikhail,
    "igor":     case_igor,
    "olga":     case_olga,
    "viktor":   case_viktor,
}


@router.post("/demo/load", summary="Загрузить демо-данные")
def load_demo(
    case: str = "anna",
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, str]:
    """
    Загружает один из шести кейсов из портретов.
    Параметр case: anna | dmitriy | mikhail | igor | olga | viktor
    Доступно только в гостевом режиме — тестовая песочница не смешивается с данными
    реального аккаунта.
    """
    if user_id is not None:
        raise HTTPException(
            status_code=403,
            detail="Демо-портреты доступны только в гостевом режиме (без входа в аккаунт).",
        )
    if case not in CASES:
        raise HTTPException(status_code=400, detail=f"Неизвестный кейс: {case}. Доступно: {list(CASES.keys())}")

    _clear_all(db, user_id=user_id)
    data = CASES[case]()
    now = datetime.utcnow()
    # Для наглядности прогресса выплат: если дата взятия не задана, считаем, что
    # term в демо задан как остаток; превращаем в ОБЩИЙ срок кредита и ставим
    # реалистичную дату взятия. «Осталось» дальше считается динамически от даты.
    for ob in data.get("obligations", []):
        if getattr(ob, "start_date", None) is None and (ob.term or 0) > 0:
            remaining = int(ob.term)
            seed = (int(ob.payment_day or 5)) % 6
            elapsed_months = max(1, int(remaining * (1.4 + seed * 0.18)))
            ob.start_date = now - timedelta(days=30 * elapsed_months)
            ob.term = remaining + elapsed_months
    for items in data.values():
        for item in items:
            item.user_id = user_id  # привязка демо-данных к текущему пользователю
        db.add_all(items)
    db.commit()
    return {"detail": f"Загружен кейс «{case}»."}


@router.get("/demo/preview", summary="Детальный портрет кейса без загрузки в БД")
def preview_demo(case: str = "anna") -> dict[str, Any]:
    """Возвращает финансовый портрет кейса (доходы, расходы, обязательства, цели,
    накопления) и базовые метрики — без записи в БД. Для раздела «Валидация»."""
    if case not in CASES:
        raise HTTPException(status_code=400, detail=f"Неизвестный кейс: {case}.")
    data = CASES[case]()
    now = datetime.utcnow()

    incomes = [t for t in data["transactions"] if t.type == "income"]
    expenses = [t for t in data["transactions"] if t.type == "expense"]
    income_total = sum(float(t.amount) for t in incomes)
    expense_total = sum(float(t.amount) for t in expenses)
    payments_total = sum(float(o.monthly_payment) for o in data["obligations"])
    cf = income_total - expense_total
    rt = cf - payments_total

    def months_left(deadline: datetime) -> int:
        return max(0, (deadline.year - now.year) * 12 + (deadline.month - now.month))

    return {
        "income": {
            "total": income_total,
            "items": [{"category": t.category, "amount": float(t.amount)} for t in incomes],
        },
        "expenses": {
            "total": expense_total,
            "items": [{"category": t.category, "amount": float(t.amount)} for t in expenses],
        },
        "obligations": [
            {
                "name": o.name,
                "monthly_payment": float(o.monthly_payment),
                "interest_rate": float(o.interest_rate),
                "term": o.term,
                "amount": float(o.amount),
                "comment": o.comment,
            }
            for o in data["obligations"]
        ],
        "goals": [
            {
                "name": g.name,
                "target_amount": float(g.target_amount),
                "current_amount": float(g.current_amount),
                "category": g.category,
                "months_left": months_left(g.deadline),
            }
            for g in data["goals"]
        ],
        "liquid_assets": [
            {"name": a.name, "amount": float(a.amount), "interest_rate": float(a.interest_rate or 0)}
            for a in data["liquid_assets"]
        ],
        "metrics": {
            "income_total": income_total,
            "expense_total": expense_total,
            "payments_total": payments_total,
            "cash_flow": cf,
            "free_resource": rt,
        },
    }


@router.post("/demo/clear", summary="Очистить все данные")
def clear_demo(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, str]:
    _clear_all(db, user_id=user_id)
    db.commit()
    return {"detail": "Все данные удалены."}


@router.get("/demo/cases", summary="Список доступных демо-кейсов")
def list_cases() -> dict[str, list[str]]:
    return {"cases": list(CASES.keys())}
