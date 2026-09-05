"""Результаты A/B отвечают «можно ли верить разнице», а не только «сколько процентов» (v8.49.0).

## Зачем это в бэкенде, а не на фронте

Экран A/B открывают, чтобы принять решение: катить вариант или нет. Голые
`assigned/converted/rate` на этот вопрос не отвечают — 12 % против 10 % на полусотне
наблюдений неотличимы от шума, и человек, увидев два числа рядом, решает в пользу
большего. Это тот же дефект, что design-critic нашёл на экране метрик: величина,
которую надо было посчитать, оставлена читателю в уме.

🔴 Считает СЕРВЕР, а не фронт: значимость — часть ответа эндпоинта, иначе каждый
клиент (React, curl, будущий мобильный) будет считать её по-своему или не считать вовсе.

## Что именно считается

Двухпропорциональный z-тест против контрольного варианта (первый в списке). Это
стандартная проверка для сравнения долей и она даёт ровно то, что нужно: вероятность
увидеть такую разницу, если варианты на самом деле одинаковы.
"""
from __future__ import annotations

import math

import pytest

from app.services.experiment_stats import compare_to_control


class TestCompareToControl:
    """Сравнение варианта с контролем: разница, значимость, честное «не знаем»."""

    def test_no_difference_is_not_significant(self) -> None:
        """Одинаковые доли — разницы нет, значимости нет.

        Базовый случай: если варианты неотличимы, экран обязан сказать это прямо,
        а не показать «+0.0 %» как достижение.
        """
        result = compare_to_control(control=(1000, 100), variant=(1000, 100))
        assert result["significant"] is False
        assert result["uplift_pct"] == 0.0

    def test_large_clear_difference_is_significant(self) -> None:
        """20 % против 10 % на тысяче наблюдений — разница есть, и это видно."""
        result = compare_to_control(control=(1000, 100), variant=(1000, 200))
        assert result["significant"] is True
        assert result["p_value"] < 0.05
        assert result["uplift_pct"] > 0

    def test_tiny_sample_is_never_significant(self) -> None:
        """🔴 Главное: на малой выборке разница НЕ объявляется значимой.

        12 % против 10 % при 50 наблюдениях — обычный шум. Именно здесь экран
        без статистики обманывает: два числа рядом выглядят как вывод.
        """
        result = compare_to_control(control=(50, 5), variant=(50, 6))
        assert result["significant"] is False
        assert result["p_value"] > 0.05

    def test_zero_assigned_says_unknown_not_zero(self) -> None:
        """🔴 Пустой вариант — «данных нет», а не «конверсия 0 %».

        Ноль назначений и ноль конверсий дают 0/0. Показать это как 0 % значит
        объявить вариант провальным, ни разу его не показав.
        """
        result = compare_to_control(control=(0, 0), variant=(0, 0))
        assert result["significant"] is False
        assert result["p_value"] is None
        assert result["uplift_pct"] is None

    def test_control_without_conversions_does_not_divide_by_zero(self) -> None:
        """Контроль без конверсий: подъём в процентах не определён, падения нет.

        Делить на ноль нельзя, и подстановка единицы в знаменатель соврала бы
        о величине эффекта. Честный ответ — None по подъёму, но значимость считается.
        """
        result = compare_to_control(control=(500, 0), variant=(500, 50))
        assert result["uplift_pct"] is None
        assert result["significant"] is True

    def test_worse_variant_gives_negative_uplift(self) -> None:
        """Вариант хуже контроля — подъём отрицательный, а не по модулю."""
        result = compare_to_control(control=(1000, 200), variant=(1000, 100))
        assert result["uplift_pct"] < 0

    @pytest.mark.parametrize(
        "control,variant",
        [((100, 10), (100, 12)), ((1000, 100), (1000, 120)), ((10000, 1000), (10000, 1200))],
    )
    def test_same_effect_becomes_significant_only_with_enough_data(
        self, control: tuple[int, int], variant: tuple[int, int]
    ) -> None:
        """Один и тот же эффект (+20 % относительно) на разных объёмах.

        Проверяет само свойство метода: значимость растёт с выборкой. Мутация
        «считать значимым всё подряд» роняет первый случай, мутация «никогда не
        значимо» — последний.
        """
        result = compare_to_control(control=control, variant=variant)
        if control[0] >= 10000:
            assert result["significant"] is True
        elif control[0] <= 100:
            assert result["significant"] is False

    def test_p_value_is_a_probability(self) -> None:
        """p-value обязано лежать в [0, 1] — иначе это не вероятность."""
        for assigned in (10, 100, 1000, 5000):
            result = compare_to_control(
                control=(assigned, assigned // 10), variant=(assigned, assigned // 8)
            )
            assert result["p_value"] is not None
            assert 0.0 <= result["p_value"] <= 1.0
            assert not math.isnan(result["p_value"])

    def test_converted_cannot_exceed_assigned(self) -> None:
        """Конверсий больше, чем назначений, быть не может — это порча данных.

        Тихо посчитать долю больше единицы значило бы показать «конверсия 150 %»
        и заставить владельца гадать, где сломалось.
        """
        with pytest.raises(ValueError):
            compare_to_control(control=(10, 20), variant=(10, 5))
