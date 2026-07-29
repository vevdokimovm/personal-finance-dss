"""Профили четырёх экспертов сквозь все пять итераций.

Зачем инструмент. В итерации 1 разбор сравнения экспертов между собой был
сделан вручную и оказался самым информативным артефактом раунда: он показал,
что четыре методологии сходятся между собой в узком коридоре, а модель —
статистический аутлайер. В раундах 2-4 практика не повторялась, и знание о том,
КАК устроен каждый эксперт, накапливалось только в прозе отчётов. Инструмент
восстанавливает практику и делает её воспроизводимой на всех пяти раундах.

Считается только по общему знаменателю схем (месячная доминанта, статусы,
бакеты, lump) — единственному набору колонок, который есть во всех пяти
`joined*`. Action-vector есть лишь в раундах 4-5 и считается отдельно, где есть.

Запуск из корня репо:
    python -m tools.model_validation.expert_profiles_cross \
        --json docs/model/expert_certification/expert_profiles_cross.json
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KNOW = REPO / "knowledge/model_validation"
EXPERTS = ("v", "m", "j", "s")
ROUNDS = {
    "r1_v1": KNOW / "joined.csv.gz",
    "r2_v2": KNOW / "joined_v2.csv.gz",
    "r3_v3": KNOW / "joined_v3.csv.gz",
    "r4_v4": KNOW / "joined_v4.csv.gz",
    "r5_v5": KNOW / "joined_v5.csv.gz",
}


def read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def num(row: dict, key: str) -> float:
    raw = row.get(key)
    try:
        return float(raw) if raw not in ("", None) else 0.0
    except ValueError:
        return 0.0


def profile_one(rows: list[dict], tag: str) -> dict:
    """Профиль одного участника: доминанты, доли бакетов, режим разовых ходов."""
    is_model = tag == "model"
    st = "model_status" if is_model else f"{tag}_status"
    dom = "model_dom" if is_model else f"{tag}_dom"
    ok = [r for r in rows if r.get(st) == "ok"]
    if is_model:
        cols = {"debt": ("model_xo",), "reserve": ("model_xr",),
                "goals+": ("model_xg", "model_invest")}
        lump_col = "model_lump"
    else:
        cols = {"debt": (f"{tag}_debt",), "reserve": (f"{tag}_res",),
                "goals+": (f"{tag}_goal", f"{tag}_inv")}
        lump_col = f"{tag}_lump"
    money = {d: sum(num(r, c) for r in rows for c in cs)
             for d, cs in cols.items()}
    total = sum(money.values()) or 1.0
    lumps = sorted(x for x in (num(r, lump_col) for r in rows) if x > 0)
    # доминанты считаются по строкам с непустым направлением, а не по
    # статусу: словарь статусов раунда 1 отличался от последующих, и фильтр
    # по "ok" молча обнулял бы весь профиль первой итерации.
    advised = [r for r in rows if r.get(dom) not in ("", "none", None)]
    doms = Counter(r.get(dom) for r in advised)
    n_ok = len(advised) or 1
    return {
        "ok": len(ok),
        "advised": len(advised),
        "status": dict(Counter(r.get(st) for r in rows)),
        "dom_share_pct": {d: round(100 * doms.get(d, 0) / n_ok, 1)
                          for d in ("debt", "reserve", "goals+", "none")},
        "money_share_pct": {d: round(100 * money[d] / total, 1)
                            for d in ("debt", "reserve", "goals+")},
        "lump_share_pct": round(100 * len(lumps) / len(rows), 1),
        "lump_median": round(lumps[len(lumps) // 2], 2) if lumps else 0.0,
    }


def corridor(rows: list[dict], field: str = "dom") -> dict:
    """Два взгляда на согласие экспертов и позиция модели между ними."""
    present = [e for e in EXPERTS if f"{e}_{field}" in (rows[0] if rows else {})]
    ok = [r for r in rows if r.get("model_status") == "ok"]
    pairwise = {}
    for a, b in combinations(present, 2):
        both = [r for r in ok
                if r[f"{a}_{field}"] not in ("", "none")
                and r[f"{b}_{field}"] not in ("", "none")]
        if both:
            same = sum(1 for r in both
                       if r[f"{a}_{field}"] == r[f"{b}_{field}"])
            pairwise[f"{a}-{b}"] = round(100 * same / len(both), 2)
    trio = {}
    for e in present:
        others = [x for x in present if x != e]
        hits = tot = 0
        for r in ok:
            votes = Counter(r[f"{o}_{field}"] for o in others
                            if r[f"{o}_{field}"] not in ("", "none"))
            if not votes:
                continue
            top, n = votes.most_common(1)[0]
            if n < len(others):
                continue
            tot += 1
            hits += r[f"{e}_{field}"] == top
        trio[e] = round(100 * hits / tot, 2) if tot else None
    model_field = "model_dom" if field == "dom" else "model_act_dom"
    hits = tot = 0
    for r in ok:
        votes = Counter(r[f"{e}_{field}"] for e in present
                        if r[f"{e}_{field}"] not in ("", "none"))
        if not votes:
            continue
        top, n = votes.most_common(1)[0]
        if n < 3:
            continue
        tot += 1
        hits += r.get(model_field) == top
    vals = list(pairwise.values())
    trio_vals = [v for v in trio.values() if v is not None]
    return {
        "pairwise": pairwise,
        "pairwise_range": [min(vals), max(vals)] if vals else None,
        "vs_unanimous_trio": trio,
        "trio_range": [min(trio_vals), max(trio_vals)] if trio_vals else None,
        "model_vs_consensus_pct": round(100 * hits / tot, 2) if tot else None,
        "model_rows_with_consensus": tot,
    }


def analyse(paths: dict[str, Path]) -> dict:
    out: dict = {}
    for name, path in paths.items():
        if not path.exists():
            out[name] = {"missing": str(path)}
            continue
        rows = read(path)
        block = {
            "n": len(rows),
            "profiles": {t: profile_one(rows, t)
                         for t in ("model",) + EXPERTS
                         if t == "model" or f"{t}_status" in rows[0]},
            "corridor_monthly": corridor(rows, "dom"),
        }
        if rows and "v_act_dom" in rows[0]:
            block["corridor_action"] = corridor(rows, "act_dom")
        out[name] = block
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Профили экспертов по раундам")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    report = analyse(ROUNDS)
    payload = json.dumps(report, ensure_ascii=False, indent=1)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
