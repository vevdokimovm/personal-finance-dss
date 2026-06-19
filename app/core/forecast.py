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


def ses_forecast(history: List[float], alpha: float = SES_ALPHA, horizon: int = 1) -> List[float]:
    """Простое экспоненциальное сглаживание (Brown 1956; Hyndman et al. 2002)."""
    if not history:
        return [0.0] * horizon
    if len(history) == 1:
        return [history[0]] * horizon

    s = history[0]
    for x in history[1:]:
        s = alpha * x + (1 - alpha) * s
    return [s] * horizon


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
