"""
Сверка импорта выписки с контрольными итогами, которые несёт сама выписка.

Зачем: тесты на фикстурах доказывают, что парсер не сломался, но не доказывают, что он
верно прочитал КОНКРЕТНЫЙ файл пользователя. Почти каждая выписка объявляет собственные
контрольные суммы (поступления, расходы, обороты, баланс). Сверка с ними — независимое
доказательство корректности импорта на живом файле, без ручной выверки. Именно так на
реальных данных были пойманы два дефекта, невидимых глазом: кешбэк, уходивший в расход
(приход недосчитывался ровно на его сумму), и потеря половины операций.

Политика при расхождении (решение владельца): **предупредить, но не блокировать**.
Операции сохраняются, пользователь видит расхождение. Блокировка опаснее: наш собственный
промах в чтении итогов оставил бы человека вообще без импорта.

Тонкость периода: ВТБ показывает операции по дате операции, а итоги считает по ДАТЕ
ОБРАБОТКИ банком. Покупка от 29.06 с обработкой 02.07 в итоги июня не входит, хотя в
таблице она есть. Без этого сверка даёт ложные тревоги ровно на таких операциях.
"""
from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Any

from app.services.statement_parser import (
    _num,
    _raif_column_map,
    _vtb_column_map,
    _vtb_row_to_transaction,
)

try:
    import pdfplumber
except ImportError:  # PDF-сверка опциональна, как и сам PDF-импорт
    pdfplumber = None

TOLERANCE = 0.01

_RE_PERIOD = re.compile(r'(\d{2}\.\d{2}\.\d{4})\s*[-—]\s*(\d{2}\.\d{2}\.\d{4})')
_RE_VTB_INCOME = re.compile(r'Поступления\s+([\d\s\u00a0.,]+?)\s*RUB')
_RE_VTB_EXPENSE = re.compile(r'Расходные операции\s+([\d\s\u00a0.,]+?)\s*RUB')
_RE_TINKOFF_INCOME = re.compile(r'Поступления\s+([\d\s\u00a0.,]+?)\s*₽')
_RE_TINKOFF_EXPENSE = re.compile(r'Расходы[\s:]*-?\s*([\d\s\u00a0.,]+?)\s*₽')
_RE_TINKOFF_CASHBACK = re.compile(r'Кэшбэк\s+([\d\s\u00a0.,]+?)\s*₽')
_RE_RAIF_TURNOVER = re.compile(
    r"(?:Обороты|Turnover)\s+([\d\s\u00a0]+,\d{2})\s+([\d\s\u00a0]+,\d{2})")


def _sums(transactions: list[dict[str, Any]]) -> dict[str, float]:
    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    return {'income': round(income, 2), 'expense': round(expense, 2)}


def _money(value: float) -> str:
    return f"{value:,.2f}".replace(',', ' ')


def _vtb_declared(text: str) -> dict[str, float | None]:
    income = _RE_VTB_INCOME.search(text)
    expense = _RE_VTB_EXPENSE.search(text)
    return {
        'income': _num(income.group(1)) if income else None,
        'expense': _num(expense.group(1)) if expense else None,
    }


def _tinkoff_declared(text: str) -> dict[str, float | None]:
    """Итоги Тинькоффа. Кэшбэк он объявляет ОТДЕЛЬНОЙ строкой от «Поступлений»
    («• Поступления 115 390.00 ₽ / • Расходы - 109 166.08 ₽ / • Кэшбэк 761.00 ₽»),
    но деньги пришли на счёт, и парсер справедливо считает его операцией прихода —
    поэтому в контрольную сумму прихода кэшбэк добавляется."""
    income = _RE_TINKOFF_INCOME.search(text)
    expense = _RE_TINKOFF_EXPENSE.search(text)
    cashback = _RE_TINKOFF_CASHBACK.search(text)
    declared_income = _num(income.group(1)) if income else None
    if declared_income is not None and cashback:
        declared_income += _num(cashback.group(1)) or 0.0
    declared_expense = _num(expense.group(1)) if expense else None
    return {
        'income': round(declared_income, 2) if declared_income is not None else None,
        'expense': abs(declared_expense) if declared_expense else None,
    }


