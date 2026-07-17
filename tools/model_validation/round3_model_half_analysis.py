"""Анализ модельной половины раунда 3: слои, D-вердикт, монотонность M1-M5.

Читает outcomes v3 + ключ координатора, печатает JSON-сводку:
  layers   — статусы и доминанты по слоям A/B/C/E;
  d_layer  — вердикт слоя D (invalid должен совпасть со слоем 1:1, причины);
  c_kinds  — статусы по kind каталога C (нет ли падений/дыр);
  metamorphic — по отношениям M1-M5: жёсткие инварианты статуса,
      частота смены доминанты, L1-расстояние сплитов (медиана/п95).

Жёсткие ожидания (модель-только, эксперты не нужны):
  M2 (ставка +1 п.п.), M3 (дедлайн +6 мес), M4 (подушка +1%): статус неизменен.
  M1 (доход +1%): допустим только переход deficit -> ok.
  M5 (все деньги x10): статус неизменен (знак потока масштабо-инвариантен).
Смены доминанты в парах — не дефект сами по себе (граничные эффекты floor/
насыщений легитимны), но их частота и структура — предмет отчёта.
"""
from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTCOMES = REPO / "knowledge/model_validation/model_outcomes_v3_4_0_on_v3.csv.gz"
KEY = REPO / "knowledge/model_validation/portraits_v3_coordinator_key.csv.gz"


def _read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    outcomes = {r["id"]: r for r in _read(OUTCOMES)}
    key = _read(KEY)
    if len(outcomes) != len(key):
        print(f"РАСХОЖДЕНИЕ РАЗМЕРОВ: outcomes {len(outcomes)} vs key {len(key)}")
        return 1

    layers: dict[str, Counter] = defaultdict(Counter)
    doms: dict[str, Counter] = defaultdict(Counter)
    c_kinds: dict[str, Counter] = defaultdict(Counter)
    d_bad = []
    invalid_outside_d = []
    reasons = Counter()
    pairs: dict[str, dict[str, tuple[dict, dict]]] = defaultdict(dict)

    for k in key:
        o = outcomes[k["id"]]
        layer = k["layer"]
        layers[layer][o["status"]] += 1
        if o["status"] == "ok":
            doms[layer][o["dom"]] += 1
        if layer == "C":
            c_kinds[k["kind"]][o["status"]] += 1
        if layer == "D":
            if o["status"] != "invalid":
                d_bad.append((k["id"], k["kind"], o["status"]))
            else:
                reasons[o["invalid_reason"].split(":")[0]] += 1
        elif o["status"] == "invalid":
            invalid_outside_d.append((k["id"], k["kind"]))
        if layer == "E":
            pairs[k["pair_id"]][k["pair_role"]] = (k, o)

    meta = {
        "layers_status": {la: dict(c) for la, c in sorted(layers.items())},
        "layers_dom_ok": {la: dict(c) for la, c in sorted(doms.items())},
        "d_layer": {
            "invalid": layers["D"].get("invalid", 0),
            "not_invalid": d_bad[:5],
            "invalid_outside_d": invalid_outside_d[:5],
            "reasons": dict(reasons),
        },
        "c_kinds_status": {kk: dict(c) for kk, c in sorted(c_kinds.items())},
    }

    mm: dict[str, dict] = {}
    for pid, pair in pairs.items():
        if set(pair) != {"base", "twin"}:
            continue
        (kb, ob), (_, ot) = pair["base"], pair["twin"]
        rel = kb["pair_relation"]
        slot = mm.setdefault(rel, {
            "pairs": 0, "status_violations": [], "dom_flips": 0,
            "l1": [], "flip_examples": [],
        })
        slot["pairs"] += 1
        sb, st = ob["status"], ot["status"]
        legal = sb == st or (rel == "M1_income" and sb == "deficit" and st == "ok")
        if not legal:
            slot["status_violations"].append((pid, sb, st))
        if sb == st == "ok":
            if ob["dom"] != ot["dom"]:
                slot["dom_flips"] += 1
                if len(slot["flip_examples"]) < 3:
                    slot["flip_examples"].append(
                        (pid, ob["dom"], "->", ot["dom"], "lt", ob["lt"]))
            l1 = sum(abs(float(ot[c]) - float(ob[c]))
                     for c in ("xo", "xr", "xg", "invest"))
            denom = max(float(ob["rt"]), 1.0)
            slot["l1"].append(l1 / denom)

    for rel, slot in mm.items():
        l1 = slot.pop("l1")
        slot["ok_pairs"] = len(l1)
        slot["dom_flip_rate"] = (round(slot["dom_flips"] / len(l1), 4)
                                 if l1 else None)
        slot["l1_rel_median"] = round(statistics.median(l1), 4) if l1 else None
        slot["l1_rel_p95"] = (round(sorted(l1)[int(0.95 * len(l1))], 4)
                              if l1 else None)
        slot["status_violations"] = slot["status_violations"][:5]
    meta["metamorphic"] = {rel: mm[rel] for rel in sorted(mm)}

    print(json.dumps(meta, ensure_ascii=False, indent=1))
    hard_fail = bool(d_bad or invalid_outside_d
                     or any(s["status_violations"] for s in mm.values()))
    print("ЖЁСТКИЕ ИНВАРИАНТЫ:", "НАРУШЕНЫ" if hard_fail else "ЧИСТО")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
