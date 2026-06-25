"""Мультивалюта в движке (FR-19): суммы приводятся к базовой валюте до расчёта.

Курс задаём через таблицу fx_rates (пивот к USD). Проверяем, что доход в USD
корректно конвертируется в RUB при расчёте показателей.
"""
from __future__ import annotations

from datetime import datetime

from app.database import crud
from app.database.models import FxRate
from app.services.currency import CurrencyConverter, to_base_currency


def _seed_rates(db):
    # fx_rates преднасеяны миграциями — задаём нужные значения через upsert.
    for code, rate in [("USD", 1.0), ("RUB", 0.0125)]:  # 1 USD = 80 RUB
        row = db.query(FxRate).filter(FxRate.currency == code).first()
        if row is None:
            db.add(FxRate(currency=code, rate_to_usd=rate))
        else:
            row.rate_to_usd = rate
    db.commit()


class TestConverterUnit:
    def test_usd_to_rub(self, db_session):
        _seed_rates(db_session)
        conv = CurrencyConverter.from_db(db_session)
        # 100 USD → 8000 RUB
        assert round(float(conv.convert(100, "USD", "RUB")), 2) == 8000.00

    def test_same_currency_noop(self, db_session):
        _seed_rates(db_session)
        conv = CurrencyConverter.from_db(db_session)
        assert float(conv.convert(500, "RUB", "RUB")) == 500.0


class TestRowsToBase:
    def test_transactions_converted_to_base(self, db_session):
        _seed_rates(db_session)
        user = crud.create_user(db_session, email="u1@test.io", password_hash="x")
        crud.create_transaction(
            db_session, amount=100.0, type="income", date=datetime.utcnow(),
            category="Salary", currency="USD", user_id=user.id,
        )
        rows = crud.get_transactions(db_session, user_id=user.id)
        converted = to_base_currency(db_session, rows, base_currency="RUB")
        assert len(converted) == 1
        assert round(converted[0]["amount"], 2) == 8000.00
        assert converted[0]["currency"] == "RUB"

    def test_mixed_currencies_sum_in_base(self, db_session):
        _seed_rates(db_session)
        user = crud.create_user(db_session, email="u1@test.io", password_hash="x")
        crud.create_transaction(
            db_session, amount=100.0, type="income", date=datetime.utcnow(),
            category="USD-income", currency="USD", user_id=user.id,
        )
        crud.create_transaction(
            db_session, amount=5000.0, type="income", date=datetime.utcnow(),
            category="RUB-income", currency="RUB", user_id=user.id,
        )
        rows = crud.get_transactions(db_session, user_id=user.id)
        converted = to_base_currency(db_session, rows, base_currency="RUB")
        total = sum(r["amount"] for r in converted)
        # 100 USD (8000 RUB) + 5000 RUB = 13000 RUB
        assert round(total, 2) == 13000.00
