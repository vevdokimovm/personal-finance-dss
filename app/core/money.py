"""Денежная политика округления (P1.4).

Деньги на путях ввода/вывода округляются до копеек по ROUND_HALF_UP — стандарт
для финансовых сумм, в отличие от банковского round-half-even у float. Источник
истины — БД (Numeric(14,2)); эта утилита задаёт предсказуемое округление на
границах: запись пользовательских сумм и материализация результата в рубли.

Безразмерное ядро выбора (нормализация, веса, U(a)) сознательно остаётся float —
ему нужны коэффициенты, а не копейки, и Decimal там не добавляет точности.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

_CENTS = Decimal("0.01")


def to_money(value: Any) -> Decimal:
    """Денежный Decimal, округлённый до копеек по ROUND_HALF_UP.

    Преобразование через str(value) исключает двоичную неточность float
    (Decimal(0.1) != Decimal('0.1')).
    """
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    return d.quantize(_CENTS, rounding=ROUND_HALF_UP)


def money(value: Any) -> float:
    """Денежное значение как float, округлённое по ROUND_HALF_UP.

    Для мест, где исторически ожидается float (выход движка, JSON-ответ),
    но округление должно быть денежным, а не банковским round-half-even.
    """
    return float(to_money(value))
