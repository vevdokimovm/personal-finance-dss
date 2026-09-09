"""Карточка демо-портрета описывает тот портрет, который загрузится.

## Что закрывает

`CASE_META` — то, что человек видит на экране выбора: имя, возраст, профессия, город.
`case_*()` — сами данные, которые загрузятся по клику. Между ними не было ни одной
связи, кроме ключа словаря.

🔴 **Замер 08.09.2026: разошлись 9 карточек из 10.** Ольга в данных — «38, библиотекарь,
Тула», а на карточке «44 · Бухгалтер · Екатеринбург»; Дмитрий 28 против 41; Екатерина
из Сочи стала москвичкой. Совпадает только Анна.

**Почему это дороже опечатки.** Витрина противоречит сама себе на том экране, который
выбран для первого впечатления: карточка обещает бухгалтера, а в списке доходов рядом —
«Заработная плата (библиотекарь)». Для продукта, чья планка — Т-Банк и Сбер, это
читается как «сгенерировали и не прочитали».

**Как это накопилось.** `CASE_META` переписывали в v8.46.0 «для человека, который впервые
видит продукт» — переписали текст и не сверили с данными. Тот же класс, что PIT-029:
формулировку обновили, число под ней осталось прежним.

Найдено восьмым проходом независимого аудита.

## Что проверяется

Возраст и город из карточки обязаны встречаться в докстроке функции портрета —
она и есть краткое описание того, кого грузим. Профессию сверяем мягко: карточка
намеренно пишет её понятнее («Своя мастерская» вместо «владелец мастерской»),
и требовать дословного совпадения значило бы запретить нормальный язык.
"""
from __future__ import annotations

import inspect
import re

import pytest

from app.api.routes_demo import CASE_META, CASES


def _portrait_doc(key: str) -> str:
    """Однострочное описание портрета из докстроки его функции."""
    factory = CASES[key]
    return " ".join((inspect.getdoc(factory) or "").split())


def _card_age(key: str) -> str | None:
    match = re.search(r",\s*(\d{2})\s*$", CASE_META[key]["name"])
    return match.group(1) if match else None


#: Один город, записанный по-разному. Сокращение — не расхождение: карточка пишет
#: «Санкт-Петербург» для читателя, докстрока портрета — «СПб» для разработчика.
CITY_ALIASES = {"Санкт-Петербург": ("СПб", "Санкт-Петербург", "Питер")}


def _card_city(key: str) -> str:
    return CASE_META[key]["role"].split("·")[-1].strip()


def _city_variants(city: str) -> tuple[str, ...]:
    return CITY_ALIASES.get(city, (city,))


class TestCardMatchesPortrait:
    """Каждая карточка описывает свой портрет, а не соседний."""

    @pytest.mark.parametrize("key", sorted(CASE_META))
    def test_age_matches(self, key: str) -> None:
        """🔴 Мутация «сменить возраст в карточке» роняет тест здесь."""
        age = _card_age(key)
        assert age, f"в карточке «{key}» не разобран возраст"
        doc = _portrait_doc(key)
        assert re.search(rf",\s*{age},", doc), (
            f"карточка «{key}» обещает {age} лет, а портрет — другой: {doc[:70]}"
        )

    @pytest.mark.parametrize("key", sorted(CASE_META))
    def test_city_matches(self, key: str) -> None:
        city = _card_city(key)
        assert city, f"в карточке «{key}» не разобран город"
        doc = _portrait_doc(key)
        assert any(variant in doc for variant in _city_variants(city)), (
            f"карточка «{key}» отправляет человека в «{city}», а портрет — нет: {doc[:70]}"
        )


class TestGateItselfWorks:
    """Сетка читает обе стороны, а не молчит на пустом месте."""

    def test_every_card_has_a_portrait(self) -> None:
        missing = sorted(set(CASE_META) - set(CASES))
        assert not missing, f"карточка есть, портрета нет: {missing}"

    def test_every_portrait_has_a_card(self) -> None:
        missing = sorted(set(CASES) - set(CASE_META))
        assert not missing, f"портрет есть, карточки нет: {missing}"

    def test_portrait_docs_are_descriptive(self) -> None:
        """Докстроки портретов — источник сверки, они не могут быть пустыми."""
        short = [k for k in CASES if len(_portrait_doc(k)) < 30]
        assert not short, f"портрет без внятного описания: {short}"
