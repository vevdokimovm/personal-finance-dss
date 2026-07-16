"""
Кризисный модуль (модель v3.1.0): план действий при отрицательном ресурсе.

Дефект G2 независимой экспертизы: при Rt < 0 модель выдавала диагностику и ни
одного действия, тогда как все четыре экспертных движка выдают кризисный план
на 100% дефицитных портретов. Для СППР по личным финансам кризисная ветка —
не edge case, а ядро ценности: именно в минусе человеку нужнее всего совет.

Состав плана (в порядке приоритета, консенсус экспертизы):

  1. close_debts_from_liquidity — балансовый ход: закрытие кредита из
     ликвидной подушки снимает платёж и разворачивает поток в плюс.
     Предлагается ТОЛЬКО если поток становится ≥ 0 при сохранении
     floor-резерва (RESERVE_FLOOR_MONTHS месяцев расходов). Жадный порядок по эффективности
     платёж/остаток: при пропорциональной модели платежа каждый рубль
     погашения возвращает P/A рублей потока, поэтому жадность оптимальна.
  2. cut_expenses — сколько именно резать расходы до нуля дефицита
     + потолок трат «сколько можно тратить на жизнь, не углубляя долг».
  3. freeze_goals — заморозка взносов в цели до выхода из дефицита.
  4. restructure_debt — реструктуризация/рефинансирование/кредитные каникулы
     приоритетного (самого дорогого) кредита.

Плюс запас хода (runway) — на сколько месяцев дефицита хватит подушки.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.money import money
from app.core.ranking import RESERVE_FLOOR_MONTHS

RUNWAY_CAP_MONTHS = 999.0


def _close_debts_from_liquidity(
    deficit: float,
    obligations: list[dict[str, Any]],
    bliq: float,
    expense_total: float,
) -> dict[str, Any] | None:
    """Ищет балансовый ход, разворачивающий поток в плюс.

    Платёж пропорционален остатку (та же модель, что в Avalanche): погашение z
    по кредиту с параметрами (A, P) возвращает z·P/A потока в месяц. Жадный
    выбор по убыванию P/A минимизирует расход ликвидности; при равной
    эффективности приоритет — более дорогая ставка.
    """
    floor_reserve = RESERVE_FLOOR_MONTHS * max(expense_total, 0.0)
    available = bliq - floor_reserve
    if available <= 0 or deficit <= 0:
        return None

    candidates = sorted(
        (
            o for o in obligations
            if float(o.get("amount", 0)) > 0 and float(o.get("monthly_payment", 0)) > 0
        ),
        key=lambda o: (
            float(o["monthly_payment"]) / float(o["amount"]),
            float(o.get("interest_rate", 0)),
        ),
        reverse=True,
    )
    if not candidates:
        return None

    steps: list[dict[str, Any]] = []
    recovered = 0.0
    spent = 0.0
    for o in candidates:
        need = deficit - recovered
        if need <= 0 or available - spent <= 0:
            break
        amount = float(o["amount"])
        payment = float(o["monthly_payment"])
        ratio = payment / amount
        left = available - spent
        if left >= amount:
            # ликвидности хватает на весь кредит — закрываем целиком: платёж
            # уходит полностью, «огрызок» долга не остаётся (кейс SP-00044)
            pay = amount
        else:
            # частичное погашение: ровно столько, сколько нужно для разворота
            # потока (+ копейка на округление), не глубже доступной ликвидности
            pay = min(left, need / ratio + 0.01)
        pay = money(pay)
        if pay <= 0:
            continue
        saved = money(payment * pay / amount)
        closed = pay >= amount - 0.005
        steps.append({
            "id": o.get("id"),
            "name": o.get("name", ""),
            "interest_rate": float(o.get("interest_rate", 0)),
            "paid_in": pay,
            "payment_saved": saved,
            "closed": closed,
        })
        recovered += saved
        spent += pay

    if recovered + 1e-9 < deficit:
        return None  # поток не разворачивается — ликвидность ценнее как запас хода

    bliq_remaining = money(bliq - spent)
    return {
        "type": "close_debts_from_liquidity",
        "steps": steps,
        "bliq_used": money(spent),
        "bliq_remaining": bliq_remaining,
        "new_rt": money(recovered - deficit),
        "new_lt": round(bliq_remaining / expense_total, 4) if expense_total > 0 else 0.0,
    }


def build_crisis_plan(
    income_total: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    bliq: float = 0.0,
    today: datetime | None = None,
) -> dict[str, Any] | None:
    """Кризисный план при Rt < 0; None при неотрицательном потоке."""
    payments = sum(float(o.get("monthly_payment", 0)) for o in obligations)
    rt = income_total - expense_total - payments
    if rt >= 0:
        return None

    deficit = -rt
    runway = min(RUNWAY_CAP_MONTHS, bliq / deficit) if deficit > 0 else None

    actions: list[dict[str, Any]] = []

    # ── 1. Балансовый ход: закрыть кредит из ликвидности ────────────────
    closure = _close_debts_from_liquidity(deficit, obligations, bliq, expense_total)
    payments_after = payments
    residual = deficit
    if closure is not None:
        actions.append(closure)
        residual = 0.0
        payments_after = payments - sum(s["payment_saved"] for s in closure["steps"])

    # ── 2. Сокращение расходов до нуля дефицита + потолок трат ──────────
    max_affordable = money(max(0.0, income_total - payments_after))
    if residual > 0 and expense_total > 0:
        cut = money(min(residual, expense_total))
        actions.append({
            "type": "cut_expenses",
            "amount": cut,
            "share_of_expenses": round(cut / expense_total, 4),
            "max_affordable_expenses": max_affordable,
        })

    # ── 3. Заморозка целей ───────────────────────────────────────────────
    frozen = [
        str(g.get("name", ""))
        for g in goals
        if float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)) > 0
    ]
    if frozen:
        actions.append({"type": "freeze_goals", "goals": frozen})

    # ── 4. Реструктуризация приоритетного (самого дорогого) кредита ─────
    if residual > 0 and obligations:
        priority = max(obligations, key=lambda o: float(o.get("interest_rate", 0)))
        actions.append({
            "type": "restructure_debt",
            "loan": priority.get("name", ""),
            "interest_rate": float(priority.get("interest_rate", 0)),
            "monthly_payment": money(float(priority.get("monthly_payment", 0))),
            "options": ["рефинансирование", "реструктуризация", "кредитные каникулы"],
        })

    # ── Тяжесть ──────────────────────────────────────────────────────────
    if closure is not None:
        severity = "recoverable_from_liquidity"
    elif income_total <= 0 or (runway is not None and runway < 1.0):
        severity = "critical"
    else:
        severity = "cut_required"

    return {
        "deficit": money(deficit),
        "runway_months": round(runway, 1) if runway is not None else None,
        "max_affordable_expenses": max_affordable,
        "severity": severity,
        "actions": actions,
        "summary": _summary(
            deficit, runway, severity, closure, residual, expense_total,
            max_affordable, bool(frozen),
        ),
    }


def _summary(
    deficit: float,
    runway: float | None,
    severity: str,
    closure: dict[str, Any] | None,
    residual: float,
    expense_total: float,
    max_affordable: float,
    has_goals: bool,
) -> str:
    """Человеческое резюме без формул (принцип FR-01/UX-02)."""
    parts: list[str] = [
        f"Бюджет в минусе на {deficit:,.0f} ₽ в месяц."
    ]
    if closure is not None:
        names = ", ".join(f"«{s['name']}»" for s in closure["steps"])
        parts.append(
            f"Ситуация исправима одним действием: погасить {names} из подушки "
            f"({closure['bliq_used']:,.0f} ₽) — платежи снизятся, и поток "
            f"станет положительным. Подушки останется {closure['bliq_remaining']:,.0f} ₽."
        )
    else:
        if runway is not None and runway >= 1:
            parts.append(
                f"Подушки хватит примерно на {runway:.0f} мес. такого дефицита — "
                f"это время на манёвр, а не решение."
            )
        elif severity == "critical":
            parts.append("Запаса на покрытие дефицита практически нет — меры срочные.")
        if residual > 0 and expense_total > 0:
            parts.append(
                f"Чтобы выйти в ноль, нужно сократить расходы минимум на "
                f"{residual:,.0f} ₽ в месяц: на жизнь сейчас можно тратить "
                f"не больше {max_affordable:,.0f} ₽."
            )
        if residual > 0:
            parts.append(
                "Параллельно стоит снизить платежи по самому дорогому кредиту: "
                "рефинансирование, реструктуризация или кредитные каникулы."
            )
    if has_goals:
        parts.append("Взносы в цели на время дефицита замораживаются.")
    return " ".join(parts)
