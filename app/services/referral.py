"""Реферальные награды / геймификация (P3.4, MVP-каркас).

Чистая детерминированная логика вех-достижений поверх счётчика приглашений —
без отдельных таблиц. Вынесено в сервис, чтобы здесь же наращивать будущую
механику наград (например, привязку порогов к премиум-бонусам при монетизации).

Поле reward в каждой вехе зарезервировано под реальную награду и пока None:
сознательно не выдумываем механику начисления до того, как она понадобится (YAGNI).
"""
from __future__ import annotations

from typing import Optional, TypedDict

# Пороги по числу приглашённых пользователей. Упорядочены по возрастанию.
REFERRAL_THRESHOLDS: tuple[int, ...] = (1, 3, 5, 10, 25)

# Человекочитаемые названия вех (индекс соответствует REFERRAL_THRESHOLDS).
_TITLES: dict[int, str] = {
    1: "Первое приглашение",
    3: "Тёплая компания",
    5: "Свой круг",
    10: "Большая семья",
    25: "Амбассадор",
}


class Milestone(TypedDict):
    threshold: int
    title: str
    reward: Optional[str]
    reached: bool


class NextMilestone(TypedDict):
    threshold: int
    title: str
    remaining: int


def referral_milestones(invited_count: int) -> list[Milestone]:
    """Все вехи с отметкой достигнутости при текущем числе приглашений."""
    return [
        Milestone(
            threshold=t,
            title=_TITLES.get(t, f"{t} приглашений"),
            reward=None,  # зарезервировано под реальные награды (монетизация)
            reached=invited_count >= t,
        )
        for t in REFERRAL_THRESHOLDS
    ]


def next_milestone(invited_count: int) -> Optional[NextMilestone]:
    """Ближайшая недостигнутая веха и сколько приглашений до неё. None — все достигнуты."""
    for t in REFERRAL_THRESHOLDS:
        if invited_count < t:
            return NextMilestone(
                threshold=t,
                title=_TITLES.get(t, f"{t} приглашений"),
                remaining=t - invited_count,
            )
    return None
