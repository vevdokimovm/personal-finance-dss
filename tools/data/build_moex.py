"""Индексы Московской биржи → `data/`.

Оригиналы (`~/raw-originals/finpilot-data/moex/`) — выгрузка ISS
`history/engines/stock/markets/index`, разделитель `;`, кодировка cp1251,
20 колонок. В каталог кладём только то, что нужно ядру: цену закрытия,
а для RGBI ещё доходность и дюрацию корзины ОФЗ.

Запуск: `python -m tools.data.build_moex`
"""
from __future__ import annotations

import argparse
import csv
import io
import logging
from pathlib import Path

from tools.data.common import Row, raw_root, to_float, write_series

logger = logging.getLogger(__name__)

INDEXES = {
    "IMOEX": ("moex_imoex_daily.csv", "index_points", ()),
    "MCFTR": ("moex_mcftr_daily.csv", "index_points", ()),
    "RTSI": ("moex_rtsi_daily.csv", "index_points", ()),
    "RGBI": ("moex_rgbi_daily.csv", "index_points", ("YIELD", "DURATION")),
    "RGBITR": ("moex_rgbitr_daily.csv", "index_points", ()),
    "MREDC": ("moex_mredc_daily.csv", "rub_per_sqm", ()),
}
EXTRA_UNITS = {"YIELD": "percent_annual", "DURATION": "days"}


def read_index(path: Path, extras: tuple[str, ...], unit: str) -> list[Row]:
    """Прочитать дневные свечи одного индекса.

    Args:
        path: путь к CSV-выгрузке ISS.
        extras: дополнительные колонки, которые нужно сохранить
            (например `YIELD` у индекса ОФЗ).
        unit: единица измерения закрытия.

    Returns:
        Строки ряда: закрытие плюс дополнительные колонки как разрезы.
    """
    text = path.read_bytes().decode("cp1251")
    reader = csv.DictReader(io.StringIO(text.lstrip("\r\n")), delimiter=";")
    rows: list[Row] = []
    for record in reader:
        date = (record.get("TRADEDATE") or "").strip()
        if not date:
            continue
        close = to_float(record.get("CLOSE"))
        if close is not None:
            rows.append(Row(date, close, unit, "RU", "close"))
        for name in extras:
            value = to_float(record.get(name))
            if value is not None:
                rows.append(Row(date, value, EXTRA_UNITS[name], "RU",
                                name.lower()))
    rows.sort(key=lambda item: (item.date, item.breakdown))
    return rows


def build(raw_dir: Path, out_dir: Path | None = None) -> None:
    """Собрать все индексы.

    Args:
        raw_dir: каталог оригиналов.
        out_dir: каталог назначения.
    """
    for secid, (name, unit, extras) in INDEXES.items():
        path = raw_dir / "moex" / f"moex_{secid}_daily.csv"
        if not path.exists():
            logger.warning("нет файла %s", path)
            continue
        write_series(name, read_index(path, extras, unit), out_dir)


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
