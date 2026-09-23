"""Цены жилья и аренды недвижимости по субъектам РФ → `data/`.

Оригиналы (`~/raw-originals/finpilot-data/rosstat_housing/`):
  * `sred_cen_perv_*.xlsx` — средние цены первичного рынка жилья;
  * `sred_cen_vtor_*.xlsx` — то же по вторичному рынку;
  * `Nedvijimost_arenda_Cena_2kv-2026.xlsx` — средние цены аренды
    коммерческой недвижимости (жилой аренды в открытой статистике нет).

Год берётся из заголовка листа, квартал — из шапки таблицы; в каждом
квартале сохраняются все классы качества квартир.

Запуск: `python -m tools.data.build_rosstat_housing`
"""
from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import openpyxl

from tools.data.common import Row, raw_root, to_float, write_series

logger = logging.getLogger(__name__)

QUARTER_END = {"I": "03-31", "II": "06-30", "III": "09-30", "IV": "12-31"}
QUARTER_HEADER = re.compile(r"^(IV|III|II|I) квартал")


def clean(text: object) -> str:
    """Сжать подпись ячейки в одну строку.

    Args:
        text: исходная ячейка.

    Returns:
        Подпись без переносов и лишних пробелов.
    """
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_code(label: str) -> str:
    """Убрать код ОКТМО из названия региона.

    Args:
        label: подпись вида `«643 - Российская Федерация»`.

    Returns:
        Название региона.
    """
    return re.sub(r"^[\d\s]+-\s*", "", clean(label))


def quarter_columns(rows: list[tuple]) -> tuple[int, dict[int, str]]:
    """Найти строку шапки с кварталами и разметить колонки.

    Подпись квартала стоит над первой колонкой своего блока; все колонки
    правее неё до следующей подписи относятся к тому же кварталу.

    Args:
        rows: строки листа (`values_only`).

    Returns:
        Номер строки шапки и отображение «номер колонки → квартал».
    """
    quarter_row = next(i for i, raw in enumerate(rows)
                       if any(QUARTER_HEADER.match(clean(cell))
                              for cell in raw if cell))
    quarters: dict[int, str] = {}
    current = ""
    for index, cell in enumerate(rows[quarter_row]):
        match = QUARTER_HEADER.match(clean(cell))
        if match:
            current = match.group(1)
        if current and index:
            quarters[index] = current
    return quarter_row, quarters


def cell_at(row: tuple, index: int) -> object:
    """Взять ячейку строки, если колонка существует.

    Args:
        row: строка листа.
        index: номер колонки.

    Returns:
        Значение ячейки или None за правым краем строки.
    """
    return row[index] if index < len(row) else None


def read_price_book(path: Path, market: str) -> list[Row]:
    """Прочитать книгу средних цен жилья.

    Args:
        path: путь к книге Росстата.
        market: `primary` или `secondary`.

    Returns:
        Строки ряда: цена м² по кварталу, региону и классу квартир.
    """
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = book[book.sheetnames[1]]
    rows = list(sheet.iter_rows(values_only=True))
    quarter_row, quarters = quarter_columns(rows)
    title = " ".join(clean(cell) for raw in rows[:quarter_row]
                     for cell in raw if cell)
    year_match = re.search(r"в (\d{4}) году", title)
    if not year_match:
        logger.warning("год не найден в заголовке %s", path.name)
        return []
    year = year_match.group(1)
    total_row, classes_row = quarter_row + 1, quarter_row + 2
    kinds: dict[int, str] = {}
    for index in quarters:
        top = clean(cell_at(rows[total_row], index))
        sub = clean(cell_at(rows[classes_row], index))
        if top and not top.lower().startswith("из них"):
            kinds[index] = top.lower()
        elif sub:
            kinds[index] = sub.lower()
    out: list[Row] = []
    for raw in rows[classes_row + 1:]:
        region = strip_code(raw[0])
        if not region:
            continue
        for index, quarter in quarters.items():
            kind = kinds.get(index)
            if not kind:
                continue
            value = to_float(cell_at(raw, index))
            if value is None:
                continue
            out.append(Row(f"{year}-{QUARTER_END[quarter]}", value,
                           "rub_per_sqm", region, f"{market}|{kind}"))
    return out


def read_rent_book(path: Path) -> list[Row]:
    """Прочитать книгу средних цен аренды КОММЕРЧЕСКОЙ недвижимости.

    🔴 Это аренда зданий, помещений, сооружений и машино-мест, а НЕ аренда
    квартир: жилой аренды в открытой статистике Росстата нет. Разрез типа
    объекта сохраняется дословно, чтобы одно не выдавалось за другое.

    Из десятка блоков по классам объектов берётся только «Все объекты»:
    остальные (энергетика, металлургия, инженерные сети) к личным финансам
    отношения не имеют и вчетверо раздували бы файл.

    Год в самой книге не указан: лист `1` — прошлый год (четыре квартала),
    лист `2` — год из имени файла (кварталы по мере выхода).

    Args:
        path: путь к книге `Nedvijimost_arenda_Cena_*.xlsx`.

    Returns:
        Строки ряда: цена аренды м² в месяц по кварталу, региону и типу
        объекта.
    """
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    name_year = re.search(r"(\d{4})", path.name)
    if not name_year:
        raise ValueError(f"год не выводится из имени файла: {path.name}")
    current_year = int(name_year.group(1))
    out: list[Row] = []
    for sheet_name, year in (("1", current_year - 1), ("2", current_year)):
        if sheet_name not in book.sheetnames:
            continue
        rows = list(book[sheet_name].iter_rows(values_only=True))
        quarter_row, quarters = quarter_columns(rows)
        kinds_row = quarter_row + 1
        block = ""
        for raw in rows[kinds_row + 1:]:
            region = strip_code(raw[0])
            if not region:
                continue
            if not any(cell not in (None, "") for cell in raw[1:]):
                block = region
                continue
            if not block.lower().startswith("все объекты"):
                continue
            for index, quarter in quarters.items():
                kind = clean(cell_at(rows[kinds_row], index))
                value = to_float(cell_at(raw, index))
                if value is None or not kind:
                    continue
                out.append(Row(f"{year}-{QUARTER_END[quarter]}", value,
                               "rub_per_sqm_month", region, kind.lower()))
    out.sort(key=lambda item: (item.date, item.region, item.breakdown))
    return out


def build(raw_dir: Path, out_dir: Path | None = None) -> None:
    """Собрать ряды цен жилья и аренды.

    Args:
        raw_dir: каталог оригиналов.
        out_dir: каталог назначения.
    """
    folder = raw_dir / "rosstat_housing"
    prices: dict[tuple[str, str, str], Row] = {}
    for path in sorted(folder.glob("sred_cen_*.xlsx")):
        market = "primary" if "_perv" in path.name else "secondary"
        for row in read_price_book(path, market):
            prices[(row.date, row.region, row.breakdown)] = row
    write_series("rosstat_housing_price_m2_region_quarter.csv",
                 [prices[key] for key in sorted(prices)], out_dir)
    rent_path = folder / "Nedvijimost_arenda_Cena_2kv-2026.xlsx"
    if rent_path.exists():
        write_series("rosstat_commercial_rent_m2_region_quarter.csv",
                     read_rent_book(rent_path), out_dir)


def main() -> None:
    """Точка входа командной строки."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=raw_root())
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    build(args.raw_dir, args.out_dir)


if __name__ == "__main__":
    main()
