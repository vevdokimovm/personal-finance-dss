"""Анализ раунда 4 по joined_v4: согласие месячное и по action-vector,
взвешивание по confidence, слой D, предзарегистрированная гипотеза
токсичного долга, E-слой.

Главное отличие от раунда 3: доминанта считается ДВАЖДЫ —
  * `dom` — по месячному сплиту (как в р.1-3, сравнимость истории);
  * `act_dom` — по action-vector (месяц x 12 + разовые ходы), который
    закрывает дефект «на stock-данных месячная доминанта частично невалидна».

Печатает JSON-сводку.
"""
from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from tools.portrait_testing.generator_v4 import PortraitGeneratorV4

REPO = Path(__file__).resolve().parents[2]
JOINED = REPO / "knowledge/model_validation/joined_v4.csv.gz"
E = ("v", "m", "j", "s")
SEED = 20260718

# Предзарегистрированная гипотеза раунда 4 (WATCHLOG v6.15.0, не внедрена):
# долг считается токсичным, если ставка >= max(30%, r_bench + 15 п.п.).
TOXIC_ABS = 0.30
TOXIC_SPREAD = 0.15


def consensus(row: dict, field: str = "dom") -> str | None:
    votes = Counter(row[f"{e}_{field}"] for e in E
                    if row[f"{e}_{field}"] != "none")
    if not votes:
        return None
    dom, n = votes.most_common(1)[0]
    return dom if n >= 3 else None


def _agreement_block(rows: list[dict], field: str, model_field: str) -> dict:
    wc = [(r, consensus(r, field)) for r in rows]
    wc = [(r, c) for r, c in wc if c]
    agree = sum(1 for r, c in wc if r[model_field] == c)
    per_e = {e: round(100 * sum(1 for r in rows
                                if r[model_field] == r[f"{e}_{field}"])
                      / len(rows), 1) for e in E}
    pairwise = {}
    for a in range(len(E)):
        for b in range(a + 1, len(E)):
            ea, eb = E[a], E[b]
            both = [r for r in rows if r[f"{ea}_{field}"] != "none"
                    and r[f"{eb}_{field}"] != "none"]
            pairwise[f"{ea}~{eb}"] = round(
                100 * sum(1 for r in both
                          if r[f"{ea}_{field}"] == r[f"{eb}_{field}"])
                / len(both), 1) if both else None
    mism = [(r, c) for r, c in wc if r[model_field] != c]
    matrix = Counter((r[model_field], c) for r, c in mism)
    return {
        "ok_with_consensus": len(wc),
        "no_consensus": len(rows) - len(wc),
        "agreement_pct": round(100 * agree / len(wc), 1) if wc else None,
        "per_expert_pct": per_e,
        "pairwise_pct": pairwise,
        "mismatch_matrix": {f"{a}->{b}": n for (a, b), n in
                            matrix.most_common(8)},
        "mismatch_n": len(mism),
    }


def _toxic_profile(portrait: dict) -> dict:
    """Токсичный долг по предзарегистрированному правилу + запас burn."""
    r_bench = float(portrait.get("r_bench") or 0)
    threshold = max(TOXIC_ABS, r_bench + TOXIC_SPREAD)
    obligations = portrait.get("obligations") or ()
    toxic = [o for o in obligations
             if float(o.get("interest_rate") or 0) >= threshold
             and float(o.get("amount") or 0) > 0]
    payments = sum(float(o.get("monthly_payment", 0)) for o in obligations)
    outflow = float(portrait["expense_total"]) + payments
    burn = float(portrait["bliq"]) / outflow if outflow > 0 else float("inf")
    return {
        "has_toxic": bool(toxic),
        "toxic_amount": sum(float(o["amount"]) for o in toxic),
        "toxic_max_rate": max((float(o["interest_rate"]) for o in toxic),
                              default=0.0),
        "burn_lt": burn,
    }


