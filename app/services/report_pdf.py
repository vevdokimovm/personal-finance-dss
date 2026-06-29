"""PDF финансовый отчёт (P3.1).

reportlab Platypus + забандленный шрифт Liberation Sans (кириллица работает на любой
системе, не зависит от наличия системных шрифтов). Возвращает готовые байты PDF.
"""
from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_FONT = "FinpilotSans"
_FONT_BOLD = "FinpilotSans-Bold"
_BRAND = colors.HexColor("#2BBF6A")
_fonts_registered = False


def _ensure_fonts() -> None:
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont(_FONT, str(_FONT_DIR / "LiberationSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(_FONT_DIR / "LiberationSans-Bold.ttf")))
    _fonts_registered = True


def _money(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ") + " руб"


def _table(rows: list[list[str]]) -> Table:
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), _FONT),
                ("FONTNAME", (0, 0), (-1, 0), _FONT_BOLD),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 0), (-1, 0), _BRAND),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9F8")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build_financial_report_pdf(report: dict) -> bytes:
    """Собирает PDF финансового отчёта из словаря данных и возвращает байты."""
    _ensure_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="FINPILOT — финансовый отчёт",
    )
    body = ParagraphStyle("Body", fontName=_FONT, fontSize=10, leading=15)
    h1 = ParagraphStyle("H1", fontName=_FONT_BOLD, fontSize=18, leading=22, textColor=_BRAND)
    h2 = ParagraphStyle("H2", fontName=_FONT_BOLD, fontSize=13,
                        leading=18, spaceBefore=12, spaceAfter=6)
    small = ParagraphStyle("Small", fontName=_FONT, fontSize=8, textColor=colors.grey, leading=11)

    story: list = [
        Paragraph("FINPILOT — финансовый отчёт", h1),
        Paragraph(f"Сформирован {report['generated_at']}", small),
        Spacer(1, 12),
        Paragraph("Сводка", h2),
        _table([
            ["Показатель", "Значение"],
            ["Доходы", _money(report["income"])],
            ["Расходы", _money(report["expense"])],
            ["Платежи по обязательствам", _money(report["obligations_payment"])],
            ["Свободный ресурс", _money(report["free_resource"])],
        ]),
        Spacer(1, 8),
        Paragraph("Обязательства", h2),
    ]

    if report["obligations"]:
        rows = [["Название", "Остаток", "Ставка", "Платёж"]]
        for obl in report["obligations"]:
            rows.append([obl["name"], _money(obl["amount"]),
                        f"{obl['rate']:.1f}%", _money(obl["payment"])])
        story.append(_table(rows))
    else:
        story.append(Paragraph("Обязательств нет.", body))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Цели", h2))
    if report["goals"]:
        rows = [["Цель", "Накоплено", "Целевая сумма", "Прогресс"]]
        for goal in report["goals"]:
            pct = (goal["current"] / goal["target"] * 100) if goal["target"] else 0
            rows.append([goal["name"], _money(goal["current"]),
                        _money(goal["target"]), f"{pct:.0f}%"])
        story.append(_table(rows))
    else:
        story.append(Paragraph("Целей нет.", body))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Информационный документ. Не является индивидуальной инвестиционной рекомендацией "
        "в значении Федерального закона № 39-ФЗ.", small,
    ))

    doc.build(story)
    return buffer.getvalue()
