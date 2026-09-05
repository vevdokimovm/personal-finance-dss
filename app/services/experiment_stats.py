"""Значимость разницы между вариантами A/B-эксперимента (v8.49.0).

Отдельный модуль, а не функция в `analytics.py`: это чистая математика без обращения
к БД, и её проверяют отдельно от запросов. `app/core/` не тронут — канон математической
модели FINPILOT (`docs/math_model.md`) про распределение денежного потока, а здесь
статистика продуктовых экспериментов, другая предметная область.

## Почему двухпропорциональный z-тест

Сравниваются две доли на независимых выборках — это его штатный случай. Точный тест
Фишера был бы строже на очень малых выборках, но там ответ всё равно «данных мало»,
и обе процедуры дают его одинаково; z-тест не требует внешних зависимостей
(`scipy` в проекте нет) и считается через `math.erfc`.
"""
from __future__ import annotations

import math

# Порог значимости. 0.05 — общепринятый по умолчанию; вынесен константой, чтобы
# менялся в одном месте, а не подставлялся числом по коду.
ALPHA = 0.05


def _normal_two_sided_p(z: float) -> float:
    """Двусторонний p-value для z-статистики стандартного нормального распределения.

    Args:
        z: Значение z-статистики.

    Returns:
        Вероятность увидеть отклонение не меньше |z| при верной нулевой гипотезе.
    """
    return math.erfc(abs(z) / math.sqrt(2.0))


def compare_to_control(
    control: tuple[int, int], variant: tuple[int, int], alpha: float = ALPHA
) -> dict:
    """Сравнить вариант с контролем по конверсии.

    Args:
        control: Пара (назначено, сконвертировалось) для контрольного варианта.
        variant: Пара (назначено, сконвертировалось) для сравниваемого варианта.
        alpha: Порог значимости.

    Returns:
        Словарь с полями `uplift_pct` (относительный подъём в процентах или None),
        `p_value` (или None, если считать не из чего) и `significant`.

    Raises:
        ValueError: Если конверсий больше, чем назначений — это порча данных,
            и молча посчитанная доля больше единицы попала бы на экран.
    """
    control_n, control_converted = control
    variant_n, variant_converted = variant

    for assigned, converted in (control, variant):
        if converted > assigned:
            raise ValueError(
                f"Конверсий ({converted}) больше, чем назначений ({assigned}): "
                "данные повреждены."
            )

    # Пустая выборка: ответ «неизвестно», а не «ноль процентов». Вариант, который
    # ни разу не показали, не провалился — про него просто нечего сказать.
    if control_n == 0 or variant_n == 0:
        return {"uplift_pct": None, "p_value": None, "significant": False}

    control_rate = control_converted / control_n
    variant_rate = variant_converted / variant_n

    # Относительный подъём. Контроль без конверсий даёт деление на ноль: величина
    # эффекта не определена, и подстановка любого знаменателя была бы выдумкой.
    uplift_pct = (
        round((variant_rate - control_rate) / control_rate * 100, 2)
        if control_rate > 0
        else None
    )

    pooled = (control_converted + variant_converted) / (control_n + variant_n)
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / control_n + 1 / variant_n))

    # Нулевая дисперсия: обе доли равны 0 или обе равны 1. Разницы нет по построению.
    if standard_error == 0:
        return {"uplift_pct": uplift_pct, "p_value": 1.0, "significant": False}

    z = (variant_rate - control_rate) / standard_error
    p_value = _normal_two_sided_p(z)

    return {
        "uplift_pct": uplift_pct,
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
    }