def main() -> int:
    with gzip.open(JOINED, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    gen = PortraitGeneratorV4(seed=SEED, n=len(rows))

    d_rows = [r for r in rows if r["layer"] == "D"]
    valid_rows = [r for r in rows if r["layer"] != "D"]
    ok_rows = [r for r in valid_rows if r["model_status"] == "ok"]

    # --- слой D ---
    inv_conf = {}
    for e in E:
        caught = sum(1 for r in d_rows if r[f"{e}_status"] == "invalid")
        fp = [r for r in valid_rows if r[f"{e}_status"] == "invalid"]
        missed = Counter(r["kind"] for r in d_rows
                         if r[f"{e}_status"] != "invalid")
        inv_conf[e] = {"caught_of_600": caught,
                       "false_positive_on_valid": len(fp),
                       "missed_kinds": dict(missed)}

    # --- статусы ---
    st_agree = {}
    for e in E:
        same = sum(1 for r in valid_rows
                   if r[f"{e}_status"] == r["model_status"])
        diff = Counter((r["model_status"], r[f"{e}_status"])
                       for r in valid_rows
                       if r[f"{e}_status"] != r["model_status"])
        st_agree[e] = {"match_pct": round(100 * same / len(valid_rows), 2),
                       "diff": {f"{a}->{b}": n for (a, b), n
                                in diff.most_common(3)}}

    monthly = _agreement_block(ok_rows, "dom", "model_dom")
    action = _agreement_block(ok_rows, "act_dom", "model_act_dom")

    # --- по слоям (action-vector) ---
    per_layer = {}
    for layer in ("A", "B", "C", "E"):
        sub = [r for r in ok_rows if r["layer"] == layer]
        if sub:
            per_layer[layer] = {
                "ok": len(sub),
                "monthly_pct": _agreement_block(sub, "dom",
                                                "model_dom")["agreement_pct"],
                "action_pct": _agreement_block(
                    sub, "act_dom", "model_act_dom")["agreement_pct"],
            }

    # --- confidence: где эксперты не уверены, там ли они расходятся? ---
    conf_bands: dict[str, dict] = {}
    for r in ok_rows:
        confs = [int(r[f"{e}_confidence"]) for e in E]
        band = str(round(statistics.mean(confs)))
        slot = conf_bands.setdefault(band, {"n": 0, "unanimous": 0,
                                            "model_agrees": 0,
                                            "has_consensus": 0})
        slot["n"] += 1
        doms = {r[f"{e}_act_dom"] for e in E}
        if len(doms) == 1:
            slot["unanimous"] += 1
        c = consensus(r, "act_dom")
        if c:
            slot["has_consensus"] += 1
            slot["model_agrees"] += r["model_act_dom"] == c
    for slot in conf_bands.values():
        slot["unanimous_pct"] = round(100 * slot["unanimous"] / slot["n"], 1)
        slot["model_agreement_pct"] = (
            round(100 * slot["model_agrees"] / slot["has_consensus"], 1)
            if slot["has_consensus"] else None)

    # взвешенный по уверенности консенсус
    weighted_agree = weighted_total = 0.0
    for r in ok_rows:
        votes: dict[str, float] = defaultdict(float)
        for e in E:
            dom = r[f"{e}_act_dom"]
            if dom != "none":
                votes[dom] += int(r[f"{e}_confidence"])
        if not votes:
            continue
        top = max(votes.values())
        winners = [d for d, v in votes.items() if v == top]
        weighted_total += 1
        weighted_agree += len(winners) == 1 and r["model_act_dom"] == winners[0]

    # --- предзарегистрированная гипотеза: токсичный долг пробивает floor ---
    tox = {"mismatch_reserve_to_debt": 0, "of_them_toxic": 0,
           "toxic_rows_total": 0, "toxic_model_reserve": 0}
    cf_agree = cf_total = 0
    for r in ok_rows:
        c = consensus(r, "act_dom")
        if not c:
            continue
        prof = _toxic_profile(gen.generate(int(r["index"])))
        cf_total += 1
        dom = r["model_act_dom"]
        # контрфакт: при токсичном долге floor опускается до ~1 burn-месяца,
        # высвобожденный поток идёт в долг
        if prof["has_toxic"] and prof["burn_lt"] >= 1.0 and dom == "reserve":
            dom = "debt"
        cf_agree += dom == c
        if prof["has_toxic"]:
            tox["toxic_rows_total"] += 1
            if r["model_act_dom"] == "reserve":
                tox["toxic_model_reserve"] += 1
        if r["model_act_dom"] == "reserve" and c == "debt":
            tox["mismatch_reserve_to_debt"] += 1
            tox["of_them_toxic"] += prof["has_toxic"]
    tox["counterfactual_agreement_pct"] = round(100 * cf_agree / cf_total, 1)
    tox["baseline_agreement_pct"] = action["agreement_pct"]

    # --- E-слой: метаморфика ---
    pairs: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        if r["layer"] == "E":
            pairs[r["pair_id"]][r["pair_role"]] = r
    emeta: dict[str, dict] = {}
    for pr in pairs.values():
        if set(pr) != {"base", "twin"}:
            continue
        rel = pr["base"]["pair_relation"]
        slot = emeta.setdefault(rel, {e: 0 for e in E}
                                | {"pairs": 0, "model": 0})
        slot["pairs"] += 1
        b, t = pr["base"], pr["twin"]
        if (b["model_status"] == t["model_status"] == "ok"
                and b["model_act_dom"] != t["model_act_dom"]):
            slot["model"] += 1
        for e in E:
            if (b[f"{e}_status"] == t[f"{e}_status"] == "ok"
                    and b[f"{e}_act_dom"] != t[f"{e}_act_dom"]):
                slot[e] += 1

    # --- lump-профили ---
    lump = {}
    for tag, prefix in [("model", "model_")] + [(e, f"{e}_") for e in E]:
        vals = [sum(float(r[f"{prefix}lump_{k}"])
                    for k in ("debt", "reserve", "goal")) for r in valid_rows]
        nz = [v for v in vals if v > 0]
        by_dir = {k: sum(float(r[f"{prefix}lump_{k}"]) for r in valid_rows)
                  for k in ("debt", "reserve", "goal")}
        total = sum(by_dir.values()) or 1
        lump[tag] = {
            "share_pct": round(100 * len(nz) / len(vals), 1),
            "median": round(statistics.median(nz)) if nz else 0,
            "direction_mix_pct": {k: round(100 * v / total, 1)
                                  for k, v in by_dir.items()},
        }

    out = {
        "invalid_confusion": inv_conf,
        "status_agreement_on_valid": st_agree,
        "dom_monthly": monthly,
        "dom_action_vector": action,
        "per_layer_action": per_layer,
        "confidence_bands": conf_bands,
        "confidence_weighted_agreement_pct":
            round(100 * weighted_agree / weighted_total, 1),
        "toxic_debt_hypothesis": tox,
        "expert_metamorphic_act_flips": emeta,
        "lump": lump,
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
