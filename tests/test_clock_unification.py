"""Унификация часов: вся «сейчас»-логика приложения привязана к UTC.

Контекст (INC-CLOCK-LOCALTIME). Релиз v4.25.2 заменил deprecated
``datetime.utcnow()`` единым helper ``utcnow()`` (naive UTC), но в коде остались
прямые ``datetime.now()`` — это ЛОКАЛЬНОЕ время сервера. В песочнице и CI оно
совпадает с UTC, поэтому баг невидим; на прод-VPS в РФ (обычно MSK, UTC+3)
появляется стабильный сдвиг между «сейчас»-логикой и UTC-хранилищем: месячный
бакетинг трат разъезжается на стыке месяца, окна «последних N дней» сдвинуты на
оффсет, fallback-даты импорта пишутся в локальном времени в naive-UTC колонки.

Тесты написаны до реализации (TDD): мокаем ``utcnow`` фиксированным моментом и
проверяем, что результат привязан к НЕМУ, а не к системным часам. Пока код зовёт
``datetime.now()`` — моки игнорируются и ассерты падают (red). После перевода всех
точек на ``utcnow()`` — зелёные. Контракт замены — naive↔naive (нулевой риск
naive/aware TypeError), поэтому моки возвращают naive datetime.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

from app.database.crud import create_transaction, get_transactions
from app.schemas.obligation import ObligationResponse
from app.services.bank_api import sync_bank
from app.services.spending import _min_period, get_spending_advice
from app.services.statement_parser import _parse_date

# Момент в заведомо «невозможном» месяце — чтобы отличить замоканные часы от
# реального «сейчас» (любой реальный месяц != 2099-07).
FIXED = datetime(2099, 7, 15, 12, 0, 0)


# --- spending: окно анализа и текущий период привязаны к UTC ----------------

def test_min_period_anchors_on_utc_clock() -> None:
    with patch("app.services.spending.utcnow", return_value=FIXED):
        assert _min_period(1) == "2099-07"


def test_min_period_window_spans_back_from_utc_clock() -> None:
    # Окно 3 месяца назад от июля-2099 включительно → нижняя граница май-2099.
    with patch("app.services.spending.utcnow", return_value=FIXED):
        assert _min_period(3) == "2099-05"


def test_current_period_anchors_on_utc_clock(db_session) -> None:
    # Транзакция в UTC-месяце FIXED (июль-2099) + более поздняя (сентябрь-2099),
    # чтобы max(periods) != UTC-месяц: иначе fallback на последний период
    # маскирует баг и тест проходит даже на локальных часах.
    create_transaction(
        db_session, amount=100.0, type="expense",
        date=datetime(2099, 7, 10), category="Еда", description="кофе",
    )
    create_transaction(
        db_session, amount=200.0, type="expense",
        date=datetime(2099, 9, 10), category="Еда", description="ужин",
    )
    with patch("app.services.spending.utcnow", return_value=FIXED):
        result = get_spending_advice(db_session)
    assert result["current_period"] == "2099-07"


# --- statement_parser: fallback-дата импорта = UTC-«сейчас» ------------------

def test_parse_date_empty_uses_utc_clock() -> None:
    with patch("app.services.statement_parser.utcnow", return_value=FIXED):
        assert _parse_date("") == FIXED


def test_parse_date_unparseable_uses_utc_clock() -> None:
    with patch("app.services.statement_parser.utcnow", return_value=FIXED):
        assert _parse_date("не-дата-вообще") == FIXED


# --- obligation: «сколько месяцев выплачивается» считается от UTC ------------

def test_obligation_months_elapsed_anchors_on_utc_clock() -> None:
    ob = ObligationResponse(
        id=1, name="Кредит", amount=600000.0, interest_rate=0.12,
        term=24, monthly_payment=15000.0, payment_day=10,
        start_date=datetime(2099, 1, 15),
    )
    with patch("app.schemas.obligation.utcnow", return_value=FIXED):
        # Январь-2099 → июль-2099 = ровно 6 месяцев.
        assert ob.months_elapsed == 6


# --- bank_api: даты синк-транзакций привязаны к UTC-«сейчас» -----------------

def test_bank_sync_dates_anchor_on_utc_clock(db_session) -> None:
    with patch("app.services.bank_api.utcnow", return_value=FIXED):
        sync_bank(db_session, bank_id="tinkoff")
    txns = get_transactions(db_session)
    assert txns, "синхронизация должна создать транзакции"
    window_start = FIXED - timedelta(days=14)
    for t in txns:
        assert window_start <= t.date <= FIXED
