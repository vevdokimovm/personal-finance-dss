"""
Ранжирование альтернатив через интегральную функцию полезности (этап 6).

Метод — Simple Additive Weighting (Fishburn, 1967):
    U(ai) = w1·R̂i + w2·L̂i + w3·(1 − D̂i) + w4·Ŝi,   Σwk = 1
    a* = argmax_{ai ∈ A'} U(ai)

Веса w1..w4 задаются профилем риска (5 профилей). Веса R, L, D, Si
для каждой альтернативы нормированы min-max к [0, 1].

Модель v3.1.0 — две правки по независимой экспертизе (12 000 портретов
против консенсуса 4 экспертных движков):

  G1. Насыщающая полезность резерва. Критерий ликвидности считается по
      Lt, ограниченному сверху целевым Lt*(risk) из коридора 3–6 месяцев:
      выше цели прирост подушки полезности не даёт (альтернативная
      стоимость положительна — деньги должны работать в целях). Без этого
      модель копила резерв бесконечно (76% всех расхождений с консенсусом).

  G6. Floor резерва: стартовый месяц ликвидности (1 мес расходов) не
      отменяется риск-профилем. Альтернативы упорядочиваются
      лексикографически: сначала заполнение floor, затем SAW. Без floor
      любой сбой дохода у агрессивного профиля конвертируется в новый долг.
"""
from __future__ import annotations

from typing import Any

# Профили риска R ∈ {1..5} → веса целевой функции + целевая подушка Lt* (мес)
# Коридор Lt* = 3–6 месяцев — консенсус независимой экспертизы и норматив
# Greninger et al. (1996): 2.5–6 месяцев расходов.
RISK_PROFILES: dict[int, dict[str, Any]] = {
    1: {"w_rt": 0.20, "w_lt": 0.45, "w_dt": 0.25, "w_goals": 0.10,
        "lt_target": 6.0, "label": "Консервативный"},
    2: {"w_rt": 0.20, "w_lt": 0.35, "w_dt": 0.25, "w_goals": 0.20,
        "lt_target": 5.0, "label": "Умеренно-консервативный"},
    3: {"w_rt": 0.25, "w_lt": 0.30, "w_dt": 0.25, "w_goals": 0.20,
        "lt_target": 4.5, "label": "Сбалансированный"},
    4: {"w_rt": 0.30, "w_lt": 0.20, "w_dt": 0.20, "w_goals": 0.30,
        "lt_target": 3.5, "label": "Умеренно-агрессивный"},
    5: {"w_rt": 0.35, "w_lt": 0.10, "w_dt": 0.15, "w_goals": 0.40,
        "lt_target": 3.0, "label": "Агрессивный"},
}

# Floor резерва: минимальный стартовый запас ликвидности в месяцах расходов.
# Не зависит от профиля риска (риск-аппетит управляет целевым размером
# подушки и инвест-миксом, но не отменяет страховку от сбоя дохода).
# 2.0 — калибровка по второй сертификации (v3.4.0): свежая четвёрка экспертов
# на датасете v2 воспроизвела «подушка до ~2 мес важнее лавины/целей»
# out-of-sample (78.9% -> 88.0% согласия). Разбор — ADR-006 (update 2026-07-16).
RESERVE_FLOOR_MONTHS = 2.0

# Ослабление floor при токсичном долге (третья сертификация, v3.5.0).
# Гипотеза предзарегистрирована ДО раунда 4: ставка >= max(30%, r_bench+15 п.п.)
# съедает подушку быстрее, чем подушка страхует сбой дохода, поэтому стартовый
# запас сокращается до одного месяца, а высвобожденный поток идёт в лавину.
# Порог двойной: абсолютный отсекает МФО/карты при любом бенчмарке, спред не
# даёт объявить токсичным нормальный потребкредит при ключевой ставке 24%.
TOXIC_RATE_ABS = 0.30
TOXIC_RATE_SPREAD = 0.15
TOXIC_FLOOR_MONTHS = 1.0

_FLOOR_EPS = 1e-9


