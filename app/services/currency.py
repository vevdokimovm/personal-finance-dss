"""Мультивалютная конвертация (FR-19, DATA-08).

Все суммы движок считает в базовой валюте пользователя. Конвертация идёт через
USD-пивот: convert(amount, A, B) = amount · rate(A) / rate(B), где rate(X) —
стоимость 1 единицы X в USD (таблица fx_rates).

Курсы кэшируются в памяти процесса и обновляются из БД; точность — Decimal.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from sqlalchemy.orm import Session

from app.database.models import FxRate

Number = Union[int, float, str, Decimal]


class CurrencyConverter:
    """Приводит суммы между валютами по таблице курсов к USD-пивоту."""

    def __init__(self, rates_to_usd: dict[str, Decimal]) -> None:
        self._rates = {code.upper(): rate for code, rate in rates_to_usd.items()}

    @classmethod
    def from_db(cls, db: Session) -> "CurrencyConverter":
        rows = db.query(FxRate).all()
        rates = {row.currency.upper(): Decimal(str(row.rate_to_usd)) for row in rows}
        rates.setdefault("USD", Decimal("1"))
        return cls(rates)

    def supports(self, currency: str) -> bool:
        return currency.upper() in self._rates

    def convert(self, amount: Number, from_currency: str, to_currency: str) -> Decimal:
        src = from_currency.upper()
        dst = to_currency.upper()
        value = self._as_decimal(amount)
        if src == dst:
            return value
        rate_src = self._rates.get(src)
        rate_dst = self._rates.get(dst)
        if rate_src is None or rate_dst is None or rate_dst == 0:
            # Неизвестная валюта — fail-loud-совместимо: не искажаем сумму.
            return value
        return (value * rate_src / rate_dst).quantize(Decimal("0.01"))

    @staticmethod
    def _as_decimal(amount: Number) -> Decimal:
        try:
            return Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")


def convert_rows_to_base(
    rows: list[dict],
    converter: CurrencyConverter,
    base_currency: str,
    amount_keys: tuple[str, ...] = ("amount", "monthly_payment", "target_amount", "current_amount"),
) -> list[dict]:
    """Возвращает копии строк с денежными полями, приведёнными к base_currency.

    Не мутирует вход. Поле currency у строки определяет исходную валюту
    (по умолчанию — base_currency, т.е. конвертация — no-op).
    """
    converted: list[dict] = []
    for row in rows:
        src_currency = str(row.get("currency") or base_currency)
        new_row = dict(row)
        for key in amount_keys:
            if key in new_row and new_row[key] is not None:
                new_row[key] = float(
                    converter.convert(new_row[key], src_currency, base_currency)
                )
        new_row["currency"] = base_currency
        converted.append(new_row)
    return converted


def get_rate(db: Session, currency: str) -> Optional[Decimal]:
    row = db.query(FxRate).filter(FxRate.currency == currency.upper()).first()
    return Decimal(str(row.rate_to_usd)) if row else None
