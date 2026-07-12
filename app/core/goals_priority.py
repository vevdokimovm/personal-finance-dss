"""
Приоритизация целей и взвешенная обеспеченность Si (форм. 15-16 ВКР).
Также — предобработка ликвидной позиции Bliq (этап 4.0 ВКР).

Два измерения приоритета:
  - стратегическая ценность по категории ks ∈ {income_growth, safety, material, emotional}
  - срочность по близости дедлайна Ts

Формула Si учитывает оба измерения, что даёт алгоритму возможность
рекомендовать вложения в цели, имеющие наибольшую отдачу для пользователя.
"""
from __future__ import annotations

from datetime import datetime
from app.utils.time import utcnow
from typing import Any

CATEGORY_WEIGHTS: dict[str, float] = {
    "income_growth": 3.0,
    "safety":        2.0,
    "material":      1.0,
    "emotional":     0.5,
}

# Пороги для предобработки ликвидной позиции (форм. этап 4.0)
BLIQ_USAGE_THRESHOLD = 0.5      # доля Bliq, доступная для разового закрытия близких целей
NEAR_GOAL_HORIZON_MONTHS = 3    # горизонт «близкой» цели

# Бессрочная цель (deadline = None): срока нет, ускорять нечего — срочность
# нейтральная. Численно равна цели с горизонтом 12 мес (12/12 = 1), но задана
# явно, а не как побочный эффект фолбэка (ROADMAP §6.3).
URGENCY_OPEN_ENDED = 1.0
FALLBACK_MONTHS = 12.0          # защитный фолбэк для нераспознанного значения дедлайна


def months_left_or_none(deadline: Any, today: datetime) -> float | None:
    """Месяцев до дедлайна; None — цель бессрочная (deadline не задан)."""
    if deadline is None:
        return None
    return _months_left(deadline, today)


def urgency_of(deadline: Any, today: datetime) -> float:
    """Срочность u_s: 12 / месяцев до срока, минимум 1. Бессрочная цель → 1.0."""
    months = months_left_or_none(deadline, today)
    if months is None:
        return URGENCY_OPEN_ENDED
    return max(1.0, 12.0 / months)


def _months_left(deadline: Any, today: datetime) -> float:
    """Сколько месяцев осталось до дедлайна (минимум 1, чтобы не делить на ноль).

    Бессрочная цель (None) здесь трактуется как нейтральный горизонт 12 мес —
    для мест, которым нужно число. Где важно различать «без срока» и «через год»,
    зовите `months_left_or_none`.
    """
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return FALLBACK_MONTHS
    if not isinstance(deadline, datetime):
        return FALLBACK_MONTHS
    delta_days = max(1, (deadline - today).days)
    return max(1.0, delta_days / 30.0)


def calculate_goals_si(
    x_goals: float,
    goals: list[dict[str, Any]],
    today: datetime | None = None,
) -> tuple[float, dict[Any, float]]:
    """
    Взвешенная обеспеченность целей (форм. 15 ВКР):
        Si = Σ(x_goa_s · w_s · u_s) / Σ((Ss − ws) · w_s · u_s)

    Распределение x_goals по целям (форм. 16):
        x_goa_s = x_goals · (w_s · u_s) / Σ(w_s' · u_s')

    Returns:
        Si: взвешенная обеспеченность в [0, 1]
        allocation: {goal_id: сколько направлено в эту цель}
    """
    today = today or utcnow()

    if not goals or x_goals <= 0:
        return 0.0, {}

    enriched = []
    for g in goals:
        remaining = max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        if remaining <= 0:
            continue
        urgency = urgency_of(g.get("deadline"), today)
        weight = CATEGORY_WEIGHTS.get(str(g.get("category", "material")), 1.0)
        enriched.append({
            **g,
            "_remaining": remaining,
            "_urgency": urgency,
            "_weight": weight,
            "_priority": weight * urgency,
        })

    total_priority = sum(g["_priority"] for g in enriched)
    if total_priority <= 0:
        return 0.0, {}

    allocation: dict[Any, float] = {}
    weighted_x = 0.0
    weighted_total = 0.0

    for g in enriched:
        share = g["_priority"] / total_priority
        x_goa_s = min(x_goals * share, g["_remaining"])  # не больше чем нужно
        allocation[g["id"]] = round(x_goa_s, 2)
        weighted_x += x_goa_s * g["_priority"]
        weighted_total += g["_remaining"] * g["_priority"]

    si = weighted_x / weighted_total if weighted_total > 0 else 0.0
    return min(si, 1.0), allocation


def preallocate_from_bliq(
    bliq: float,
    goals: list[dict[str, Any]],
    today: datetime | None = None,
) -> tuple[float, list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Этап 4.0 ВКР — разовое закрытие близких целей (дедлайн ≤ 3 мес) из Bliq.

    Условие срабатывания:
        Σ S_близкие ≤ Bliq · BLIQ_USAGE_THRESHOLD

    Returns:
        bliq_remaining: оставшаяся ликвидная позиция
        closed_goals: цели, закрытые единовременно (со списанием со счёта Bliq)
        active_goals: цели, остающиеся в оптимизации
    """
    today = today or utcnow()

    if bliq <= 0 or not goals:
        return bliq, [], list(goals)

    near, far = [], []
    for g in goals:
        remaining = max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        if remaining <= 0:
            far.append(g)
            continue
        months = months_left_or_none(g.get("deadline"), today)
        if months is not None and months <= NEAR_GOAL_HORIZON_MONTHS:
            near.append({**g, "_remaining": remaining})
        else:
            far.append(g)

    total_near = sum(g["_remaining"] for g in near)
    max_use = bliq * BLIQ_USAGE_THRESHOLD

    if total_near == 0 or total_near > max_use:
        return bliq, [], list(goals)

    return bliq - total_near, near, far


def goals_allocation_breakdown(
    x_goals: float,
    goals: list[dict[str, Any]],
    today: datetime | None = None,
) -> list[dict[str, Any]]:
    """
    Объяснимое распределение x_goals по целям (форм. 16 ВКР) — для UI.

    Возвращает по каждой цели: имя, категорию, вес категории w_s,
    срочность u_s, приоритет w_s·u_s, долю и сумму.
    """
    today = today or utcnow()
    if not goals or x_goals <= 0:
        return []

    enriched = []
    for g in goals:
        remaining = max(0.0, float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)))
        if remaining <= 0:
            continue
        months = months_left_or_none(g.get("deadline"), today)
        urgency = urgency_of(g.get("deadline"), today)
        weight = CATEGORY_WEIGHTS.get(str(g.get("category", "material")), 1.0)
        enriched.append({
            "id": g.get("id"),
            "name": g.get("name", ""),
            "category": str(g.get("category", "material")),
            "weight": round(weight, 2),
            "urgency": round(urgency, 2),
            "months_left": round(months, 1) if months is not None else None,
            "priority": weight * urgency,
            "remaining": round(remaining, 2),
        })

    total_priority = sum(g["priority"] for g in enriched)
    if total_priority <= 0:
        return []

    for g in enriched:
        share = g["priority"] / total_priority
        g["share"] = round(share, 4)
        g["amount"] = round(min(x_goals * share, g["remaining"]), 2)
        g["priority"] = round(g["priority"], 2)
    return enriched
