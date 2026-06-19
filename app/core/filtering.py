"""
Фильтрация альтернатив по ограничениям допустимости (этап 5, refined model v3.0).

Жёсткие инварианты безопасности (gate):
    Rt' ≥ B_min = 0      — план не уводит свободный поток в минус
    Dt' ≤ Dmax = 0.40    — долговая нагрузка в пределах ПДН Банка России

Ликвидность — мягкий критерий:
    Lt' ≥ lt_crit, где lt_crit = минимум месяцев автономии (по умолчанию 0 = выключен).
    Ликвидность влияет на выбор через свёртку полезности, а не через отсев. Так
    пользователь с тонким бюджетом всё равно получает осмысленный совет, а не отказ.
"""
from __future__ import annotations

from typing import Any

# Пороговые значения по умолчанию
DT_MAX = 0.40      # ПДН: строже регуляторного подхода Банка России (Указ. № 4892-У)
LT_CRIT = 0.0      # минимум месяцев автономии; 0 = не отсевать по ликвидности
B_MIN = 0.0        # Rt' не должен становиться отрицательным после распределения


def filter_alternatives(
    alternatives: list[dict[str, Any]],
    b_min: float = B_MIN,
    lt_crit: float = LT_CRIT,
    dt_max: float = DT_MAX,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Returns: (допустимые, отклонённые с указанием нарушенных ограничений).
    """
    accepted, rejected = [], []

    for alt in alternatives:
        violations = []
        if alt.get("Rt_new", 0) < b_min:
            violations.append("увёл бы бюджет в минус — свободных денег не осталось бы")
        if lt_crit > 0 and alt.get("Lt_new", 0) < lt_crit:
            violations.append(
                f"оставил бы подушку меньше требуемых {lt_crit:g} мес. автономии"
            )
        if alt.get("Dt_new", 0) > dt_max:
            violations.append(f"долговая нагрузка осталась бы выше безопасного порога {dt_max*100:.0f}%")

        alt["violations"] = violations
        alt["is_admissible"] = len(violations) == 0

        if alt["is_admissible"]:
            accepted.append(alt)
        else:
            rejected.append(alt)

    return accepted, rejected
