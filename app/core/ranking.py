"""
Ранжирование альтернатив через интегральную функцию полезности (этап 6 ВКР).

Метод — Simple Additive Weighting (Fishburn, 1967):
    U(ai) = w1·R̂i + w2·L̂i + w3·(1 − D̂i) + w4·Ŝi,   Σwk = 1
    a* = argmax_{ai ∈ A'} U(ai)

Веса w1..w4 задаются профилем риска (5 профилей). Веса R, L, D, Si
для каждой альтернативы нормированы min-max к [0, 1].
"""
from __future__ import annotations

from typing import Any


# Профили риска R ∈ {1..5} → веса целевой функции (форм. 22 ВКР)
RISK_PROFILES: dict[int, dict[str, Any]] = {
    1: {"w_rt": 0.15, "w_lt": 0.40, "w_dt": 0.35, "w_goals": 0.10, "label": "Консервативный"},
    2: {"w_rt": 0.20, "w_lt": 0.35, "w_dt": 0.30, "w_goals": 0.15, "label": "Умеренно-консервативный"},
    3: {"w_rt": 0.25, "w_lt": 0.30, "w_dt": 0.25, "w_goals": 0.20, "label": "Сбалансированный"},
    4: {"w_rt": 0.30, "w_lt": 0.20, "w_dt": 0.20, "w_goals": 0.30, "label": "Умеренно-агрессивный"},
    5: {"w_rt": 0.30, "w_lt": 0.15, "w_dt": 0.15, "w_goals": 0.40, "label": "Агрессивный"},
}


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
) -> list[dict[str, Any]]:
    """
    Ранжирование через U(a). Лучшая альтернатива получает is_recommended=True.
    """
    if not alternatives:
        return []

    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])
    w_rt, w_lt, w_dt, w_goals = profile["w_rt"], profile["w_lt"], profile["w_dt"], profile["w_goals"]

    rt_values = [a["Rt_new"] for a in alternatives]
    lt_values = [a["Lt_new"] for a in alternatives]
    dt_values = [a["Dt_new"] for a in alternatives]
    si_values = [a.get("Si", 0) for a in alternatives]

    rt_min, rt_max = min(rt_values), max(rt_values)
    lt_min, lt_max = min(lt_values), max(lt_values)
    dt_min, dt_max = min(dt_values), max(dt_values)
    si_min, si_max = min(si_values), max(si_values)

    for alt in alternatives:
        rt_norm = normalize_value(alt["Rt_new"], rt_min, rt_max, minimize=False)
        lt_norm = normalize_value(alt["Lt_new"], lt_min, lt_max, minimize=False)
        dt_norm = normalize_value(alt["Dt_new"], dt_min, dt_max, minimize=True)
        si_norm = normalize_value(alt.get("Si", 0), si_min, si_max, minimize=False)

        utility = w_rt * rt_norm + w_lt * lt_norm + w_dt * dt_norm + w_goals * si_norm
        alt["utility"] = round(utility, 4)
        alt["scores"] = {
            "Rt_norm": round(rt_norm, 3),
            "Lt_norm": round(lt_norm, 3),
            "Dt_norm": round(dt_norm, 3),
            "Si_norm": round(si_norm, 3),
        }

    alternatives.sort(key=lambda a: a["utility"], reverse=True)
    if alternatives:
        alternatives[0]["is_recommended"] = True

    return alternatives