def _raif_declared(text: str, tables: list) -> dict[str, float | None]:
    """Обороты Райффайзена — два числа в строке. Порядок берём из шапки таблицы: в
    русском шаблоне первой идёт колонка «Поступления», в английском — «Debit»."""
    match = _RE_RAIF_TURNOVER.search(text)
    if not match:
        return {'income': None, 'expense': None}
    first, second = _num(match.group(1)), _num(match.group(2))
    credit_first = True
    for table in tables:
        cmap = _raif_column_map(table)
        if 'credit' in cmap and 'debit' in cmap:
            credit_first = cmap['credit'] < cmap['debit']
            break
    return ({'income': first, 'expense': second} if credit_first
            else {'income': second, 'expense': first})


def _vtb_parsed_by_processing_date(tables: list, text: str) -> dict[str, float]:
    """Суммы ВТБ в той же логике, в какой считает банк, — по дате обработки."""
    period = _RE_PERIOD.search(text)
    start = datetime.strptime(period.group(1), '%d.%m.%Y') if period else None
    end = datetime.strptime(period.group(2), '%d.%m.%Y') if period else None
    income = expense = 0.0
    cmap: dict[str, int] = {}
    for table in tables:
        cmap = _vtb_column_map(table) or cmap
        for row in table:
            if not row or not row[0] or not re.match(r'\d{2}\.\d{2}\.\d{4}', str(row[0])):
                continue
            txn = _vtb_row_to_transaction(row, cmap, str(row[0])[:10])
            if not txn:
                continue
            processed = re.match(r'(\d{2}\.\d{2}\.\d{4})', str(row[1] or ''))
            if processed and start:
                date = datetime.strptime(processed.group(1), '%d.%m.%Y')
                if not start <= date <= end:
                    continue  # обработана вне периода — в итоги банка не входит
            if txn['type'] == 'income':
                income += txn['amount']
            else:
                expense += txn['amount']
    return {'income': round(income, 2), 'expense': round(expense, 2)}


def _read_pdf(raw: bytes) -> tuple[str, list]:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        tables = [t for page in pdf.pages for t in page.extract_tables()]
    return text, tables


def _verdict(declared: dict, parsed: dict) -> dict[str, Any]:
    pairs = [(name, declared.get(name), parsed[name]) for name in ('income', 'expense')]
    checked = [(name, want, got) for name, want, got in pairs if want is not None]
    if not checked:
        return {
            'status': 'unavailable',
            'declared': declared,
            'parsed': parsed,
            'message': '',
        }
    bad = [(name, want, got) for name, want, got in checked if abs(got - want) >= TOLERANCE]
    if not bad:
        return {
            'status': 'ok',
            'declared': declared,
            'parsed': parsed,
            'message': (f"Сверено с итогами банка: приход {_money(parsed['income'])} ₽, "
                        f"расход {_money(parsed['expense'])} ₽ — сходится."),
        }
    label = {'income': 'приход', 'expense': 'расход'}
    details = "; ".join(
        f"{label[name]}: распознано {_money(got)} ₽, банк заявляет {_money(want)} ₽"
        for name, want, got in bad
    )
    return {
        'status': 'mismatch',
        'declared': declared,
        'parsed': parsed,
        'message': (f"Расхождение с итогами банка ({details}). Операции импортированы, "
                    f"но выписку стоит проверить."),
    }


def reconcile_statement(raw: bytes, bank_id: str,
                        transactions: list[dict[str, Any]]) -> dict[str, Any]:
    """Сверяет распознанные операции с контрольными итогами выписки.

    Возвращает `{status, declared, parsed, message}`, где status:
    `ok` — сошлось, `mismatch` — расхождение, `unavailable` — сверить нечем
    (выписка не объявляет итогов либо формат банка пока не поддержан).

    Асимметрия по устройству: у ВТБ итоги считаются по дате обработки, а её в транзакции
    нет, поэтому суммы пересчитываются из таблицы файла; у остальных банков сверяется
    именно переданный список `transactions`.
    """
    parsed = _sums(transactions)
    empty = {'income': None, 'expense': None}
    if pdfplumber is None or raw[:5] != b'%PDF-':
        return _verdict(empty, parsed)
    try:
        text, tables = _read_pdf(raw)
    except Exception:  # битый PDF не должен ронять импорт — операции уже распознаны
        return _verdict(empty, parsed)

    if bank_id == 'vtb':
        return _verdict(_vtb_declared(text), _vtb_parsed_by_processing_date(tables, text))
    if bank_id == 'raiffeisen':
        return _verdict(_raif_declared(text, tables), parsed)
    if bank_id == 'tinkoff':
        return _verdict(_tinkoff_declared(text), parsed)
    return _verdict(empty, parsed)
