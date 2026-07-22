"""Стенд предзарегистрированной гипотезы р.4: floor при токсичном долге.

Считает согласие модели с консенсусом экспертов по action-vector при
выключенном и включённом правиле G8, плюс split-half валидацию (эффект,
измеренный на половине выборки, должен воспроизводиться на второй — иначе
это подгонка под шум).

Прогон делается напрямую через run_planning, без пересборки joined:
экспертные колонки берутся из готового joined_v4.
"""
from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import Counter
from datetime import datetime, time
from pathlib import Path

from tools.model_validation.build_joined_v4 import action_vector
from tools.model_validation.expert_agreement import lump_split
from tools.portrait_testing.generator_v4 import PortraitGeneratorV4

REPO = Path(__file__).resolve().parents[2]
JOINED = REPO / "knowledge/model_validation/joined_v4.csv.gz"
E = ("v", "m", "j", "s")
SEED = 20260718


def consensus(row: dict) -> str | None:
    votes = Counter(row[f"{e}_act_dom"] for e in E
                    if row[f"{e}_act_dom"] != "none")
    if not votes:
        return None
    dom, n = votes.most_common(1)[0]
    return dom if n >= 3 else None


def _act_dom(result: dict) -> str:
    """Доминанта action-vector строго из ЭТОГО прогона (не из model_outcome:
    тот перезапускает планирование со своими умолчаниями и стирает режим)."""
    best = result.get("best")
    if best is None:
        return "none"
    xo = float(best.get("x_obl_effective", best.get("x_obligations", 0)))
    xr = float(best.get("x_reserve", 0))
    xg = sum(float(v) for v in (best.get("goal_allocation", {}) or {}).values())
    invest = float((best.get("investment_tranche") or {}).get("amount", 0))
    monthly = {"debt": xo, "reserve": xr - invest, "goals+": xg + invest}
    _, dom = action_vector(monthly, lump_split(result))
    return dom


def run(toxic_floor: bool) -> dict[int, str]:
    """index -> доминанта action-vector модели при заданном режиме floor."""
    with gzip.open(JOINED, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    gen = PortraitGeneratorV4(seed=SEED, n=len(rows))
    today = datetime.combine(gen.frozen_today, time(12, 0))
    from app.services.planning import run_planning

    out: dict[int, str] = {}
    for r in rows:
        if r["layer"] == "D" or r["model_status"] != "ok":
            continue
        i = int(r["index"])
        p = gen.generate(i)
        result = run_planning(
            income_total=p["income_total"], expense_total=p["expense_total"],
            obligations=p["obligations"], goals=p["goals"], bliq=p["bliq"],
            r_bench=p["r_bench"], risk_tolerance=p["risk_tolerance"],
            l_min=p["l_min"], today=today, toxic_floor=toxic_floor)
        out[i] = _act_dom(result)
    return out


def score(doms: dict[int, str], rows: list[dict],
          subset: set[int] | None = None) -> tuple[float, int]:
    agree = total = 0
    for r in rows:
        i = int(r["index"])
        if i not in doms or (subset is not None and i not in subset):
            continue
        c = consensus(r)
        if not c:
            continue
        total += 1
        agree += doms[i] == c
    return (round(100 * agree / total, 2) if total else 0.0), total


def main() -> int:
    with gzip.open(JOINED, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    base = run(toxic_floor=False)
    tox = run(toxic_floor=True)

    changed = [i for i in base if base[i] != tox[i]]
    fixed = broken = 0
    by_index = {int(r["index"]): r for r in rows}
    for i in changed:
        c = consensus(by_index[i])
        if not c:
            continue
        if base[i] != c and tox[i] == c:
            fixed += 1
        elif base[i] == c and tox[i] != c:
            broken += 1

    halves = ({i for i in base if i % 2 == 0}, {i for i in base if i % 2 == 1})
    split = []
    for h in halves:
        b, _ = score(base, rows, h)
        t, n = score(tox, rows, h)
        split.append({"n": n, "off_pct": b, "on_pct": t,
                      "delta_pp": round(t - b, 2)})

    off, n_off = score(base, rows)
    on, n_on = score(tox, rows)
    out = {
        "n_scored": n_off,
        "agreement_off_pct": off,
        "agreement_on_pct": on,
        "delta_pp": round(on - off, 2),
        "rows_changed": len(changed),
        "fixed": fixed,
        "broken": broken,
        "split_half": split,
        "transition_matrix": dict(
            Counter(f"{base[i]}->{tox[i]}" for i in changed).most_common(6)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
