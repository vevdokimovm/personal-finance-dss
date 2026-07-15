"""
Распределение досрочного погашения x_obl между обязательствами
с фильтром по альтернативной доходности (форм. 41 ВКР).

Алгоритм Avalanche (Bach, 2003) с OCR-фильтром (Brealey-Myers-Allen):
  1. Берём только обязательства со ставкой rl ≥ r_bench
  2. Сортируем по убыванию ставки
  3. Применяем x_obl последовательно к самым дорогим
  4. Если ни один кредит не проходит фильтр — досрочка экономически
     невыгодна, средства возвращаются в свободный поток

При досрочке платёж снижается пропорционально новому остатку
(сохраняем срок кредита, уменьшаем тело долга).
"""
from __future__ import annotations

from typing import Any


def allocate_obligations_avalanche(
    x_obl: float,
    obligations: list[dict[str, Any]],
    r_bench: float,
) -> tuple[float, list[dict[str, Any]], float]:
    """
    Распределяет x_obl между обязательствами по правилу Avalanche
    с фильтрацией по альтернативной доходности r_bench (форм. 41).

    Returns:
        x_obl_effective: фактически направлено на досрочку
        new_obligations: обновлённые обязательства (с новыми A и P)
        x_obl_unused:    нераспределённый остаток (возвращается в свободный поток)
    """
    if x_obl <= 0 or not obligations:
        return 0.0, [dict(o) for o in obligations], x_obl

    targets = sorted(
        [o for o in obligations if float(o.get("interest_rate", 0)) >= r_bench],
        key=lambda o: float(o.get("interest_rate", 0)),
        reverse=True,
    )

    if not targets:
        # Все долги ниже бенчмарка — досрочка невыгодна (NPV-правило)
        return 0.0, [dict(o) for o in obligations], x_obl

    remaining = float(x_obl)
    updated = {o["id"]: dict(o) for o in obligations if "id" in o}
    if not updated:
        updated = {i: dict(o) for i, o in enumerate(obligations)}

    for loan in targets:
        if remaining <= 0:
            break
        loan_obj = updated.get(loan["id"])
        if loan_obj is None:
            continue

        old_amount = float(loan_obj["amount"])
        old_payment = float(loan_obj.get("monthly_payment", 0))

        apply = min(remaining, old_amount)
        new_amount = old_amount - apply

        # Платёж снижается пропорционально новому остатку (срок сохраняется)
        if old_amount > 0:
            loan_obj["monthly_payment"] = old_payment * (new_amount / old_amount)
        else:
            loan_obj["monthly_payment"] = 0
        loan_obj["amount"] = new_amount
        remaining -= apply

    x_obl_effective = float(x_obl) - remaining
    return x_obl_effective, list(updated.values()), remaining
