"""
Генератор эталонных шаблонов банковских выписок (§6.4).

Кладёт в `app/data/statement_templates/` по одному образцу на каждый формат/парсер:
CSV (Тинькофф, Сбер, универсальный знаковый, универсальный split Приход/Расход),
XLSX (универсальный), PDF (Тинькофф текст, Сбер текст, ВТБ таблица, Райффайзен
таблица), 1C-обмен. Образцы синтетические (не реальные выписки — приватность), но
1-в-1 повторяют формат каждого банка, поэтому существующие парсеры читают их без
правок. Служат тройной цели: golden-фикстуры для тестов корректности чтения
(`tests/test_statement_templates.py`), эталон формата для разработчика и образец
«как должна выглядеть выписка» для пользователя.

PDF рендерятся DejaVuSans (кириллица + знак ₽); pdfplumber извлекает текст/таблицы
обратно бит-в-бит (проверено round-trip). Запуск:
    python -m tools.statement_templates.build_templates
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

import openpyxl
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path("app/data/statement_templates")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT = "DejaVu"


def _ensure_font() -> None:
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))


def _write_csv(name: str, header: list[str], rows: list[list[str]], bom: bool = False) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(header)
    w.writerows(rows)
    text = ("\ufeff" if bom else "") + buf.getvalue()
    (OUT / name).write_text(text, encoding="utf-8")


def build_tinkoff_csv() -> None:
    # Формат ЛК Тинькофф; строка со статусом FAILED должна отсеяться парсером.
    header = [
        "Дата операции", "Дата платежа", "Номер карты", "Статус", "Сумма операции",
        "Валюта операции", "Сумма платежа", "Валюта платежа", "Кэшбэк", "Категория",
        "MCC", "Описание",
    ]
    rows = [
        ["15.01.2026 12:30:00", "15.01.2026", "*1234", "OK", "-1234.56", "RUB",
         "-1234.56", "RUB", "12", "Супермаркеты", "5411", "Пятёрочка"],
        ["16.01.2026 09:00:00", "16.01.2026", "*1234", "OK", "80000.00", "RUB",
         "80000.00", "RUB", "0", "Пополнения", "", "Зарплата"],
        ["17.01.2026 20:00:00", "17.01.2026", "*1234", "FAILED", "-500.00", "RUB",
         "-500.00", "RUB", "0", "Прочее", "", "Отменённая операция"],
    ]
    _write_csv("tinkoff.csv", header, rows, bom=True)


def build_sber_csv() -> None:
    header = ["№", "Дата", "Описание", "Категория", "Сумма", "Валюта", "Статус"]
    rows = [
        ["1", "10.01.2026", "Магнит", "Супермаркеты", "-899.00", "RUB", "OK"],
        ["2", "11.01.2026", "Аванс", "Зарплата", "45000.00", "RUB", "OK"],
    ]
    _write_csv("sber.csv", header, rows)


def build_universal_single_csv() -> None:
    # Метаданные счёта над таблицей — проверяют детекцию строки-заголовка.
    lines = [
        "Выписка по счёту 40817810000000000001",
        "Период: 01.01.2026 - 31.01.2026",
        "",
        "Дата операции;Категория;Сумма;Назначение платежа",
        "05.01.2026;Кафе;-450.00;Кофейня на углу",
        "06.01.2026;Доход;30000.00;Фриланс-проект",
    ]
    (OUT / "universal_single.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_universal_split_csv() -> None:
    # Раздельные колонки Приход/Расход (частый формат выгрузок).
    header = ["Дата", "Описание", "Расход", "Приход"]
    rows = [
        ["07.01.2026", "Аптека Ригла", "350.00", ""],
        ["08.01.2026", "Возврат за товар", "", "1200.00"],
    ]
    _write_csv("universal_split.csv", header, rows)


def build_universal_xlsx() -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Отчёт по карте", None, None, None])   # метаданные над шапкой
    ws.append(["Дата", "Категория", "Сумма", "Назначение"])
    ws.append(["09.01.2026", "Транспорт", -120.00, "Метро"])
    ws.append(["10.01.2026", "Кэшбэк", 250.00, "Возврат кэшбэка"])
    wb.save(OUT / "universal.xlsx")


def build_tinkoff_pdf() -> None:
    # Текстовая PDF-выписка: дата(2-знач. год) дата2 описание [±]сумма ₽.
    _ensure_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont(FONT, 11)
    c.drawString(40, 800, "Справка о движении средств — Тинькофф")
    c.setFont(FONT, 10)
    y = 770
    for line in [
        "15.01.26 15.01.26 Пятёрочка -1 234,56 ₽",
        "16.01.26 16.01.26 Зарплата +80 000,00 ₽",
    ]:
        c.drawString(40, y, line)
        y -= 16
    c.save()
    (OUT / "tinkoff.pdf").write_bytes(buf.getvalue())


def build_sber_pdf() -> None:
    # Текстовая PDF-выписка Сбера: строка операции + строка описания следом.
    _ensure_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont(FONT, 11)
    c.drawString(40, 800, "Выписка по платёжному счёту — СберБанк")
    c.setFont(FONT, 10)
    y = 770
    for line in [
        "10.01.2026 12:30 Супермаркеты -899,00 15 000,00",
        "10.01.2026 AUTH123 Магнит у дома",
        "11.01.2026 09:00 Зарплата +45 000,00 60 000,00",
        "11.01.2026 AUTH999 Аванс компании",
    ]:
        c.drawString(40, y, line)
        y -= 16
    c.save()
    (OUT / "sber.pdf").write_bytes(buf.getvalue())


def _table_pdf(name: str, title: str, data: list[list[str]],
               intro: list[str] | None = None) -> None:
    """Табличный PDF. `intro` — строки над таблицей: реальные выписки несут там
    контрольные итоги (период, поступления, расходы), по которым импорт себя сверяет."""
    _ensure_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
    style = ParagraphStyle("intro", fontName=FONT, fontSize=9, leading=13)
    flow: list = [Paragraph(line, style) for line in (intro or [])]
    if flow:
        flow.append(Spacer(1, 12))
    table = Table(data)
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT, 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    flow.append(table)
    doc.build(flow)
    (OUT / name).write_bytes(buf.getvalue())


def build_vtb_pdf() -> None:
    # Табличная выписка ВТБ: колонка[2] — знаковая сумма в валюте операции.
    data = [
        ["Дата", "Дата обр.", "Сумма", "Приход", "Расход", "Комиссия", "Описание"],
        ["12.01.2026 10:00", "12.01.2026", "-1 500,00", "", "1 500,00", "0,00", "Ozon"],
        ["13.01.2026 11:00", "13.01.2026", "25 000,00", "25 000,00", "", "0,00", "Перевод"],
    ]
    # Контрольные итоги в шапке — по ним импорт сверяет сам себя (см.
    # app/services/statement_reconcile.py): приход 25 000, расход 1 500.
    _table_pdf("vtb.pdf", "Выписка ВТБ", data, intro=[
        "Банк ВТБ (ПАО). Выписка по счёту",
        "Период выписки 01.01.2026 - 31.01.2026",
        "Баланс на начало периода 10000.00 RUB Поступления 25000.00 RUB",
        "Баланс на конец периода 33500.00 RUB Расходные операции 1500.00 RUB",
    ])


def build_raiffeisen_pdf() -> None:
    # Реальный РУССКИЙ шаблон Райффайзена: колонки «Поступления»/«Расходы» (в английском
    # шаблоне на их местах зеркально стоят Debit/Credit), значения — со знаком, служебная
    # строка «Выполнена банком» между шапкой и данными.
    data = [
        ["№ П/П", "Дата операции", "Номер документа", "Поступления", "Расходы",
         "Детали операции", "Номер карты"],
        ["", "Выполнена банком", "", "", "", "", ""],
        ["1", "14.01.2026 08:00", "DOC1", "", "- 780,00 ₽", "Аптека Ригла", "*5678"],
        ["2", "15.01.2026 09:00", "DOC2", "+ 3 000,00 ₽", "", "Кэшбэк", "*5678"],
    ]
    # «Обороты» — контрольные итоги: сначала приход, затем расход (порядок повторяет
    # порядок колонок шаблона, по нему сверка и определяет, где что).
    _table_pdf("raiffeisen.pdf", "Выписка Райффайзен", data, intro=[
        "АО «Райффайзенбанк». Выписка по счёту",
        "Обороты 3 000,00 780,00",
    ])


def build_1c() -> None:
    # Формат 1CClientBankExchange (бизнес-счета). Владелец — 40817...0001.
    lines = [
        "1CClientBankExchange",
        "СекцияРасчСчет",
        "РасчСчет=40817810000000000001",
        "КонецРасчСчет",
        "СекцияДокумент=Платежное поручение",
        "Сумма=5000.00",
        "ПлательщикСчет=40817810000000000001",
        "ПолучательСчет=40702810000000000999",
        "НазначениеПлатежа=Оплата услуг связи",
        "Дата=16.01.2026",
        "КонецДокумента",
        "СекцияДокумент=Платежное поручение",
        "Сумма=90000.00",
        "ПлательщикСчет=40702810000000000888",
        "ПолучательСчет=40817810000000000001",
        "НазначениеПлатежа=Поступление зарплаты",
        "Дата=17.01.2026",
        "КонецДокумента",
    ]
    (OUT / "sberbank_1c.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Реальные банки РФ отдают 1C в windows-1251 (шапка `Кодировка=Windows`) — вариант
    # для теста надёжного декодирования (декодер форсит cp1251 по магии 1CClientBankExchange).
    (OUT / "sberbank_1c_cp1251.bin").write_bytes(
        ("\n".join(lines) + "\n").encode("cp1251"))


MANIFEST = """# Эталонные шаблоны банковских выписок

