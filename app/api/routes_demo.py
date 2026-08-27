"""
Демо-данные FINPILOT — десять типовых пользовательских профилей (эталонные портреты).

Кейсы покрывают все основные функции и разные формы прогноза:
  1. Анна (Москва, маркетолог) — пограничный, оптимизация долга (Avalanche)
  2. Дмитрий (СПб, IT senior) — здоровый, акцент на цели, растущий доход
  3. Михаил (Казань, мастерская) — критический, структурный диагноз, падающий доход
  4. Игорь (НН, junior) — старт карьеры, без долгов
  5. Ольга (Тула, библиотекарь) — микс-стратегия
  6. Виктор (ЕКБ, инженер) — пред-пенсионный, ликвидная позиция
  7. Екатерина (Сочи, фрилансер) — волатильный доход, широкий коридор прогноза
  8. Артём (Москва, тимлид) — агрессивный профиль, Avalanche на 3 ставках, инвестиции
  9. Наталья (Самара, пенсия) — крупная ликвидность, разовое закрытие близких целей
 10. Павел (Тюмень, прораб) — сезонный доход, перегруз ПДН, кризис-модуль

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
from pydantic import BaseModel, Field
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.models import Goal, LiquidAsset, Obligation, Transaction
from app.dependencies import get_current_user_id, get_db
from app.services.cbr_rate import get_opportunity_cost_rate
from app.services.forecasting import build_monthly_history, forecast_indicators
from app.services.planning import run_planning
from app.utils.time import utcnow

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
        date=utcnow() - timedelta(days=days_ago),
    )


def _make_expense(amount: float, category: str, days_ago: int = 7) -> Transaction:
    return Transaction(
        amount=amount, category=category, type="expense",
        date=utcnow() - timedelta(days=days_ago),
    )


# ─── Шесть кейсов ─────────────────────────────────────────────────────────

def case_anna() -> dict[str, list[Any]]:
    """Кейс 1 · Анна Петрова, 36, маркетолог, Москва (пограничный)."""
    now = utcnow()
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
    now = utcnow()
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
    now = utcnow()
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
    now = utcnow()
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
    now = utcnow()
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
    now = utcnow()
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


def case_ekaterina() -> dict[str, list[Any]]:
    """Кейс 7 · Екатерина Волкова, 32, фрилансер-дизайнер, Сочи (волатильный доход)."""
    now = utcnow()
    return {
        "transactions": [
            _make_income(140000, "Проект (студия, разовый)", 12),
            _make_income(45000, "Маркетплейс шаблонов (роялти)", 8),
            _make_income(30000, "Консультации", 5),
            _make_expense(28000, "Аренда студии-квартиры", 12),
            _make_expense(22000, "Продукты и кафе", 10),
            _make_expense(9000, "Софт и подписки (Adobe, Figma)", 9),
            _make_expense(7000, "Транспорт и связь", 6),
            _make_expense(6000, "Здоровье и спорт", 4),
            _make_expense(8000, "Материалы и оборудование", 2),
        ],
        "obligations": [
            Obligation(name="Рассрочка на технику · Тинькофф", amount=180000, interest_rate=0.0,
                       term=12, monthly_payment=15000, payment_day=12,
                       comment="MacBook Pro + монитор для работы, рассрочка 0%"),
            Obligation(name="Кредитка · Альфа", amount=90000, interest_rate=0.249,
                       term=0, monthly_payment=9000, payment_day=25,
                       comment="Кассовый разрыв между проектами"),
        ],
        "goals": [
            Goal(name="Финансовая подушка (нерегулярный доход)", target_amount=420000,
                 current_amount=90000, deadline=now + timedelta(days=365), category="safety"),
            Goal(name="Обучение 3D/motion (рост дохода)",
                 target_amount=150000, current_amount=20000,
                 deadline=now + timedelta(days=180), category="income_growth"),
            Goal(name="Своя студия (аренда+ремонт)", target_amount=800000, current_amount=110000,
                 deadline=now + timedelta(days=900), category="material"),
            Goal(name="Путешествие в Японию", target_amount=350000, current_amount=40000,
                 deadline=now + timedelta(days=500), category="emotional"),
        ],
        "liquid_assets": [
            LiquidAsset(name="Накопительный счёт", amount=140000, interest_rate=0.16,
                        type="savings", comment="Буфер на месяцы без проектов"),
        ],
    }


def case_artyom() -> dict[str, list[Any]]:
    """Кейс 8 · Артём Новиков, 34, тимлид в финтехе, Москва (агрессивный, Avalanche)."""
    now = utcnow()
    return {
        "transactions": [
            _make_income(420000, "Заработная плата (team lead)", 13),
            _make_income(120000, "Годовой бонус (амортизация/мес)", 11),
            _make_income(35000, "Дивиденды и купоны", 6),
            _make_expense(70000, "Продукты, рестораны, доставка", 12),
            _make_expense(35000, "Аренда паркинга и авто", 10),
            _make_expense(25000, "Путешествия (фонд)", 8),
            _make_expense(20000, "Спорт, здоровье, велнес", 6),
            _make_expense(18000, "Подписки, гаджеты, обучение", 4),
            _make_expense(15000, "ЖКХ и связь", 2),
        ],
        "obligations": [
            Obligation(name="Кредитка премиум · Тинькофф", amount=380000, interest_rate=0.279,
                       term=0, monthly_payment=25000, payment_day=20,
                       comment="Самый дорогой долг — приоритет Avalanche"),
            Obligation(name="Автокредит · Райффайзен", amount=1450000, interest_rate=0.155,
                       term=48, monthly_payment=38000, payment_day=15,
                       comment="Премиальный кроссовер"),
            Obligation(name="Ипотека · Сбер", amount=14500000, interest_rate=0.078,
                       term=300, monthly_payment=110000, payment_day=10,
                       comment="Дешёвый долг — гасить досрочно невыгодно"),
        ],
        "goals": [
            Goal(name="Инвестпортфель (ИИС + брокер)",
                 target_amount=5000000, current_amount=1200000,
                 deadline=now + timedelta(days=1460), category="income_growth"),
            Goal(name="Резерв 6 месяцев", target_amount=1200000, current_amount=900000,
                 deadline=now + timedelta(days=180), category="safety"),
            Goal(name="Дом за городом — взнос", target_amount=6000000, current_amount=1500000,
                 deadline=now + timedelta(days=1800), category="material"),
        ],
        "liquid_assets": [
            LiquidAsset(name="Брокерский счёт (ликвидная часть)", amount=650000, interest_rate=0.19,
                        type="brokerage", comment="Фонды денежного рынка"),
            LiquidAsset(name="Накопительный счёт", amount=550000, interest_rate=0.17,
                        type="savings", comment="Часть подушки"),
        ],
    }


def case_natalya() -> dict[str, list[Any]]:
    """Кейс 9 · Наталья Морозова, 61, на пенсии + подработка, Самара (ликвидная, lump-sum)."""
    now = utcnow()
    return {
        "transactions": [
            _make_income(28000, "Пенсия", 14),
            _make_income(40000, "Подработка (репетитор)", 9),
            _make_expense(16000, "Продукты", 12),
            _make_expense(7000, "ЖКХ", 10),
            _make_expense(9000, "Лекарства и врачи", 8),
            _make_expense(5000, "Связь, интернет, ТВ", 6),
            _make_expense(6000, "Внуки, подарки, помощь", 3),
        ],
        "obligations": [],
        "goals": [
            Goal(name="Ремонт кухни (близкий срок)", target_amount=280000, current_amount=60000,
                 deadline=now + timedelta(days=45), category="material"),
            Goal(name="Лечение зубов (близкий срок)", target_amount=180000, current_amount=30000,
                 deadline=now + timedelta(days=30), category="safety"),
            Goal(name="Поездка к морю с внуками", target_amount=150000, current_amount=20000,
                 deadline=now + timedelta(days=210), category="emotional"),
            # Бессрочная цель: срока нет — копится фоном (deadline = None).
            Goal(name="Наследство внукам (бессрочно)",
                 target_amount=1000000, current_amount=400000,
                 deadline=None, category="material"),
        ],
        "liquid_assets": [
            LiquidAsset(name="Вклад в Сбере", amount=1250000, interest_rate=0.185,
                        type="deposit", comment="Основные накопления за жизнь"),
            LiquidAsset(name="Накопительный счёт", amount=320000, interest_rate=0.16,
                        type="savings", comment="Текущий резерв"),
        ],
    }


def case_pavel() -> dict[str, list[Any]]:
    """Кейс 10 · Павел Зайцев, 39, прораб (сезонный доход), Тюмень (перегруз, кризис-модуль)."""
    now = utcnow()
    return {
        "transactions": [
            _make_income(90000, "Зарплата межсезонье (зима)", 13),
            _make_expense(32000, "Продукты и быт (семья 4 чел.)", 12),
            _make_expense(14000, "ЖКХ (частный дом, зима)", 10),
            _make_expense(11000, "Транспорт и топливо", 8),
            _make_expense(9000, "Школа и секции детей", 6),
            _make_expense(7000, "Связь, интернет", 4),
            _make_expense(6000, "Одежда, обувь детям", 2),
        ],
        "obligations": [
            Obligation(name="Потребкредит · Совкомбанк", amount=680000, interest_rate=0.229,
                       term=36, monthly_payment=26000, payment_day=10,
                       comment="Ремонт дома, взят на пике сезона"),
            Obligation(name="Автокредит (рабочий пикап) · ВТБ", amount=890000, interest_rate=0.169,
                       term=48, monthly_payment=27000, payment_day=15,
                       comment="Нужен для работы круглый год"),
            Obligation(name="Кредитка · Тинькофф", amount=210000, interest_rate=0.299,
                       term=0, monthly_payment=12000, payment_day=22,
                       comment="Перекрытие зимнего разрыва"),
            Obligation(name="Микрозайм · онлайн", amount=45000, interest_rate=0.365,
                       term=6, monthly_payment=9000, payment_day=28,
                       comment="Худший долг — гасить первым"),
        ],
        "goals": [
            Goal(name="Резерв на межсезонье", target_amount=300000, current_amount=15000,
                 deadline=now + timedelta(days=150), category="safety"),
            Goal(name="Инструмент и бригада (рост дохода)",
                 target_amount=500000, current_amount=30000,
                 deadline=now + timedelta(days=400), category="income_growth"),
        ],
        "liquid_assets": [],
    }


CASES = {
    "anna":       case_anna,
    "dmitriy":    case_dmitriy,
    "mikhail":    case_mikhail,
    "igor":       case_igor,
    "olga":       case_olga,
    "viktor":     case_viktor,
    "ekaterina":  case_ekaterina,
    "artyom":     case_artyom,
    "natalya":    case_natalya,
    "pavel":      case_pavel,
}


# Форма динамики дохода/расхода по типу портрета — задаёт наклон/волну прогноза.
CASE_PATTERN: dict[str, str] = {
    "anna": "stable", "dmitriy": "rise", "mikhail": "fall", "igor": "rise",
    "olga": "stable", "viktor": "stable", "ekaterina": "volatile", "artyom": "rise",
    "natalya": "fall", "pavel": "season",
}


def _pattern_factor(pattern: str, k: int) -> tuple[float, float]:
    """Множители (доход, расход) для месяца k назад (1 = месяц назад, больше = старее)
    относительно ТЕКУЩЕГО месяца. rise: раньше было меньше; fall: раньше больше;
    volatile: пилит; season: волна; stable: почти ровно."""
    import math
    if pattern == "rise":
        return max(1 - 0.045 * k, 0.4), max(1 - 0.02 * k, 0.6)
    if pattern == "fall":
        return 1 + 0.05 * k, max(1 - 0.01 * k, 0.85)
    if pattern == "volatile":
        return max(1 + 0.24 * math.sin(k * 1.7), 0.4), 1 + 0.05 * math.sin(k * 1.1)
    if pattern == "season":
        wave = math.sin(k * 1.05 - 0.5) * 0.5 + 0.5   # 0..1
        return 0.70 + 0.55 * wave, 0.92 + 0.12 * wave
    return 0.98 + 0.04 * (k % 2), 0.98 + 0.03 * (k % 2)  # stable


def _history_transactions(cur_income: float, cur_expense: float, pattern: str,
                          months: int = 7) -> list[Transaction]:
    """Реальные транзакции за прошлые `months` месяцев (по одной income+expense на
    месяц), датированные так, что каждый месяц попадает в свою 30-дневную корзину и
    ИСКЛЮЧАЕТСЯ из окна текущего месяца (30 дней). Дают прогнозу настоящий тренд."""
    out: list[Transaction] = []
    for k in range(1, months + 1):
        fi, fe = _pattern_factor(pattern, k)
        days = 30 * k + 8  # k=1 → 38 дн (bin 1), вне окна текущего месяца
        out.append(_make_income(round(cur_income * max(fi, 0.05)),
                                "Доход за прошлый месяц", days))
        out.append(_make_expense(round(cur_expense * max(fe, 0.05)),
                                 "Расходы за прошлый месяц", days))
    return out


def _case_data(case_key: str) -> dict[str, list[Any]]:
    """Данные кейса: текущий месяц (детальные операции) + сгенерированная многомесячная
    история транзакций. history_transactions хранятся отдельным ключом — они реальные
    записи БД, но НЕ входят в детальную разбивку текущего месяца."""
    data = CASES[case_key]()
    cur_income = sum(float(t.amount) for t in data["transactions"] if t.type == "income")
    cur_expense = sum(float(t.amount) for t in data["transactions"] if t.type == "expense")
    data["history_transactions"] = _history_transactions(
        cur_income, cur_expense, CASE_PATTERN.get(case_key, "stable"))
    return data


@router.post("/demo/load", summary="Загрузить демо-данные")
def load_demo(
    case: str = "anna",
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, str]:
    """
    Загружает один из десяти эталонных кейсов.
    Доступно только в гостевом режиме — тестовая песочница не смешивается с данными
    реального аккаунта.
    """
    if user_id is not None:
        raise HTTPException(
            status_code=403,
            detail="Демо-портреты доступны только в гостевом режиме (без входа в аккаунт).",
        )
    if case not in CASES:
        raise HTTPException(
            status_code=400, detail=f"Неизвестный кейс: {case}. Доступно: {list(CASES.keys())}")

    _clear_all(db, user_id=user_id)
    data = _case_data(case)
    now = utcnow()
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


def _months_left(deadline: datetime | None, now: datetime) -> int | None:
    if deadline is None:
        return None
    return max(0, (deadline.year - now.year) * 12 + (deadline.month - now.month))


def _obligation_dict(o: Any) -> dict[str, Any]:
    return {
        "name": getattr(o, "name", ""),
        "monthly_payment": float(getattr(o, "monthly_payment", 0) or 0),
        "interest_rate": float(getattr(o, "interest_rate", 0) or 0),
        "term": getattr(o, "term", 0),
        "amount": float(getattr(o, "amount", 0) or 0),
        "comment": getattr(o, "comment", None),
    }


def _goal_dict(g: Any) -> dict[str, Any]:
    return {
        "name": getattr(g, "name", ""),
        "target_amount": float(getattr(g, "target_amount", 0) or 0),
        "current_amount": float(getattr(g, "current_amount", 0) or 0),
        "category": getattr(g, "category", "material"),
        "deadline": getattr(g, "deadline", None),
    }


def _analyze_portrait(
    income_items: list[dict[str, Any]],
    expense_items: list[dict[str, Any]],
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    liquid_assets: list[dict[str, Any]],
    history: dict[str, list[float]] | None,
    risk_tolerance: int = 3,
    horizon: int = 6,
) -> dict[str, Any]:
    """Единый расчёт для раздела «Валидация»: метрики + рекомендация (run_planning) +
    прогноз (forecast_indicators). Используется и готовыми кейсами, и загруженным
    портретом. Прогноз строится по помесячной истории (history) — отсюда РАЗНАЯ форма
    графика у разных портретов, а не одинаковая прямая."""
    # run_planning адресует аллокации по id — эталонные объекты его не имеют, проставим.
    for i, g in enumerate(goals):
        if not g.get("id"):
            g["id"] = f"g{i + 1}"
    for i, o in enumerate(obligations):
        if not o.get("id"):
            o["id"] = f"o{i + 1}"

    income_total = sum(float(i["amount"]) for i in income_items)
    expense_total = sum(float(e["amount"]) for e in expense_items)
    payments_total = sum(float(o.get("monthly_payment", 0)) for o in obligations)
    bliq = sum(float(a.get("amount", 0)) for a in liquid_assets)
    # r_bench — канонная ставка (ключевая ЦБ × (1−НДФЛ), фолбэк 0.14), ТА ЖЕ, что в
    # /planning: витрина «Валидация» и реальный расчёт компаундят баланс одинаково.
    r_bench = float(get_opportunity_cost_rate(fallback=0.14)["r_bench"])
    balance = sum(float(g.get("current_amount", 0)) for g in goals)

    cf = income_total - expense_total
    rt = cf - payments_total
    lt = bliq / expense_total if expense_total > 0 else 0.0
    dt = payments_total / income_total if income_total > 0 else 0.0

    plan_summary: dict[str, Any] = {}
    try:
        plan = run_planning(
            income_total=income_total, expense_total=expense_total,
            obligations=obligations, goals=goals, bliq=bliq,
            r_bench=r_bench, risk_tolerance=risk_tolerance,
        )
        best = plan.get("best")
        plan_summary = {
            "indicators": plan.get("indicators", {}),
            "risk_profile": plan.get("risk_profile"),
            "best": {
                "explanation": (best or {}).get("explanation"),
                "obligation_allocation": (best or {}).get("obligation_allocation"),
                "reserve_allocation": (best or {}).get("reserve_allocation"),
                "goal_allocation": (best or {}).get("goal_allocation"),
            } if best else None,
            "closed_goals": plan.get("bliq_preallocation", {}).get("closed_goals", []),
            "crisis_plan": plan.get("crisis_plan"),
            "surplus_plan": plan.get("surplus_plan"),
            "admissible_count": plan.get("admissible_count"),
            "alternatives_total": plan.get("alternatives_total"),
        }
    except Exception as exc:  # portrait из загрузки может быть невалиден — не роняем страницу
        plan_summary = {"error": f"Не удалось построить план: {exc}"}

    inc_hist = (history or {}).get("income") or None
    exp_hist = (history or {}).get("expense") or None
    forecast = forecast_indicators(
        balance=balance, rt=rt, lt=lt, dt=dt,
        income_total=income_total, expense_total=expense_total,
        obligation_payments=payments_total, horizon=horizon,
        income_history=inc_hist, expense_history=exp_hist, r_bench=r_bench,
    )

    return {
        "metrics": {
            "income_total": income_total,
            "expense_total": expense_total,
            "payments_total": payments_total,
            "cash_flow": cf,
            "free_resource": rt,
            "Lt": round(lt, 2),
            "Dt": round(dt, 4),
            "bliq": bliq,
            "r_bench": round(r_bench, 4),
        },
        "plan": plan_summary,
        "forecast": forecast,
    }


@router.get("/demo/preview", summary="Портрет кейса + метрики + прогноз + рекомендация")
def preview_demo(case: str = "anna") -> dict[str, Any]:
    """Полный расчёт кейса без записи в БД: портрет, метрики, прогноз и рекомендация.
    Для раздела «Валидация» — визуальная проверка всех основных функций сразу."""
    if case not in CASES:
        raise HTTPException(status_code=400, detail=f"Неизвестный кейс: {case}.")
    data = _case_data(case)
    now = utcnow()

    incomes = [t for t in data["transactions"] if t.type == "income"]  # текущий месяц
    expenses = [t for t in data["transactions"] if t.type == "expense"]
    income_items = [{"category": t.category, "amount": float(t.amount)} for t in incomes]
    expense_items = [{"category": t.category, "amount": float(t.amount)} for t in expenses]
    obl_dicts = [_obligation_dict(o) for o in data["obligations"]]
    goal_dicts = [_goal_dict(g) for g in data["goals"]]
    liquid_dicts = [
        {"name": a.name, "amount": float(a.amount), "interest_rate": float(a.interest_rate or 0)}
        for a in data["liquid_assets"]
    ]

    # Прогнозная история — из РЕАЛЬНЫХ транзакций (текущий месяц + сгенерированная
    # многомесячная история), ровно как её увидит /planning после загрузки кейса.
    all_txs = data["transactions"] + data.get("history_transactions", [])
    history = build_monthly_history(all_txs)

    analysis = _analyze_portrait(
        income_items, expense_items, obl_dicts, goal_dicts, liquid_dicts,
        history=history,
    )

    return {
        "income": {"total": analysis["metrics"]["income_total"], "items": income_items},
        "expenses": {"total": analysis["metrics"]["expense_total"], "items": expense_items},
        "obligations": obl_dicts,
        "goals": [
            {**g, "months_left": _months_left(g.get("deadline"), now)} for g in goal_dicts
        ],
        "liquid_assets": liquid_dicts,
        "history": history,
        "metrics": analysis["metrics"],
        "plan": analysis["plan"],
        "forecast": analysis["forecast"],
    }


class _AnalyzeItem(BaseModel):
    category: str = "Прочее"
    amount: float = 0.0


class _AnalyzeObligation(BaseModel):
    name: str = "Обязательство"
    monthly_payment: float = 0.0
    interest_rate: float = 0.0
    amount: float = 0.0
    term: int = 0


class _AnalyzeGoal(BaseModel):
    name: str = "Цель"
    target_amount: float = 0.0
    current_amount: float = 0.0
    category: str = "material"
    months_left: int | None = None


class _AnalyzeAsset(BaseModel):
    name: str = "Актив"
    amount: float = 0.0
    interest_rate: float = 0.0


class AnalyzePortrait(BaseModel):
    """Произвольный портрет для проверки на странице «Валидация» (загрузка/вставка JSON)."""
    income: list[_AnalyzeItem] = Field(default_factory=list)
    expenses: list[_AnalyzeItem] = Field(default_factory=list)
    obligations: list[_AnalyzeObligation] = Field(default_factory=list)
    goals: list[_AnalyzeGoal] = Field(default_factory=list)
    liquid_assets: list[_AnalyzeAsset] = Field(default_factory=list)
    income_history: list[float] = Field(default_factory=list)
    expense_history: list[float] = Field(default_factory=list)
    risk_tolerance: int = Field(3, ge=1, le=5)


@router.post("/demo/analyze", summary="Проверить произвольный портрет (валидация)")
def analyze_demo(payload: AnalyzePortrait) -> dict[str, Any]:
    """Принимает произвольный портрет (JSON) и возвращает метрики, прогноз и
    рекомендацию — не записывая в БД. Позволяет валидировать алгоритм на своих данных.
    Дедлайны целей задаются как months_left; переводим в дату для preallocation."""
    now = utcnow()
    goals = []
    for g in payload.goals:
        deadline = now + timedelta(days=30 * g.months_left) if g.months_left is not None else None
        goals.append({
            "name": g.name, "target_amount": g.target_amount,
            "current_amount": g.current_amount, "category": g.category, "deadline": deadline,
        })
    history = {
        "income": payload.income_history,
        "expense": payload.expense_history,
    }
    return _analyze_portrait(
        income_items=[i.model_dump() for i in payload.income],
        expense_items=[e.model_dump() for e in payload.expenses],
        obligations=[o.model_dump() for o in payload.obligations],
        goals=goals,
        liquid_assets=[a.model_dump() for a in payload.liquid_assets],
        history=history,
        risk_tolerance=payload.risk_tolerance,
    )


@router.post("/demo/clear", summary="Очистить все данные")
def clear_demo(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, str]:
    _clear_all(db, user_id=user_id)
    db.commit()
    return {"detail": "Все данные удалены."}


CASE_META: dict[str, dict[str, str]] = {
    "anna": {"n": "1", "name": "Анна Петрова, 36", "role": "Маркетолог · Москва",
             "tag": "Пограничный", "accent": "amber",
             "situation": "Доход 180 000 ₽, ипотека+автокредит+рассрочка, несколько целей."
                          "Свободный поток положительный, но нагрузка ощутимая.",
             "expect": "Avalanche гасит дорогой долг, ликвидность держится ≥ нормы, остаток — на"
                       "цели по важности. Прогноз почти ровный (стабильная зарплата)."},
    "dmitriy": {"n": "2", "name": "Дмитрий, 41", "role": "Senior IT · Санкт-Петербург",
                "tag": "Здоровый бюджет", "accent": "green",
                "situation": "Высокий растущий доход (зарплата+фриланс), дешёвая IT-ипотека,"
                             "накопления.",
                "expect": "Акцент на цели и рост; дешёвый долг досрочно гасить невыгодно. Прогноз"
                          "уверенно растущий (доход в истории поднимается)."},
    "mikhail": {"n": "3", "name": "Михаил, 49", "role": "Своя мастерская · Казань",
                "tag": "Критический", "accent": "red",
                "situation": "Четыре кредита, расходы+платежи съедают почти весь доход, доход"
                             "падает.",
                "expect": "Fail-loud: вместо «красивой» рекомендации — структурный диагноз. Прогноз"
                          "снижается (падающая история дохода)."},
    "igor": {"n": "4", "name": "Игорь, 26", "role": "Junior-разработчик · Нижний Новгород",
             "tag": "Старт карьеры", "accent": "cyan",
             "situation": "Невысокий, но растущий доход, кредитов нет, накоплений почти нет.",
             "expect": "Приоритет — подушка (BLR ниже нормы), затем цели роста дохода. Прогноз"
                       "плавно растущий."},
    "olga": {"n": "5", "name": "Ольга, 44", "role": "Библиотекарь · Тула",
             "tag": "Микс-стратегия", "accent": "violet",
             "situation": "Умеренный доход (+алименты), один кредит, частичная подушка, близкие"
                          "цели.",
             "expect": "Сбалансированное распределение по всем трём направлениям, компромиссная"
                       "альтернатива."},
    "viktor": {"n": "6", "name": "Виктор, 58", "role": "Инженер · Екатеринбург",
               "tag": "Пред-пенсионный", "accent": "slate",
               "situation": "Стабильный доход, крупный депозит (850 000 ₽), близкие по сроку цели.",
               "expect": "Высокий вес ликвидности; разовое закрытие близких целей из накоплений"
                         "(Bliq). Прогноз растёт за счёт капитализации депозита."},
    "ekaterina": {"n": "7", "name": "Екатерина, 32", "role": "Фрилансер-дизайнер · Сочи",
                  "tag": "Волатильный доход", "accent": "amber",
                  "situation": "Нерегулярный доход (проекты+роялти+консультации), рассрочка 0% и"
                               "дорогая кредитка, 4 цели, буфер.",
                  "expect": "Упор на подушку под нерегулярный доход, Avalanche по кредитке. Прогноз"
                            "«пилит» — широкий коридор неопределённости."},
    "artyom": {"n": "8", "name": "Артём, 34", "role": "Тимлид в финтехе · Москва",
               "tag": "Агрессивный", "accent": "green",
               "situation": "Высокий растущий доход, три долга (кредитка 27.9% / авто 15.5% /"
                            "ипотека 7.8%), инвестиции, брокерский счёт.",
               "expect": "Avalanche чётко ранжирует 3 ставки, дешёвую ипотеку не трогает; профиль 5"
                         "— вес роста/инвестиций высокий. Прогноз круто растущий."},
    "natalya": {"n": "9", "name": "Наталья, 61", "role": "Пенсия + репетитор · Самара",
                "tag": "Ликвидная позиция", "accent": "slate",
                "situation": "Пенсия+подработка, без долгов, вклад 1.25 млн + счёт, две цели с"
                             "близким сроком, бессрочная цель.",
                "expect": "Разовое закрытие близких целей из вклада (Bliq), а не из потока. Прогноз"
                          "растёт за счёт капитализации крупного депозита."},
    "pavel": {"n": "10", "name": "Павел, 39", "role": "Прораб (сезон) · Тюмень",
              "tag": "Перегруз ПДН", "accent": "red",
              "situation": "Сезонный доход (зимой мало), четыре долга включая микрозайм 36.5%,"
                           "дефицит в межсезонье.",
              "expect": "Кризис-модуль: план на дефицит (пересмотр, реструктуризация, runway)."
                        "Прогноз сезонный — заметная волна."},
}


@router.get("/demo/cases", summary="Список демо-кейсов с метаданными")
def list_cases() -> dict[str, Any]:
    return {
        "cases": [{"key": k, **CASE_META.get(k, {})} for k in CASES],
        "keys": list(CASES.keys()),
    }
