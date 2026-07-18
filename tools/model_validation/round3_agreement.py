"""Анализ раунда 3 по joined_v3: согласие, слой D, burn-гипотеза, E-слой.

Печатает JSON-сводку:
  invalid_confusion — по экспертам: пойманные D (из 600), ложные срабатывания
      на валидных, разрез по kind слоя D (кто какой вид битья принял за данные);
  status_agreement — модель vs эксперт на валидных по манифесту записях;
  dom_agreement — доля совпадения доминанты модели с консенсусом >=3/4
      (валидные, model ok, консенсус существует) + по-экспертно + попарно;
  mismatch — матрица модель->консенсус + страты Lt;
  burn_hypothesis — прямой замер предзарегистрированной гипотезы р.2:
      lt_burn = bliq/(Σe+ΣP); доля расхождений в зоне lt>=2>lt_burn и
      приближённый контрфакт «floor на burn-месяцах» (floor-bound => reserve);
  expert_metamorphic — уважают ли эксперты M1-M5 (смены доминанты в парах);
  lump — профили разовых ходов экспертов.
"""
from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from tools.portrait_testing.generator_v3 import PortraitGeneratorV3

REPO = Path(__file__).resolve().parents[2]
JOINED = REPO / "knowledge/model_validation/joined_v3.csv.gz"
E = ("v", "m", "j", "s")


def consensus(row: dict) -> str | None:
    votes = Counter(row[f"{e}_dom"] for e in E if row[f"{e}_dom"] != "none")
    if not votes:
        return None
    dom, n = votes.most_common(1)[0]
    return dom if n >= 3 else None