def is_toxic_debt(obligation: dict[str, Any], r_bench: float) -> bool:
    """Долг токсичен, если ставка >= max(30%, r_bench + 15 п.п.)."""
    if float(obligation.get("amount", 0) or 0) <= 0:
        return False
    threshold = max(TOXIC_RATE_ABS, float(r_bench) + TOXIC_RATE_SPREAD)
    return float(obligation.get("interest_rate", 0) or 0) >= threshold


def effective_floor_months(obligations: list[dict[str, Any]],
                           r_bench: float) -> float:
    """Floor резерва с учётом токсичного долга (хотя бы одного)."""
    if any(is_toxic_debt(o, r_bench) for o in obligations or ()):
        return TOXIC_FLOOR_MONTHS
    return RESERVE_FLOOR_MONTHS


def normalize_value(value: float, v_min: float, v_max: float, minimize: bool = False) -> float:
    """
    Min-max нормализация показателя к [0, 1].
    При minimize=True показатель инвертируется (для D — чем меньше, тем лучше).
    """
    if v_max == v_min:
        return 1.0
    if minimize:
        return (v_max - value) / (v_max - v_min)
    return (value - v_min) / (v_max - v_min)


def rank_alternatives(
    alternatives: list[dict[str, Any]],
    risk_tolerance: int = 3,
    floor_months: float | None = None,
) -> list[dict[str, Any]]:
    """
    Ранжирование через U(a). Лучшая альтернатива получает is_recommended=True.

    Порядок — лексикографический (floor_level, utility):
      1) floor_level = min(Lt', RESERVE_FLOOR_MONTHS) — заполнение стартового
         месяц ликвидности (G6);
      2) utility — SAW-свёртка с насыщением критерия ликвидности на Lt* (G1).
    Поле utility остаётся в [0, 1] (для отображения и объяснений).
    """
    if not alternatives:
        return []

    floor = RESERVE_FLOOR_MONTHS if floor_months is None else float(floor_months)
    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])
    w_rt, w_lt, w_dt, w_goals = (
        profile["w_rt"], profile["w_lt"], profile["w_dt"], profile["w_goals"]
    )
    lt_target = float(profile["lt_target"])

    rt_values = [a["Rt_new"] for a in alternatives]
    # G1: насыщение — выше целевой подушки прирост Lt полезности не даёт
    lt_capped = [min(float(a["Lt_new"]), lt_target) for a in alternatives]
    dt_values = [a["Dt_new"] for a in alternatives]
    si_values = [a.get("Si", 0) for a in alternatives]

    rt_min, rt_max = min(rt_values), max(rt_values)
    lt_min, lt_max = min(lt_capped), max(lt_capped)
    dt_min, dt_max = min(dt_values), max(dt_values)
    si_min, si_max = min(si_values), max(si_values)

    for alt, lt_eff in zip(alternatives, lt_capped):
        rt_norm = normalize_value(alt["Rt_new"], rt_min, rt_max, minimize=False)
        lt_norm = normalize_value(lt_eff, lt_min, lt_max, minimize=False)
        dt_norm = normalize_value(alt["Dt_new"], dt_min, dt_max, minimize=True)
        si_norm = normalize_value(alt.get("Si", 0), si_min, si_max, minimize=False)

        utility = w_rt * rt_norm + w_lt * lt_norm + w_dt * dt_norm + w_goals * si_norm
        alt["utility"] = round(utility, 4)
        # G6: уровень заполнения стартового месяца ликвидности
        alt["floor_level"] = round(min(float(alt["Lt_new"]), floor), 6)
        alt["scores"] = {
            "Rt_norm": round(rt_norm, 3),
            "Lt_norm": round(lt_norm, 3),
            "Dt_norm": round(dt_norm, 3),
            "Si_norm": round(si_norm, 3),
            "Lt_capped": round(lt_eff, 4),
        }

    alternatives.sort(
        key=lambda a: (a["floor_level"], a["utility"]), reverse=True
    )
    if alternatives:
        alternatives[0]["is_recommended"] = True

    return alternatives
