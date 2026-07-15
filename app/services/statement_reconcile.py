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

import csv
import io
import re
from datetime import datetime
from typing import Any

from app.services.statement_parser import (
    SKIP_SERVICE,
    SKIP_STATUS,
    SKIP_ZERO,
    _norm,
    _num,
    _raif_column_map,
    _vtb_column_map,
    _vtb_row_to_transaction,
    decode_statement_bytes,
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


_RE_SBER_INCOME = re.compile(r'Пополнение\s+([\d\s\u00a0.,]+)')
_RE_SBER_EXPENSE = re.compile(r'Списание\s+([\d\s\u00a0.,]+)')
_RE_VTB_BAL_START = re.compile(r'Баланс на начало периода\s+(-?[\d\s\u00a0.,]+?)\s*RUB')
_RE_VTB_BAL_END = re.compile(r'Баланс на конец периода\s+(-?[\d\s\u00a0.,]+?)\s*RUB')
_RE_TINKOFF_BALANCE = re.compile(r'Баланс на \d{2}\.\d{2}\.\d{2}\s+(-?[\d\s\u00a0.,]+?)\s*₽')


# Контрольные итоги в CSV. Считалось, что CSV сверить нечем — на реальной выписке
# Альфа-Банка они лежат в метаданных над таблицей отдельными ячейками:
# «Поступления», "", "", "224 805,37 RUR». Регулярка по сырому тексту здесь бесполезна
# (между меткой и значением — пустые ячейки в кавычках), поэтому читаем именно ячейки.
_CSV_TOTAL_LABELS = {
    'income': ('поступления', 'поступление', 'пополнение', 'всего поступлений'),
    'expense': ('расходы', 'расход', 'списание', 'всего расходов'),
}

# Пропуски, которые НЕ являются потерей данных: банк сам отклонил операцию, строка —
# оформление документа, либо движения нет. Всё остальное — наш промах, и о нём надо
# сказать вслух: на файле в 12 788 строк потеря полусотни иначе незаметна.
_EXPLAINED_SKIPS = (SKIP_STATUS, SKIP_SERVICE, SKIP_ZERO)


def csv_declared(text: str) -> dict[str, float | None]:
    """Контрольные итоги из метаданных CSV, если банк их печатает.

    Метка сверяется ТОЧНО, а не по подстроке: «Поступления»/«Расходы» — это ещё и названия
    колонок таблицы, и подстрочный матч принял бы шапку за итоги. В строке-шапке справа от
    метки чисел нет, поэтому ложного срабатывания не возникает.
    """
    head = text[:4000]
    delimiter = ';' if head.count(';') > head.count(',') else ','
    result: dict[str, float | None] = {'income': None, 'expense': None}
    for row in csv.reader(io.StringIO(text), delimiter=delimiter):
        cells = [str(c) for c in row]
        for i, cell in enumerate(cells):
            label = _norm(cell)
            for role, labels in _CSV_TOTAL_LABELS.items():
                if result[role] is not None or label not in labels:
                    continue
                value = next((_num(c) for c in cells[i + 1:] if _num(c) is not None), None)
                if value is not None:
                    result[role] = abs(value)
    return result


def completeness_verdict(report: dict, parsed: dict) -> dict[str, Any]:
    """Вердикт по полноте разбора: все ли строки файла превратились в операции.

    Для CSV это часто единственная доступная проверка — контрольных сумм в нём обычно нет.
    Она отвечает не на вопрос «верны ли суммы», а на вопрос «не потеряли ли мы строки
    молча», и именно так был найден дефект, из-за которого у выписки Райффайзена терялись
    ВСЕ приходы (14 строк → 8 операций).
    """
    rows = report.get('rows', 0)
    skipped = report.get('skipped', {}) or {}
    explained = sum(n for reason, n in skipped.items() if reason in _EXPLAINED_SKIPS)
    lost = {reason: n for reason, n in skipped.items() if reason not in _EXPLAINED_SKIPS}
    base = {'declared': {'income': None, 'expense': None}, 'parsed': parsed,
            'checked': ['полнота разбора']}
    if lost:
        details = ", ".join(f"{reason}: {n}" for reason, n in lost.items())
        return {**base, 'status': 'mismatch',
                'message': (f"Из {rows} строк файла не разобрано {sum(lost.values())} "
                            f"({details}). Операции импортированы, но часть данных потеряна.")}
    note = f", {explained} пропущено по причине банка/оформления" if explained else ""
    return {**base, 'status': 'ok',
            'message': (f"Разобраны все строки файла: {report.get('parsed', 0)} операций из "
                        f"{rows}{note}. Контрольных сумм файл не содержит — сверены не суммы, "
                        f"а полнота разбора.")}


def _sums(transactions: list[dict[str, Any]]) -> dict[str, float]:
    income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    return {'income': round(income, 2), 'expense': round(expense, 2)}


def _money(value: float) -> str:
    return f"{value:,.2f}".replace(',', ' ')


def _sber_declared(text: str) -> dict[str, float | None]:
    """Итоги Сбера: блок «ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД» → «Пополнение X» / «Списание Y».
    В извлечённом тексте они разнесены по строкам с реквизитами счёта, поэтому ищем по
    метке, а не по позиции."""
    income = _RE_SBER_INCOME.search(text)
    expense = _RE_SBER_EXPENSE.search(text)
    return {
        'income': _num(income.group(1)) if income else None,
        'expense': _num(expense.group(1)) if expense else None,
    }


def _raif_totals_from_tables(tables: list) -> dict[str, float | None]:
    """Шаблон Райффайзена без колонки «№» не печатает строку «Обороты», но кладёт итоги
    в таблицу: «Всего поступлений + 14 281,50 ₽» / «Total income»."""
    income = expense = None
    for table in tables:
        for row in table:
            cells = [str(c) for c in row if c]
            if len(cells) < 2:
                continue
            label, value = _norm(cells[0]), _num(cells[1])
            if value is None:
                continue
            if 'всего поступлений' in label or 'total income' in label:
                income = abs(value)
            elif 'всего расходов' in label or 'total expenses' in label:
                expense = abs(value)
    return {'income': income, 'expense': expense}


def _raif_declared_count(tables: list) -> int | None:
    """«Количество операций 3 4» — счётчик приходов и расходов. Проверяет полноту набора:
    ловит пропуск или задвоение строки даже там, где суммы случайно сошлись."""
    for table in tables:
        for row in table:
            cells = [str(c) for c in row if c]
            if len(cells) >= 3 and 'количество операций' in _norm(cells[0]):
                first, second = _num(cells[1]), _num(cells[2])
                if first is not None and second is not None:
                    return int(first + second)
    return None


def _balance_delta(text: str, bank_id: str) -> float | None:
    """Изменение остатка: остаток_конец − остаток_начало. Свидетель, независимый от
    заявленных сумм.

    Только для ВТБ и Тинькоффа, где тождество эмпирически замыкается. У Сбера оно НЕ
    сходится у самого банка (в реальной выписке остаток шёл −150 → 0 при нулевом нетто
    операций), поэтому вешать на него вердикт там нельзя: получили бы ложную тревогу на
    полностью исправном парсе.
    """
    if bank_id == 'vtb':
        start, end = _RE_VTB_BAL_START.search(text), _RE_VTB_BAL_END.search(text)
        if start and end:
            first, last = _num(start.group(1)), _num(end.group(1))
            if first is not None and last is not None:
                return round(last - first, 2)
    if bank_id == 'tinkoff':
        found = _RE_TINKOFF_BALANCE.findall(text)
        if len(found) >= 2:
            first, last = _num(found[0]), _num(found[1])
            if first is not None and last is not None:
                return round(last - first, 2)
    return None


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
        return _raif_totals_from_tables(tables)
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


def _verdict(declared: dict, parsed: dict,
             extras: list[tuple[str, Any, Any]] | None = None) -> dict[str, Any]:
    """Вердикт по нескольким независимым свидетелям: заявленные суммы плюс, где есть,
    изменение остатка и количество операций. Чем больше свидетелей сошлось, тем сильнее
    доказательство: суммы могут совпасть при взаимно погасившихся ошибках, счётчик
    операций ловит пропуск строки, а остаток проверяет нетто независимо от сумм."""
    pairs = [('приход', declared.get('income'), parsed['income']),
             ('расход', declared.get('expense'), parsed['expense'])]
    pairs += list(extras or [])
    checked = [(name, want, got) for name, want, got in pairs if want is not None]
    if not checked:
        return {
            'status': 'unavailable',
            'declared': declared,
            'parsed': parsed,
            'checked': [],
            'message': '',
        }
    bad = [(name, want, got) for name, want, got in checked if abs(got - want) >= TOLERANCE]
    if not bad:
        witnesses = ", ".join(name for name, _, _ in checked)
        return {
            'status': 'ok',
            'declared': declared,
            'parsed': parsed,
            'checked': [name for name, _, _ in checked],
            'message': (f"Сверено с итогами банка: приход {_money(parsed['income'])} ₽, "
                        f"расход {_money(parsed['expense'])} ₽ — сходится "
                        f"(проверено: {witnesses})."),
        }
    details = "; ".join(
        f"{name}: распознано {_money(got)} ₽, банк заявляет {_money(want)} ₽"
        for name, want, got in bad
    )
    return {
        'status': 'mismatch',
        'declared': declared,
        'parsed': parsed,
        'checked': [name for name, _, _ in checked],
        'message': (f"Расхождение с итогами банка ({details}). Операции импортированы, "
                    f"но выписку стоит проверить."),
    }


def reconcile_statement(raw: bytes, bank_id: str,
                        transactions: list[dict[str, Any]],
                        report: dict | None = None) -> dict[str, Any]:
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
    if raw[:5] != b'%PDF-':
        # Текстовая выписка. Контрольные итоги в CSV — редкость, но встречаются
        # (Альфа-Банк печатает их в метаданных над таблицей); если их нет, проверяем
        # хотя бы полноту разбора.
        text = decode_statement_bytes(raw)
        declared = csv_declared(text)
        if declared['income'] is not None or declared['expense'] is not None:
            return _verdict(declared, parsed)
        if report:
            return completeness_verdict(report, parsed)
        return _verdict(empty, parsed)
    if pdfplumber is None:
        return _verdict(empty, parsed)
    try:
        text, tables = _read_pdf(raw)
    except Exception:  # битый PDF не должен ронять импорт — операции уже распознаны
        return _verdict(empty, parsed)

    if bank_id == 'vtb':
        totals = _vtb_parsed_by_processing_date(tables, text)
        return _verdict(_vtb_declared(text), totals, _balance_extras(text, 'vtb', totals))
    if bank_id == 'raiffeisen':
        extras: list[tuple[str, Any, Any]] = []
        count = _raif_declared_count(tables)
        if count is not None:
            extras.append(('количество операций', float(count), float(len(transactions))))
        return _verdict(_raif_declared(text, tables), parsed, extras)
    if bank_id == 'tinkoff':
        return _verdict(_tinkoff_declared(text), parsed, _balance_extras(text, 'tinkoff', parsed))
    if bank_id == 'sber':
        return _verdict(_sber_declared(text), parsed)
    return _verdict(empty, parsed)


def _balance_extras(text: str, bank_id: str,
                    totals: dict[str, float]) -> list[tuple[str, Any, Any]]:
    """Изменение остатка как дополнительный свидетель (там, где тождество замыкается)."""
    delta = _balance_delta(text, bank_id)
    if delta is None:
        return []
    return [('изменение остатка', delta, round(totals['income'] - totals['expense'], 2))]
