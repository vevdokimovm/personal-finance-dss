"""Слой 0 — роутер детекции формата выписки по СОДЕРЖИМОМУ (не по bank_id).

Стратегия — `docs/universal_statement_parser_strategy.md` §3-4. Проверяем:
- `detect_format(raw)` определяет семейство формата по magic-байтам/сигнатуре
  (XLSX=ZIP, PDF=%PDF, 1C по префиксу, MT940 по тегам, CSV по табличности), НЕ по bank_id;
- `parse_statement(raw, bank_id=None)` — единая точка входа: детекция → декод → разбор,
  возвращает `StatementParseResult` c форматом, статусом и user-facing сообщением;
- вежливая деградация (Слой 5): скан-PDF → `needs_ocr`, неизвестный формат → `unsupported`,
  MT940 → `unsupported` (распознан, но не реализован в этом батче);
- `bank_id` — только подсказка: детекция и деградация от него не зависят.

PDF в тестах строятся reportlab'ом только там, где нужен реальный текстовый слой
(проверка скан vs текст) — по образцу существующих тестов, живые выписки с PII не кладём.
"""
from __future__ import annotations

import inspect
import io

import openpyxl

from app.services.statement_parser import (
    StatementParseResult,
    _pdf_has_text_layer,
    detect_format,
    parse_statement,
)


def _text_pdf_bytes(line: str = "01.01.2026 02.01.2026 TEST SHOP 100,00 руб") -> bytes:
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 720, line)
    c.save()
    return buf.getvalue()


def _blank_pdf_bytes() -> bytes:
    """PDF без текстового слоя — прокси скан-выписки (image-only тоже даёт пустой extract_text)."""
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.showPage()
    c.save()
    return buf.getvalue()


