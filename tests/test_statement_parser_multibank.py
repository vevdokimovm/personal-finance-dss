"""Тесты мульти-банк импорта: устойчивый универсальный парсер (CSV + XLSX).

Покрывают реальные кейсы выгрузок (Альфа, ВТБ, Райф): заголовок не на первой
строке (метаданные счёта сверху), раздельные колонки Приход/Расход, неразрывные
пробелы и ё/е в заголовках и суммах, чтение XLSX теми же эвристиками.
"""
import io

import openpyxl

from app.services.statement_parser import _num, parse_universal_csv, parse_xlsx


class TestHeaderDetection:
    def test_header_not_on_first_line(self):
        # метаданные счёта над таблицей (Альфа-стиль) — заголовок ищем, а не берём 1-ю строку
        content = (
            "Выписка по счету\n"
            "Номер счета,40817810104980500173,За период с 01.05.2026\n"
            "Валюта счета,RUR,Поступления,224 805 RUR\n"
            "\n"
            "Операции по счету\n"
            "Дата операции,Дата проводки,Категория,Описание,Сумма в валюте счета,Статус\n"
            "01.05.2026,01.05.2026,Прочее,Перевод по СБП,-2000,Выполнен\n"
            "05.05.2026,05.05.2026,Зарплата,Оклад,50000,Выполнен\n"
        )
        txns = parse_universal_csv(content)
        assert len(txns) == 2
        assert {t["type"] for t in txns} == {"expense", "income"}
        assert all(t["amount"] > 0 for t in txns)

    def test_nbsp_and_yo_in_headers_and_values(self):
        # неразрывные пробелы в заголовке и сумме, ё вместо е
        content = (
            "Дата операции;Сумма в\xa0валюте\xa0счёта;Описание\n"
            "01.05.2026;-2\xa0000,50;Магазин\n"
        )
        txns = parse_universal_csv(content)
        assert len(txns) == 1
        assert txns[0]["amount"] == 2000.5
        assert txns[0]["type"] == "expense"

    def test_no_table_returns_empty(self):
        assert parse_universal_csv("просто текст\nбез таблицы\n") == []

    def test_header_on_first_line_still_works(self):
        # регресс: классический формат с заголовком на 1-й строке не сломан
        content = "Дата;Сумма;Описание\n01.06.2025;-1500;Магазин\n05.06.2025;50000;Оклад\n"
        assert len(parse_universal_csv(content)) == 2


class TestSplitDebitCredit:
    def test_credit_debit_columns(self):
        # ВТБ-стиль: раздельные Приход/Расход вместо одной знаковой суммы
        content = (
            "Дата операции,Приход,Расход,Описание\n"
            "01.05.2026,3000,0,Зарплата\n"
            "02.05.2026,0,741.74,Магазин\n"
        )
        txns = parse_universal_csv(content)
        by = {t["description"]: (t["type"], t["amount"]) for t in txns}
        assert by["Зарплата"] == ("income", 3000.0)
        assert by["Магазин"] == ("expense", 741.74)

    def test_credit_debit_with_nbsp(self):
        content = (
            "Дата,Поступление,Списание,Назначение\n"
            "01.05.2026,1 114,54,0,Перевод\n"
        )
        txns = parse_universal_csv(content)
        assert len(txns) == 1
        assert txns[0]["type"] == "income"


class TestNumParsing:
    def test_signed_nbsp_decimal_comma(self):
        assert _num("-2\xa0000,50") == -2000.5

    def test_space_thousands(self):
        assert _num("8 500") == 8500.0

    def test_currency_suffix_stripped(self):
        assert _num("1 114,54 RUR") == 1114.54

    def test_empty_and_none(self):
        assert _num("") is None
        assert _num(None) is None

    def test_no_digits(self):
        assert _num("—") is None
        assert _num("RUR") is None


class TestXlsx:
    def _book(self, rows):
        wb = openpyxl.Workbook()
        ws = wb.active
        for r in rows:
            ws.append(r)
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def test_parse_xlsx_with_metadata_above_header(self):
        raw = self._book([
            ["Выписка по счету"],
            ["Номер счета", "40817", "За период"],
            [],
            ["Дата операции", "Категория", "Описание", "Сумма в валюте счета", "Статус"],
            ["01.05.2026", "Прочее", "Перевод", "-2000", "Выполнен"],
            ["02.05.2026", "Зарплата", "Оклад", "50000", "Выполнен"],
        ])
        txns = parse_xlsx(raw)
        assert len(txns) == 2
        assert {t["type"] for t in txns} == {"expense", "income"}

    def test_parse_xlsx_no_table(self):
        raw = self._book([["просто"], ["текст"]])
        assert parse_xlsx(raw) == []