def main() -> int:
    with gzip.open(JOINED, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    gen = PortraitGeneratorV3(seed=20260716, n=len(rows))

    burn_lt: dict[int, float] = {}
    for r in rows:
        i = int(r["index"])
        if r["layer"] == "D":
            continue
        p = gen.generate(i)
        pay = sum(float(o.get("monthly_payment", 0))
                  for o in p.get("obligations") or ())
        outflow = float(p["expense_total"]) + pay
        burn_lt[i] = float(p["bliq"]) / outflow if outflow > 0 else float("inf")

    # --- слой D: конфьюжн ---
    inv_conf: dict[str, dict] = {}
    d_rows = [r for r in rows if r["layer"] == "D"]
    valid_rows = [r for r in rows if r["layer"] != "D"]
    for e in E:
        caught = sum(1 for r in d_rows if r[f"{e}_status"] == "invalid")
        fp = [r for r in valid_rows if r[f"{e}_status"] == "invalid"]
        missed = Counter(r["kind"] for r in d_rows
                         if r[f"{e}_status"] != "invalid")
        inv_conf[e] = {
            "caught_of_600": caught,
            "false_positive_on_valid": len(fp),
            "fp_kinds": dict(Counter(r["kind"] for r in fp).most_common(4)),
            "missed_kinds": dict(missed),
        }

    # --- статусы на валидных ---
    st_agree = {}
    for e in E:
        same = sum(1 for r in valid_rows
                   if r[f"{e}_status"] == r["model_status"])
        diff = Counter((r["model_status"], r[f"{e}_status"])
                       for r in valid_rows
                       if r[f"{e}_status"] != r["model_status"])
        st_agree[e] = {"match_pct": round(100 * same / len(valid_rows), 2),
                       "diff": {f"{a}->{b}": n
                                for (a, b), n in diff.most_common(4)}}

    # --- доминанты ---
    ok_rows = [r for r in valid_rows if r["model_status"] == "ok"]
    wc = [(r, consensus(r)) for r in ok_rows]
    wc = [(r, c) for r, c in wc if c]
    agree = sum(1 for r, c in wc if r["model_dom"] == c)
    per_e = {e: round(100 * sum(1 for r in ok_rows
                                if r["model_dom"] == r[f"{e}_dom"])
                      / len(ok_rows), 1) for e in E}
    pairwise = {}
    for a in range(len(E)):
        for b in range(a + 1, len(E)):
            ea, eb = E[a], E[b]
            both = [r for r in ok_rows
                    if r[f"{ea}_dom"] != "none" and r[f"{eb}_dom"] != "none"]
            pairwise[f"{ea}~{eb}"] = round(
                100 * sum(1 for r in both
                          if r[f"{ea}_dom"] == r[f"{eb}_dom"]) / len(both), 1)

    per_layer = {}
    for layer in ("A", "B", "C", "E"):
        sub = [r for r in ok_rows if r["layer"] == layer]
        lwc = [(r, consensus(r)) for r in sub]
        lwc = [(r, c) for r, c in lwc if c]
        pw = []
        for a in range(len(E)):
            for b in range(a + 1, len(E)):
                both = [r for r in sub if r[f"{E[a]}_dom"] != "none"
                        and r[f"{E[b]}_dom"] != "none"]
                if both:
                    pw.append(100 * sum(
                        1 for r in both
                        if r[f"{E[a]}_dom"] == r[f"{E[b]}_dom"]) / len(both))
        per_layer[layer] = {
            "ok": len(sub),
            "no_consensus_pct": round(100 * (len(sub) - len(lwc)) / len(sub), 1),
            "agreement_pct": round(100 * sum(
                1 for r, c in lwc if r["model_dom"] == c) / len(lwc), 1),
            "expert_corridor": [round(min(pw), 1), round(max(pw), 1)],
        }

    mism = [(r, c) for r, c in wc if r["model_dom"] != c]
    matrix = Counter((r["model_dom"], c) for r, c in mism)
    lts = [float(r["lt"]) for r, _ in mism]

    # --- burn-гипотеза ---
    zone = [(r, c) for r, c in mism
            if c == "reserve"
            and float(r["lt"]) >= 2.0 > burn_lt[int(r["index"])]]
    cf_agree = 0
    for r, c in wc:
        dom = r["model_dom"]
        if burn_lt[int(r["index"])] < 2.0 and float(r["rt"]) > 0:
            dom = "reserve"  # приближение: floor на burn-месяцах связывает выбор
        cf_agree += dom == c
    burn = {
        "mismatches_to_reserve": sum(1 for _, c in mism if c == "reserve"),
        "of_them_lt_ge2_but_burn_lt2": len(zone),
        "counterfactual_floor_on_burn_agreement_pct":
            round(100 * cf_agree / len(wc), 1),
        "note": "контрфакт приближённый (floor-bound => reserve); "
                "точная цифра требует полного перегона модели",
    }

    # --- E-слой: метаморфика экспертов ---
    pairs: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        if r["layer"] == "E":
            pairs[r["pair_id"]][r["pair_role"]] = r
    emeta: dict[str, dict] = {}
    for pid, pr in pairs.items():
        if set(pr) != {"base", "twin"}:
            continue
        rel = pr["base"]["pair_relation"]
        slot = emeta.setdefault(rel, {e: 0 for e in E} | {"pairs": 0})
        slot["pairs"] += 1
        for e in E:
            b, t = pr["base"], pr["twin"]
            if (b[f"{e}_status"] == t[f"{e}_status"] == "ok"
                    and b[f"{e}_dom"] != t[f"{e}_dom"]):
                slot[e] += 1

    # --- lump: модель против экспертов ---
    ml = [float(r.get("model_lump") or 0) for r in valid_rows]
    nzm = [v for v in ml if v > 0]
    dg = [(r, c) for r, c in wc if c == "goals+" and r["model_dom"] == "debt"]
    dg_model_covers = 0
    for r, _ in dg:
        p = gen.generate(int(r["index"]))
        debt_total = sum(float(o.get("amount", 0))
                         for o in p.get("obligations") or ())
        if float(r.get("model_lump") or 0) >= debt_total > 0:
            dg_model_covers += 1
    lump = {"model": {
        "share_pct": round(100 * len(nzm) / len(valid_rows), 1),
        "median": round(statistics.median(nzm)) if nzm else 0,
        "debt_to_goals_covered_by_model_lump":
            f"{dg_model_covers}/{len(dg)}",
    }}
    for e in E:
        vals = [float(r[f"{e}_lump"]) for r in valid_rows]
        nz = [v for v in vals if v > 0]
        lump[e] = {
            "share_pct": round(100 * len(nz) / len(vals), 1),
            "median": round(statistics.median(nz)) if nz else 0,
            "in_deficit": sum(1 for r in valid_rows
                              if r[f"{e}_status"] == "deficit"
                              and float(r[f"{e}_lump"]) > 0),
        }

    out = {
        "invalid_confusion": inv_conf,
        "status_agreement_on_valid": st_agree,
        "dom": {
            "ok_with_consensus": len(wc),
            "no_consensus": len(ok_rows) - len(wc),
            "agreement_pct": round(100 * agree / len(wc), 1),
            "per_expert_pct": per_e,
            "pairwise_pct": pairwise,
        },
        "per_layer": per_layer,
        "mismatch": {
            "matrix": {f"{a}->{b}": n for (a, b), n in matrix.most_common(8)},
            "lt_median": round(statistics.median(lts), 2) if lts else None,
            "n": len(mism),
        },
        "burn_hypothesis": burn,
        "expert_metamorphic_dom_flips": emeta,
        "lump": lump,
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
