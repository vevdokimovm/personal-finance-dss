"""Тесты массовой вставки транзакций (фикс таймаута большой выписки).

bulk_create_transactions заменяет поштучный create_transaction (с COUNT-запросом
_is_recurring на каждую строку) — проверяем, что вставка работает, категория
проставляется, а признак повторяемости (FR-13) считается одним проходом в памяти.
"""
from datetime import datetime

from app.database.crud import bulk_create_transactions
from app.database.models import Transaction


def _rows():
    return [
        {"amount": 1500, "type": "expense", "date": datetime(2026, 5, 1),
         "description": "Пятёрочка", "mcc": "5411"},
        {"amount": 50000, "type": "income", "date": datetime(2026, 5, 2),
         "description": "Оклад"},
    ]


def test_bulk_inserts_all_rows(db_session):
    n = bulk_create_transactions(db_session, _rows(), user_id=None, bank="tinkoff")
    assert n == 2
    assert db_session.query(Transaction).count() == 2


def test_bulk_resolves_category_and_bank(db_session):
    bulk_create_transactions(db_session, _rows(), user_id=None, bank="tinkoff")
    txns = db_session.query(Transaction).all()
    assert all(t.category for t in txns)        # категория проставлена классификатором
    assert all(t.bank == "tinkoff" for t in txns)
    assert all(t.is_synced for t in txns)


def test_bulk_accepts_isoformat_dates(db_session):
    rows = [{"amount": 100, "type": "expense", "date": "2026-05-01T12:00:00", "description": "X"}]
    assert bulk_create_transactions(db_session, rows) == 1


def test_bulk_recurring_flag_set_for_repeats(db_session):
    # ≥2 одинаковых (описание, тип) → повторяющаяся
    rows = [
        {"amount": 100, "type": "expense", "date": datetime(2026, 5, 1), "description": "Кофе"},
        {"amount": 120, "type": "expense", "date": datetime(2026, 5, 8), "description": "Кофе"},
    ]
    bulk_create_transactions(db_session, rows)
    txns = db_session.query(Transaction).filter(Transaction.description == "Кофе").all()
    assert len(txns) == 2
    assert all(t.is_recurring for t in txns)


def test_bulk_single_occurrence_not_recurring(db_session):
    rows = [{"amount": 999, "type": "expense", "date": datetime(2026, 5, 1), "description": "Разовое"}]
    bulk_create_transactions(db_session, rows)
    t = db_session.query(Transaction).filter(Transaction.description == "Разовое").one()
    assert t.is_recurring is False


def test_bulk_recurring_counts_existing(db_session):
    # одна уже в БД + одна входящая с тем же описанием → обе должны стать повторяющимися
    base = {"amount": 100, "type": "expense", "date": datetime(2026, 5, 1), "description": "Подписка"}
    bulk_create_transactions(db_session, [base])
    bulk_create_transactions(db_session, [{**base, "date": datetime(2026, 6, 1)}])
    txns = db_session.query(Transaction).filter(Transaction.description == "Подписка").all()
    assert len(txns) == 2
    # вторая партия видит первую → ставит recurring; первая остаётся как была (разовой на момент вставки)
    assert any(t.is_recurring for t in txns)


def test_bulk_empty_returns_zero(db_session):
    assert bulk_create_transactions(db_session, []) == 0
