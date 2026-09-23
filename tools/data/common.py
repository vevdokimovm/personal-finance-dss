"""Общие примитивы сборки каталога данных.

Каждый ряд в `data/` — CSV с фиксированными колонками
`date, value, unit, region, breakdown`. Модуль держит запись в этом
формате, разбор русских чисел из выгрузок Росстата и подгонку
логнормального распределения по интервальному ряду.
"""
from __future__ import annotations

import csv
import hashlib
import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

logger = logging.getLogger(__name__)

COLUMNS = ("date", "value", "unit", "region", "breakdown")

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"


def raw_root() -> Path:
    """Каталог оригиналов вне репозитория.

    Returns:
        Путь из переменной окружения `FINPILOT_RAW_DIR`, иначе
        `~/raw-originals/finpilot-data`.
    """
    env = os.environ.get("FINPILOT_RAW_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / "raw-originals" / "finpilot-data"


@dataclass(frozen=True)
class Row:
    """Одна точка ряда."""

    date: str
    value: float | str
    unit: str
    region: str = ""
    breakdown: str = ""


def write_series(name: str, rows: Iterable[Row], out_dir: Path | None = None) -> Path:
    """Записать ряд в CSV каталога данных.

    Args:
        name: имя файла вида `<источник>_<показатель>_<шаг>.csv`.
        rows: точки ряда.
        out_dir: каталог назначения (по умолчанию `data/` репозитория).

    Returns:
        Путь записанного файла.
    """
    target_dir = out_dir or DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / name
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            value = row.value
            if isinstance(value, float):
                value = f"{value:.6g}"
            writer.writerow([row.date, value, row.unit, row.region, row.breakdown])
            count += 1
    logger.info("%s: %d строк, %d Б", path.name, count, path.stat().st_size)
    return path


def sha256_of(path: Path) -> str:
    """Посчитать sha256 файла.

    Args:
        path: путь к файлу.

    Returns:
        Шестнадцатеричный дайджест.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_float(value: object) -> float | None:
    """Привести ячейку выгрузки к числу.

    Понимает запятую как десятичный разделитель, неразрывные пробелы
    как разделитель разрядов и прочерки Росстата как отсутствие данных.

    Args:
        value: ячейка исходного файла.

    Returns:
        Число или None, если ячейка пустая либо не числовая.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    for junk in ("\xa0", " ", " ", " "):
        text = text.replace(junk, "")
    text = text.replace(",", ".")
    if text in {"", "-", "–", "—", "...", "…", "нд", "н.д."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def norm_ppf(p: float) -> float:
    """Квантиль стандартного нормального распределения.

    Алгоритм Acklam (относительная ошибка < 1.15e-9); собственная
    реализация, чтобы не тянуть scipy в зависимости проекта.

    Args:
        p: вероятность в интервале (0, 1).

    Returns:
        Значение обратной функции распределения.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("p должно лежать строго между 0 и 1")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        num = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
        den = ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        return num / den
    if p > p_high:
        q = math.sqrt(-2 * math.log(1 - p))
        num = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
        den = ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        return -num / den
    q = p - 0.5
    r = q * q
    num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
    den = (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    return num / den


def norm_cdf(x: float) -> float:
    """Функция стандартного нормального распределения.

    Args:
        x: аргумент.

    Returns:
        Вероятность P(X <= x).
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@dataclass(frozen=True)
class LogNormalFit:
    """Результат подгонки логнормали по интервальному ряду."""

    mu: float
    sigma: float
    r_squared: float
    points: int

    @property
    def median(self) -> float:
        """Медиана распределения."""
        return math.exp(self.mu)

    @property
    def mean(self) -> float:
        """Среднее распределения."""
        return math.exp(self.mu + self.sigma ** 2 / 2)

    def quantile(self, p: float) -> float:
        """Квантиль уровня p.

        Args:
            p: уровень квантиля в (0, 1).

        Returns:
            Значение показателя на этом квантиле.
        """
        return math.exp(self.mu + self.sigma * norm_ppf(p))


def fit_lognormal(bounds: Sequence[float], shares: Sequence[float]) -> LogNormalFit:
    """Подогнать логнормаль по долям населения в интервалах.

    Метод: накопленная доля до каждой верхней границы переводится в
    `Φ⁻¹`, дальше обычная линейная регрессия `ln(граница)` на `Φ⁻¹`.
    Наклон даёт σ, свободный член — μ.

    Args:
        bounds: верхние границы интервалов (последний интервал открыт
            сверху и границы не имеет).
        shares: доли в процентах, по одной на интервал; длина на единицу
            больше длины `bounds`.

    Returns:
        Подгонка с μ, σ и коэффициентом детерминации.

    Raises:
        ValueError: если точек для регрессии меньше двух.
    """
    total = sum(shares)
    cumulative = 0.0
    xs: list[float] = []
    ys: list[float] = []
    for bound, share in zip(bounds, shares):
        cumulative += share / total
        if 0.0 < cumulative < 1.0 and bound > 0:
            xs.append(norm_ppf(cumulative))
            ys.append(math.log(bound))
    if len(xs) < 2:
        raise ValueError("недостаточно точек для подгонки")
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    sigma = cov / var_x
    mu = mean_y - sigma * mean_x
    ss_res = sum((y - (mu + sigma * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return LogNormalFit(mu=mu, sigma=sigma, r_squared=r_squared, points=n)
