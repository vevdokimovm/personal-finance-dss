"""
Сверка импорта выписки с контрольными итогами самого банка.

Зачем: тесты на фикстурах доказывают, что парсер не сломался, но не доказывают, что он
правильно прочитал КОНКРЕТНЫЙ реальный файл. Выписка почти всегда несёт собственные
контрольные суммы (поступления, расходные операции, баланс на начало/конец) — по ним парс
проверяется независимо, без ручной выверки. Если сумма распознанных операций сходится с
итогами банка и баланс замыкается — файл прочитан верно.

Реальные выписки содержат персональные данные и в репозиторий не кладутся. Инструмент
работает по пути к файлу на диске, ничего никуда не отправляет и не сохраняет.

Запуск:
    python -m tools.statement_audit.reconcile ~/Downloads/vypiska.pdf [ещё.pdf ...]

Важно про период: ВТБ считает контрольные итоги по ДАТЕ ОБРАБОТКИ банком, а операции
показывает по дате операции. Поэтому покупка от 29.06 с обработкой 02.07 в итоги июня не
входит, хотя в таблице она есть. Сверка это учитывает — иначе получаются ложные тревоги.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.statement_parser import (
    _num,
    _vtb_column_map,
    _vtb_row_to_transaction,
    classify_non_statement,
    parse_bank_pdf,
)

try:
    import pdfplumber
except ImportError:  # pragma: no cover - инструмент требует pdfplumber
    pdfplumber = None

RESET, RED, GREEN, YELLOW, BOLD = "\033[0m", "\033[31m", "\033[32m", "\033[33m", "\033[1m"


def info(msg: str) -> None:
    print(f"{YELLOW}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"{GREEN}✓{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}⚠{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}✗ {msg}{RESET}")


_BANK_MARKERS = (
    ('vtb', ('банк втб', 'втб (пао)', 'vtb')),
    ('sber', ('сбербанк', 'сбербанк', 'пао сбербанк')),
    ('tinkoff', ('тинькофф', 'т-банк', 'tinkoff')),
    ('raiffeisen', ('райффайзен', 'raiffeisen')),
)


def detect_bank(text: str) -> str | None:
    """Банк по содержимому выписки (имя файла не показатель — проверено на реальных файлах)."""
    low = text.lower()
    for bank, markers in _BANK_MARKERS:
        if any(mk in low for mk in markers):
            return bank
    return None


def _grab(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text)
    return _num(match.group(1)) if match else None


def declared_totals(text: str) -> dict[str, Any]:
    """Контрольные итоги, объявленные в самой выписке."""
    period = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})', text)
    return {
        'period': (period.group(1), period.group(2)) if period else None,
        'income': _grab(text, r'Поступления\s+([\d\s,.\u00a0]+)\s*RUB'),
        'expense': _grab(text, r'Расходные операции\s+([\d\s,.\u00a0]+)\s*RUB'),
        'balance_start': _grab(text, r'Баланс на начало периода\s+([\d\s,.\u00a0]+)\s*RUB'),
        'balance_end': _grab(text, r'Баланс на конец периода\s+([\d\s,.\u00a0]+)\s*RUB'),
    }


def vtb_totals_by_processing_date(tables: list, period: tuple[str, str] | None) -> dict[str, float]:
    """Суммы прихода/расхода по дате обработки — в той же логике, в какой считает банк."""
    start = datetime.strptime(period[0], '%d.%m.%Y') if period else None
    end = datetime.strptime(period[1], '%d.%m.%Y') if period else None
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
                    continue  # обработана вне периода — банк её в итоги не включает
            if txn['type'] == 'income':
                income += txn['amount']
            else:
                expense += txn['amount']
    return {'income': round(income, 2), 'expense': round(expense, 2)}


def _compare(label: str, got: float | None, want: float | None) -> bool:
    if want is None:
        warn(f"{label}: в выписке нет контрольного итога — сверить нечем")
        return True
    if got is not None and abs(got - want) < 0.01:
        ok(f"{label}: {got:,.2f} = {want:,.2f} (итог банка)".replace(',', ' '))
        return True
    fail(f"{label}: распознано {got:,.2f}, банк заявляет {want:,.2f} — "
         f"расхождение {abs((got or 0) - want):,.2f}".replace(',', ' '))
    return False


def reconcile_file(path: Path) -> bool:
    print(f"\n{BOLD}=== {path.name} ==={RESET}")
    raw = path.read_bytes()
    if raw[:5] != b'%PDF-':
        warn("не PDF — сверка поддержана только для PDF-выписок")
        return True
    with pdfplumber.open(path) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        tables = [t for page in pdf.pages for t in page.extract_tables()]

    reason = classify_non_statement(text)
    if reason:
        warn(f"это {reason}, а не выписка операций — операций тут нет по определению")
        return True

    bank = detect_bank(text)
    if bank is None:
        fail("банк не опознан по содержимому — сверка невозможна")
        return False
    info(f"банк: {bank}")

    transactions = parse_bank_pdf(raw, bank)
    info(f"распознано операций: {len(transactions)}")
    if not transactions:
        fail("операций не распознано — парсер не понял формат")
        return False

    blank = [t for t in transactions if t['description'] in ('', 'Операция')]
    if blank:
        warn(f"операций без описания: {len(blank)} — категоризатор по ним работать не сможет")

    declared = declared_totals(text)
    if bank != 'vtb':
        warn(f"сверка итогов реализована для ВТБ; для {bank} — только счёт операций")
        return True

    totals = vtb_totals_by_processing_date(tables, declared['period'])
    if declared['period']:
        info(f"период: {declared['period'][0]} - {declared['period'][1]} "
             "(итоги банка — по дате обработки)")
    good = _compare("приход", totals['income'], declared['income'])
    good &= _compare("расход", totals['expense'], declared['expense'])

    start, end = declared['balance_start'], declared['balance_end']
    if start is not None and end is not None:
        calc = round(start + totals['income'] - totals['expense'], 2)
        if abs(calc - end) < 0.01:
            ok(f"баланс замыкается: {start:,.2f} + {totals['income']:,.2f} − "
               f"{totals['expense']:,.2f} = {end:,.2f}".replace(',', ' '))
        else:
            good = False
            fail(f"баланс не замыкается: расчёт {calc:,.2f} vs выписка "
                 f"{end:,.2f}".replace(',', ' '))
    return good


def main(argv: list[str]) -> int:
    if pdfplumber is None:
        fail("нужен pdfplumber: pip install pdfplumber")
        return 2
    if not argv:
        print(__doc__)
        return 2
    results = []
    for arg in argv:
        path = Path(arg).expanduser()
        if not path.exists():
            fail(f"файл не найден: {path}")
            results.append(False)
            continue
        results.append(reconcile_file(path))
    print()
    if all(results):
        ok(f"ИТОГ: сверка пройдена ({len(results)} файл(ов))")
        return 0
    fail(f"ИТОГ: расхождения в {results.count(False)} из {len(results)} файл(ов)")
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
