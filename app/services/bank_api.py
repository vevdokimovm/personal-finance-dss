"""
Модуль интеграции с банковскими API.
Реализует архитектуру адаптеров для подключения к различным банкам.
В режиме разработки используются Mock-имплементации, имитирующие реальные API.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.database.crud import create_transaction


# ── Конфигурация банков ───────────────────────────────────────
BANKS = {
    "tinkoff": {
        "name": "Тинькофф Банк",
        "color": "#FFDD2D",
        "expenses": [
            ("Супермаркет Перекрёсток", 450, 3200),
            ("Яндекс.Такси", 150, 900),
            ("Яндекс.Плюс подписка", 299, 299),
            ("Кофейня Surf Coffee", 180, 520),
            ("Ozon заказ", 800, 6500),
            ("АЗС Лукойл", 1200, 3800),
        ],
        "incomes": [
            ("Зарплата", 45000, 120000),
            ("Кэшбэк Tinkoff", 50, 2500),
            ("Перевод от физ. лица", 1000, 15000),
        ],
    },
    "sber": {
        "name": "Сбербанк",
        "color": "#21A038",
        "expenses": [
            ("Пятёрочка", 300, 2800),
            ("РЖД билет", 1500, 5000),
            ("Аптека Озерки", 200, 1800),
            ("Магнит Косметик", 300, 2000),
            ("МТС связь", 500, 800),
        ],
        "incomes": [
            ("Зарплата (осн.)", 50000, 150000),
            ("Пенсия", 12000, 25000),
            ("Перевод СберОнлайн", 500, 10000),
        ],
    },
    "alfa": {
        "name": "Альфа-Банк",
        "color": "#EF3124",
        "expenses": [
            ("Delivery Club", 400, 2500),
            ("Steam покупка", 300, 4000),
            ("IKEA заказ", 2000, 15000),
            ("Спортмастер", 1500, 8000),
            ("Кинопоиск подписка", 269, 269),
        ],
        "incomes": [
            ("Зарплата Альфа", 60000, 180000),
            ("Кэшбэк Alfa", 100, 3000),
            ("Возврат товара", 500, 5000),
        ],
    },
    "vtb": {
        "name": "ВТБ",
        "color": "#009FDF",
        "expenses": [
            ("ЖКХ квартплата", 3000, 8000),
            ("Ростелеком интернет", 600, 1200),
            ("Wildberries", 500, 7000),
            ("Аренда парковки", 2000, 5000),
        ],
        "incomes": [
            ("Зарплата ВТБ", 40000, 100000),
            ("Дивиденды", 5000, 30000),
        ],
    },
    "raiffeisen": {
        "name": "Райффайзен Банк",
        "color": "#FEE600",
        "expenses": [
            ("Starbucks", 300, 800),
            ("Apple подписка", 299, 599),
            ("Аптека 36.6", 150, 1500),
            ("Lamoda заказ", 2000, 12000),
        ],
        "incomes": [
            ("Зарплата Raiff", 55000, 140000),
            ("Кэшбэк Raiffeisen", 80, 2000),
        ],
    },
}


def sync_bank(db: Session, bank_id: str) -> dict[str, Any]:
    """
    Синхронизация с конкретным банком.
    Имитирует OAuth → получение выписки → парсинг → сохранение.
    """
    if bank_id not in BANKS:
        return {"status": "error", "message": f"Банк '{bank_id}' не найден."}

    bank = BANKS[bank_id]
    now = datetime.now()
    num_transactions = random.randint(4, 10)
    added = 0
    total = 0.0

    for _ in range(num_transactions):
        is_expense = random.random() < 0.75
        if is_expense:
            cat, lo, hi = random.choice(bank["expenses"])
            amount = round(random.uniform(lo, hi), 2)
            t_type = "expense"
            total -= amount
        else:
            cat, lo, hi = random.choice(bank["incomes"])
            amount = round(random.uniform(lo, hi), 2)
            t_type = "income"
            total += amount

        days_ago = random.randint(0, 14)
        t_date = now - timedelta(days=days_ago)

        create_transaction(
            db=db,
            amount=amount,
            category=f"{cat} ({bank['name']})",
            type=t_type,
            date=t_date,
            is_synced=True,
        )
        added += 1

    return {
        "status": "success",
        "bank_id": bank_id,
        "bank_name": bank["name"],
        "message": f"{bank['name']}: загружено {added} операций.",
        "added_count": added,
        "net_flow": round(total, 2),
    }


def sync_all_banks(db: Session) -> dict[str, Any]:
    """Синхронизация всех подключённых банков одним запросом."""
    results = []
    total_added = 0
    total_flow = 0.0

    for bank_id in BANKS:
        r = sync_bank(db, bank_id)
        results.append(r)
        total_added += r.get("added_count", 0)
        total_flow += r.get("net_flow", 0)

    return {
        "status": "success",
        "message": f"Синхронизация завершена: {total_added} операций из {len(BANKS)} банков.",
        "total_added": total_added,
        "total_net_flow": round(total_flow, 2),
        "banks": results,
    }


def get_available_banks() -> list[dict[str, str]]:
    """Возвращает список всех доступных банков."""
    return [
        {"id": k, "name": v["name"], "color": v["color"]}
        for k, v in BANKS.items()
    ]
