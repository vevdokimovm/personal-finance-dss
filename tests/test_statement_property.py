"""
Property-тесты парсера: сгенерировали выписку → распарсили → сверили с задуманным (Б2).

**Границы метода.** Генератор знает ровно те шаблоны, что и парсер, поэтому зелёный прогон
здесь НЕ доказывает, что читаются двести банков — это замкнутый круг. Что он доказывает:
устойчивость ВНУТРИ известного формата к вариациям, которые встречаются в живых выписках
(неразрывные пробелы, разделители тысяч и их отсутствие, запятая против точки, суффиксы
валюты, перенос описания внутри ячейки, копеечные суммы, длинные описания). Реальных файлов
на руках одиннадцать — фаззинг закрывает пространство между ними.

Доказательство корректности на конкретном файле — сверка с контрольными итогами банка
(`tests/test_statement_reconcile.py`), а не эти тесты.
"""
from __future__ import annotations

from datetime import date

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.services.statement_parser import (
    decode_statement_bytes,
    parse_bank_statement,
    parse_raiffeisen_pdf,
    parse_tinkoff_csv,
    parse_universal_csv,
    parse_vtb_pdf,
)
from tools.statement_templates.synth import Op, Style, render_1c
from tools.statement_templates.synth import render_raif_en, render_raif_nonum, render_raif_ru
from tools.statement_templates.synth import render_tinkoff_csv, render_universal_csv
from tools.statement_templates.synth import render_universal_split_csv, render_vtb_a, render_vtb_b

# Описания — как в живых выписках: кириллица, латиница, цифры, точки. Без «;» и переводов
# строки: они разрушили бы сам формат файла, а не проверили парсер.
_WORDS = st.text(alphabet="абвгдеж ЁЙABCXYZ0123456789.-", min_size=1, max_size=40)


@st.composite
def operations(draw, min_size: int = 1, max_size: int = 8) -> list[Op]:
    count = draw(st.integers(min_value=min_size, max_value=max_size))
    ops = []
    for _ in range(count):
        kopecks = draw(st.integers(min_value=1, max_value=99_999_999))
        # Описание нормализуем сразу: CSV и 1C отдают его дословно, а табличные PDF
        # схлопывают пробелы при извлечении ячейки. Сравнивать «как есть» можно только
        # с уже нормализованным текстом, иначе тест ловит различие форматов, а не дефект.
        raw_text = " ".join(draw(_WORDS).split())
        ops.append(Op(
            day=draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))),
            kind=draw(st.sampled_from(["income", "expense"])),
            amount=round(kopecks / 100, 2),
            description=raw_text or "Операция",
        ))
    return ops


@st.composite
def styles(draw) -> Style:
    return Style(
        thousands=draw(st.sampled_from([" ", "\u00a0", ""])),
        decimal=draw(st.sampled_from([",", "."])),
        suffix=draw(st.sampled_from([" ₽", " RUB", ""])),
        wrap_description=draw(st.booleans()),
    )


def assert_roundtrip(ops: list[Op], parsed: list[dict]) -> None:
    """Распознанное обязано совпасть с задуманным: состав, порядок, знак, сумма, дата."""
    assert len(parsed) == len(ops), f"операций {len(parsed)}, а задумано {len(ops)}"
    for want, got in zip(ops, parsed):
        assert got["date"][:10] == want.day.isoformat(), f"дата {got['date']} != {want.day}"
        assert got["type"] == want.kind, f"тип {got['type']} != {want.kind} ({want.description})"
        assert got["amount"] == pytest.approx(want.amount), \
            f"сумма {got['amount']} != {want.amount}"
        assert got["description"] == want.description, \
            f"описание {got['description']!r} != {want.description!r}"


PDF_SETTINGS = settings(max_examples=25, deadline=None,
                        suppress_health_check=[HealthCheck.too_slow])
TEXT_SETTINGS = settings(max_examples=100, deadline=None,
                         suppress_health_check=[HealthCheck.too_slow])


@pytest.mark.property
class TestVtbRoundtrip:
    """Оба реальных шаблона ВТБ: A («Комиссия» на 5, «Расход» положительный) и
    B («Описание» на 5, контрагент на 6, «Расход» отрицательный)."""

    @given(ops=operations(), style=styles())
    @PDF_SETTINGS
    def test_template_a(self, ops, style):
        assert_roundtrip(ops, parse_vtb_pdf(render_vtb_a(ops, style)))

    @given(ops=operations(), style=styles())
    @PDF_SETTINGS
    def test_template_b(self, ops, style):
        assert_roundtrip(ops, parse_vtb_pdf(render_vtb_b(ops, style)))


