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


# Порог длины истории, при котором вообще имеет смысл говорить о тренде. Ниже него
# наклон неотличим от шума: при трёх точках Holt берёт тренд как разницу первых двух
# наблюдений, и одна случайная разница задаёт наклон на весь горизонт (ДК-37).
TREND_MIN_HISTORY = 9


def choose_point_forecast(history: List[float], horizon: int = 1) -> List[float]:
    """Точечный прогноз по канону §15: SES α = 0.3, БЕЗ компоненты тренда.

    Замер Г43 на 300 портретах шести типов рядов при истории 3/6/12 месяцев сравнил
    14 методов, включая эту функцию в прежней редакции (демпфированный Holt с зашитыми
    α, β, φ). Ошибка суммы за шесть месяцев в долях среднего дохода: 0.606 против 0.205
    у среднего при трёх точках, 0.319 против 0.180 при шести, 0.227 против 0.144 при
    двенадцати — последнее место из четырнадцати на всех длинах. Парный бутстрэп по 600
    портретам: +0.135 [+0.106, +0.165] к ошибке против SES α = 0.3, то есть 43 % всей
    ошибки метода; с поправкой Холма Holt значимо хуже 12 из 13 альтернатив.

    Тренд вернётся сюда только вместе с проверкой значимости наклона на истории от
    TREND_MIN_HISTORY точек — отдельной задачей. До тех пор `holt_forecast` остаётся
    в модуле как проверенная реализация, но по умолчанию не вызывается: на наших длинах
    истории она выдумывает наклон, которого в данных нет.
    """
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


# Квантиль распределения Стьюдента уровня 0.90 (для двустороннего 80 %-коридора)
# по числу степеней свободы. Таблица, а не scipy: зависимость ради одного числа
# не оправдана, а значения фиксированы и проверяемы.
_T90 = {1: 3.078, 2: 1.886, 3: 1.638, 4: 1.533, 5: 1.476, 6: 1.440, 7: 1.415,
        8: 1.397, 9: 1.383, 10: 1.372, 11: 1.363, 12: 1.356, 13: 1.350, 14: 1.345,
        15: 1.341, 16: 1.337, 17: 1.333, 18: 1.330, 19: 1.328, 20: 1.325,
        25: 1.316, 30: 1.310, 40: 1.303, 60: 1.296, 120: 1.289}
_T90_INF = 1.2816


def t_quantile_90(df: int) -> float:
    """Квантиль Стьюдента уровня 0.90 по степеням свободы (ближайшее сверху из таблицы)."""
    if df <= 0:
        return _T90[1]
    if df in _T90:
        return _T90[df]
    if df > 120:
        return _T90_INF
    return _T90[min(k for k in _T90 if k >= df)]


def flow_based_intervals(
    point_forecast: List[float],
    flow_sigma: float,
    history_len: int,
    extra_flow_terms: int = 0,
    ci_lower: float = MC_CI_LOWER,
    ci_upper: float = MC_CI_UPPER,
) -> List[dict]:
    r"""Коридор прогноза от РАЗБРОСА СОБСТВЕННОГО ПОТОКА человека (ДК-15).

    Прежняя реализация брала ширину от величины показателя (`|Rt| · 5 %`), из-за чего
    у человека с нулевым остатком коридор схлопывался в точку, а у человека с запасом
    был шире в двадцать раз — при одинаковой неопределённости дохода и трат. Замер:
    коридор, заявленный как 80 %, накрывал правду в 7–47 % случаев, при нулевом
    балансе — в 6,8 %.

    Здесь ширина растёт из того, из чего неопределённость и берётся:
      * `flow_sigma` — выборочное стандартное отклонение месячного чистого потока;
      * рост по числу вошедших месяцев — неопределённость СУММЫ независимых месяцев;
      * поправка √(1 + h/n) — на то, что среднее оценено по короткой истории;
      * квантиль Стьюдента вместо нормального — на ту же короткость.

    🔴 `extra_flow_terms` — сколько РАЗ поток текущего месяца входит в показатель
    сверх одного. Для ресурса канона это единица: формула $R_t = B_t + CF_t - P_t$
    учитывает поток месяца повторно, потому что он уже накоплен в $B_t$ (известный
    дефект ДК-22). Пока формула такая, честная ширина обязана это учитывать — иначе
    коридор будет узким именно у того числа, которое видит человек. Дисперсия суммы:
    $\sigma^2\,[(h-1) + (1+\text{extra})^2]$. Когда ДК-22 починят, параметр станет
    нулём, и выражение вернётся к привычному $\sigma\sqrt{h}$.

    Монте-Карло здесь не нужен: для симметричного шума вокруг точки квантиль считается
    формулой, а тысяча прогонов добавляет только собственный шум выборки.
    """
    n = max(int(history_len), 2)
    t = t_quantile_90(n - 1)
    extra = max(int(extra_flow_terms), 0)
    out: List[dict] = []
    for h, point in enumerate(point_forecast, start=1):
        units = (h - 1) + (1 + extra) ** 2
        half = t * flow_sigma * math.sqrt(units) * math.sqrt(1.0 + h / n)
        out.append({
            "p10": round(point - half, 2),
            "p50": round(point, 2),
            "p90": round(point + half, 2),
        })
    return out


def net_flow_sigma(
    income_history: List[float],
    expense_history: List[float],
    obligation_history: Optional[List[float]] = None,
) -> float:
    """Разброс месячного чистого потока по собственной истории человека.

    Берётся стандартное отклонение ряда (доход − расход − платежи по обязательствам)
    с поправкой Бесселя. Ряды разной длины выравниваются по самому короткому: смысл
    величины — «насколько скачет свободный поток», и брать для этого месяцы, у которых
    нет пары, нельзя.
    """
    n = min(len(income_history or []), len(expense_history or []))
    if obligation_history:
        n = min(n, len(obligation_history))
    if n < 2:
        return 0.0
    inc = list(income_history)[-n:]
    exp = list(expense_history)[-n:]
    obl = list(obligation_history)[-n:] if obligation_history else [0.0] * n
    flows = [inc[i] - exp[i] - obl[i] for i in range(n)]
    mean = sum(flows) / n
    var = sum((x - mean) ** 2 for x in flows) / (n - 1)
    return math.sqrt(max(var, 0.0))


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
