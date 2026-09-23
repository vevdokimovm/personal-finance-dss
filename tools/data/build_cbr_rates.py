"""Курсы, ключевая ставка и RUONIA Банка России → `data/`.

Оригиналы (`~/raw-originals/finpilot-data/cbr/`):
  * `cbr_usd_rub_daily_1992_2026.xml`, `cbr_eur_rub_daily_1999_2026.xml`,
    `cbr_cny_rub_daily_2010_2026.xml` — выгрузка `XML_dynamic.asp`, cp1251;
  * `cbr_key_rate_daily_2013_2026.xml` — SOAP `KeyRateXML`;
  * `cbr_ruonia_daily_2010_2026.xml` — SOAP `Ruonia`.

Кроме самих рядов считает производный ряд месячной волатильности курса
с разметкой режима среды (спокойный / напряжённый / кризисный).

Запуск: `python -m tools.data.build_cbr_rates`
"""
from __future__ import annotations

import argparse
import logging
import math
import re
import statistics
from pathlib import Path

from tools.data.common import Row, raw_root, to_float, write_series

logger = logging.getLogger(__name__)

TRADING_DAYS = 252
CALM_MAX = 0.20
STRESS_MAX = 0.35
FX_FILES = {
    "USD": "cbr_usd_rub_daily_1992_2026.xml",
    "EUR": "cbr_eur_rub_daily_1999_2026.xml",
    "CNY": "cbr_cny_rub_daily_2010_2026.xml",
}


def read_fx(path: Path) -> list[tuple[str, float]]:
    """Прочитать дневной ряд курса из выгрузки `XML_dynamic.asp`.

    Курс приводится к «рублей за одну единицу валюты»: в выгрузке ЦБ он
    дан на номинал (10, 100 единиц), и без деления ряд рвётся на сменах
    номинала.

    Args:
        path: путь к XML-файлу.

    Returns:
        Список пар «дата ISO → курс за одну единицу».
    """
    text = path.read_bytes().decode("cp1251")
    pattern = re.compile(
        r'<Record Date="(\d{2})\.(\d{2})\.(\d{4})"[^>]*>'
        r"<Nominal>(\d+)</Nominal><Value>([\d,\.]+)</Value>"
    )
    series: list[tuple[str, float]] = []
    for day, month, year, nominal, value in pattern.findall(text):
        rate = to_float(value)
        if rate is None:
            continue
        series.append((f"{year}-{month}-{day}", rate / float(nominal)))
    series.sort()
    return series


def read_soap_pairs(path: Path, date_tag: str, value_tag: str) -> list[
        tuple[str, float]]:
    """Прочитать ряд «дата → число» из SOAP-ответа ЦБ.

    Args:
        path: путь к XML-файлу ответа.
        date_tag: имя тега с датой (`DT`, `D0`).
        value_tag: имя тега со значением (`Rate`, `ruo`).

    Returns:
        Отсортированный список пар «дата ISO → значение».
    """
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"<{date_tag}>(\d{{4}}-\d{{2}}-\d{{2}})[^<]*</{date_tag}>"
        rf"\s*<{value_tag}>([\d\.,]+)</{value_tag}>"
    )
    series = []
    for date, value in pattern.findall(text):
        number = to_float(value)
        if number is not None:
            series.append((date, number))
    series.sort()
    return series


def monthly_volatility(series: list[tuple[str, float]]) -> list[Row]:
    """Посчитать месячную реализованную волатильность курса и режим.

    Волатильность — стандартное отклонение дневных логарифмических
    приращений внутри месяца, аннуализированное умножением на √252.
    Режим: до 20 % — спокойный, 20–35 % — напряжённый, выше —
    кризисный.

    Args:
        series: дневной ряд курса.

    Returns:
        Строки ряда: аннуализированная волатильность, σ месячного
        лог-приращения и метка режима на каждый месяц.
    """
    returns: dict[str, list[float]] = {}
    month_levels: dict[str, tuple[float, float]] = {}
    previous = None
    for date, rate in series:
        if previous is not None and previous[1] > 0 and rate > 0:
            returns.setdefault(date[:7], []).append(math.log(rate / previous[1]))
        month = date[:7]
        first, _ = month_levels.get(month, (rate, rate))
        month_levels[month] = (first, rate)
        previous = (date, rate)
    rows: list[Row] = []
    for month in sorted(returns):
        daily = returns[month]
        if len(daily) < 5:
            continue
        annual = statistics.pstdev(daily) * math.sqrt(TRADING_DAYS)
        if annual < CALM_MAX:
            regime = "calm"
        elif annual < STRESS_MAX:
            regime = "stress"
        else:
            regime = "crisis"
        date = f"{month}-01"
        rows.append(Row(date, annual, "annualized_volatility", "RU", "usd_rub"))
        rows.append(Row(date, regime, "regime_label", "RU", "usd_rub"))
        first, last = month_levels[month]
        rows.append(Row(date, math.log(last / first), "log_return_month", "RU",
                        "usd_rub"))
    return rows


def build(raw_dir: Path, out_dir: Path | None = None) -> None:
    """Собрать все ряды ЦБ.

    Args:
        raw_dir: каталог оригиналов.
        out_dir: каталог назначения.
    """
    usd: list[tuple[str, float]] = []
    for code, name in FX_FILES.items():
        path = raw_dir / "cbr" / name
        if not path.exists():
            logger.warning("нет файла %s", path)
            continue
        series = read_fx(path)
        if code == "USD":
            usd = series
        write_series(
            f"cbr_fx_{code.lower()}_rub_daily.csv",
            [Row(date, rate, "rub_per_unit", "RU", code) for date, rate in series],
            out_dir,
        )
    if usd:
        write_series("cbr_fx_usd_rub_volatility_month.csv",
                     monthly_volatility(usd), out_dir)
    key = read_soap_pairs(raw_dir / "cbr" / "cbr_key_rate_daily_2013_2026.xml",
                          "DT", "Rate")
    write_series("cbr_key_rate_daily.csv",
                 [Row(d, v, "percent_annual", "RU", "key_rate") for d, v in key],
                 out_dir)
    ruonia = read_soap_pairs(raw_dir / "cbr" / "cbr_ruonia_daily_2010_2026.xml",
                             "D0", "ruo")
    write_series("cbr_ruonia_daily.csv",
                 [Row(d, v, "percent_annual", "RU", "ruonia") for d, v in ruonia],
                 out_dir)


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