@pytest.mark.property
class TestRaiffeisenRoundtrip:
    """Три реальных шаблона Райффайзена, включая зеркальные RU/EN и вариант без колонки «№»."""

    @given(ops=operations(), style=styles())
    @PDF_SETTINGS
    def test_russian_template(self, ops, style):
        assert_roundtrip(ops, parse_raiffeisen_pdf(render_raif_ru(ops, style)))

    @given(ops=operations(), style=styles())
    @PDF_SETTINGS
    def test_english_template(self, ops, style):
        assert_roundtrip(ops, parse_raiffeisen_pdf(render_raif_en(ops, style)))

    @given(ops=operations(), style=styles())
    @PDF_SETTINGS
    def test_template_without_number_column(self, ops, style):
        assert_roundtrip(ops, parse_raiffeisen_pdf(render_raif_nonum(ops, style)))


@pytest.mark.property
class TestCsvRoundtrip:
    @given(ops=operations(max_size=20), style=styles())
    @TEXT_SETTINGS
    def test_tinkoff_csv(self, ops, style):
        raw = render_tinkoff_csv(ops, style)
        assert_roundtrip(ops, parse_tinkoff_csv(decode_statement_bytes(raw)))

    @given(ops=operations(max_size=20), style=styles())
    @TEXT_SETTINGS
    def test_universal_signed_csv(self, ops, style):
        raw = render_universal_csv(ops, style)
        assert_roundtrip(ops, parse_universal_csv(decode_statement_bytes(raw)))

    @given(ops=operations(max_size=20), style=styles())
    @TEXT_SETTINGS
    def test_universal_split_csv(self, ops, style):
        raw = render_universal_split_csv(ops, style)
        assert_roundtrip(ops, parse_universal_csv(decode_statement_bytes(raw)))


@pytest.mark.property
class TestOneCRoundtrip:
    @given(ops=operations(max_size=20), style=styles())
    @TEXT_SETTINGS
    def test_cp1251_exchange(self, ops, style):
        raw = render_1c(ops, style, encoding="cp1251")
        assert_roundtrip(ops, parse_bank_statement(decode_statement_bytes(raw)))

    @given(ops=operations(max_size=20), style=styles())
    @TEXT_SETTINGS
    def test_utf8_exchange(self, ops, style):
        raw = render_1c(ops, style, encoding="utf-8")
        assert_roundtrip(ops, parse_bank_statement(decode_statement_bytes(raw)))


@pytest.mark.property
class TestRobustness:
    """Случаи, которые случайный фаззинг не нащупает, а реальность подкидывает."""

    def _many(self, count: int) -> list[Op]:
        return [Op(day=date(2026, 1, 1 + i % 28),
                   kind="income" if i % 3 == 0 else "expense",
                   amount=round(10 + i * 13.7, 2),
                   description=f"Операция номер {i}")
                for i in range(count)]

    @pytest.mark.parametrize("render,parse", [
        (render_vtb_a, parse_vtb_pdf),
        (render_vtb_b, parse_vtb_pdf),
        (render_raif_ru, parse_raiffeisen_pdf),
        (render_raif_nonum, parse_raiffeisen_pdf),
    ])
    def test_multipage_statement_keeps_every_operation(self, render, parse):
        # 60 операций — таблица уходит на несколько страниц. Шапка при этом печатается
        # ОДИН раз, поэтому на второй странице карту колонок нужно унаследовать: иначе
        # хвост выписки молча потеряется или уедет в позиционный фолбэк.
        ops = self._many(60)
        assert_roundtrip(ops, parse(render(ops, Style())))

    def test_kopeck_amounts_survive(self):
        ops = [Op(date(2026, 3, 1), "expense", 0.01, "Копейка"),
               Op(date(2026, 3, 2), "income", 0.99, "Почти рубль")]
        assert_roundtrip(ops, parse_vtb_pdf(render_vtb_b(ops, Style())))

    def test_large_amounts_with_nbsp_separator(self):
        ops = [Op(date(2026, 3, 3), "income", 999999.99, "Крупный перевод")]
        style = Style(thousands="\u00a0", decimal=",", suffix=" ₽")
        assert_roundtrip(ops, parse_raiffeisen_pdf(render_raif_ru(ops, style)))
