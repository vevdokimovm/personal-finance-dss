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

            merchant = (
                (description.strip() if description else '')
                or category.strip() or 'Операция'
            )
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

            merchant = (
                (description.strip() if description else '')
                or category.strip() or 'Операция'
            )
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
    """Сумма → float, устойчиво к RU и EN форматам.

    Десятичный разделитель — последний из «.» или «,»; второй считается разделителем
    тысяч. «−2 000,50»/«1 114,54 RUR» (RU) и «3,000.00»/«-741.74» (ВТБ, EN) → корректно.
    """
    if value is None:
        return None
    s = str(value).replace('\xa0', '').replace(' ', '').replace('\u2212', '-')
    s = re.sub(r'[^0-9.,\-+]', '', s)
    if not re.search(r'\d', s):
        return None
    last_comma, last_dot = s.rfind(','), s.rfind('.')
    if last_comma > last_dot:      # запятая — десятичная (RU)
        s = s.replace('.', '').replace(',', '.')
    elif last_dot > last_comma:    # точка — десятичная (EN)
        s = s.replace(',', '')
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


# ── PDF-выписка ВТБ (табличная сетка → extract_tables) ────────────────────
def _vtb_table_to_transactions(tables: list) -> list[dict[str, Any]]:
    """Таблицы pdfplumber ВТБ → транзакции. Колонки: [дата+время, дата обработки,
    ЗНАКОВАЯ сумма в валюте операции, Приход, Расход, Комиссия, Описание].
    Берём знаковую колонку (минус → расход), даёт и приход, и расход одной логикой."""
    out: list[dict[str, Any]] = []
    for table in tables:
        for row in table:
            if not row or not row[0]:
                continue
            m = re.match(r'(\d{2}\.\d{2}\.\d{4})', str(row[0]))
            if not m:  # строки-заголовки таблицы
                continue
            amount = _num(row[2]) if len(row) > 2 else None
            if amount is None or amount == 0:
                continue
            desc = re.sub(r'\s+', ' ', str(row[6])).strip() if len(row) > 6 and row[6] else ''
            t_type, amount = _classify(amount)
            out.append({
                'amount': round(amount, 2),
                'description': (desc or 'Операция')[:255],
                'mcc': None,
                'type': t_type,
                'date': _parse_date(m.group(1)).isoformat(),
                'is_synced': True,
            })
    return out


def parse_vtb_pdf(raw: bytes) -> list[dict[str, Any]]:
    """PDF-выписка ВТБ: таблица со знаковой суммой в «валюте операции»."""
    if pdfplumber is None:
        raise ValueError("Для импорта PDF установите pdfplumber: pip install pdfplumber")
    tables: list = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return _vtb_table_to_transactions(tables)


# ── PDF-выписка Сбербанка («Выписка по платёжному счёту» → текст) ──────────
# Строка операции: дата время <категория> <сумма в валюте счёта> <остаток>.
# Знак «+» у суммы → приход, иначе расход. Описание — на следующей строке.
_SBER_OP = re.compile(
    r'^(\d{2}\.\d{2}\.\d{4})\s+\d{2}:\d{2}\s+(.+?)\s+'
    r'([+\-]?\d[\d ]*,\d{2})\s+[+\-]?\d[\d ]*,\d{2}\s*$'
)


