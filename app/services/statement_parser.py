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
import unicodedata
from datetime import datetime
from typing import Any

from app.utils.time import utcnow

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


# ── Учёт пропущенных строк ────────────────────────────────────────────────
# CSV не несёт контрольных сумм, поэтому сверить его с банком нечем. Но главный риск CSV —
# не неверная сумма, а МОЛЧАЛИВАЯ ПОТЕРЯ строки: на реальном файле в 12 788 строк пропажа
# полусотни незаметна. Поэтому каждая точка `continue` обязана назвать причину, а
# `statement_reconcile` отделяет законные пропуски (банк сам отклонил операцию) от наших
# промахов (сумму не разобрали).
SKIP_STATUS = 'операция отклонена банком'
SKIP_NO_AMOUNT = 'сумма не указана'
SKIP_BAD_AMOUNT = 'сумма не распознана'
SKIP_NO_DATE = 'дата не распознана'
SKIP_ZERO = 'нулевая сумма'
SKIP_SERVICE = 'служебная строка (не операция)'
SKIP_UNPARSED = 'строка не разобрана'


def _skip(stats: dict[str, int], reason: str) -> None:
    stats[reason] = stats.get(reason, 0) + 1


def _fill_report(report: dict | None, rows: int, parsed: int, skipped: dict[str, int]) -> None:
    if report is not None:
        report['rows'] = rows
        report['parsed'] = parsed
        report['skipped'] = skipped


def parse_tinkoff_csv(content: str,
                      report: dict | None = None) -> list[dict[str, Any]]:
    """
    Парсит CSV-выписку из Тинькофф Банка.

    Формат Тинькофф (обычно с разделителем ;):
    Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;
    Валюта операции;Сумма платежа;Валюта платежа;Кэшбэк;Категория;MCC;Описание
    """
    transactions = []
    skipped: dict[str, int] = {}
    rows = 0
    delimiter = ';' if ';' in content[:500] else ','
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lstrip('\ufeff') for f in reader.fieldnames]

    for row in reader:
        if not any((value or '').strip() for value in row.values()):
            continue  # пустая строка-разделитель, не операция
        rows += 1
        try:
            date_str = _get_field(row, ['Дата операции', 'Дата платежа', 'date'])
            amount_str = _get_field(row, ['Сумма платежа', 'Сумма операции', 'amount'])
            category = _get_field(row, ['Категория', 'category']) or 'Без категории'
            description = _get_field(row, ['Описание', 'description'])
            mcc = _get_field(row, ['MCC', 'mcc'])
            status = _get_field(row, ['Статус', 'status']) or ''

            if status and status.upper() not in ('OK', 'COMPLETED', ''):
                _skip(skipped, SKIP_STATUS)   # банк сам отклонил — законный пропуск
                continue
            if not amount_str:
                _skip(skipped, SKIP_NO_AMOUNT)
                continue

            # Через `_num`, а не через наивный float: он держит и RU («1 234,56»), и EN
            # («1,234.56») форматы. Наивная замена ломалась на EN-разделителе тысяч и
            # роняла строку в `except` — то есть теряла операцию молча.
            amount = _num(amount_str)
            if amount is None:
                _skip(skipped, SKIP_BAD_AMOUNT)
                continue
            t_date = _parse_date(date_str) if date_str else utcnow()
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
            _skip(skipped, SKIP_UNPARSED)
            continue

    _fill_report(report, rows, len(transactions), skipped)
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
            t_date = _parse_date(date_str) if date_str else utcnow()
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
# ВАЖНО: только ОСНОВЫ слов. «поступление» не подстрока «Поступления» (последняя буква
# другая), и на реальной выписке Райффайзена из-за этого молча терялись ВСЕ приходы:
# 14 строк → 8 операций, и в модель попадал человек без единого дохода.
_H_CREDIT = ['приход', 'поступлени', 'зачислени', 'кредит', 'credit']
_H_DEBIT = ['расход', 'списани', 'дебет', 'debit']
_H_CATEGORY = ['категория', 'category']
_H_DESC = ['назначение платежа', 'назначение', 'описание', 'description', 'merchant']
_H_MCC = ['mcc']


