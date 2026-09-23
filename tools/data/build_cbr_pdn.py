"""Долговая нагрузка (ПДН) и качество выдач из «Обзора финансовой
стабильности» Банка России → `data/`.

Оригинал: `~/raw-originals/finpilot-data/cbr_finstab/4q_2025_1q_2026.pdf`
(№ 1 (28), IV квартал 2025 – I квартал 2026).

🔴 Числа берутся из ТЕКСТА обзора, а не из графиков: подписи диаграмм в
текстовом слое идут вперемешку с осями и надёжно не разбираются. Каждое
значение привязано к дословной фразе; если фраза в новом выпуске изменится,
скрипт скажет об этом вслух, а не подставит старое число.

Запуск: `python -m tools.data.build_cbr_pdn`
"""
from __future__ import annotations

import argparse
import logging
import re
import subprocess
import tempfile
from pathlib import Path

from tools.data.common import Row, raw_root, write_series

logger = logging.getLogger(__name__)

SOURCE = "cbr_finstab/4q_2025_1q_2026.pdf"

# (дата, разрез, единица, шаблон, номер группы со значением)
PATTERNS: list[tuple[str, str, str, str, int]] = [
    ("2026-03-31", "share_of_new_loans_pti_over_50|cash_loans", "percent",
     r"В I квартале 2026 г\. доля выдач кредитов с ПДН выше 50% составила (\d+)%"
     r"\s+по кредитам наличными", 1),
    ("2026-03-31", "share_of_new_loans_pti_over_50|credit_cards", "percent",
     r"по кредитам наличными\s+и (\d+)% по кредитным картам", 1),
    ("2022-12-31", "share_of_new_loans_pti_over_50|unsecured_total", "percent",
     r"с (\d+)% по итогам\s+IV квартала 2022 г\.", 1),
    ("2025-12-31", "share_of_new_loans_pti_over_50|unsecured_total", "percent",
     r"до (\d+)% по итогам IV квартала 2025 года", 1),
    ("2026-04-01", "share_of_portfolio_pti_over_50|unsecured_total", "percent",
     r"на 01\.04\.2026 на кредиты с ПДН выше 50% приходилось (\d+)% задолженности",
     1),
    ("2026-01-31", "npl30_at_3mob|cash_loans", "percent",
     r"в январе 2026 г\. , составила (\d+,\d)% по кредитам наличными", 1),
    ("2026-01-31", "npl30_at_3mob|credit_cards", "percent",
     r"по кредитам наличными и (\d+,\d)% по кредитным картам", 1),
    ("2026-01-31", "npl30_at_3mob|cash_loans_pti_over_80", "percent",
     r"более 30 дней на 3 MOB составила (\d+,\d)%", 1),
]


def extract_text(pdf: Path) -> str:
    """Вытащить текстовый слой PDF в одну строку.

    Args:
        pdf: путь к файлу обзора.

    Returns:
        Текст обзора со сжатыми пробелами.

    Raises:
        RuntimeError: если в системе нет `pdftotext`.
    """
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "review.txt"
        try:
            subprocess.run(["pdftotext", "-layout", str(pdf), str(target)],
                           check=True, capture_output=True)
        except FileNotFoundError as error:
            raise RuntimeError("нужен pdftotext (poppler)") from error
        raw = target.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"[ \t]+", " ", raw)


def build(source: Path, out_dir: Path | None = None) -> None:
    """Собрать ряд показателей долговой нагрузки.

    Args:
        source: путь к PDF обзора.
        out_dir: каталог назначения.
    """
    text = extract_text(source)
    flat = re.sub(r"\n", " ", text)
    rows: list[Row] = []
    for date, breakdown, unit, pattern, group in PATTERNS:
        match = re.search(pattern, flat)
        if not match:
            logger.warning("фраза не найдена, показатель пропущен: %s", breakdown)
            continue
        value = float(match.group(group).replace(",", "."))
        rows.append(Row(date, value, unit, "RU", breakdown))
    rows.sort(key=lambda item: (item.date, item.breakdown))
    write_series("cbr_pdn_distribution.csv", rows, out_dir)


def main() -> None:
    """Точка входа командной строки."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=raw_root() / SOURCE)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()
    build(args.source, args.out_dir)


if __name__ == "__main__":
    main()
