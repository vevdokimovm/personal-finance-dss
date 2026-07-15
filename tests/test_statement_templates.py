"""
Golden-тесты корректности чтения выписок (§6.4).

Каждый эталонный шаблон из `app/data/statement_templates/` парсится своим парсером,
результат сверяется с известными значениями (дата/тип/сумма/описание). Это ловит
регрессии парсеров на реальных форматах: любой сдвиг в извлечении знака, суммы или
описания валит тест на конкретном банке. Шаблоны генерируются
`tools/statement_templates/build_templates.py`; ожидаемые значения здесь —
независимый golden (не импортируются из генератора).

Плюс проверка стратегии покрытия ~200 банков: универсальный парсер читает выписку
произвольного банка (незнакомый порядок и названия колонок) без выделенного парсера.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.statement_parser import (
    parse_1c_exchange,
    parse_bank_statement,
    parse_raiffeisen_pdf,
    parse_sber_csv,
    parse_sber_pdf,
    parse_tinkoff_csv,
    parse_tinkoff_pdf,
    parse_universal_csv,
    parse_vtb_pdf,
    parse_xlsx,
)

TPL = Path("app/data/statement_templates")


def _check(txns: list[dict], expected: list[tuple]) -> None:
    """expected: (date_prefix, type, amount, description)."""
    assert len(txns) == len(expected), f"ожидалось {len(expected)} операций, получено {len(txns)}"
    for got, (date_p, typ, amount, desc) in zip(txns, expected):
        assert got["date"].startswith(date_p), f"дата {got['date']} != {date_p}"
        assert got["type"] == typ, f"тип {got['type']} != {typ} ({desc})"
        assert got["amount"] == pytest.approx(amount), f"сумма {got['amount']} != {amount} ({desc})"
        assert got["description"] == desc, f"описание {got['description']!r} != {desc!r}"


class TestTemplatesExistInProduct:
    def test_all_templates_present(self):
        expected_files = {
            "tinkoff.csv", "sber.csv", "universal_single.csv", "universal_split.csv",
            "universal.xlsx", "tinkoff.pdf", "sber.pdf", "vtb.pdf", "raiffeisen.pdf",
            "sberbank_1c.txt", "MANIFEST.md",
        }
        present = {p.name for p in TPL.iterdir()}
        assert expected_files <= present, f"нет шаблонов: {expected_files - present}"


class TestCsvTemplates:
    def test_tinkoff_csv(self):
        # FAILED-операция должна отсеяться → остаётся 2.
        _check(parse_tinkoff_csv((TPL / "tinkoff.csv").read_text("utf-8")), [
            ("2026-01-15T12:30", "expense", 1234.56, "Пятёрочка"),
            ("2026-01-16T09:00", "income", 80000.00, "Зарплата"),
        ])

    def test_sber_csv(self):
        _check(parse_sber_csv((TPL / "sber.csv").read_text("utf-8")), [
            ("2026-01-10", "expense", 899.00, "Магнит"),
            ("2026-01-11", "income", 45000.00, "Аванс"),
        ])

    def test_universal_single_csv(self):
        # Метаданные над таблицей не должны сбить детекцию заголовка.
        _check(parse_universal_csv((TPL / "universal_single.csv").read_text("utf-8")), [
            ("2026-01-05", "expense", 450.00, "Кофейня на углу"),
            ("2026-01-06", "income", 30000.00, "Фриланс-проект"),
        ])

    def test_universal_split_csv(self):
        # Раздельные Приход/Расход: расход = отрицательная нетто-сумма.
        _check(parse_universal_csv((TPL / "universal_split.csv").read_text("utf-8")), [
            ("2026-01-07", "expense", 350.00, "Аптека Ригла"),
            ("2026-01-08", "income", 1200.00, "Возврат за товар"),
        ])


class TestXlsxTemplate:
    def test_universal_xlsx(self):
        _check(parse_xlsx((TPL / "universal.xlsx").read_bytes()), [
            ("2026-01-09", "expense", 120.00, "Метро"),
            ("2026-01-10", "income", 250.00, "Возврат кэшбэка"),
        ])


class TestPdfTemplates:
    def test_tinkoff_pdf(self):
        _check(parse_tinkoff_pdf((TPL / "tinkoff.pdf").read_bytes()), [
            ("2026-01-15", "expense", 1234.56, "Пятёрочка"),
            ("2026-01-16", "income", 80000.00, "Зарплата"),
        ])

    def test_sber_pdf(self):
        # Описание берётся со следующей строки (дата обработки + код + текст).
        _check(parse_sber_pdf((TPL / "sber.pdf").read_bytes()), [
            ("2026-01-10", "expense", 899.00, "Магнит у дома"),
            ("2026-01-11", "income", 45000.00, "Аванс компании"),
        ])

    def test_vtb_pdf(self):
        # Табличная выписка, знаковая сумма в валюте операции (колонка 3).
        _check(parse_vtb_pdf((TPL / "vtb.pdf").read_bytes()), [
            ("2026-01-12", "expense", 1500.00, "Ozon"),
            ("2026-01-13", "income", 25000.00, "Перевод"),
        ])

    def test_raiffeisen_pdf(self):
        # Табличная выписка, split Debit(−)/Credit(+).
        _check(parse_raiffeisen_pdf((TPL / "raiffeisen.pdf").read_bytes()), [
            ("2026-01-14", "expense", 780.00, "Аптека Ригла"),
            ("2026-01-15", "income", 3000.00, "Кэшбэк"),
        ])


class TestOneCTemplate:
    def test_1c_exchange(self):
        # Знак операции — по тому, чей счёт (владельца 40817...0001) плательщик/получатель.
        _check(parse_1c_exchange((TPL / "sberbank_1c.txt").read_text("utf-8")), [
            ("2026-01-16", "expense", 5000.00, "Оплата услуг связи"),
            ("2026-01-17", "income", 90000.00, "Поступление зарплаты"),
        ])


class TestDispatcher:
    def test_dispatch_routes_1c_by_content(self):
        # parse_bank_statement сам детектит 1C по первой строке, минуя bank_id.
        content = (TPL / "sberbank_1c.txt").read_text("utf-8")
        txns = parse_bank_statement(content, bank_id="universal")
        assert len(txns) == 2 and txns[0]["type"] == "expense"

    def test_dispatch_routes_by_bank_id(self):
        txns = parse_bank_statement((TPL / "sber.csv").read_text("utf-8"), bank_id="sber")
        assert len(txns) == 2 and txns[1]["type"] == "income"


class TestUniversalCoverageStrategy:
    """Стратегия покрытия ~200 банков: universal-парсер читает выписку любого банка
    без выделенного парсера — по эвристикам колонок, а не по имени банка."""

    def test_unknown_bank_arbitrary_column_order(self):
        # «Неизвестный банк»: другой порядок и названия колонок, метаданные сверху.
        content = (
            "Некий Банк, выписка по счёту\n"
            "\n"
            "Назначение;Дата транзакции;Сумма операции\n"
            "Кофе;03.02.2026;-180.00\n"
            "Гонорар;04.02.2026;15000.00\n"
        )
        _check(parse_universal_csv(content), [
            ("2026-02-03", "expense", 180.00, "Кофе"),
            ("2026-02-04", "income", 15000.00, "Гонорар"),
        ])

    def test_unknown_bank_english_headers(self):
        # Англоязычная шапка тоже покрывается синонимами.
        content = (
            "date,description,amount\n"
            "05.02.2026,Taxi,-320.00\n"
            "06.02.2026,Refund,500.00\n"
        )
        _check(parse_universal_csv(content), [
            ("2026-02-05", "expense", 320.00, "Taxi"),
            ("2026-02-06", "income", 500.00, "Refund"),
        ])