Синтетические образцы (не реальные выписки) в формате каждого банка. Golden-фикстуры
для `tests/test_statement_templates.py`, эталон формата и образец для пользователя.
Регенерация: `python -m tools.statement_templates.build_templates`.

| Файл | Формат | Парсер | bank_id | Операций |
|---|---|---|---|---|
| `tinkoff.csv` | CSV (`;`, BOM) | `parse_tinkoff_csv` | tinkoff | 2 (+1 FAILED отсеяна) |
| `sber.csv` | CSV (`;`) | `parse_sber_csv` | sber | 2 |
| `universal_single.csv` | CSV знаковая | `parse_universal_csv` | universal | 2 |
| `universal_split.csv` | CSV (split Приход/Расход) | `parse_universal_csv` | universal | 2 |
| `universal.xlsx` | XLSX | `parse_xlsx` | universal | 2 |
| `tinkoff.pdf` | PDF (текст) | `parse_tinkoff_pdf` | tinkoff | 2 |
| `sber.pdf` | PDF (текст, описание на след. строке) | `parse_sber_pdf` | sber | 2 |
| `vtb.pdf` | PDF (таблица, знаковая сумма) | `parse_vtb_pdf` | vtb | 2 |
| `raiffeisen.pdf` | PDF таблица (Поступления/Расходы) | `parse_raiffeisen_pdf` | raiffeisen | 2 |
| `sberbank_1c.txt` | 1CClientBankExchange | `parse_1c_exchange` | — | 2 |

Стратегия покрытия ~200 банков — `docs/universal_statement_parser_strategy.md`:
5 выделенных парсеров под крупные банки + универсальный (CSV/XLSX по эвристикам
колонок) + 1C-обмен покрывают длинный хвост без парсера на каждый банк.
"""


def build_all() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_tinkoff_csv()
    build_sber_csv()
    build_universal_single_csv()
    build_universal_split_csv()
    build_universal_xlsx()
    build_tinkoff_pdf()
    build_sber_pdf()
    build_vtb_pdf()
    build_raiffeisen_pdf()
    build_1c()
    (OUT / "MANIFEST.md").write_text(MANIFEST, encoding="utf-8")
    print(f"✓ шаблоны собраны в {OUT}/ ({len(list(OUT.iterdir()))} файлов)")


if __name__ == "__main__":
    build_all()
