"""Валидация портрета перед прогоном через модель (стенд раунда 3, слой D).

Правило зеркально экспертному брифу v3 (`docs/model/expert_brief_v3.md`):
запись дефектна, если её нельзя однозначно прочитать как валидные финансовые
данные — нарушен тип/знак/формат поля или обязательное поле отсутствует.
Пограничные, но читаемые значения (гигантские суммы, ставка 59% годовых,
просроченный дедлайн) дефектом НЕ считаются.

Возвращаемое значение `invalid_reason` — человекочитаемая причина первой
найденной проблемы или None для валидной записи. Модель на invalid-записях
не запускается: статус `invalid`, dom `none`, нулевые сплиты — симметрично
тому, что бриф требует от экспертов.

Порог ставки: 0 <= r <= 3.0 (300% годовых) — покрывает весь легальный и
серый рынок РФ включая МФО; выше — только мусор слоя D (absurd_rate_12).
Дубли id — дефект уровня ВЫГРУЗКИ, per-record валидатор их не видит;
их обработка — забота сборщика joined раунда 3 (сопоставление по порядку).
"""
from __future__ import annotations

from datetime import date, datetime

RATE_MAX = 3.0
REQUIRED_NUMERIC = ("income_total", "expense_total", "bliq")


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _bad_deadline(goal: dict) -> str | None:
    if "deadline" not in goal:
        return "у цели отсутствует поле deadline"
    value = goal["deadline"]
    if value is None or isinstance(value, (date, datetime)):
        return None
    if isinstance(value, str):
        try:
            date.fromisoformat(value)
            return None
        except ValueError:
            return f"непарсящаяся дата дедлайна: {value!r}"
    return f"дедлайн неожиданного типа: {type(value).__name__}"


def invalid_reason(portrait: dict) -> str | None:
    """Причина дефектности записи или None, если запись валидна."""
    for field in REQUIRED_NUMERIC:
        if field not in portrait:
            return f"отсутствует поле {field}"
        value = portrait[field]
        if not _is_number(value):
            return f"{field} не число: {value!r}"
        if value < 0:
            return f"{field} отрицательное: {value!r}"

    risk = portrait.get("risk_tolerance")
    if not isinstance(risk, int) or isinstance(risk, bool) or not 1 <= risk <= 5:
        return f"risk_tolerance вне 1..5: {risk!r}"
    r_bench = portrait.get("r_bench")
    if not _is_number(r_bench) or not 0 < r_bench < 1:
        return f"r_bench вне (0; 1): {r_bench!r}"

    for o in portrait.get("obligations") or ():
        for field in ("amount", "monthly_payment"):
            value = o.get(field)
            if not _is_number(value):
                return f"кредит: {field} не число: {value!r}"
            if value < 0:
                return f"кредит: {field} отрицательное: {value!r}"
        rate = o.get("interest_rate")
        if not _is_number(rate):
            return f"кредит: ставка не число: {rate!r}"
        if rate < 0:
            return f"кредит: отрицательная ставка: {rate!r}"
        if rate > RATE_MAX:
            return f"кредит: ставка {rate!r} выше порога {RATE_MAX} (300%)"

    for g in portrait.get("goals") or ():
        for field in ("target_amount", "current_amount"):
            value = g.get(field)
            if not _is_number(value):
                return f"цель: {field} не число: {value!r}"
            if value < 0:
                return f"цель: {field} отрицательное: {value!r}"
        bad = _bad_deadline(g)
        if bad:
            return bad
    return None