def _norm(value: Any) -> str:
    """Нормализует заголовок/ячейку для матчинга: NFC, неразрывный пробел, ё→е, регистр.

    NFC обязателен: macOS отдаёт имена файлов (а иногда и текст PDF) в NFD, где «й» —
    это «и» + U+0306. Подстрочный матчинг по «райффайзен» или замена «ё» на «е» в NFD
    молча не срабатывают, и файл уходит не в тот парсер.
    """
    text = unicodedata.normalize('NFC', str(value))
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ').replace('ё', 'е')).strip().lower()


def _field(row: dict, candidates: list[str], exclude: list[str] | None = None) -> str | None:
    """Значение колонки по списку синонимов заголовка (нормализованный матч по подстроке).

    `exclude` отсекает заголовки, которые совпали с кандидатом, но принадлежат другой роли:
    «Amount in operation currency (credit)» ловится и кандидатом «amount», и «credit».
    """
    norm_row = [(_norm(k), v) for k, v in row.items() if k is not None]
    blocked = [_norm(e) for e in (exclude or [])]
    for cand in candidates:
        nc = _norm(cand)
        for nk, value in norm_row:
            if any(b in nk for b in blocked):
                continue
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


def _looks_like_value(text: str) -> bool:
    """Ячейка похожа на ЗНАЧЕНИЕ (дата или число), а не на название колонки."""
    return bool(re.search(r'\d{2}\.\d{2}\.\d{4}', text)) or _num(text) is not None


def _is_header_row(cells: list[Any]) -> bool:
    """Строка-заголовок: есть колонка даты И колонка суммы (или приход/расход), и при этом
    НИ ОДНА ячейка не является значением.

    Проверка на значения обязательна: над таблицей банки печатают метаданные парами
    «метка — значение», и такая пара легко имитирует заголовок. Реальный случай:
    строка «Дата открытия счета | 24.12.2018 | Поступления | 224 805,37 RUR» содержит и
    «дату», и «поступления» — и принималась за шапку, после чего разбор давал 0 операций.
    """
    norm = [_norm(c) for c in cells if c is not None and str(c).strip()]
    if any(_looks_like_value(n) for n in norm):
        return False
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


def _rows_to_transactions(rows: list[dict], report: dict | None = None) -> list[dict[str, Any]]:
    """Единая логика извлечения транзакций из строк-словарей (CSV и XLSX).

    Каждый пропуск строки называет причину: CSV сверить с итогами банка нечем, поэтому
    единственная доступная проверка — полнота разбора (см. `statement_reconcile`).
    """
    transactions = []
    skipped: dict[str, int] = {}
    for row in rows:
        try:
            # Кандидат «amount» обязан исключать колонки прихода/расхода: заголовок
            # «Amount in operation currency (credit)» ловится и тем, и другим, и на
            # реальной выписке Райффайзена вся она читалась как доход (расход = 0).
            amount = _num(_field(row, _H_AMOUNT, exclude=_H_CREDIT + _H_DEBIT))
            if amount is None:  # split-колонки Приход/Расход (ВТБ и пр.)
                credit = _num(_field(row, _H_CREDIT)) or 0.0
                debit = _num(_field(row, _H_DEBIT)) or 0.0
                if credit or debit:
                    amount = credit - abs(debit)
            date_str = _field(row, _H_DATE)
            has_date = bool(date_str) and bool(re.search(r'\d{2}\.\d{2}\.\d{4}', str(date_str)))
            if amount is None:
                # Подвал документа («Страница 1 из 1», «(подпись сотрудника)») — законная
                # не-операция. Отличаем по дате: без разобранной даты это не строка
                # операции, а оформление. Иначе получим ложную тревогу о потере данных.
                _skip(skipped, SKIP_BAD_AMOUNT if has_date else SKIP_SERVICE)
                continue
            if amount == 0:
                _skip(skipped, SKIP_ZERO)
                continue

            category = _field(row, _H_CATEGORY) or 'Импорт'
            description = _field(row, _H_DESC)
            mcc = _field(row, _H_MCC)

            t_date = _parse_date(date_str) if date_str else utcnow()
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
            _skip(skipped, SKIP_UNPARSED)
            continue
    _fill_report(report, len(rows), len(transactions), skipped)
    return transactions


