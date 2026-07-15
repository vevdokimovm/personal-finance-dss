"""
Прогнозирование показателей финансового состояния (этап 3 ВКР, форм. 14, 35).

Подход:
  1. SES α = 0.3 (Brown 1956; совр. state-space трактовка — Hyndman et al. 2002)
  2. Накопление баланса B(t+h) по формуле 35 ВКР
  3. Monte-Carlo N=1000 (Metropolis & Ulam 1949) с растущей σ(h) — интервал 80% [p10..p90]
"""
from __future__ import annotations

import math
import random
from typing import List, Optional

SES_ALPHA = 0.3
MC_SIMULATIONS = 1000
MC_SIGMA_BASE = 0.05
MC_SIGMA_GROWTH = 0.5
# Доверительный интервал прогноза: 80% (p10..p90). Для персонального планирования на
# 1–3 месяца 80% даёт читаемый коридор; 95% при растущей σ был бы слишком широким,
# чтобы служить ориентиром для пользователя.
MC_CI_LOWER = 0.10
MC_CI_UPPER = 0.90


HOLT_ALPHA = 0.4
HOLT_BETA = 0.3
HOLT_PHI = 0.9  # демпфирование тренда (Gardner & McKenzie 1985) — гасит разгон экстраполяции


def ses_forecast(history: List[float], alpha: float = SES_ALPHA, horizon: int = 1) -> List[float]:
    """Простое экспоненциальное сглаживание (Brown 1956; Hyndman et al. 2002).
    Точечный прогноз ПЛОСКИЙ (нет компоненты тренда) — используется как фолбэк для
    короткой/безтрендовой истории."""
    if not history:
        return [0.0] * horizon
    if len(history) == 1:
        return [history[0]] * horizon

    s = history[0]
    for x in history[1:]:
        s = alpha * x + (1 - alpha) * s
    return [s] * horizon


def holt_forecast(
    history: List[float],
    alpha: float = HOLT_ALPHA,
    beta: float = HOLT_BETA,
    phi: float = HOLT_PHI,
    horizon: int = 1,
    non_negative: bool = True,
) -> List[float]:
    """Демпфированное двойное экспоненциальное сглаживание (Holt 1957; Gardner &
    McKenzie 1985): уровень + затухающий тренд. Прогноз ŷ(t+h) = level + (φ+…+φ^h)·trend.

    В отличие от SES, прогноз НАКЛОНЁН по данным истории: растущая история даёт
    растущий прогноз, падающая — падающий. Демпфирование φ<1 не даёт тренду
    «улетать» на длинном горизонте. non_negative клампит денежные величины ≥ 0.
    """
    if not history:
        return [0.0] * horizon
    if len(history) < 2:
        v = max(history[0], 0.0) if non_negative else history[0]
        return [v] * horizon

    level = history[0]
    trend = history[1] - history[0]
    for x in history[1:]:
        prev_level = level
        level = alpha * x + (1 - alpha) * (level + phi * trend)
        trend = beta * (level - prev_level) + (1 - beta) * phi * trend

    out: List[float] = []
    damp = 0.0
    for h in range(1, horizon + 1):
        damp += phi ** h
        y = level + damp * trend
        out.append(max(y, 0.0) if non_negative else y)
    return out


def choose_point_forecast(history: List[float], horizon: int = 1) -> List[float]:
    """Выбор метода точечного прогноза: демпфированный Holt при ≥3 наблюдениях
    (ловит тренд реальной истории), иначе SES (плоский фолбэк)."""
    if history is not None and len(history) >= 3:
        return holt_forecast(history, horizon=horizon)
    return ses_forecast(history, horizon=horizon)


def monthly_rate(annual_rate: float) -> float:
    """Эффективная месячная ставка из годовой: (1+r)^(1/12) − 1.
    Используется для капитализации накоплений в прогнозе баланса (форм. 35 v3.3.0)."""
    if annual_rate <= -1.0:
        return 0.0
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0


def monte_carlo_intervals(
    point_forecast: List[float],
    horizon: int,
    sigma_base: float = MC_SIGMA_BASE,
    sigma_growth: float = MC_SIGMA_GROWTH,
    n_sim: int = MC_SIMULATIONS,
    seed: Optional[int] = 42,
) -> List[dict]:
    """Monte-Carlo вокруг точечного прогноза с растущей σ(h)=σ₀√(1+0.5·h)."""
    if seed is not None:
        random.seed(seed)
    intervals = []
    for h, point in enumerate(point_forecast, start=1):
        sigma_h = sigma_base * math.sqrt(1 + sigma_growth * h)
        sigma_abs = abs(point) * sigma_h
        samples = [point + random.gauss(0.0, sigma_abs) for _ in range(n_sim)]
        samples.sort()
        p10 = samples[int(MC_CI_LOWER * n_sim)]
        p50 = samples[int(0.50 * n_sim)]
        p90 = samples[min(int(MC_CI_UPPER * n_sim), n_sim - 1)]
        intervals.append({"p10": round(p10, 2), "p50": round(p50, 2), "p90": round(p90, 2)})
    return intervals


def build_history_from_current(
    value: float, periods: int = 6, noise: float = 0.05, seed: int = 1
) -> List[float]:
    """Синтетическая история из 6 точек для SES, когда реальной истории нет."""
    if value <= 0:
        return [value] * periods
    rng = random.Random(seed)
    history = []
    base = value * 0.96
    for i in range(periods):
        x = base * (1 + (i / periods) * 0.04 + rng.gauss(0.0, noise))
        history.append(round(x, 2))
    return history


def detect_trend(current: float, future_series: List[float]) -> str:
    if not future_series:
        return "stable"
    last = future_series[-1]
    delta = last - current
    threshold = max(abs(current), 1.0) * 0.05
    if abs(delta) < threshold:
        return "stable"
    return "improving" if delta > 0 else "deteriorating"
