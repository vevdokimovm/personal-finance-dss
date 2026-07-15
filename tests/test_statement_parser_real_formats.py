"""
Тесты парсера на РЕАЛЬНЫЕ форматные особенности (найдены прогоном настоящих выписок).

Проверяют то, на чём парсер спотыкался на живых данных банков:
- ВТБ PDF: движение в раздельных колонках Приход/Расход/Комиссия (реальная раскладка),
  а не знаковая сумма в одной колонке; чисто-комиссионная операция = расход.
- 1C-обмен: реальные банки шлют файл в windows-1251, не UTF-8 — декодер обязан это учесть.
- Детекция не-выписок: банк в окне «выписки» отдаёт справки об остатке/реквизиты/о
  задолженности — операций там нет, приложение не должно принять их за пустую выписку.

Фикстуры синтетические (реальные выписки содержат PII и в репозиторий не кладутся), но
воспроизводят те же форматные особенности, на которых ломались настоящие файлы.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.statement_parser import (
    _vtb_column_map,
    _vtb_table_to_transactions,
    classify_non_statement,
    decode_statement_bytes,
    parse_1c_exchange,
    parse_bank_statement,
)

TPL = Path("app/data/statement_templates")


class TestVtbRealLayout:
    """Реальная раскладка ВТБ: [дата, дата2, сумма_в_валюте_операции, Приход, Расход,
    Комиссия, Описание] с двухрядной шапкой. Знаковая колонка[2] для рублёвой комиссии = 0,
    поэтому нетто считается по Приход − Расход − Комиссия. На реальном файле это давало 0."""

    def _rows(self):
        return [[
            ["Операции по счёту", "", "", "", "", "", ""],
            ["Дата и время\nоперации", "Дата обработки", "Сумма в валюте\nоперации",
             "Сумма в валюте счёта", "", "Комиссия", "Описание операции"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["14.12.2025\n23:04:46", "14.12.2025", "0.00 RUB", "0\nRUB", "0\nRUB",
             "69.01\nRUB", "Комиссия за обслуживание счета."],
            ["10.12.2025\n10:00:00", "10.12.2025", "0.00 RUB", "5 000,00\nRUB", "0\nRUB",
             "0\nRUB", "Перевод СБП"],
            ["09.12.2025\n11:00:00", "09.12.2025", "0.00 RUB", "0\nRUB", "1 200,00\nRUB",
             "0\nRUB", "Оплата покупки"],
        ]]

    def test_commission_only_is_expense(self):
        # Приход=0, Расход=0, только Комиссия 69.01 → расход 69.01 (было: 0 операций).
        t = _vtb_table_to_transactions(self._rows())
        assert t[0]["type"] == "expense"
        assert t[0]["amount"] == pytest.approx(69.01)
        assert t[0]["description"] == "Комиссия за обслуживание счета."

    def test_prihod_is_income(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[1]["type"] == "income"
        assert t[1]["amount"] == pytest.approx(5000.0)

    def test_rashod_is_expense(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[2]["type"] == "expense"
        assert t[2]["amount"] == pytest.approx(1200.0)

    def test_header_and_title_rows_skipped(self):
        # Строки-заголовки (без даты в первой ячейке) не попадают в операции.
        assert len(_vtb_table_to_transactions(self._rows())) == 3

    def test_signed_single_column_variant_still_works(self):
        # Второй формат ВТБ: знаковая сумма в одной колонке, Приход/Расход пусты.
        rows = [[["30.05.2026\n19:56:44", "02.06.2026", "-741.74 RUB", None, None,
                  "0.00", "PYATEROCHKA"]]]
        t = _vtb_table_to_transactions(rows)
        assert t[0]["type"] == "expense" and t[0]["amount"] == pytest.approx(741.74)


class TestVtbTemplateB:
    """Второй реальный шаблон ВТБ: вместо «Комиссия» на индексе 5 стоит ОПИСАНИЕ, а на 6 —
    наименование получателя. Привязка к индексам брала описание из колонки контрагента
    (все расходы получали заглушку «Операция») и читала текст описания как комиссию."""

    def _rows(self):
        return [[
            ["Операции по счёту", "", "", "", "", "", ""],
            ["Дата и время\nоперации", "Дата обработки\nбанком",
             "Сумма операции в\nвалюте операции",
             "Сумма операции в валюте\nсчета/карты", "", "Описание операции",
             "Наименование\nполучателя/\nОтправителя"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["29.06.2026\n11:00:00", "02.07.2026", "-186.65 RUB", "0.00 RUB", "-186.65 RUB",
             "Оплата товаров и услуг. SHOP-1. РОССИЯ. Podolsk. 991000240508.", ""],
            ["27.06.2026\n12:00:00", "27.06.2026", "3000.00 RUB", "3000.00 RUB", "0.00 RUB",
             "Переводы через СБП. Перевод денежных средств.", "Иванова Мария Петровна"],
            ["18.06.2026\n09:00:00", "18.06.2026", "-126.00 RUB", "0.00 RUB", "-126.00 RUB",
             "Оплата услуг коммерческих провайдеров. Лицевой счет: 850010068828.", "Ростелеком"],
        ]]

    def test_description_taken_from_its_own_column(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[0]["type"] == "expense" and t[0]["amount"] == pytest.approx(186.65)
        assert t[0]["description"].startswith("Оплата товаров и услуг. SHOP-1")

    def test_negative_rashod_column(self):
        # В этом шаблоне Расход идёт со знаком минус (в шаблоне A — положительный).
        t = _vtb_table_to_transactions(self._rows())
        assert [x["type"] for x in t] == ["expense", "income", "expense"]

    def test_counterparty_appended_to_description(self):
        # Контрагент — сырьё для merchant-аналитики: «Ростелеком» терять нельзя.
        t = _vtb_table_to_transactions(self._rows())
        assert t[1]["description"].endswith("Иванова Мария Петровна")
        assert "Ростелеком" in t[2]["description"]

    def test_numeric_description_not_read_as_commission(self):
        # Ландмайна: `_num('Перевод 1500') == 1500.0`. При привязке к индексам описание
        # попадало в слот «Комиссия» и молча вычиталось из суммы (200 → 1700).
        rows = self._rows()
        rows[0].append(["25.06.2026\n10:00:00", "25.06.2026", "-200.00 RUB", "0.00 RUB",
                        "-200.00 RUB", "Перевод 1500", ""])
        t = _vtb_table_to_transactions(rows)
        assert t[3]["amount"] == pytest.approx(200.00)
        assert t[3]["description"] == "Перевод 1500"

    def test_column_map_detects_both_templates(self):
        b = _vtb_column_map(self._rows()[0])
        assert (b["prihod"], b["rashod"], b["desc"], b["party"]) == (3, 4, 5, 6)
        assert "komis" not in b
        a = _vtb_column_map(TestVtbRealLayout()._rows()[0])
        assert (a["prihod"], a["rashod"], a["komis"], a["desc"]) == (3, 4, 5, 6)


class TestVtbCommissionColumn:
    """В колонку «Комиссия» ВТБ кладёт и списания, и зачисления (кешбэк) при нулевых
    Приход/Расход. Знак — только из описания: на реальной майской выписке кешбэк 656 ₽
    уходил в расход, и приход недосчитывался ровно на 656 ₽ против итогов банка."""

    def _table(self, amount, description):
        return [[
            ["Дата и время\nоперации", "Дата обработки\nбанком",
             "Сумма операции в\nвалюте операции",
             "Сумма операции в валюте\nсчета/карты", "", "Комиссия", "Описание операции"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["07.05.2026\n13:41:20", "07.05.2026", "0.00 RUB", "0\nRUB", "0\nRUB",
             amount, description],
        ]]

    def test_cashback_in_commission_column_is_income(self):
        t = _vtb_table_to_transactions(self._table("656.00\nRUB",
                                                   "Зачисление кешбэка по программе лояльности."))
        assert t[0]["type"] == "income"
        assert t[0]["amount"] == pytest.approx(656.00)

    def test_commission_in_commission_column_is_expense(self):
        t = _vtb_table_to_transactions(self._table("69.01\nRUB", "Комиссия за обслуживание счета."))
        assert t[0]["type"] == "expense"
        assert t[0]["amount"] == pytest.approx(69.01)

    @pytest.mark.parametrize("desc", [
        "Зачисление кешбэка по программе лояльности.",
        "Возврат средств за отменённую покупку",
        "Начисление процентов на остаток",
    ])
    def test_credit_markers(self, desc):
        assert _vtb_table_to_transactions(self._table("100.00", desc))[0]["type"] == "income"

    @pytest.mark.parametrize("desc", [
        "Комиссия за обслуживание счета.",
        "Оплата за пролонгацию пакета Карты+.",
    ])
    def test_debit_markers(self, desc):
        assert _vtb_table_to_transactions(self._table("100.00", desc))[0]["type"] == "expense"


class TestOneCEncoding:
    """1C от банков РФ — windows-1251. Декодер форсит cp1251 по магии `1CClientBankExchange`,
    не полагаясь на «utf-8 удачно упал» (на других файлах может не упасть → каша)."""

    def test_decode_forces_cp1251_for_1c(self):
        raw = (TPL / "sberbank_1c_cp1251.bin").read_bytes()
        content = decode_statement_bytes(raw)
        assert content.startswith("1CClientBankExchange")
        assert "СекцияДокумент" in content  # кириллица раскодирована верно

    def test_cp1251_1c_parses_correctly(self):
        raw = (TPL / "sberbank_1c_cp1251.bin").read_bytes()
        txns = parse_bank_statement(decode_statement_bytes(raw))
        assert len(txns) == 2
        assert txns[0]["type"] == "expense" and txns[0]["amount"] == pytest.approx(5000.0)
        assert txns[1]["type"] == "income" and txns[1]["amount"] == pytest.approx(90000.0)

    def test_utf8_1c_still_parses(self):
        raw = (TPL / "sberbank_1c.txt").read_bytes()
        assert len(parse_1c_exchange(decode_statement_bytes(raw))) == 2

    def test_decode_csv_utf8(self):
        raw = "Дата;Сумма\n01.01.2026;-100.00\n".encode("utf-8")
        assert decode_statement_bytes(raw).startswith("Дата")


class TestNonStatementDetection:
    """Справки об остатке/реквизиты/о задолженности — не выписки. Операций нет; приложение
    должно распознать тип, а не показать «пустую выписку» (silent-0 опасен)."""

    @pytest.mark.parametrize("text,expected", [
        ("СберБанк\nСправка о доступном остатке\nЕвдокимов", "справка о доступном остатке"),
        ("Реквизиты счёта\n40817...", "реквизиты счёта"),
        ("Реквизиты счета для перевода", "реквизиты счёта"),
        ("Справка о задолженности по кредитным продуктам", "справка о задолженности"),
        ("Справка о видах и размерах пенсий", "справка о выплатах/пенсиях"),
        ("Справка о состоянии вклада", "справка о состоянии вклада"),
    ])
    def test_certificates_detected(self, text, expected):
        assert classify_non_statement(text) == expected

    def test_real_statement_not_flagged(self):
        # Настоящая выписка операций не должна опознаваться как справка.
        text = "Выписка по платёжному счёту\n02.07.2025 13:28 Перевод 550,00 0,00"
        assert classify_non_statement(text) is None