def parse_universal_csv(content: str, report: dict | None = None) -> list[dict[str, Any]]:
    """Универсальный CSV-парсер: сам находит строку-заголовок и колонки даты/суммы.

    Работает с любым банком, где в CSV есть дата и сумма (одной знаковой колонкой
    или раздельными Приход/Расход). Терпит метаданные над таблицей, \xa0 и ё/е.
    """
    head = content[:2000]
    delimiter = ';' if head.count(';') > head.count(',') else ','
    cells_rows = list(csv.reader(io.StringIO(content), delimiter=delimiter))
    return _rows_to_transactions(_table_rows(cells_rows), report)


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
        return utcnow()

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

    return utcnow()


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
# У ВТБ несколько шаблонов выписки, и колонки в них СДВИНУТЫ друг относительно друга:
#   A) [дата, дата обработки, сумма в валюте операции, Приход, Расход, Комиссия, Описание]
#   B) [дата, дата обработки, сумма в валюте операции, Приход, Расход, Описание,
#       Наименование получателя/отправителя]
# В шаблоне B индекс 5 — ОПИСАНИЕ, а не комиссия. Жёсткая привязка к индексам читала текст
# описания как число (`_num('Перевод 1500') = 1500.0` — молчаливая порча суммы) и брала
# описание из колонки контрагента. Поэтому колонки определяются по шапке; позиционная
# раскладка A — фолбэк, если шапки в таблице нет.
_VTB_ROLES = (
    ('prihod', ('приход',)),
    ('rashod', ('расход',)),
    ('komis', ('комисси',)),
    ('desc', ('описание',)),
    ('party', ('наименование', 'получател', 'отправител')),
    ('signed', ('сумма',)),
)
_VTB_LEGACY_MAP = {'signed': 2, 'prihod': 3, 'rashod': 4, 'komis': 5, 'desc': 6}

# В колонку «Комиссия» ВТБ кладёт и списания (комиссия за обслуживание счёта), и
# ЗАЧИСЛЕНИЯ (кешбэк по программе лояльности) — при нулевых Приход/Расход/сумме.
# Направление кодируется только в описании: на реальной выписке кешбэк 656 ₽ уходил в
# расход, и приход недосчитывался ровно на эту сумму (сверка с итогами банка).
_VTB_CREDIT_WORDS = ('зачислен', 'кешбэк', 'кэшбэк', 'возврат', 'начислен',
                     'процент', 'пополнен', 'поступлен')


def _vtb_is_credit(description: str) -> bool:
    """Зачисление ли это, если сумма стоит в колонке «Комиссия» (кешбэк/возврат/проценты)."""
    low = _norm(description)
    return any(word in low for word in _VTB_CREDIT_WORDS)


# ── Общий движок табличных выписок ────────────────────────────────────────
# Раскладка колонок у ОДНОГО банка меняется от шаблона к шаблону: у ВТБ их три, у
# Райффайзена три, и русский с английским бывают зеркальны (на месте «Debit» стоит
# «Поступления»). Привязка к индексам ломается на каждом новом шаблоне — оба раза это
# стоило нам молчаливой потери данных. Поэтому роль колонки определяется по её заголовку,
# а поддержка нового банка сводится к словарю ролей, а не к новому парсеру.
# Как добавить банк — см. docs/universal_statement_parser_strategy.md.
def _column_map(table: list, roles_spec: tuple, date_cells: int = 1) -> dict[str, int]:
    """Индексы колонок по тексту (возможно, двухрядной) шапки таблицы.

    `roles_spec` — кортеж пар «роль → маркеры заголовка», порядок значим: роль, стоящая
    раньше, забирает колонку первой (поэтому «приход» проверяется до «суммы», иначе
    заголовок «Сумма операции в валюте счёта/карты · Приход» уедет не в ту роль).
    `date_cells` — сколько первых ячеек проверять на дату, чтобы понять, что шапка
    кончилась и пошли операции: у ВТБ дата в первой ячейке, у Райффайзена во второй,
    когда есть колонка «№ П/П».
    """
    header: dict[int, str] = {}
    for row in table:
        if not row:
            continue
        if any(c and re.match(r'\d{2}\.\d{2}\.\d{4}', str(c).strip()) for c in row[:date_cells]):
            break  # начались строки операций
        for i, cell in enumerate(row):
            if cell:
                header[i] = f"{header.get(i, '')} {_norm(cell)}".strip()
    roles: dict[str, int] = {}
    for i, text in header.items():
        for role, markers in roles_spec:
            if role not in roles and any(mk in text for mk in markers):
                roles[role] = i
                break
    return roles