def _xlsx_bytes(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


_CSV_SEMI = (
    "Дата;Сумма;Описание\n"
    "01.05.2026;-2000,50;Магазин\n"
    "05.05.2026;50000;Оклад\n"
)

_ONE_C = (
    "1CClientBankExchange\n"
    "ВерсияФормата=1.02\n"
    "РасчСчет=40817810000000000001\n"
    "СекцияДокумент=Платежное поручение\n"
    "Сумма=1500.00\n"
    "ПлательщикСчет=40817810000000000001\n"
    "Дата=01.05.2026\n"
    "НазначениеПлатежа=Оплата\n"
    "КонецДокумента\n"
)

_MT940 = (
    ":20:STARTUMS\n"
    ":25:40817810000000000001\n"
    ":28C:00001/001\n"
    ":60F:C260501RUB0,00\n"
    ":61:2605010501D2000,50NTRFNONREF\n"
    ":86:Magazin\n"
    ":62F:C260531RUB47999,50\n"
)


class TestDetectFormat:
    def test_xlsx_by_zip_magic(self):
        raw = _xlsx_bytes([["Дата", "Сумма"], ["01.05.2026", -100]])
        assert raw[:4] == b"PK\x03\x04"
        assert detect_format(raw) == "xlsx"

    def test_pdf_by_magic(self):
        assert detect_format(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n") == "pdf"
        assert detect_format(_text_pdf_bytes()) == "pdf"
        assert detect_format(_blank_pdf_bytes()) == "pdf"

    def test_1c_by_prefix(self):
        assert detect_format(_ONE_C.encode("utf-8")) == "1c"

    def test_1c_prefix_wins_over_delimiters(self):
        # у 1C внутри есть '=' и может встречаться ',' — префикс имеет приоритет над CSV
        assert detect_format(_ONE_C.encode("cp1251")) == "1c"

    def test_1c_detected_in_cp1251(self):
        # сигнатура ASCII — кодировка тела не мешает детекции
        assert detect_format(_ONE_C.encode("cp1251")) == "1c"

    def test_mt940_by_tags(self):
        assert detect_format(_MT940.encode("utf-8")) == "mt940"

    def test_csv_semicolon(self):
        assert detect_format(_CSV_SEMI.encode("utf-8")) == "csv"

    def test_csv_comma(self):
        content = "Date,Amount,Description\n01.05.2026,-100.00,Shop\n05.05.2026,5000.00,Salary\n"
        assert detect_format(content.encode("utf-8")) == "csv"

    def test_csv_in_cp1251(self):
        assert detect_format(_CSV_SEMI.encode("cp1251")) == "csv"

    def test_plain_prose_is_unknown(self):
        assert detect_format("Просто текст, без таблицы".encode("utf-8")) == "unknown"

    def test_single_comma_line_not_csv(self):
        # одна строка с запятой — не таблица
        assert detect_format(b"Hello, world") == "unknown"

    def test_empty_bytes_unknown(self):
        assert detect_format(b"") == "unknown"

    def test_detect_ignores_bank_id(self):
        # detect_format вообще не принимает bank_id — сигнатура чисто по содержимому
        assert list(inspect.signature(detect_format).parameters) == ["raw"]


class TestPdfTextLayer:
    def test_text_pdf_has_layer(self):
        assert _pdf_has_text_layer(_text_pdf_bytes()) is True

    def test_blank_pdf_no_layer(self):
        assert _pdf_has_text_layer(_blank_pdf_bytes()) is False


class TestParseStatementResult:
    def test_returns_result_dataclass(self):
        res = parse_statement(_CSV_SEMI.encode("utf-8"))
        assert isinstance(res, StatementParseResult)
        for attr in ("transactions", "format", "status", "message"):
            assert hasattr(res, attr)

    def test_csv_ok(self):
        res = parse_statement(_CSV_SEMI.encode("utf-8"))
        assert res.format == "csv"
        assert res.status == "ok"
        assert len(res.transactions) == 2
        assert {t["type"] for t in res.transactions} == {"expense", "income"}

    def test_one_c_ok(self):
        res = parse_statement(_ONE_C.encode("utf-8"))
        assert res.format == "1c"
        assert res.status == "ok"
        assert len(res.transactions) == 1
        assert res.transactions[0]["type"] == "expense"  # ПлательщикСчет = счёт владельца

    def test_xlsx_ok(self):
        raw = _xlsx_bytes([
            ["Дата", "Сумма", "Описание"],
            ["01.05.2026", -2000, "Магазин"],
            ["05.05.2026", 50000, "Оклад"],
        ])
        res = parse_statement(raw)
        assert res.format == "xlsx"
        assert res.status == "ok"
        assert len(res.transactions) == 2

    def test_scanned_pdf_needs_ocr(self):
        res = parse_statement(_blank_pdf_bytes())
        assert res.format == "pdf"
        assert res.status == "needs_ocr"
        assert res.transactions == []
        assert "OCR" in res.message or "скан" in res.message.lower()

    def test_text_pdf_no_match_is_empty_not_ocr(self):
        # текстовый PDF, чья раскладка не совпала ни с одним банковским парсером →
        # это "empty" (не смогли разобрать операции), а НЕ "needs_ocr" (текст-слой есть)
        res = parse_statement(_text_pdf_bytes("some text without a parseable operation row"))
        assert res.format == "pdf"
        assert res.status == "empty"

    def test_unknown_unsupported(self):
        res = parse_statement("просто текст".encode("utf-8"))
        assert res.format == "unknown"
        assert res.status == "unsupported"
        assert res.message  # есть подсказка про CSV/XLSX/1C

    def test_mt940_recognized_but_unsupported(self):
        res = parse_statement(_MT940.encode("utf-8"))
        assert res.format == "mt940"
        assert res.status == "unsupported"
        assert "MT940" in res.message

    def test_empty_csv_is_empty_status(self):
        res = parse_statement(b"Date,Amount\n")  # шапка без строк данных
        assert res.format == "csv"
        assert res.status == "empty"


class TestBankIdIsHintNotCondition:
    def test_detection_independent_of_bank_id(self):
        raw = _blank_pdf_bytes()
        # какой бы bank_id ни передали, скан остаётся сканом (детекция по содержимому)
        for bank in (None, "tinkoff", "sber", "unknown-bank"):
            res = parse_statement(raw, bank_id=bank)
            assert res.status == "needs_ocr"

    def test_csv_parsed_same_without_bank_id(self):
        raw = _CSV_SEMI.encode("utf-8")
        a = parse_statement(raw, bank_id=None)
        b = parse_statement(raw, bank_id="universal")
        assert a.transactions == b.transactions
        assert a.status == b.status == "ok"
