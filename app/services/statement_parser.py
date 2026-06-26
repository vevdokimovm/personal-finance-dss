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

try:
    import openpyxl
except ImportError:  # XLSX-парсер опционален: без него работает всё, кроме импорта XLSX
    openpyxl = None


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


# ── Универсальный табличный парсер (CSV + XLSX) ───────────────────────────
# Синонимы заголовков (нормализованные: \xa0→' ', ё→е, нижний регистр). Матчинг —
# по подстроке, поэтому «Сумма в валюте счёта» ловится кандидатом «сумма».
_H_DATE = ['дата операции', 'дата проводки', 'дата платежа', 'дата транзакции',
           'дата', 'transaction date', 'date']
_H_AMOUNT = ['сумма в валюте счета', 'сумма операции', 'сумма платежа', 'сумма',
             'amount', 'sum']
_H_CREDIT = ['приход', 'поступление', 'зачисление', 'кредит', 'credit']
_H_DEBIT = ['расход', 'списание', 'дебет', 'debit']
_H_CATEGORY = ['категория', 'category']
_H_DESC = ['назначение платежа', 'назначение', 'описание', 'description', 'merchant']
_H_MCC = ['mcc']


def _norm(value: Any) -> str:
    """Нормализует заголовок/ячейку для матчинга: неразрывный пробел, ё→е, регистр."""
    return re.sub(r'\s+', ' ', str(value).replace('\xa0', ' ').replace('ё', 'е')).strip().lower()


def _field(row: dict, candidates: list[str]) -> str | None:
    """Значение колонки по списку синонимов заголовка (нормализованный матч по подстроке)."""
    norm_row = [(_norm(k), v) for k, v in row.items() if k is not None]
    for cand in candidates:
        nc = _norm(cand)
        for nk, value in norm_row:
            if (nc == nk or nc in nk) and value is not None and str(value).strip():
                return str(value)
    return None


def _num(value: str | None) -> float | None:
    """«−2\xa0000,50» / «8 500» / «1 114,54 RUR» → float. Чужие символы отбрасываются."""
    if value is None:
        return None
    s = str(value).replace('\xa0', '').replace(' ', '').replace('\u2212', '-').replace(',', '.')
    s = re.sub(r'[^0-9.\-+]', '', s)
    if s in ('', '-', '+', '.', '-.', '+.'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _is_header_row(cells: list[Any]) -> bool:
    """Строка-заголовок: есть колонка даты И колонка суммы (или приход/расход)."""
    norm = [_norm(c) for c in cells if c is not None and str(c).strip()]
    has_date = any(any(h == n or h in n for h in _H_DATE) for n in norm)
    has_amount = any(
        any(h == n or h in n for h in (_H_AMOUNT + _H_CREDIT + _H_DEBIT)) for n in norm
    )
    return has_date and has_amount


def _table_rows(cells_rows: list[list[Any]]) -> list[dict]:
    """Находит строку-заголовок (а не берёт первую) и отдаёт строки как dict.

    Решает кейс банков (Альфа и пр.), где над таблицей идут метаданные счёта.
    """
    header_idx = next((i for i, r in enumerate(cells_rows) if _is_header_row(r)), None)
    if header_idx is None:
        return []
    header = [str(c).lstrip('\ufeff') if c is not None else '' for c in cells_rows[header_idx]]
    out = []
    for cells in cells_rows[header_idx + 1:]:
        if not any(c is not None and str(c).strip() for c in cells):
            continue
        out.append({header[j]: (cells[j] if j < len(cells) else None) for j in range(len(header))})
    return out


def _rows_to_transactions(rows: list[dict]) -> list[dict[str, Any]]:
    """Единая логика извлечения транзакций из строк-словарей (CSV и XLSX)."""
    transactions = []
    for row in rows:
        try:
            amount = _num(_field(row, _H_AMOUNT))
            if amount is None:  # split-колонки Приход/Расход (ВТБ и пр.)
                credit = _num(_field(row, _H_CREDIT)) or 0.0
                debit = _num(_field(row, _H_DEBIT)) or 0.0
                if credit or debit:
                    amount = credit - abs(debit)
            if amount is None or amount == 0:
                continue

            date_str = _field(row, _H_DATE)
            category = _field(row, _H_CATEGORY) or 'Импорт'
            description = _field(row, _H_DESC)
            mcc = _field(row, _H_MCC)

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


def parse_universal_csv(content: str) -> list[dict[str, Any]]:
    """Универсальный CSV-парсер: сам находит строку-заголовок и колонки даты/суммы.

    Работает с любым банком, где в CSV есть дата и сумма (одной знаковой колонкой
    или раздельными Приход/Расход). Терпит метаданные над таблицей, \xa0 и ё/е.
    """
    head = content[:2000]
    delimiter = ';' if head.count(';') > head.count(',') else ','
    cells_rows = list(csv.reader(io.StringIO(content), delimiter=delimiter))
    return _rows_to_transactions(_table_rows(cells_rows))


def parse_xlsx(raw: bytes, bank_id: str = 'universal') -> list[dict[str, Any]]:
    """Парсит XLSX-выписку через те же эвристики, что и универсальный CSV."""
    if openpyxl is None:
        raise ValueError("Для импорта XLSX установите openpyxl: pip install openpyxl")
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    cells_rows = [list(r) for r in wb.active.iter_rows(values_only=True)]
    return _rows_to_transactions(_table_rows(cells_rows))


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