def _vtb_column_map(table: list) -> dict[str, int]:
    """Колонки ВТБ по шапке (три реальных шаблона). Пусто, если шапки в таблице нет."""
    return _column_map(table, _VTB_ROLES, date_cells=1)


def _vtb_row_to_transaction(row: list, cmap: dict[str, int], date_s: str) -> dict[str, Any] | None:
    """Строка таблицы ВТБ → транзакция по карте колонок (или None, если движения нет)."""
    def num(role: str) -> float:
        i = cmap.get(role)
        return (_num(row[i]) or 0.0) if i is not None and i < len(row) else 0.0

    def text(role: str) -> str:
        i = cmap.get(role)
        if i is None or i >= len(row) or not row[i]:
            return ''
        return re.sub(r'\s+', ' ', str(row[i])).strip()

    prihod, rashod, komis, signed = num('prihod'), num('rashod'), num('komis'), num('signed')
    if prihod or rashod:      # движение в раздельных колонках (Расход бывает и со знаком)
        amount = prihod - abs(rashod) - abs(komis)
    elif signed:              # знаковая сумма одной колонкой
        amount = signed - abs(komis)
    elif komis:               # движение только в колонке «Комиссия»: знак — из описания
        amount = abs(komis) if _vtb_is_credit(text('desc')) else -abs(komis)
    else:
        amount = 0.0
    if amount == 0:
        return None
    desc, party = text('desc'), text('party')
    if party and party not in desc:  # контрагент — сырьё для merchant-аналитики (FR-14)
        desc = f"{desc} {party}".strip()
    t_type, amount = _classify(amount)
    return {
        'amount': round(amount, 2),
        'description': (desc or 'Операция')[:255],
        'mcc': None,
        'type': t_type,
        'date': _parse_date(date_s).isoformat(),
        'is_synced': True,
    }


def _vtb_table_to_transactions(tables: list) -> list[dict[str, Any]]:
    """Таблицы pdfplumber ВТБ → транзакции. Колонки — по шапке (шаблоны A и B), нетто по
    счёту = Приход − Расход − Комиссия. Знаковая колонка «в валюте операции» у рублёвой
    комиссии равна 0, поэтому опираться только на неё нельзя (давало 0 операций на живом
    файле). Шапка повторяется на каждой странице; если её нет — берём карту предыдущей."""
    out: list[dict[str, Any]] = []
    cmap: dict[str, int] = {}
    for table in tables:
        cmap = _vtb_column_map(table) or cmap or dict(_VTB_LEGACY_MAP)
        for row in table:
            if not row or not row[0]:
                continue
            m = re.match(r'(\d{2}\.\d{2}\.\d{4})', str(row[0]))
            if not m:  # строки шапки таблицы
                continue
            txn = _vtb_row_to_transaction(row, cmap, m.group(1))
            if txn:
                out.append(txn)
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


