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
from app.services.statement_reconcile import (
    _raif_declared,
    _tinkoff_declared,
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
