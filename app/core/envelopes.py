"""Ядро «конвертов»: связь цель↔ликвидный актив (мат-модель, вариант B).

Цель может быть привязана к ликвидному активу, где физически копятся деньги.
Тогда её накопление и ставка берутся из актива, а сам актив исключается из
свободного резерва (Bliq) — чтобы одни деньги не учитывались дважды:
привязанный актив виден только через цель (Sn), свободный — только в подушке.

Чистая логика без ORM: работает и с dict, и с моделями через get_value.
"""
from __future__ import annotations

from typing import Any

from app.core.metrics import Item, get_value, to_float


def assets_index(assets: list[Item]) -> dict[int, Item]:
    """Индекс активов по id (id → актив)."""
    index: dict[int, Item] = {}
    for asset in assets:
        aid = get_value(asset, "id", None)
        if aid is not None:
            index[int(aid)] = asset
    return index


def linked_asset_ids(goals: list[Item]) -> set[int]:
    """Множество id активов, привязанных к целям."""
    ids: set[int] = set()
    for goal in goals:
        aid = get_value(goal, "linked_asset_id", None)
        if aid:
            ids.add(int(aid))
    return ids


def free_assets(assets: list[Item], goals: list[Item]) -> list[Item]:
    """Свободные активы (не привязанные к целям) — идут в Bliq/подушку."""
    linked = linked_asset_ids(goals)
    return [a for a in assets if get_value(a, "id", None) not in linked]


def effective_goal_values(goal: Item, index: dict[int, Item]) -> tuple[float, float]:
    """(current_amount, savings_rate) цели с учётом привязки к активу.

    Привязана к существующему активу → значения из актива.
    Иначе (нет привязки или актив не найден) → собственные значения цели.
    """
    aid = get_value(goal, "linked_asset_id", None)
    if aid and int(aid) in index:
        asset = index[int(aid)]
        return to_float(get_value(asset, "amount", 0.0)), to_float(get_value(asset, "interest_rate", 0.0))
    return to_float(get_value(goal, "current_amount", 0.0)), to_float(get_value(goal, "savings_rate", 0.0))


def apply_envelopes(goals: list[Item], assets: list[Item]) -> tuple[list[dict[str, Any]], list[Item]]:
    """Применяет логику конвертов.

    Возвращает (цели с эффективными current_amount/savings_rate, свободные активы).
    Цели возвращаются как новые dict, чтобы не мутировать исходные объекты.
    """
    index = assets_index(assets)
    effective_goals: list[dict[str, Any]] = []
    for goal in goals:
        current, rate = effective_goal_values(goal, index)
        effective_goals.append({
            "id": get_value(goal, "id", None),
            "name": get_value(goal, "name", ""),
            "target_amount": to_float(get_value(goal, "target_amount", 0.0)),
            "current_amount": current,
            "savings_rate": rate,
            "deadline": get_value(goal, "deadline", None),
            "category": get_value(goal, "category", "material"),
            "linked_asset_id": get_value(goal, "linked_asset_id", None),
        })
    return effective_goals, free_assets(assets, goals)