# Изменение кредитного лимита — НЕ движение денег. В выписке по кредитной карте оно
# проходит обычной строкой операции («Прочие операции +110 000,00»), и без фильтра
# модель получала 220 000 ₽ фиктивного дохода на реальной выписке: для СППР это
# отравленный вход (завышенный доход → завышенный свободный поток).
_SBER_NON_CASH = (
    'установка кредитного лимита',
    'увеличение кредитного лимита',
    'уменьшение кредитного лимита',
    'изменение кредитного лимита',
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
        if any(marker in _norm(description) for marker in _SBER_NON_CASH):
            continue  # изменение лимита, а не операция по счёту
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


# ── PDF-выписка Райффайзенбанка (табличная сетка) ─────────────────────────
# Три реальных шаблона, колонки не совпадают ни по смыслу, ни по количеству:
#   RU:     [№ П/П, Дата операции, Номер документа, Поступления, Расходы, Детали, Карта]
#   EN:     [№ P/P, Posting date, Номер документа, Debit, Credit, Payment details, Card]
#   без №:  [Дата операции, Номер документа, Сумма в валюте операции, Сумма в валюте
#            счёта, Детали операции, Номер карты]
# RU и EN ЗЕРКАЛЬНЫ: на месте англоязычного «Debit» в русском шаблоне стоит
# «Поступления». Спасали только знаки ± внутри ячеек. А шаблон без колонки «№» парсер
# отбрасывал целиком (требовал номер в первой ячейке) — 0 операций на живом файле.
# Поэтому колонки — по шапке, строка данных — по колонке даты, знак — из семантики
# колонки (приход/расход), а не из знака в ячейке.
_RAIF_ROLES = (
    ('credit', ('поступлени', 'credit')),
    ('debit', ('расход', 'debit')),
    ('account', ('в валюте счета', 'currency of account')),
    ('operation', ('в валюте операции', 'currency of operation')),
    ('desc', ('детали', 'payment details', 'назначение', 'описание', 'description')),
    ('date', ('дата', 'date')),
)
_RAIF_LEGACY_MAP = {'date': 1, 'debit': 3, 'credit': 4, 'desc': 5}


def _raif_column_map(table: list) -> dict[str, int]:
    """Колонки Райффайзена по шапке (три реальных шаблона, RU и EN зеркальны)."""
    return _column_map(table, _RAIF_ROLES, date_cells=2)


def _raif_row_to_transaction(row: list, cmap: dict[str, int]) -> dict[str, Any] | None:
    """Строка таблицы Райффайзена → транзакция (или None: шапка/итоги/нет движения)."""
    def num(role: str) -> float:
        i = cmap.get(role)
        return (_num(row[i]) or 0.0) if i is not None and i < len(row) else 0.0

    def text(role: str) -> str:
        i = cmap.get(role)
        if i is None or i >= len(row) or not row[i]:
            return ''
        return re.sub(r'\s+', ' ', str(row[i])).strip()

    date_i = cmap.get('date', 1)
    cell = str(row[date_i]) if date_i < len(row) and row[date_i] else ''
    m = re.match(r'(\d{2}\.\d{2}\.\d{4})', cell.strip())
    if not m:  # шапка, «Выполнена банком», строка «Количество операций»
        return None
    credit, debit = num('credit'), num('debit')
    if credit:      # колонка прихода: знак — из смысла колонки, а не из ячейки
        amount = abs(credit)
    elif debit:
        amount = -abs(debit)
    else:           # шаблон без Поступлений/Расходов: знаковая сумма в валюте счёта
        amount = num('account') or num('operation')
    if amount == 0:
        return None
    t_type, amount = _classify(amount)
    return {
        'amount': round(amount, 2),
        'description': (text('desc') or 'Операция')[:255],
        'mcc': None,
        'type': t_type,
        'date': _parse_date(m.group(1)).isoformat(),
        'is_synced': True,
    }


def _raif_table_to_transactions(tables: list) -> list[dict[str, Any]]:
    """Таблицы pdfplumber Райффайзена → транзакции. Колонки — по шапке (три шаблона);
    если шапки нет, берём карту предыдущей таблицы, иначе позиционный фолбэк."""
    out: list[dict[str, Any]] = []
    cmap: dict[str, int] = {}
    for table in tables:
        cmap = _raif_column_map(table) or cmap or dict(_RAIF_LEGACY_MAP)
        for row in table:
            if not row or len(row) < 4:
                continue
            txn = _raif_row_to_transaction(row, cmap)
            if txn:
                out.append(txn)
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
            'date': _parse_date(date_s).isoformat() if date_s else utcnow().isoformat(),
            'is_synced': True,
        })
    return out


# ── Определение банка по СОДЕРЖИМОМУ ──────────────────────────────────────
# Ни имя файла, ни выбор в форме не являются показателем: на реальном наборе угадывание
# по имени трижды отправило выписку не в тот парсер и дало ложный ноль (macOS пишет имена
# в NFD, поэтому «райф» в «Райф 1.pdf» даже не находится). Реквизиты банка в выписке —
# единственный надёжный признак.
_BANK_MARKERS = (
    ('vtb', ('банк втб', 'втб (пао)', 'vtb bank', 'банка втб')),
    ('raiffeisen', ('райффайзен', 'raiffeisen')),
    # У Тинькоффа в тексте PDF имени банка нет вовсе (логотип — картинка), поэтому
    # добавлен структурный признак его выписки.
    ('tinkoff', ('тинькофф', 'т-банк', 'тбанк', 'tinkoff', 'tbank', 'выписка по договору')),
    ('alfa', ('альфа-банк', 'альфа банк', 'alfa-bank', 'alfabank')),
    ('gazprom', ('газпромбанк', 'gazprombank')),
    ('sber', ('сбербанк', 'sberbank')),
)


