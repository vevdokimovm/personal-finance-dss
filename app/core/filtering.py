"""
Фильтрация альтернатив по ограничениям модели (этап 5 ВКР, форм. 18):
    Ri ≥ B_min,   Li ≥ Lcrit,   Di ≤ Dmax
"""
from __future__ import annotations

from typing import Any

# Пороговые значения по умолчанию
DT_MAX = 0.40      # ПДН: строже регуляторного порога ЦБ РФ (Указ. № 4892-У, 50%)
LT_CRIT = 0.0      # Lt' не должна быть отрицательной (параметр пользователя Lmin)
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
        if alt.get("Lt_new", 0) < lt_crit:
            violations.append("почти не оставил бы свободных денег — ниже безопасного запаса прочности")
        if alt.get("Dt_new", 0) > dt_max:
            violations.append(f"долговая нагрузка осталась бы выше безопасного порога {dt_max*100:.0f}%")

        alt["violations"] = violations
        alt["is_admissible"] = len(violations) == 0

        if alt["is_admissible"]:
            accepted.append(alt)
        else:
            rejected.append(alt)

    return accepted, rejected