def _sber_text_to_transactions(lines: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, line in enumerate(lines):
        m = _SBER_OP.match(line.strip())
        if not m:
            continue
        date_s, category, amount_s = m.group(1), m.group(2).strip(), m.group(3)
        amount = _num(amount_s)
        if amount is None or amount == 0:
            continue
        t_type = 'income' if amount_s.strip().startswith('+') else 'expense'
        description = category
        if i + 1 < len(lines):  # описание + дата обработки + код авторизации
            nxt = re.match(r'^\d{2}\.\d{2}\.\d{4}\s+\S+\s+(.+)$', lines[i + 1].strip())
            if nxt:
                description = nxt.group(1).strip()
        out.append({
            'amount': round(abs(amount), 2),
            'description': (description or category or 'Операция')[:255],
            'mcc': None,
            'type': t_type,
            'date': _parse_date(date_s).isoformat(),
            'is_synced': True,
        })
    return out


def parse_sber_pdf(raw: bytes) -> list[dict[str, Any]]:
    """PDF-выписка Сбербанка («Выписка по платёжному счёту»)."""
    if pdfplumber is None:
        raise ValueError("Для импорта PDF установите pdfplumber: pip install pdfplumber")
    lines: list[str] = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            lines.extend((page.extract_text() or "").split("\n"))
    return _sber_text_to_transactions(lines)


# ── PDF-выписка Райффайзенбанка (табличная сетка, split Debit/Credit) ──────
def _raif_table_to_transactions(tables: list) -> list[dict[str, Any]]:
    """Таблицы pdfplumber Райффайзена → транзакции. Колонки: [№, дата+время, документ,
    Debit, Credit, назначение, карта]. Debit (−) → расход, Credit (+) → приход.
    По позициям колонок — поэтому EN- и RU-шапка обрабатываются одинаково."""
    out: list[dict[str, Any]] = []
    for table in tables:
        for row in table:
            if not row or len(row) < 5 or not row[0] or not str(row[0]).strip().isdigit():
                continue  # данные — строки с номером № P/P; заголовки/служебные пропускаем
            m = re.match(r'(\d{2}\.\d{2}\.\d{4})', str(row[1]) if row[1] else '')
            if not m:
                continue
            debit = _num(row[3])
            credit = _num(row[4]) if len(row) > 4 else None
            amount = debit if debit not in (None, 0) else credit
            if amount is None or amount == 0:
                continue
            desc = re.sub(r'\s+', ' ', str(row[5])).strip() if len(row) > 5 and row[5] else ''
            t_type, amount = _classify(amount)
            out.append({
                'amount': round(amount, 2),
                'description': (desc or 'Операция')[:255],
                'mcc': None,
                'type': t_type,
                'date': _parse_date(m.group(1)).isoformat(),
                'is_synced': True,
            })
    return out


def parse_raiffeisen_pdf(raw: bytes) -> list[dict[str, Any]]:
    """PDF-выписка Райффайзенбанка: табличная сетка со split Debit/Credit."""
    if pdfplumber is None:
        raise ValueError("Для импорта PDF установите pdfplumber: pip install pdfplumber")
    tables: list = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return _raif_table_to_transactions(tables)


PDF_PARSERS = {
    'tinkoff': parse_tinkoff_pdf,
    'vtb': parse_vtb_pdf,
    'sber': parse_sber_pdf,
    'raiffeisen': parse_raiffeisen_pdf,
}


def parse_bank_pdf(raw: bytes, bank_id: str = 'tinkoff') -> list[dict[str, Any]]:
    """Выбирает PDF-парсер по bank_id (по умолчанию — Тинькофф)."""
    return PDF_PARSERS.get(bank_id, parse_tinkoff_pdf)(raw)


BANK_PARSERS = {
    'tinkoff': parse_tinkoff_csv,
    'sber': parse_sber_csv,
    'alfa': parse_universal_csv,
    'vtb': parse_universal_csv,
    'raiffeisen': parse_universal_csv,
    'universal': parse_universal_csv,
}


# ── Формат 1CClientBankExchange (универсальный для бизнес-счетов) ──────────
# Текстовый формат обмена «банк-клиент» ↔ 1С: один парсер на ~все банки.
# Шапка несёт РасчСчет владельца; знак операции — по тому, чей счёт плательщик/
# получатель относительно владельца. Документы — между СекцияДокумент … КонецДокумента.
def parse_1c_exchange(content: str) -> list[dict[str, Any]]:
    """Парсит выписку формата 1CClientBankExchange (kl_to_1c).

    Расход — если ПлательщикСчет = счёт владельца (деньги уходят); приход — если
    ПолучательСчет = счёт владельца. Сумма из `Сумма=`, описание — `НазначениеПлатежа=`.
    """
    owner_accounts: set[str] = set()
    docs: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    in_doc = False

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith('СекцияДокумент'):
            in_doc, cur = True, {}
            continue
        if line.startswith('КонецДокумента'):
            if in_doc:
                docs.append(cur)
            in_doc, cur = False, {}
            continue
        if '=' not in line:
            continue
        key, _, val = line.partition('=')
        key, val = key.strip(), val.strip()
        if in_doc:
            cur[key] = val
        elif key == 'РасчСчет' and val:  # счёт владельца (шапка / СекцияРасчСчет)
            owner_accounts.add(val)

    out: list[dict[str, Any]] = []
    for d in docs:
        amount = _num(d.get('Сумма'))
        if amount is None or amount == 0:
            continue
        payer, payee = d.get('ПлательщикСчет', ''), d.get('ПолучательСчет', '')
        if owner_accounts and payer in owner_accounts:
            t_type = 'expense'
        elif owner_accounts and payee in owner_accounts:
            t_type = 'income'
        else:  # владельца не определили — по наличию даты поступления/списания
            t_type = 'income' if d.get('ДатаПоступило') else 'expense'
        date_s = d.get('Дата') or d.get('ДатаСписано') or d.get('ДатаПоступило')
        desc = (d.get('НазначениеПлатежа') or d.get('Получатель')
                or d.get('Плательщик') or 'Операция')
        out.append({
            'amount': round(abs(amount), 2),
            'description': desc[:255],
            'mcc': None,
            'type': t_type,
            'date': _parse_date(date_s).isoformat() if date_s else datetime.now().isoformat(),
            'is_synced': True,
        })
    return out


def parse_bank_statement(content: str, bank_id: str = 'universal') -> list[dict[str, Any]]:
    """Выбирает парсер по содержимому/bank_id и парсит выписку."""
    if content.lstrip().startswith('1CClientBankExchange'):
        return parse_1c_exchange(content)
    parser = BANK_PARSERS.get(bank_id, parse_universal_csv)
    return parser(content)
