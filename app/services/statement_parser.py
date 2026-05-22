"""
Парсеры банковских выписок (CSV / Excel).
Поддерживаемые банки:
  - Тинькофф (CSV-выписка из личного кабинета)
  - Сбербанк (CSV-выписка)
  - Универсальный формат (дата, категория, сумма, тип)
"""
from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any


def parse_tinkoff_csv(content: str) -> list[dict[str, Any]]:
    """
    Парсит CSV-выписку из Тинькофф Банка.
    
    Формат Тинькофф (обычно с разделителем ;):
    Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;
    Валюта операции;Сумма платежа;Валюта платежа;Кэшбэк;Категория;MCC;Описание
    """
    transactions = []
    
    # Тинькофф может использовать ; или , как разделитель
    delimiter = ';' if ';' in content[:500] else ','
    
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    
    # Нормализуем заголовки (убираем BOM и пробелы)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lstrip('\ufeff') for f in reader.fieldnames]
    
    for row in reader:
        try:
            # Ищем нужные поля (Тинькофф может менять названия колонок)
            date_str = _get_field(row, ['Дата операции', 'Дата платежа', 'date'])
            amount_str = _get_field(row, ['Сумма платежа', 'Сумма операции', 'amount'])
            category = _get_field(row, ['Категория', 'category']) or 'Без категории'
            description = _get_field(row, ['Описание', 'description']) or ''
            status = _get_field(row, ['Статус', 'status']) or ''
            
            # Пропускаем неуспешные операции
            if status and status.upper() not in ('OK', 'COMPLETED', ''):
                continue
            
            if not amount_str:
                continue
                
            # Парсим сумму (может быть с запятой как десятичный)
            amount = float(amount_str.replace(' ', '').replace(',', '.'))
            
            # Парсим дату
            t_date = _parse_date(date_str) if date_str else datetime.now()
            
            # Определяем тип: отрицательная = расход, положительная = доход
            if amount < 0:
                t_type = 'expense'
                amount = abs(amount)
            else:
                t_type = 'income'
            
            # Имя категории — если есть описание, добавляем
            cat_name = category.strip()
            if description.strip() and description.strip() != cat_name:
                cat_name = f"{cat_name}: {description.strip()}"
            
            transactions.append({
                'amount': round(amount, 2),
                'category': cat_name[:100],  # Обрезаем до 100 символов
                'type': t_type,
                'date': t_date.isoformat(),
                'is_synced': True,
            })
        except (ValueError, KeyError, TypeError):
            continue  # Пропускаем невалидные строки
    
    return transactions


def parse_sber_csv(content: str) -> list[dict[str, Any]]:
    """
    Парсит CSV-выписку из Сбербанка.
    Формат может варьироваться, но обычно:
    №;Дата;Описание;Категория;Сумма;Валюта;Статус
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
            category = _get_field(row, ['Категория', 'Описание', 'category']) or 'Без категории'
            
            if not amount_str:
                continue
            
            amount = float(amount_str.replace(' ', '').replace(',', '.').replace('\xa0', ''))
            t_date = _parse_date(date_str) if date_str else datetime.now()
            
            if amount < 0:
                t_type = 'expense'
                amount = abs(amount)
            else:
                t_type = 'income'
            
            transactions.append({
                'amount': round(amount, 2),
                'category': category.strip()[:100],
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
            category = _get_field(row, [
                'Категория', 'Описание', 'Category', 'Description',
                'Назначение', 'Merchant', 'MCC Description'
            ]) or 'Импорт'
            
            if not amount_str:
                continue
            
            amount = float(amount_str.replace(' ', '').replace(',', '.').replace('\xa0', ''))
            t_date = _parse_date(date_str) if date_str else datetime.now()
            
            if amount < 0:
                t_type = 'expense'
                amount = abs(amount)
            else:
                t_type = 'income'
            
            transactions.append({
                'amount': round(amount, 2),
                'category': category.strip()[:100],
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
