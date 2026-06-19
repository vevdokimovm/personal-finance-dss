"""Unit-тесты парсера банковских выписок (разные форматы и знаки сумм)."""
from __future__ import annotations

from app.services.statement_parser import (
    parse_bank_statement,
    parse_sber_csv,
    parse_tinkoff_csv,
    parse_universal_csv,
)


def test_universal_csv_income_and_expense() -> None:
    csv = (
        "Дата;Сумма;Категория;Описание;MCC\n"
        "01.06.2025;-1500;Продукты;Магазин;5411\n"
        "05.06.2025;50000;Зарплата;Оклад;\n"
    )
    txns = parse_universal_csv(csv)
    assert len(txns) == 2
    by_type = {t["type"] for t in txns}
    assert by_type == {"expense", "income"}
    # суммы хранятся положительными, знак отражён в type
    assert all(t["amount"] > 0 for t in txns)


def test_tinkoff_csv_parsed() -> None:
    csv = (
        "Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;Валюта операции;"
        "Сумма платежа;Валюта платежа;Кэшбэк;Категория;MCC;Описание\n"
        "01.06.2025 12:00:00;01.06.2025;*1234;OK;-1500.00;RUB;-1500.00;RUB;0;Продукты;5411;Пятёрочка\n"
    )
    txns = parse_tinkoff_csv(csv)
    assert len(txns) == 1
    assert txns[0]["type"] == "expense"
    assert txns[0]["amount"] == 1500.0


def test_sber_csv_parsed() -> None:
    csv = (
        "№;Дата;Описание;Категория;Сумма;Валюта;Статус\n"
        "1;01.06.2025;Перевод;Зарплата;75000.00;RUB;OK\n"
    )
    txns = parse_sber_csv(csv)
    assert len(txns) == 1
    assert txns[0]["type"] == "income"


def test_dispatch_by_bank_id() -> None:
    csv = "Дата;Сумма;Категория;Описание;MCC\n01.06.2025;-100;Прочее;X;\n"
    txns = parse_bank_statement(csv, bank_id="universal")
    assert len(txns) == 1


def test_malformed_rows_are_skipped() -> None:
    csv = (
        "Дата;Сумма;Категория;Описание;MCC\n"
        "01.06.2025;-1500;Продукты;Магазин;5411\n"
        "битая;строка;без;суммы\n"
        ";;;;\n"
    )
    txns = parse_universal_csv(csv)
    # Валидная строка распарсилась, мусор отброшен без падения
    assert len(txns) >= 1
