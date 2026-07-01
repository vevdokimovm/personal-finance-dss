"""Тесты PDF-парсеров ВТБ и Сбербанка (детерминированно, без LLM).

Тестовые seam'ы (`_vtb_table_to_transactions`, `_sber_text_to_transactions`)
проверяются синтетикой, повторяющей реальную раскладку — реальные выписки с
персональными данными в репозиторий не кладём. Полный путь pdfplumber на живых
файлах проверяется отдельно при разработке.
"""
from app.services.statement_parser import (
    PDF_PARSERS,
    _num,
    _raif_table_to_transactions,
    _sber_text_to_transactions,
    _vtb_table_to_transactions,
)


class TestNumDualLocale:
    def test_en_thousands_comma(self):
        assert _num("3,000.00") == 3000.0      # ВТБ: запятая-тысячи, точка-десятичная

    def test_en_negative(self):
        assert _num("-741.74") == -741.74

    def test_en_thousands_negative(self):
        assert _num("-2,150.00") == -2150.0

    def test_ru_decimal_comma(self):
        assert _num("-2\xa0000,50") == -2000.5

    def test_ru_with_currency_suffix(self):
        assert _num("1 114,54 RUR") == 1114.54


class TestVtbTable:
    def _row(self, dt, amount, desc):
        # [дата+время, дата обработки, знаковая сумма, Приход, Расход, Комиссия, Описание]
        return [dt, "02.06.2026", amount, None, None, "0.00", desc]

    def test_expense_negative(self):
        txns = _vtb_table_to_transactions(
            [[self._row("30.05.2026\n19:56:44", "-741.74 RUB", "PYATEROCHKA *6667")]])
        assert len(txns) == 1
        assert txns[0]["type"] == "expense"
        assert txns[0]["amount"] == 741.74

    def test_income_positive_en_thousands(self):
        txns = _vtb_table_to_transactions(
            [[self._row("29.05.2026\n11:27:02", "3,000.00 RUB", "Перевод СБП")]])
        assert txns[0]["type"] == "income"
        assert txns[0]["amount"] == 3000.0

    def test_header_rows_skipped(self):
        rows = [[
            ["Дата и время\nоперации", "Дата обработки", "Сумма", None, None, "Комиссия", "Описание"],  # noqa: E501
            [None, None, None, "Приход", "Расход", None, None],
            self._row("30.05.2026", "-100.00 RUB", "X"),
        ]]
        assert len(_vtb_table_to_transactions(rows)) == 1

    def test_zero_amount_skipped(self):
        txns = _vtb_table_to_transactions([[self._row("30.05.2026", "0 RUB", "Кэшбэк")]])
        assert txns == []

    def test_date_parsed_from_first_line(self):
        txns = _vtb_table_to_transactions([[self._row("30.05.2026\n19:56:44", "-50.00 RUB", "X")]])
        assert txns[0]["date"].startswith("2026-05-30")

    def test_description_whitespace_collapsed(self):
        txns = _vtb_table_to_transactions(
            [[self._row("30.05.2026", "-50.00 RUB", "Оплата\nтоваров   *6667")]])
        assert txns[0]["description"] == "Оплата товаров *6667"


class TestSberText:
    def test_expense_no_sign(self):
        lines = [
            "02.07.2025 13:28 Перевод с карты 550,00 0,00",
            "02.07.2025 924257 Перевод для Е. Василий Максимович. Операция по счету",
        ]
        txns = _sber_text_to_transactions(lines)
        assert len(txns) == 1
        assert txns[0]["type"] == "expense"
        assert txns[0]["amount"] == 550.0
        assert "Перевод для" in txns[0]["description"]

    def test_income_plus_sign(self):
        lines = [
            "02.07.2025 13:26 Перевод СБП +550,00 550,00",
            "02.07.2025 444669 Перевод от Е. Василий Максимович. Операция по счету",
        ]
        txns = _sber_text_to_transactions(lines)
        assert txns[0]["type"] == "income"
        assert txns[0]["amount"] == 550.0

    def test_thousands_in_amount(self):
        lines = ["10.05.2026 12:00 Покупка 1 649,00 0,00"]
        txns = _sber_text_to_transactions(lines)
        assert txns[0]["amount"] == 1649.0

    def test_non_operation_lines_ignored(self):
        lines = ["Расшифровка операций", "ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД:", "просто текст без даты"]
        assert _sber_text_to_transactions(lines) == []

    def test_date_parsed(self):
        txns = _sber_text_to_transactions(["25.06.2025 11:33 Прочие операции 150,00 0,00"])
        assert txns[0]["date"].startswith("2025-06-25")


class TestRaiffeisenTable:
    def _row(self, num, dt, debit, credit, desc):
        # [№, дата+время, документ, Debit, Credit, назначение, карта]
        return [num, dt, "DOC123", debit, credit, desc, ""]

    def test_debit_is_expense(self):
        rows = [[self._row("1", "17.01.2025 17:30\n1", "- 2 670,12 ₽", "", "Телефон получателя")]]
        txns = _raif_table_to_transactions(rows)
        assert len(txns) == 1
        assert txns[0]["type"] == "expense"
        assert txns[0]["amount"] == 2670.12

    def test_credit_is_income(self):
        rows = [[self._row("2", "17.01.2025 17:29\n1", "", "+ 2 670,12 ₽", "Продали доллары")]]
        txns = _raif_table_to_transactions(rows)
        assert txns[0]["type"] == "income"
        assert txns[0]["amount"] == 2670.12

    def test_header_and_service_rows_skipped(self):
        rows = [[
            ["№ P/P", "Posting date", "Document number", "Debit", "Credit", "Payment details", "Card"],  # noqa: E501
            [None, "Executed by the bank", None, None, None, None, None],
            self._row("1", "26.09.2024 20:04\n2", "- 89,00 ₽", "", "Продукты"),
        ]]
        assert len(_raif_table_to_transactions(rows)) == 1

    def test_date_from_first_line(self):
        rows = [[self._row("1", "26.09.2024 20:04\n2", "- 89,00 ₽", "", "Продукты")]]
        assert _raif_table_to_transactions(rows)[0]["date"].startswith("2024-09-26")

    def test_empty_debit_and_credit_skipped(self):
        rows = [[self._row("1", "26.09.2024", "", "", "Пустая")]]
        assert _raif_table_to_transactions(rows) == []


class TestPdfDispatch:
    def test_known_banks_mapped(self):
        assert set(PDF_PARSERS) >= {"tinkoff", "vtb", "sber", "raiffeisen"}
