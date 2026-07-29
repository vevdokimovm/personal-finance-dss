"""Разбор раунда 5: согласие, коридор экспертов, гипотезы H5, профили четвёрки.

Один проход по `joined_v5.csv.gz` даёт всё, что нужно для отчёта раунда:

  * согласие модели с консенсусом (>= 3/4) по месячной доминанте и по
    action-vector, срезы по слоям / семействам / уверенности;
  * КОРИДОР попарного согласия самих экспертов — потолок метрики модели;
  * решающие деревья предзарегистрированных гипотез H5-1 и H5-3;
  * конфьюжн слоя D по каждому эксперту (в т.ч. кромка ПСК — вопрос В1);
  * ПРОФИЛИ экспертов: доли направлений, режим разовых ходов, поведение в
    полосе тонкой подушки — то есть «из какой позиции работает каждый».

Запуск из корня репо:
    python -m tools.model_validation.round5_agreement \
        --joined knowledge/model_validation/joined_v5.csv.gz \
        --json docs/model/expert_certification/iterations/5/round5_agreement.json
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

EXPERTS = ("v", "m", "j", "s")
DIRECTIONS = ("debt", "reserve", "goals+")


def read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def consensus(row: dict, field: str) -> str | None:
    """Консенсус = совпадение у >= 3 из 4; `none` не голосует."""
    votes = Counter(row[f"{e}_{field}"] for e in EXPERTS
                    if row[f"{e}_{field}"] != "none")
    if not votes:
        return None
    dom, n = votes.most_common(1)[0]
    return dom if n >= 3 else None


def num(row: dict, key: str) -> float:
    raw = row.get(key)
    return float(raw) if raw not in ("", None) else 0.0


def agreement(rows: list[dict], field: str, model_field: str) -> dict:
    pairs = [(r, consensus(r, field)) for r in rows]
    with_c = [(r, c) for r, c in pairs if c is not None]
    agree = sum(1 for r, c in with_c if r[model_field] == c)
    confusion = Counter((c, r[model_field]) for r, c in with_c
                        if r[model_field] != c)
    return {
        "rows": len(rows),
        "with_consensus": len(with_c),
        "no_consensus": len(rows) - len(with_c),
        "model_agrees": agree,
        "agreement_pct": round(100 * agree / len(with_c), 2) if with_c else None,
        "top_confusions": [{"consensus": k[0], "model": k[1], "n": v}
                           for k, v in confusion.most_common(6)],
    }


def expert_corridor(rows: list[dict], field: str) -> dict:
    """Попарное согласие экспертов между собой + согласие каждого с консенсусом
    остальных трёх. Верхняя граница коридора — потолок метрики модели."""
    pairwise = {}
    for a, b in combinations(EXPERTS, 2):
        both = [r for r in rows
                if r[f"{a}_{field}"] != "none" and r[f"{b}_{field}"] != "none"]
        same = sum(1 for r in both if r[f"{a}_{field}"] == r[f"{b}_{field}"])
        pairwise[f"{a}-{b}"] = round(100 * same / len(both), 2) if both else None
    leave_one_out = {}
    for e in EXPERTS:
        others = [x for x in EXPERTS if x != e]
        hits = tot = 0
        for r in rows:
            votes = Counter(r[f"{o}_{field}"] for o in others
                            if r[f"{o}_{field}"] != "none")
            if not votes:
                continue
            dom, n = votes.most_common(1)[0]
            if n < 3:
                continue
            tot += 1
            if r[f"{e}_{field}"] == dom:
                hits += 1
        leave_one_out[e] = round(100 * hits / tot, 2) if tot else None
    vals = [v for v in pairwise.values() if v is not None]
    loo = [v for v in leave_one_out.values() if v is not None]
    return {
        "pairwise": pairwise,
        "pairwise_range": [min(vals), max(vals)] if vals else None,
        "leave_one_out": leave_one_out,
        "corridor": [min(loo), max(loo)] if loo else None,
    }


def profiles(rows: list[dict]) -> dict:
    """Из какой позиции работает каждый эксперт: направления, lump, полоса."""
    out: dict = {}
    ok = [r for r in rows if r["model_status"] != "invalid"]
    for e in list(EXPERTS) + ["model"]:
        pre = "model" if e == "model" else e
        st = f"{pre}_status" if e != "model" else "model_status"
        rows_ok = [r for r in rows if r[st] == "ok"]
        if e == "model":
            monthly = {"debt": "model_xo", "reserve": "model_xr"}
            goal_cols = ("model_xg", "model_invest")
            lump_cols = ("model_lump_debt", "model_lump_reserve",
                         "model_lump_goal")
            act = "model_act_dom"
        else:
            monthly = {"debt": f"{e}_debt", "reserve": f"{e}_res"}
            goal_cols = (f"{e}_goal", f"{e}_inv")
            lump_cols = (f"{e}_lump_debt", f"{e}_lump_reserve",
                         f"{e}_lump_goal")
            act = f"{e}_act_dom"
        flow = {"debt": 0.0, "reserve": 0.0, "goals+": 0.0}
        for r in rows_ok:
            flow["debt"] += num(r, monthly["debt"])
            flow["reserve"] += num(r, monthly["reserve"])
            flow["goals+"] += sum(num(r, c) for c in goal_cols)
        lumps = [sum(num(r, c) for c in lump_cols) for r in rows]
        nz = sorted(x for x in lumps if x > 0)
        lump_dir = {d: sum(num(r, c) for r in rows)
                    for d, c in zip(DIRECTIONS, lump_cols)}
        total_flow = sum(flow.values()) or 1.0
        total_lump = sum(lump_dir.values()) or 1.0
        out[e] = {
            "ok": len(rows_ok),
            "monthly_share": {d: round(100 * flow[d] / total_flow, 1)
                              for d in DIRECTIONS},
            "lump_share_pct": round(100 * len(nz) / len(rows), 1),
            "lump_median": round(nz[len(nz) // 2], 2) if nz else 0.0,
            "lump_direction_share": {d: round(100 * lump_dir[d] / total_lump, 1)
                                     for d in DIRECTIONS},
            "act_dom": dict(Counter(r[act] for r in rows_ok).most_common()),
        }
    out["_ok_universe"] = len(ok)
    return out


def h5_cells(rows: list[dict], field: str) -> dict:
    """Ячейки предзарегистрированных гипотез: доли направлений у всех сторон."""
    cells = ("floor_edge_with_near_goal", "floor_edge_no_near_goal",
             "whale_thin_cushion")
    out: dict = {}
    for cell in cells:
        sub = [r for r in rows if r["kind"] == cell]
        block = {"n": len(sub)}
        for who in ("model",) + EXPERTS:
            st = "model_status" if who == "model" else f"{who}_status"
            col = "model_act_dom" if who == "model" else f"{who}_{field}"
            ok = [r for r in sub if r[st] == "ok"]
            c = Counter(r[col] for r in ok)
            total = sum(c.values()) or 1
            block[who] = {"ok": len(ok),
                          "reserve_pct": round(100 * c["reserve"] / total, 1),
                          "debt_pct": round(100 * c["debt"] / total, 1),
                          "goals_pct": round(100 * c["goals+"] / total, 1)}
        out[cell] = block
    for who in ("model",) + EXPERTS:
        w = out["floor_edge_with_near_goal"][who]["reserve_pct"]
        n = out["floor_edge_no_near_goal"][who]["reserve_pct"]
        out.setdefault("h5_1_gap_reserve_pp", {})[who] = round(w - n, 1)
    return out


def defect_layer(rows: list[dict]) -> dict:
    """Слой D: кто что отклонил; отдельно кромка ПСК (вопрос В1)."""
    d = [r for r in rows if r["layer"] == "D"]
    psk = [r for r in d if r["kind"] == "near_rate_above_cap"]
    other = [r for r in d if r["kind"] != "near_rate_above_cap"]
    block = {"d_total": len(d), "psk_edge": len(psk), "other": len(other),
             "model": {"psk_invalid": sum(1 for r in psk
                                          if r["model_status"] == "invalid"),
                       "other_invalid": sum(1 for r in other
                                            if r["model_status"] == "invalid")}}
    for e in EXPERTS:
        block[e] = {
            "psk_invalid": sum(1 for r in psk if r[f"{e}_status"] == "invalid"),
            "other_invalid": sum(1 for r in other
                                 if r[f"{e}_status"] == "invalid"),
            "false_positive_on_valid": sum(
                1 for r in rows
                if r["layer"] != "D" and r[f"{e}_status"] == "invalid"),
        }
    return block


def by_confidence(rows: list[dict], field: str) -> dict:
    """Инверсия уверенности р.4: проверяем, воспроизводится ли."""
    buckets: dict[int, dict] = defaultdict(lambda: {"n": 0, "agree": 0})
    for r in rows:
        c = consensus(r, field)
        if c is None:
            continue
        confs = [int(float(r[f"{e}_confidence"])) for e in EXPERTS]
        lvl = round(statistics.mean(confs))
        b = buckets[lvl]
        b["n"] += 1
        if r["model_act_dom"] == c:
            b["agree"] += 1
    return {str(k): {"n": v["n"],
                     "agreement_pct": round(100 * v["agree"] / v["n"], 2)}
            for k, v in sorted(buckets.items()) if v["n"]}


def analyse(rows: list[dict]) -> dict:
    payable = [r for r in rows if r["model_status"] == "ok"]
    report: dict = {
        "n": len(rows),
        "status_counts": {e: dict(Counter(r[f"{e}_status"] for r in rows))
                          for e in EXPERTS},
        "model_status": dict(Counter(r["model_status"] for r in rows)),
        "monthly_dominant": agreement(payable, "dom", "model_dom"),
        "action_vector": agreement(payable, "act_dom", "model_act_dom"),
        "corridor_monthly": expert_corridor(payable, "dom"),
        "corridor_action": expert_corridor(payable, "act_dom"),
        "by_confidence": by_confidence(payable, "act_dom"),
        "defect_layer": defect_layer(rows),
        "h5": h5_cells(rows, "act_dom"),
        "profiles": profiles(rows),
    }
    by_layer, by_family = {}, {}
    for key, store in (("layer", by_layer), ("family", by_family)):
        groups: dict[str, list] = defaultdict(list)
        for r in payable:
            if r[key]:
                groups[r[key]].append(r)
        for name, sub in sorted(groups.items()):
            store[name] = agreement(sub, "act_dom", "model_act_dom")
    report["by_layer"] = by_layer
    report["by_family"] = by_family
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Разбор раунда 5")
    parser.add_argument("--joined", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    report = analyse(read(args.joined))
    payload = json.dumps(report, ensure_ascii=False, indent=1)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
