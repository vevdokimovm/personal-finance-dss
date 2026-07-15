"""
Тесты сверки импорта с контрольными итогами, объявленными в самой выписке.

Сверка — единственное доказательство того, что КОНКРЕТНЫЙ файл прочитан верно: на живых
данных она поймала два дефекта, невидимых глазом (кешбэк, уходивший в расход, и кредитный
лимит, посчитанный доходом). Здесь заперты разборы контрольных сумм каждого банка и
политика вердикта: расхождение предупреждает, но не блокирует импорт.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.statement_parser import parse_raiffeisen_pdf, parse_vtb_pdf
from app.services.statement_parser import SKIP_SERVICE, SKIP_STATUS
from app.services.statement_reconcile import (
    _balance_delta,
    _raif_declared,
    _raif_declared_count,
    _sber_declared,
    _tinkoff_declared,
    completeness_verdict,
    csv_declared,
    _verdict,
    _vtb_declared,
    reconcile_statement,
)

TPL = Path("app/data/statement_templates")


def _txn(amount: float, t_type: str) -> dict:
    return {'amount': amount, 'type': t_type, 'description': 'x',
            'date': '2026-01-01T00:00:00', 'mcc': None, 'is_synced': True}


class TestVtbDeclared:
    def test_income_and_expense(self):
        text = ("Баланс на начало периода 3234.85 RUB Поступления 100624.00 RUB\n"
                "Баланс на конец периода 2573.76 RUB Расходные операции 101285.09 RUB")
        assert _vtb_declared(text) == {'income': 100624.00, 'expense': 101285.09}

    def test_thousands_separated_by_comma(self):
        # ВТБ печатает и «32,156.00», и «32156.00» — оба формата валидны.
        text = "Поступления 32,156.00 RUB\nРасходные операции 32,410.30 RUB"
        assert _vtb_declared(text) == {'income': 32156.00, 'expense': 32410.30}

    def test_absent_totals(self):
        assert _vtb_declared("Выписка по счёту") == {'income': None, 'expense': None}


class TestTinkoffDeclared:
    def test_cashback_added_to_income(self):
        # Тинькофф объявляет кэшбэк ОТДЕЛЬНОЙ строкой от поступлений, но деньги пришли
        # на счёт и парсер справедливо считает их приходом: 115 390 + 761 = 116 151.
        text = ("• Поступления 115 390.00 ₽\n"
                "• Расходы - 109 166.08 ₽\n"
                "• Кэшбэк 761.00 ₽")
        assert _tinkoff_declared(text) == {'income': 116151.00, 'expense': 109166.08}

    def test_without_cashback_line(self):
        text = "• Поступления 5 000.00 ₽\n• Расходы - 1 200.00 ₽"
        assert _tinkoff_declared(text) == {'income': 5000.00, 'expense': 1200.00}

    def test_absent_totals(self):
        assert _tinkoff_declared("Выписка по договору") == {'income': None, 'expense': None}


class TestRaifDeclared:
    """«Обороты 13 670,12 13 842,50» — два числа без подписей. Что из них приход,
    определяется порядком колонок в шапке: в RU-шаблоне первой идёт «Поступления»,
    в EN — «Debit», то есть порядок зеркальный."""

    RU = [[["№ П/П", "Дата операции", "Номер документа", "Поступления", "Расходы",
            "Детали операции", "Номер карты"]]]
    EN = [[["№ P/P", "Posting date", "Document number", "Debit", "Credit",
            "Payment details", "Card number"]]]

    def test_ru_order_income_first(self):
        text = "Обороты 13 670,12 13 842,50"
        assert _raif_declared(text, self.RU) == {'income': 13670.12, 'expense': 13842.50}

    def test_en_order_expense_first(self):
        text = "Turnover 13 670,12 13 842,50"
        assert _raif_declared(text, self.EN) == {'income': 13842.50, 'expense': 13670.12}

    def test_absent_turnover(self):
        # Шаблон без колонки «№» оборотов не печатает — сверять нечем, и это не ошибка.
        assert _raif_declared("Выписка", self.RU) == {'income': None, 'expense': None}


class TestVerdict:
    def test_ok_when_matches(self):
        result = _verdict({'income': 100.0, 'expense': 50.0}, {'income': 100.0, 'expense': 50.0})
        assert result['status'] == 'ok'
        assert 'сходится' in result['message']

    def test_mismatch_reports_both_numbers(self):
        result = _verdict({'income': 32156.0, 'expense': 32410.3},
                          {'income': 31500.0, 'expense': 33066.3})
        assert result['status'] == 'mismatch'
        assert '32 156.00' in result['message'] and '31 500.00' in result['message']

    def test_mismatch_does_not_block_import(self):
        # Политика: предупреждаем, но не блокируем — операции уже распознаны.
        result = _verdict({'income': 100.0, 'expense': 0.0}, {'income': 90.0, 'expense': 0.0})
        assert result['status'] == 'mismatch'
        assert 'импортированы' in result['message']

    def test_unavailable_when_nothing_declared(self):
        result = _verdict({'income': None, 'expense': None}, {'income': 10.0, 'expense': 5.0})
        assert result['status'] == 'unavailable'
        assert result['message'] == ''

    def test_tolerance_is_one_kopeck(self):
        assert _verdict({'income': 100.0, 'expense': 0.0},
                        {'income': 100.004, 'expense': 0.0})['status'] == 'ok'
        assert _verdict({'income': 100.0, 'expense': 0.0},
                        {'income': 100.02, 'expense': 0.0})['status'] == 'mismatch'


class TestReconcileStatement:
    def test_vtb_template_reconciles(self):
        raw = (TPL / "vtb.pdf").read_bytes()
        result = reconcile_statement(raw, 'vtb', parse_vtb_pdf(raw))
        assert result['status'] == 'ok'
        assert result['declared'] == {'income': 25000.0, 'expense': 1500.0}

    def test_raiffeisen_template_reconciles(self):
        raw = (TPL / "raiffeisen.pdf").read_bytes()
        result = reconcile_statement(raw, 'raiffeisen', parse_raiffeisen_pdf(raw))
        assert result['status'] == 'ok'

    def test_raiffeisen_wrong_transactions_detected_as_mismatch(self):
        raw = (TPL / "raiffeisen.pdf").read_bytes()
        result = reconcile_statement(raw, 'raiffeisen', [_txn(999.0, 'income')])
        assert result['status'] == 'mismatch'

    def test_vtb_sums_are_rederived_from_file(self):
        # Асимметрия по устройству: у ВТБ итоги считаются по ДАТЕ ОБРАБОТКИ, а её нет в
        # транзакции — поэтому суммы пересчитываются из таблицы файла, а не берутся из
        # переданного списка. Для остальных банков сверяется именно переданный список.
        raw = (TPL / "vtb.pdf").read_bytes()
        result = reconcile_statement(raw, 'vtb', [])
        assert result['status'] == 'ok'
        assert result['parsed'] == {'income': 25000.0, 'expense': 1500.0}

    def test_csv_is_unavailable(self):
        # Сверка построена на контрольных итогах PDF-выписки; CSV их не несёт.
        result = reconcile_statement(b"date;amount\n01.01.2026;-100", 'tinkoff',
                                     [_txn(100.0, 'expense')])
        assert result['status'] == 'unavailable'
        assert result['parsed'] == {'income': 0.0, 'expense': 100.0}

    def test_unsupported_bank_is_unavailable(self):
        raw = (TPL / "vtb.pdf").read_bytes()
        assert reconcile_statement(raw, 'sber', [])['status'] == 'unavailable'

    def test_broken_pdf_does_not_raise(self):
        # Битый PDF не должен ронять импорт: операции уже распознаны.
        result = reconcile_statement(b"%PDF-broken", 'vtb', [_txn(1.0, 'income')])
        assert result['status'] == 'unavailable'

    @pytest.mark.parametrize("bank", ['vtb', 'raiffeisen', 'tinkoff'])
    def test_parsed_sums_always_returned(self, bank):
        result = reconcile_statement(b"not a pdf", bank, [_txn(10.0, 'income'),
                                                          _txn(4.0, 'expense')])
        assert result['parsed'] == {'income': 10.0, 'expense': 4.0}


class TestSberDeclared:
    """Сбер печатает итоги в блоке «ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД», но в извлечённом
    тексте они разнесены по строкам с реквизитами счёта — искать надо по метке."""

    def test_popolnenie_and_spisanie(self):
        text = ("ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД:\n"
                "Номер счёта 40817 810 0 4010 2386464 Пополнение 1 649,00\n"
                "Валюта Российский рубль Списание 1 649,00")
        assert _sber_declared(text) == {'income': 1649.00, 'expense': 1649.00}

    def test_absent_totals(self):
        assert _sber_declared("Выписка по счёту") == {'income': None, 'expense': None}


class TestRaifTotalsFromTables:
    """Шаблон без колонки «№» строку «Обороты» не печатает, но кладёт итоги в таблицу."""

    def test_totals_from_table_rows_ru(self):
        tables = [[["Всего поступлений", "+ 14 281,50 ₽"],
                   ["Всего расходов", "- 14 281,50 ₽"]]]
        assert _raif_declared("Выписка без оборотов", tables) == {
            'income': 14281.50, 'expense': 14281.50}

    def test_totals_from_table_rows_en(self):
        tables = [[["Total income", "+ 14 281,50 ₽"], ["Total expenses", "- 14 281,50 ₽"]]]
        assert _raif_declared("Statement", tables) == {'income': 14281.50, 'expense': 14281.50}

    def test_turnover_line_wins_over_tables(self):
        tables = [[["№ П/П", "Дата операции", "x", "Поступления", "Расходы", "y", "z"]]]
        assert _raif_declared("Обороты 13 670,12 13 842,50", tables) == {
            'income': 13670.12, 'expense': 13842.50}


class TestRaifOperationCount:
    """«Количество операций 3 4» ловит пропуск строки даже там, где суммы сошлись."""

    def test_count_is_sum_of_both_columns(self):
        tables = [[["", "Количество операций", "", "3", "4", "", ""]]]
        assert _raif_declared_count(tables) == 7

    def test_absent_count(self):
        assert _raif_declared_count([[["Дата операции", "Сумма"]]]) is None


class TestBalanceDelta:
    """Изменение остатка — свидетель, независимый от заявленных сумм."""

    def test_vtb_balance_delta(self):
        text = ("Баланс на начало периода 3234.85 RUB Поступления 100624.00 RUB\n"
                "Баланс на конец периода 2573.76 RUB Расходные операции 101285.09 RUB")
        assert _balance_delta(text, 'vtb') == pytest.approx(-661.09)

    def test_tinkoff_two_balance_lines(self):
        text = "Баланс на 24.04.26 1 065.44 ₽\nБаланс на 23.05.26 8 050.36 ₽"
        assert _balance_delta(text, 'tinkoff') == pytest.approx(6984.92)

    def test_sber_balance_not_used(self):
        # У Сбера тождество не сходится у самого банка (реальная выписка: остаток −150 → 0
        # при нулевом нетто операций) — свидетель осознанно не подключён.
        assert _balance_delta("Остаток на 01.06.2024 -150,00", 'sber') is None

    def test_absent_balances(self):
        assert _balance_delta("Выписка", 'vtb') is None


class TestMultipleWitnesses:
    def test_extra_witness_can_fail_alone(self):
        # Суммы сошлись, а остаток — нет: это всё равно расхождение.
        result = _verdict({'income': 100.0, 'expense': 50.0}, {'income': 100.0, 'expense': 50.0},
                          [('изменение остатка', 999.0, 50.0)])
        assert result['status'] == 'mismatch'
        assert 'изменение остатка' in result['message']

    def test_checked_witnesses_listed(self):
        result = _verdict({'income': 100.0, 'expense': 50.0}, {'income': 100.0, 'expense': 50.0},
                          [('изменение остатка', 50.0, 50.0)])
        assert result['status'] == 'ok'
        assert result['checked'] == ['приход', 'расход', 'изменение остатка']


class TestCsvDeclared:
    """Считалось, что CSV сверить нечем. На реальной выписке Альфа-Банка контрольные итоги
    лежат в метаданных отдельными ячейками — и парс сходится с ними до копейки."""

    ALFA = ('"Дата открытия счета","","24.12.2018","","","","","","","",'
            '"Поступления","","","224\u00a0805,37 RUR"\n'
            '"Валюта счета","","RUR","","","","","","","",'
            '"Расходы","","","221\u00a0195,56 RUR"\n')

    def test_totals_from_metadata_cells(self):
        assert csv_declared(self.ALFA) == {'income': 224805.37, 'expense': 221195.56}

    def test_table_header_is_not_mistaken_for_totals(self):
        # «Поступления»/«Расходы» — ещё и названия колонок. Справа от них в шапке чисел
        # нет, поэтому точный матч метки не даёт ложного срабатывания.
        header = ('"Дата операции";"Номер документа";"Поступления";"Расходы";"Валюта"\n'
                  '"17.01.2025";"ZP001";"";"2 670,12";"RUB"\n')
        assert csv_declared(header) == {'income': None, 'expense': None}

    def test_no_totals(self):
        assert csv_declared("Дата;Сумма\n01.01.2026;-100") == {'income': None, 'expense': None}


class TestCompletenessVerdict:
    """Полнота разбора — единственная проверка для CSV без контрольных сумм. Отвечает не на
    вопрос «верны ли суммы», а на «не потеряли ли мы строки молча»."""

    def test_all_rows_parsed(self):
        report = {'rows': 14, 'parsed': 14, 'skipped': {}}
        result = completeness_verdict(report, {'income': 1.0, 'expense': 2.0})
        assert result['status'] == 'ok'
        assert result['checked'] == ['полнота разбора']

    def test_explained_skips_are_ok(self):
        # Отклонённые банком операции и подвал документа — законные пропуски.
        report = {'rows': 12788, 'parsed': 12614,
                  'skipped': {SKIP_STATUS: 174, SKIP_SERVICE: 0}}
        assert completeness_verdict(report, {'income': 0.0, 'expense': 0.0})['status'] == 'ok'

    def test_silent_loss_is_mismatch(self):
        # Ровно этот случай был реальным: у выписки Райффайзена терялись ВСЕ приходы.
        report = {'rows': 14, 'parsed': 8, 'skipped': {'сумма не распознана': 6}}
        result = completeness_verdict(report, {'income': 0.0, 'expense': 100.0})
        assert result['status'] == 'mismatch'
        assert 'не разобрано 6' in result['message']

    def test_message_names_what_was_proven(self):
        report = {'rows': 5, 'parsed': 5, 'skipped': {}}
        message = completeness_verdict(report, {'income': 0.0, 'expense': 0.0})['message']
        assert 'сверены не суммы' in message
