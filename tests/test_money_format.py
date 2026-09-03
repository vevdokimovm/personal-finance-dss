"""Текстовое представление денег на бэкенде (v8.32.0).

Заведено, потому что нашлось место, где продукт показывает пользователю голое
машинное число: `app/services/notifications.py` собирал тело уведомления как
`f"доход {digest['income']:.0f}"` — «доход 125000», без знака рубля, без разделителя
разрядов, без запятой. Единственное такое место в продукте: на фронте есть канон
`shared/lib/money/formatMoney.ts` с тестами, а этот текст мимо него проходил.

🔴 Почему форматируем на БЭКЕНДЕ, хотя фронтовый канон говорит «форматирование только
на границе представления». Для уведомлений граница не одна: то же тело уходит в email
(`email_service.send_digest`) и в Telegram (`notify_telegram_if_linked`), где фронта нет
вовсе. Отдать структурные числа и собрать текст на фронте — значит оставить два других
канала с машинными числами. Поэтому формат один и живёт там, где текст собирается.

Правила — те же, что у `formatMoney.ts` (skill finpilot-money-format):
неразрывный пробел разрядов, запятая как десятичный разделитель, знак рубля
после числа через неразрывный пробел, копейки скрыты при |сумма| > 100 000,
отрицательные — минусом перед числом.
"""
from __future__ import annotations

import pytest

from app.core.money import format_money

NBSP = " "


class TestFormatMoney:
    @pytest.mark.parametrize("value,expected", [
        (0, f"0,00{NBSP}₽"),
        (5, f"5,00{NBSP}₽"),
        (1234.5, f"1{NBSP}234,50{NBSP}₽"),
        (39500, f"39{NBSP}500,00{NBSP}₽"),
        (100000, f"100{NBSP}000,00{NBSP}₽"),
    ])
    def test_below_threshold_keeps_kopecks(self, value, expected):
        assert format_money(value) == expected

    @pytest.mark.parametrize("value,expected", [
        (100000.01, f"100{NBSP}000{NBSP}₽"),
        (125000, f"125{NBSP}000{NBSP}₽"),
        (1234567.89, f"1{NBSP}234{NBSP}568{NBSP}₽"),
    ])
    def test_above_threshold_hides_kopecks(self, value, expected):
        """Порог 100 000 — тот же, что во фронтовом каноне: на крупных суммах
        копейки шум, а расхождение форматов между экраном и письмом читается
        как ошибка данных."""
        assert format_money(value) == expected

    def test_negative_uses_minus_not_parentheses(self):
        assert format_money(-1500) == f"-1{NBSP}500,00{NBSP}₽"

    def test_separator_is_non_breaking(self):
        """Обычный пробел разорвал бы сумму переносом строки в письме и в теле
        уведомления — «125 000» на двух строках читается как два числа."""
        assert " " not in format_money(125000)

    def test_matches_frontend_canon_on_reference_value(self):
        """39 500,00 ₽ — эталон из тестов `formatMoney.ts`. Если фронт и бэкенд
        разойдутся, пользователь увидит одну и ту же сумму по-разному на экране
        и в письме."""
        assert format_money(39500) == f"39{NBSP}500,00{NBSP}₽"

    def test_accepts_decimal_and_int_alike(self):
        from decimal import Decimal
        assert format_money(Decimal("1234.5")) == format_money(1234.5)
