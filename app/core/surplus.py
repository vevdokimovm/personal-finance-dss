"""
Слой управления накопленным запасом (модель v3.2.0, дефект G4 экспертизы).

Месячная решётка распределяет ПОТОК; уже накопленный запас сверх целевой
подушки Lt*·Σe до v3.2.0 не разворачивался никем, кроме узкого этапа 4.0
(разовое закрытие почти готовых целей). Экспертиза: «эксперты развернули
0.5–1 млрд ₽ излишков разовыми ходами, модель — 14 млн» — держать излишек
в кэше при живых долгах под 25–35% значит платить (ставка − r_bench) в год
за каждый рубль.

План разовых ходов (advisory-слой: месячную решётку, гейты и инварианты сумм
не трогает — как кризисный модуль, только для профицита):

  1. repay_debt   — Avalanche по излишку: полное/частичное разовое погашение
                    долгов со ставкой >= r_bench (дешёвые долги выгоднее
                    держать — OCR-логика канона §11), от самой дорогой ставки.
  2. fund_goal    — разовые взносы в ДЕДЛАЙНОВЫЕ цели (ближайший дедлайн
                    первым); бессрочные цели питаются месячным потоком.
                    Инструмент накопления — по горизонту до дедлайна (G5).
  3. invest_lump  — остаток излишка: разовый инвестиционный транш по
                    профильной полке (депозит / облигации / акции) с нотой АСВ.

Слой активен только при Rt >= 0: в дефиците запасом распоряжается кризисный
модуль (runway + балансовый ход). Целевая подушка неприкосновенна:
bliq_after >= Lt*·Σe — исполняемый инвариант I14.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.goals_priority import _months_left
from app.core.investment import (
    DEPOSIT_INSURANCE_NOTE,
    build_shelf_split,
    instrument_for_horizon,
)
from app.core.money import money


def build_surplus_plan(
    bliq: float,
    expense_total: float,
    obligations: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    r_bench: float,
    risk_tolerance: int,
    lt_target: float,
    today: datetime | None = None,
) -> dict[str, Any] | None:
    """План разовых ходов из излишка Bliq сверх целевой подушки; None если излишка нет."""
    if expense_total <= 0:
        return None  # целевая подушка в месяцах не определена
    reserve_target = money(lt_target * expense_total)
    deployable = money(bliq - reserve_target)
    if deployable <= 0:
        return None

    today = today or datetime.now()
    moves: list[dict[str, Any]] = []
    left = deployable

    # ── 1. Avalanche по излишку: дорогие долги, от самой дорогой ставки ──
    expensive = sorted(
        (
            o for o in obligations
            if float(o.get("amount", 0)) > 0
            and float(o.get("interest_rate", 0)) >= r_bench
        ),
        key=lambda o: float(o.get("interest_rate", 0)),
        reverse=True,
    )
    for o in expensive:
        if left <= 0:
            break
        amount = float(o["amount"])
        payment = float(o.get("monthly_payment", 0))
        rate = float(o.get("interest_rate", 0))
        pay = money(min(amount, left))
        closed = pay >= amount - 0.005
        moves.append({
            "type": "repay_debt",
            "id": o.get("id"),
            "name": o.get("name", ""),
            "amount": pay,
            "closed": closed,
            "interest_rate": rate,
            # платёж пропорционален остатку — освобождаемый месячный поток
            "payment_freed": money(payment * pay / amount) if amount > 0 else 0.0,
            # честная годовая выгода против безрисковой альтернативы
            "opportunity_gain_yearly": money(pay * (rate - r_bench)),
        })
        left = money(left - pay)

    # ── 2. Разовые взносы в дедлайновые цели (ближайший дедлайн первым) ──
    deadline_goals = sorted(
        (
            g for g in goals
            if g.get("deadline") is not None
            and float(g.get("target_amount", 0)) - float(g.get("current_amount", 0)) > 0
        ),
        key=lambda g: _months_left(g.get("deadline"), today),
    )
    for g in deadline_goals:
        if left <= 0:
            break
        remaining = float(g["target_amount"]) - float(g.get("current_amount", 0))
        pay = money(min(remaining, left))
        months = _months_left(g.get("deadline"), today)
        moves.append({
            "type": "fund_goal",
            "id": g.get("id"),
            "name": g.get("name", ""),
            "amount": pay,
            "closed": pay >= remaining - 0.005,
            "months_left": round(months, 1),
            "instrument": instrument_for_horizon(months),
        })
        left = money(left - pay)

    # ── 3. Остаток — разовый инвестиционный транш по профильной полке ────
    if left > 0:
        moves.append({
            "type": "invest_lump",
            "amount": left,
            "split": build_shelf_split(left, risk_tolerance),
            "note": DEPOSIT_INSURANCE_NOTE,
        })
        left = 0.0

    deployed = money(sum(m["amount"] for m in moves))
    return {
        "deployable": deployable,
        "reserve_target": reserve_target,
        "bliq_after": money(bliq - deployed),
        "moves": moves,
        "summary": _summary(deployable, reserve_target, moves),
    }


def _summary(
    deployable: float, reserve_target: float, moves: list[dict[str, Any]]
) -> str:
    """Человеческое резюме без формул (FR-01/UX-02)."""
    parts = [
        f"Накоплений больше целевой подушки ({reserve_target:,.0f} ₽): "
        f"{deployable:,.0f} ₽ могут работать, а не лежать."
    ]
    for m in moves:
        if m["type"] == "repay_debt":
            verb = "полностью закрыть" if m["closed"] else "частично погасить"
            parts.append(
                f"Разово {verb} «{m['name']}» на {m['amount']:,.0f} ₽ — "
                f"выгода против безрисковой ставки ~{m['opportunity_gain_yearly']:,.0f} ₽/год, "
                f"платежи снизятся на {m['payment_freed']:,.0f} ₽/мес."
            )
        elif m["type"] == "fund_goal":
            verb = "закрыть цель" if m["closed"] else "пополнить цель"
            parts.append(
                f"Разово {verb} «{m['name']}» на {m['amount']:,.0f} ₽; "
                f"копить лучше так: {m['instrument']}."
            )
        elif m["type"] == "invest_lump":
            parts.append(
                f"Остаток {m['amount']:,.0f} ₽ разместить как инвестиции по профилю. "
                + str(m.get("note", ""))
            )
    return " ".join(parts)
