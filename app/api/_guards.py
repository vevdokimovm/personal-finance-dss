"""Входные guard-проверки для расчётных эндпоинтов (BUG-04)."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Union

from fastapi import HTTPException, status

from app.core.metrics import calculate_income_total, sum_obligation_payments

Item = Union[dict[str, Any], Any]


def ensure_calculable(transactions: Iterable[Item], obligations: Iterable[Item]) -> None:
    """
    BUG-04: при нулевом доходе и наличии обязательств расчёт показателей
    (ПДН, ликвидность) бессмысленен и опасен делением на ноль — возвращаем
    понятный 422-диагноз вместо тихого нуля или 500.

    Пустой профиль (нет дохода и нет обязательств) проходит как валидный —
    эндпоинт вернёт нулевые показатели, а UI покажет онбординг.
    """
    income = calculate_income_total(transactions)
    payments = sum_obligation_payments(obligations)
    if income <= 0 and payments > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Нет данных о доходах при наличии обязательств — "
                "рассчитать финансовые показатели невозможно. "
                "Добавьте хотя бы один источник дохода."
            ),
        )
