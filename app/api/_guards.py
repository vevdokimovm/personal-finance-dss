"""Входные guard-проверки для расчётных эндпоинтов (BUG-04)."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Optional, Union

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.metrics import calculate_income_total, sum_obligation_payments
from app.database.crud import can_write_household

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


def ensure_can_share(db: Session, household_id: Optional[int], user_id: Optional[str]) -> None:
    """Право писать в общий семейный котёл (v8.55.0).

    🔴 **Что закрывает.** `household_id` был заведён в схемах и колонках ПЯТИ сущностей,
    а проверка стояла в одной — целях. Остальные эндпоинты поле из тела запроса не читали
    вовсе: человек отправлял операцию с `household_id`, получал `201` и личную запись.
    Продукт принимал данные и молча их терял — не отказ, который можно заметить, а тихое
    расхождение между сказанным и записанным.

    **Почему общая функция, а не проверка на месте.** Начать передавать поле, не добавив
    проверку, значило бы открыть запись в чужой household всякому, кто угадает число, —
    хуже исходного дефекта, потому что данные не теряются, а появляются у посторонних.
    Четыре одинаковых проверки, скопированные по эндпоинтам, расходятся при первой
    же правке; одна — нет.

    Несуществующий household и чужой дают ОДИН ответ: `get_household_role` вернёт `None`
    в обоих случаях, и это правильно — по коду отказа посторонний не должен различать
    «такого нет» и «есть, но не ваш».

    Args:
        household_id: Из тела запроса; `None` — личная запись, проверять нечего.
        user_id: Текущий владелец.

    Raises:
        HTTPException: 403, если household чужой или не существует.
    """
    if household_id is None:
        return
    if not can_write_household(db, household_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на запись в этот household",
        )
