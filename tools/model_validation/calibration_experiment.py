"""Грид-эксперимент: можно ли поднять согласие с экспертами выше 87.4%.

Ручки — только константы v3.1.0 (веса профилей — канон, не трогаем):
  floor      — RESERVE_FLOOR_MONTHS (лексикографический стартовый резерв)
  lt_target  — целевая подушка профилей 4/5 (в пределах коридора 3–6)

Каждая конфигурация прогоняется стендом по эталону joined.csv.gz
(12 000 портретов, консенсус 4 экспертов). Печатает JSON-строки по варианту.
"""
from __future__ import annotations

import json
from pathlib import Path

import app.core.ranking as rk
from tools.model_validation.expert_agreement import load_joined, run_validation

JOINED = Path("knowledge/model_validation/joined.csv.gz")

BASE_TARGETS = {r: rk.RISK_PROFILES[r]["lt_target"] for r in rk.RISK_PROFILES}
BASE_FLOOR = rk.RESERVE_FLOOR_MONTHS

VARIANTS = [
    ("A_base", BASE_FLOOR, BASE_TARGETS),
    ("B_floor_1.5", 1.5, BASE_TARGETS),
    ("C_floor_2.0", 2.0, BASE_TARGETS),
    ("D_targets_45_up", BASE_FLOOR, {1: 6.0, 2: 5.0, 3: 4.5, 4: 4.0, 5: 3.5}),
    ("E_floor1.5_targets_up", 1.5, {1: 6.0, 2: 5.0, 3: 4.5, 4: 4.0, 5: 3.5}),
]


def apply(floor: float, targets: dict[int, float]) -> None:
    rk.RESERVE_FLOOR_MONTHS = floor
    for r, t in targets.items():
        rk.RISK_PROFILES[r]["lt_target"] = t


def main() -> None:
    rows = load_joined(JOINED)
    for name, floor, targets in VARIANTS:
        apply(floor, targets)
        stats = run_validation(rows)
        ag = stats["agreement"]
        pct = ag["agree"] / ag["with_consensus"] * 100 if ag["with_consensus"] else 0
        mism = {f"{a}->{b}": n for (a, b), n in ag["mismatch"].most_common(4)}
        print(json.dumps({
            "variant": name,
            "floor": floor,
            "targets_45": [targets[4], targets[5]],
            "agreement_pct": round(pct, 1),
            "agree": ag["agree"],
            "n": ag["with_consensus"],
            "top_mismatch": mism,
        }, ensure_ascii=False), flush=True)
    apply(BASE_FLOOR, BASE_TARGETS)  # откат


if __name__ == "__main__":
    main()