def detect_bank(text: str) -> str | None:
    """Банк по содержимому выписки (реквизиты в шапке/подвале), иначе None."""
    low = _norm(text)
    for bank, markers in _BANK_MARKERS:
        if any(marker in low for marker in markers):
            return bank
    return None


def detect_pdf_bank(raw: bytes) -> str | None:
    """Банк по тексту PDF. Читаем первые и последние страницы: у ВТБ реквизиты банка
    только в подвале последней страницы, шапка — картинка-логотип."""
    if pdfplumber is None:
        return None
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            pages = pdf.pages[:2] + pdf.pages[-2:] if len(pdf.pages) > 2 else pdf.pages
            text = "\n".join((page.extract_text() or "") for page in pages)
    except Exception:
        return None
    return detect_bank(text)


def parse_bank_statement(content: str, bank_id: str = 'universal',
                         report: dict | None = None) -> list[dict[str, Any]]:
    """Выбирает парсер по содержимому/bank_id и парсит выписку.

    `report` (опционально) заполняется статистикой разбора: сколько строк было, сколько
    операций распознано и сколько пропущено с какими причинами. Для CSV это единственная
    доступная проверка: контрольных сумм CSV не несёт.
    """
    if content.lstrip().startswith('1CClientBankExchange'):
        return parse_1c_exchange(content)
    parser = BANK_PARSERS.get(bank_id, parse_universal_csv)
    if parser in (parse_tinkoff_csv, parse_universal_csv):
        return parser(content, report)
    return parser(content)


# ── Декодирование сырых байтов выписки (CSV/1C) ────────────────────────────
# cp1251 однобайтовая и НИКОГДА не падает, поэтому её нельзя пробовать первой —
# utf-8-файл раскодируется в кашу. Правильный порядок: utf-8 (strict) первым; на
# реальном cp1251 (кириллица = невалидный utf-8) он падает → фолбэк cp1251. Так
# 1C от банков РФ (windows-1251, `Кодировка=Windows`) читается корректно.
def decode_statement_bytes(raw: bytes) -> str:
    """Байты текстовой выписки (CSV/1C) → строка. Перебор кодировок: utf-8 → cp1251."""
    for enc in ('utf-8-sig', 'utf-8', 'cp1251', 'windows-1251', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')


# ── Детекция «это не выписка операций» (справки/реквизиты) ──────────────────
# Банки в одном окне «выписки» отдают и справки об остатке, реквизиты, справки о
# задолженности/вкладе/пенсиях. Операций там нет — парсер вернёт 0, и приложение
# НЕ должно принять это за пустую выписку. Возвращаем человекочитаемую причину.
_NON_STATEMENT_MARKERS = (
    ('справка о доступном остатке', 'справка о доступном остатке'),
    ('справка о состоянии вклада', 'справка о состоянии вклада'),
    ('справка о задолженности', 'справка о задолженности'),
    ('справка по арестам и взысканиям', 'справка по арестам и взысканиям'),
    ('справка о наличии', 'справка о наличии счетов'),
    ('сведения о наличии счетов', 'сведения о наличии счетов'),
    ('справка о видах и размерах', 'справка о выплатах/пенсиях'),
    ('реквизиты счета', 'реквизиты счёта'),
    ('имеет открытый счет', 'справка о наличии счёта'),
    ('для предоставления по месту требования', 'справка банка'),
    ('certificate', 'справка банка (англ.)'),
)


def classify_non_statement(text: str) -> str | None:
    """Если текст PDF — справка/реквизиты, а не выписка операций, вернуть причину; иначе None.

    Матчинг через `_norm` (NFC + ё→е, иначе маркеры молча не срабатывают на NFD-тексте)
    и дополнительно по тексту без пробелов: Альфа-Банк отдаёт «имеетоткрытыйсчёт» слитно,
    Газпромбанк печатает заголовок вразрядку («С П Р А В К А»).
    """
    low = _norm(text)
    low_nospace = low.replace(' ', '')
    for marker, label in _NON_STATEMENT_MARKERS:
        if marker in low or marker.replace(' ', '') in low_nospace:
            return label
    return None


def pdf_non_statement_reason(raw: bytes) -> str | None:
    """Причина, по которой PDF — не выписка операций (справка/реквизиты), или None."""
    if pdfplumber is None:
        return None
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            text = "\n".join((pg.extract_text() or "") for pg in pdf.pages[:2])
    except Exception:
        return None
    return classify_non_statement(text)
