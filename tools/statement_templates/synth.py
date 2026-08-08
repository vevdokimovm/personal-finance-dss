"""
Генератор синтетических выписок для property-тестов (Б2).

**Что это доказывает и что НЕ доказывает — читать обязательно.**

Генератор знает ровно те шаблоны, которые умеет парсер. Поэтому «синтетика зелёная» НЕ
означает «двести банков читаются»: генератор и парсер знают одно и то же, круг замкнут, и
зелёный прогон здесь — не доказательство покрытия. Единственное доказательство того, что
конкретный файл прочитан верно, — сверка с контрольными итогами самого банка
(`app/services/statement_reconcile.py`).

Что генератор даёт на самом деле — фаззинг ВНУТРИ известного формата. Тысячи выписок с
краевыми случаями: неразрывные пробелы, разделители тысяч и их отсутствие, запятая против
точки, суффиксы валюты, перенос описания внутри ячейки, нулевые и копеечные суммы, длинные
описания, кириллица с латиницей. Это ловит хрупкость и регрессии там, где реальных файлов
на руках всего одиннадцать.

Каждый рендерер повторяет РЕАЛЬНЫЙ шаблон банка, включая его особенности:
- ВТБ, шаблон A: индекс 5 — «Комиссия», индекс 6 — «Описание», «Расход» положительный;
- ВТБ, шаблон B: индекс 5 — «Описание», индекс 6 — контрагент, «Расход» отрицательный;
- Райффайзен RU: «Поступления»/«Расходы»; EN: «Debit»/«Credit» — колонки ЗЕРКАЛЬНЫ;
- Райффайзен без «№»: знаковая сумма в валюте операции и в валюте счёта.
"""
from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Docker/CI — Linux; локальный macOS — путь, куда DejaVu ставится через brew/Font Book.
FONT_PATH_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/DejaVuSans.ttf",
)
FONT = "DejaVu"
_FONT_READY = False


def _resolve_font_path() -> str:
    for path in FONT_PATH_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "DejaVuSans.ttf не найден: " + ", ".join(FONT_PATH_CANDIDATES)
    )


@dataclass(frozen=True)
class Op:
    """Одна операция «как задумано» — эталон для сверки после парса."""
    day: date
    kind: str          # 'income' | 'expense'
    amount: float      # положительная величина
    description: str


@dataclass(frozen=True)
class Style:
    """Вариации форматирования, которые встречаются в живых выписках."""
    thousands: str = " "      # " ", "\u00a0" или ""
    decimal: str = ","        # "," или "."
    suffix: str = " ₽"        # " ₽", " RUB" или ""
    wrap_description: bool = False   # перенос описания внутри ячейки


def _ensure_font() -> None:
    global _FONT_READY
    if not _FONT_READY:
        pdfmetrics.registerFont(TTFont(FONT, _resolve_font_path()))
        _FONT_READY = True


def money(amount: float, style: Style, sign: str = "") -> str:
    """Сумма в виде, в каком её печатают банки."""
    text = f"{amount:,.2f}"                      # 1,234.56
    if style.decimal == ",":
        text = text.replace(",", "\x00").replace(".", ",").replace("\x00", style.thousands)
    else:
        text = text.replace(",", style.thousands)
    return f"{sign}{text}{style.suffix}"


def _desc(op: Op, style: Style) -> str:
    """Описание в ячейке. Реальные выписки переносят его на несколько строк внутри ячейки,
    а парсер схлопывает пробелы — поэтому перенос обязан быть безразличен."""
    if style.wrap_description and " " in op.description:
        head, _, tail = op.description.partition(" ")
        return f"{head}\n{tail}"
    return op.description


def _table_pdf(rows: list[list[str]]) -> bytes:
    _ensure_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
    table = Table(rows)
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT, 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    doc.build([table])
    return buf.getvalue()


def render_vtb_a(ops: list[Op], style: Style) -> bytes:
    """ВТБ, шаблон A: «Комиссия» на 5, «Описание» на 6, «Расход» положительный."""
    rows = [
        ["Операции по счёту", "", "", "", "", "", ""],
        ["Дата и время\nоперации", "Дата обработки\nбанком", "Сумма операции в\nвалюте операции",
         "Сумма операции в валюте\nсчета/карты", "", "Комиссия", "Описание операции"],
        ["", "", "", "Приход", "Расход", "", ""],
    ]
    for op in ops:
        day = op.day.strftime("%d.%m.%Y")
        signed = money(op.amount, style, "-" if op.kind == "expense" else "")
        income = money(op.amount, style) if op.kind == "income" else money(0, style)
        expense = money(op.amount, style) if op.kind == "expense" else money(0, style)
        rows.append([f"{day}\n10:00:00", day, signed, income, expense,
                     money(0, style), _desc(op, style)])
    return _table_pdf(rows)


def render_vtb_b(ops: list[Op], style: Style) -> bytes:
    """ВТБ, шаблон B: «Описание» на 5, контрагент на 6, «Расход» ОТРИЦАТЕЛЬНЫЙ."""
    rows = [
        ["Операции по счёту", "", "", "", "", "", ""],
        ["Дата и время\nоперации", "Дата обработки\nбанком", "Сумма операции в\nвалюте операции",
         "Сумма операции в валюте\nсчета/карты", "", "Описание операции",
         "Наименование\nполучателя/\nОтправителя"],
        ["", "", "", "Приход", "Расход", "", ""],
    ]
    for op in ops:
        day = op.day.strftime("%d.%m.%Y")
        signed = money(op.amount, style, "-" if op.kind == "expense" else "")
        income = money(op.amount, style) if op.kind == "income" else money(0, style)
        expense = money(op.amount, style, "-") if op.kind == "expense" else money(0, style)
        rows.append([f"{day}\n11:00:00", day, signed, income, expense, _desc(op, style), ""])
    return _table_pdf(rows)


