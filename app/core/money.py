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


# Полкопейки: допуск денежной арифметики на float. Поток |Rt| <= FLOW_EPS —
# численный ноль, а не дефицит: кризисный режим не должен включаться от
# остатка округления (находка R3-F1 второй сертификации, раунд 3).
FLOW_EPS = 0.005


def money(value: Any) -> float:
    """Денежное значение как float, округлённое по ROUND_HALF_UP.

    Для мест, где исторически ожидается float (выход движка, JSON-ответ),
    но округление должно быть денежным, а не банковским round-half-even.
    """
    return float(to_money(value))


# Неразрывный пробел: обычный разорвал бы сумму переносом строки в письме и в теле
# уведомления, и «125 000» на двух строках прочиталось бы как два разных числа.
NBSP = " "

# Выше этого порога копейки — шум. Значение совпадает с фронтовым каноном
# (frontend/src/shared/lib/money/formatMoney.ts) намеренно: расхождение форматов
# между экраном и письмом про ОДНУ И ТУ ЖЕ сумму читается как ошибка данных.
_KOPECKS_HIDDEN_ABOVE = Decimal("100000")


def format_money(value: Any) -> str:
    """Сумма для показа пользователю: «39 500,00 ₽», «125 000 ₽», «-1 500,00 ₽».

    Правила — skill finpilot-money-format и `formatMoney.ts`: неразрывный пробел
    разделяет разряды, запятая отделяет копейки, знак рубля идёт после числа через
    неразрывный пробел, копейки скрыты при |сумме| > 100 000, отрицательные —
    минусом перед числом, а не скобками.

    🔴 Живёт на бэкенде, хотя общий канон говорит «форматирование только на границе
    представления». У уведомлений граница не одна: то же тело уходит в email и в
    Telegram, где фронта нет. Держать формат только во фронте значило бы оставить
    два канала с машинными числами вида «доход 125000».
    """
    amount = to_money(value)
    negative = amount < 0
    abs_amount = -amount if negative else amount

    if abs_amount > _KOPECKS_HIDDEN_ABOVE:
        digits = f"{int(abs_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)):,}"
        body = digits.replace(",", NBSP)
    else:
        whole, _, kopecks = f"{abs_amount:.2f}".partition(".")
        body = f"{int(whole):,}".replace(",", NBSP) + "," + kopecks

    return f"{'-' if negative else ''}{body}{NBSP}₽"
