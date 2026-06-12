"""
Парсеры банковских выписок (CSV / Excel).
Поддерживаемые банки:
  - Тинькофф (CSV-выписка из личного кабинета)
  - Сбербанк (CSV-выписка)
  - Универсальный формат (дата, категория, сумма, тип)

DATA-04: описание операции и MCC сохраняются в отдельном поле `description`
и НЕ склеиваются в строку категории — это сырьё для категоризатора (FR-13)
и merchant-аналитики (FR-14).
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from typing import Any

try:
    import pdfplumber
except ImportError:  # PDF-парсер опционален: без него работает всё, кроме импорта PDF
    pdfplumber = None


def _classify(amount: float) -> tuple[str, float]:
    """Знак суммы → тип операции. Возвращает (type, abs_amount)."""
    if amount < 0:
        return "expense", abs(amount)
    return "income", amount


def parse_tinkoff_csv(content: str) -> list[dict[str, Any]]:
    """
    Парсит CSV-выписку из Тинькофф Банка.

    Формат Тинькофф (обычно с разделителем ;):
    Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;
    Валюта операции;Сумма платежа;Валюта платежа;Кэшбэк;Категория;MCC;Описание
    """
    transactions = []
    delimiter = ';' if ';' in content[:500] else ','
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lstrip('\ufeff') for f in reader.fieldnames]

    for row in reader:
        try:
            date_str = _get_field(row, ['Дата операции', 'Дата платежа', 'date'])
            amount_str = _get_field(row, ['Сумма платежа', 'Сумма операции', 'amount'])
            category = _get_field(row, ['Категория', 'category']) or 'Без категории'
            description = _get_field(row, ['Описание', 'description'])
            mcc = _get_field(row, ['MCC', 'mcc'])
            status = _get_field(row, ['Статус', 'status']) or ''

            if status and status.upper() not in ('OK', 'COMPLETED', ''):
                continue
            if not amount_str:
                continue

            amount = float(amount_str.replace(' ', '').replace(',', '.').replace('\xa0', ''))
            t_date = _parse_date(date_str) if date_str else datetime.now()
            t_type, amount = _classify(amount)

            merchant = (description.strip() if description else '') or category.strip() or 'Операция'
            transactions.append({
                'amount': round(amount, 2),
                'description': merchant[:255],
                'mcc': mcc,
                'type': t_type,
                'date': t_date.isoformat(),
                'is_synced': True,
            })
        except (ValueError, KeyError, TypeError):
            continue

    return transactions


def parse_sber_csv(content: str) -> list[dict[str, Any]]:
    """
    Парсит CSV-выписку из Сбербанка.
    Формат обычно: №;Дата;Описание;Категория;Сумма;Валюта;Статус
    """
    transactions = []
    delimiter = ';' if ';' in content[:500] else ','
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lstrip('\ufeff') for f in reader.fieldnames]

    for row in reader:
        try:
            date_str = _get_field(row, ['Дата', 'Дата операции', 'date'])
            amount_str = _get_field(row, ['Сумма', 'Сумма операции', 'amount'])
            category = _get_field(row, ['Категория', 'category']) or 'Без категории'
            description = _get_field(row, ['Описание', 'Назначение', 'description'])

            if not amount_str:
                continue

            amount = float(amount_str.replace(' ', '').replace(',', '.').replace('\xa0', ''))
            t_date = _parse_date(date_str) if date_str else datetime.now()
            t_type, amount = _classify(amount)

            merchant = (description.strip() if description else '') or category.strip() or 'Операция'
            transactions.append({
                'amount': round(amount, 2),
                'description': merchant[:255],
                'mcc': None,
                'type': t_type,
                'date': t_date.isoformat(),
                'is_synced': True,
            })
        except (ValueError, KeyError, TypeError):
            continue

    return transactions


def parse_universal_csv(content: str) -> list[dict[str, Any]]:
    """
    Универсальный парсер — пытается найти колонки с датой, суммой, категорией.
    Работает с любым банком если в CSV есть хотя бы дата и сумма.
    """
    transactions = []
    delimiter = ';' if ';' in content[:500] else ','
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lstrip('\ufeff') for f in reader.fieldnames]

    for row in reader:
        try:
            date_str = _get_field(row, [
                'Дата операции', 'Дата платежа', 'Дата', 'Date', 'date',
                'Дата транзакции', 'Transaction Date'
            ])
            amount_str = _get_field(row, [
                'Сумма платежа', 'Сумма операции', 'Сумма', 'Amount', 'amount',
                'Сумма в валюте счёта', 'Sum'
            ])
            category = _get_field(row, ['Категория', 'Category']) or 'Импорт'
            description = _get_field(row, [
                'Описание', 'Назначение', 'Description', 'Merchant', 'MCC Description'
            ])
            mcc = _get_field(row, ['MCC', 'mcc'])

            if not amount_str:
                continue

            amount = float(amount_str.replace(' ', '').replace(',', '.').replace('\xa0', ''))
            t_date = _parse_date(date_str) if date_str else datetime.now()
            t_type, amount = _classify(amount)

            merchant = (description.strip() if description else '') or category.strip() or 'Импорт'
            transactions.append({
                'amount': round(amount, 2),
                'description': merchant[:255],
                'mcc': mcc,
                'type': t_type,
                'date': t_date.isoformat(),
                'is_synced': True,
            })
        except (ValueError, KeyError, TypeError):
            continue

    return transactions


# ── Helpers ───────────────────────────────────────────────────

def _get_field(row: dict, candidates: list[str]) -> str | None:
    """Ищет первое совпадение из списка кандидатов в строке CSV."""
    for key in candidates:
        if key in row and row[key] and row[key].strip():
            return row[key].strip()
    return None


def _parse_date(s: str) -> datetime:
    """Парсит дату из различных форматов."""
    if not s:
        return datetime.now()

    s = s.strip()
    formats = [
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',
        '%d.%m.%Y',
        '%d.%m.%y %H:%M',
        '%d.%m.%y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue

    return datetime.now()


# Маппинг банков → парсеров
# ── PDF-выписка Тинькофф ──────────────────────────────────────────────────
_PDF_DATE = r"\d{2}\.\d{2}\.\d{2}"
# Строка операции: дата [время] дата_обработки описание [знак] сумма ₽.
# Сумма берётся последняя в строке («в валюте счёта») — она не склеивается
# с числами из описания. Знак «+» → поступление, иначе расход.
_PDF_OP = re.compile(
    rf"^({_PDF_DATE})(?:\s+\d{{2}}:\d{{2}})?\s+{_PDF_DATE}\s+(.+?)\s+([+\-]?)\s*"
    rf"(\d{{1,3}}(?:\s\d{{3}})*[.,]\d{{2}})\s*₽\s*$"
)


def parse_tinkoff_pdf(raw: bytes) -> list[dict[str, Any]]:
    """Парсит PDF-выписку Тинькофф: извлекает операции по картам."""
    if pdfplumber is None:
        raise ValueError("Для импорта PDF установите pdfplumber: pip install pdfplumber")
    transactions: list[dict[str, Any]] = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                match = _PDF_OP.match(line.strip())
                if match is None:
                    continue
                date_str, description, sign, amount_str = match.groups()
                amount = float(
                    amount_str.replace(" ", "").replace("\u00a0", "").replace(",", ".")
                )
                merchant = description.strip() or "Операция"
                transactions.append({
                    "amount": round(amount, 2),
                    "description": merchant[:255],
                    "mcc": None,
                    "type": "income" if sign == "+" else "expense",
                    "date": _parse_date(date_str).isoformat(),
                    "is_synced": True,
                })
    return transactions


BANK_PARSERS = {
    'tinkoff': parse_tinkoff_csv,
    'sber': parse_sber_csv,
    'alfa': parse_universal_csv,
    'vtb': parse_universal_csv,
    'raiffeisen': parse_universal_csv,
    'universal': parse_universal_csv,
}


def parse_bank_statement(content: str, bank_id: str = 'universal') -> list[dict[str, Any]]:
    """Выбирает парсер по bank_id и парсит выписку."""
    parser = BANK_PARSERS.get(bank_id, parse_universal_csv)
    return parser(content)