def render_raif_ru(ops: list[Op], style: Style) -> bytes:
    """Райффайзен, русский шаблон: «Поступления» перед «Расходами»."""
    rows = [
        ["№ П/П", "Дата операции", "Номер\nдокумента", "Поступления", "Расходы",
         "Детали операции", "Номер\nкарты"],
        ["", "Выполнена банком", "", "", "", "", ""],
    ]
    for i, op in enumerate(ops, 1):
        day = op.day.strftime("%d.%m.%Y")
        income = money(op.amount, style, "+ ") if op.kind == "income" else ""
        expense = money(op.amount, style, "- ") if op.kind == "expense" else ""
        rows.append([str(i), f"{day} 17:30\n{day}", f"DOC{i:05d}", income, expense,
                     _desc(op, style), ""])
    return _table_pdf(rows)


def render_raif_en(ops: list[Op], style: Style) -> bytes:
    """Райффайзен, английский шаблон: «Debit» перед «Credit» — зеркально русскому."""
    rows = [
        ["№ P/P", "Posting date", "Document number", "Debit", "Credit",
         "Payment details", "Card\nnumber"],
        ["", "Executed by the bank", "", "", "", "", ""],
    ]
    for i, op in enumerate(ops, 1):
        day = op.day.strftime("%d.%m.%Y")
        debit = money(op.amount, style, "- ") if op.kind == "expense" else ""
        credit = money(op.amount, style, "+ ") if op.kind == "income" else ""
        rows.append([str(i), f"{day} 17:30\n{day}", f"DOC{i:05d}", debit, credit,
                     _desc(op, style), ""])
    return _table_pdf(rows)


def render_raif_nonum(ops: list[Op], style: Style) -> bytes:
    """Райффайзен, шаблон без колонки «№»: знаковая сумма в валюте операции и счёта."""
    rows = [
        ["Дата операции", "Номер\nдокумента", "Сумма в валюте\nоперации",
         "Сумма в валюте\nсчета", "Детали операции", "Номер\nкарты"],
        ["Выполнена банком", "", "", "", "", ""],
    ]
    for i, op in enumerate(ops, 1):
        day = op.day.strftime("%d.%m.%Y")
        sign = "- " if op.kind == "expense" else "+ "
        value = money(op.amount, style, sign)
        rows.append([f"{day} 16:10\n{day}", f"DOC{i:05d}", value, value, _desc(op, style), ""])
    return _table_pdf(rows)


def _csv_bytes(header: list[str], rows: list[list[str]], encoding: str = "utf-8",
               bom: bool = False) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(header)
    writer.writerows(rows)
    text = ("\ufeff" if bom else "") + buf.getvalue()
    return text.encode(encoding)


def render_tinkoff_csv(ops: list[Op], style: Style) -> bytes:
    header = ["Дата операции", "Дата платежа", "Номер карты", "Статус", "Сумма операции",
              "Валюта операции", "Сумма платежа", "Валюта платежа", "Кэшбэк", "Категория",
              "MCC", "Описание"]
    rows = []
    for op in ops:
        day = op.day.strftime("%d.%m.%Y")
        amount = f"{'-' if op.kind == 'expense' else ''}{op.amount:.2f}"
        rows.append([f"{day} 12:30:00", day, "*1234", "OK", amount, "RUB", amount, "RUB",
                     "0", "Прочее", "", op.description])
    return _csv_bytes(header, rows, bom=True)


def render_universal_csv(ops: list[Op], style: Style) -> bytes:
    """Универсальный CSV со знаковой суммой."""
    header = ["Дата операции", "Категория", "Сумма", "Назначение платежа"]
    rows = []
    for op in ops:
        amount = money(op.amount, style, "-" if op.kind == "expense" else "")
        rows.append([op.day.strftime("%d.%m.%Y"), "Прочее", amount, op.description])
    return _csv_bytes(header, rows)


def render_universal_split_csv(ops: list[Op], style: Style) -> bytes:
    """Универсальный CSV с раздельными колонками «Приход»/«Расход»."""
    header = ["Дата", "Описание", "Расход", "Приход"]
    rows = []
    for op in ops:
        expense = money(op.amount, style) if op.kind == "expense" else ""
        income = money(op.amount, style) if op.kind == "income" else ""
        rows.append([op.day.strftime("%d.%m.%Y"), op.description, expense, income])
    return _csv_bytes(header, rows)


OWNER_ACCOUNT = "40817810000000000001"


def render_1c(ops: list[Op], style: Style, encoding: str = "cp1251") -> bytes:
    """Формат 1CClientBankExchange. Реальные банки РФ отдают его в windows-1251."""
    lines = ["1CClientBankExchange", "СекцияРасчСчет", f"РасчСчет={OWNER_ACCOUNT}",
             "КонецРасчСчет"]
    for op in ops:
        payer = OWNER_ACCOUNT if op.kind == "expense" else "40702810000000000888"
        payee = "40702810000000000999" if op.kind == "expense" else OWNER_ACCOUNT
        lines += ["СекцияДокумент=Платежное поручение", f"Сумма={op.amount:.2f}",
                  f"ПлательщикСчет={payer}", f"ПолучательСчет={payee}",
                  f"НазначениеПлатежа={op.description}",
                  f"Дата={op.day.strftime('%d.%m.%Y')}", "КонецДокумента"]
    return ("\n".join(lines) + "\n").encode(encoding)
