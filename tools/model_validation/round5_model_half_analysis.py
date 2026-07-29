"""Анализ модельной половины раунда 5: слои, вердикт D, M1-M5, семейства H5.

Продолжает `round3_model_half_analysis.py` тем же методом (числа сравнимы между
раундами) и добавляет то, что появилось в раунде 5:

  * `d_layer.missed_by_expected_error` — РАЗБОР ПРОПУСКОВ слоя D по манифесту
    ожидаемых отказов. В раунде 4 модель ловила 600/600, в раунде 5 датасет
    заполнил кромку ПСК (ставки 2.93-3.00) — пропуски обязаны быть названы
    поимённо, иначе «600/625» не отличить от неизвестной течи валидатора;
  * `families` — базлайн по семействам предзарегистрированных гипотез H5-1/
    H5-2/H5-3 (`floor_edge` и разрезы), чтобы модельная половина была готова
    к разбору до прихода экспертных пакетов.

Жёсткие инварианты (модель-только, эксперты не нужны):
  M2 (ставка +1 п.п.), M3 (дедлайн +6 мес), M4 (подушка +1%): статус неизменен.
  M1 (доход +1%): допустим только переход deficit -> ok.
  M5 (все деньги x k): статус неизменен (знак потока масштабо-инвариантен).
Смена доминанты внутри пары дефектом сама по себе не считается (граничные
эффекты floor и насыщений легитимны), но частота и структура — предмет отчёта.

Запуск из корня репо:
    python -m tools.model_validation.round5_model_half_analysis \
        --outcomes knowledge/model_validation/model_outcomes_v3_5_0_on_v5.csv.gz \
        --key knowledge/model_validation/coordinator_key_v5.csv.gz \
        --json docs/model/expert_certification/iterations/5/round5_model_half.json
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTCOMES = (REPO
                    / "knowledge/model_validation/model_outcomes_v3_5_0_on_v5.csv.gz")
DEFAULT_KEY = REPO / "knowledge/model_validation/coordinator_key_v5.csv.gz"


def _read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _money(row: dict, col: str) -> float:
    value = row.get(col)
    return float(value) if value not in ("", None) else 0.0


def analyse(outcomes_rows: list[dict], key_rows: list[dict]) -> dict:
    outcomes = {r["id"]: r for r in outcomes_rows}
    if len(outcomes) != len(key_rows):
        raise SystemExit(f"РАСХОЖДЕНИЕ РАЗМЕРОВ: outcomes {len(outcomes)} "
                         f"vs key {len(key_rows)}")

    layers: dict[str, Counter] = defaultdict(Counter)
    doms: dict[str, Counter] = defaultdict(Counter)
    c_kinds: dict[str, Counter] = defaultdict(Counter)
    fam_status: dict[str, Counter] = defaultdict(Counter)
    fam_dom: dict[str, Counter] = defaultdict(Counter)
    d_missed: list[dict] = []
    d_missed_by_err: Counter = Counter()
    d_total_by_err: Counter = Counter()
    invalid_outside_d: list[tuple[str, str]] = []
    reasons: Counter = Counter()
    pairs: dict[str, dict[str, tuple[dict, dict]]] = defaultdict(dict)

    for k in key_rows:
        o = outcomes[k["id"]]
        layer = k["layer"]
        layers[layer][o["status"]] += 1
        if o["status"] == "ok":
            doms[layer][o["dom"]] += 1
        if k["family"]:
            fam_status[k["family"]][o["status"]] += 1
            if o["status"] == "ok":
                fam_dom[k["family"]][o["dom"]] += 1
        if layer == "C":
            c_kinds[k["kind"]][o["status"]] += 1
        if layer == "D":
            d_total_by_err[k["expected_error"]] += 1
            if o["status"] != "invalid":
                d_missed.append({"id": k["id"], "kind": k["kind"],
                                 "expected_error": k["expected_error"],
                                 "model_status": o["status"], "dom": o["dom"]})
                d_missed_by_err[k["expected_error"]] += 1
            else:
                reasons[o["invalid_reason"].split(":")[0]] += 1
        elif o["status"] == "invalid":
            invalid_outside_d.append((k["id"], k["kind"]))
        if k["pair_relation"].startswith("M"):
            pairs[k["pair_id"]][k["pair_role"]] = (k, o)

    meta: dict = {
        "layers_status": {la: dict(c) for la, c in sorted(layers.items())},
        "layers_dom_ok": {la: dict(c) for la, c in sorted(doms.items())},
        "d_layer": {
            "total": sum(layers["D"].values()),
            "invalid": layers["D"].get("invalid", 0),
            "missed": len(d_missed),
            "missed_by_expected_error": {
                err: {"missed": n, "total": d_total_by_err[err]}
                for err, n in d_missed_by_err.most_common()
            },
            "missed_sample": d_missed[:10],
            "invalid_outside_d": invalid_outside_d[:5],
            "false_positives_on_valid": len(invalid_outside_d),
            "reasons": dict(reasons.most_common()),
        },
        "c_kinds_status": {kk: dict(c) for kk, c in sorted(c_kinds.items())},
        "families": {
            f: {"n": sum(c.values()), "status": dict(c),
                "dom_ok": dict(fam_dom[f])}
            for f, c in sorted(fam_status.items())
        },
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
        legal = sb == st or (rel == "M1_income" and sb == "deficit"
                             and st == "ok")
        if not legal:
            slot["status_violations"].append((pid, sb, st))
        if sb == st == "ok":
            if ob["dom"] != ot["dom"]:
                slot["dom_flips"] += 1
                if len(slot["flip_examples"]) < 3:
                    slot["flip_examples"].append(
                        (pid, ob["dom"], "->", ot["dom"], "lt", ob["lt"]))
            l1 = sum(abs(_money(ot, c) - _money(ob, c))
                     for c in ("xo", "xr", "xg", "invest"))
            denom = max(_money(ob, "rt"), 1.0)
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

    lumps = sorted(x for x in (_money(r, "model_lump") for r in outcomes_rows)
                   if x > 0)
    meta["lump"] = {
        "share_pct": round(100 * len(lumps) / len(outcomes_rows), 2),
        "median": round(lumps[len(lumps) // 2], 2) if lumps else 0.0,
    }
    return meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Модельная половина раунда 5")
    parser.add_argument("--outcomes", type=Path, default=DEFAULT_OUTCOMES)
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)

    meta = analyse(_read(args.outcomes), _read(args.key))
    payload = json.dumps(meta, ensure_ascii=False, indent=1)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload + "\n", encoding="utf-8")
    print(payload)

    d = meta["d_layer"]
    hard_fail = bool(d["false_positives_on_valid"]
                     or any(s["status_violations"]
                            for s in meta["metamorphic"].values()))
    print("ЖЁСТКИЕ ИНВАРИАНТЫ:", "НАРУШЕНЫ" if hard_fail else "ЧИСТО")
    print(f"СЛОЙ D: {d['invalid']}/{d['total']} отклонено, "
          f"пропущено {d['missed']}, ложных {d['false_positives_on_valid']}")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
