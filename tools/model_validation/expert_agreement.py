"""Валидация мат-модели против независимого экспертного консенсуса (веха 6).

Протокол (см. docs/reports/testing/independent_expert_review_2026_07.md):
  1. Портреты регенерируются детерминированно (генератор v1, seed 20260702) —
     совпадение с joined.csv доказано сверкой rt/kind/risk до копейки.
  2. Каждый портрет прогоняется через run_planning (текущий код).
  3. Доминирующее направление плана сравнивается с консенсусом >=3 из 4
     независимых экспертных движков (колонки v_/m_/j_/s_ в joined.csv).
  4. Self-check: производные модели сверяются с колонками model_* из joined.csv —
     если код не менялся, совпадение обязано быть ~100% (валидация самого стенда).

Запуск из корня репо:
    python -m tools.model_validation.expert_agreement \
        --joined knowledge/model_validation/joined.csv.gz \
        --report docs/reports/testing/expert_agreement_report.md
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.money import FLOW_EPS
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

FROZEN_TODAY = datetime(2026, 7, 2, 12, 0, 0)
EXPERTS = ("v", "m", "j", "s")
LT_SURPLUS_THRESHOLD = 6.0  # верхняя граница консервативного норматива подушки


def load_joined(path: Path) -> list[dict[str, str]]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def expert_consensus(row: dict[str, str]) -> str | None:
    """Консенсус = совпадение доминанты у >=3 из 4 экспертов (none не голосует)."""
    votes = Counter(
        row[f"{e}_dom"] for e in EXPERTS if row[f"{e}_dom"] != "none"
    )
    if not votes:
        return None
    dom, n = votes.most_common(1)[0]
    return dom if n >= 3 else None


def model_outcome(portrait: dict[str, Any],
                  today: datetime = FROZEN_TODAY) -> dict[str, Any]:
    """Прогон портрета через ядро → статус, эффективный сплит, доминанта.

    `today` — дата среза датасета (у v1/v2 это FROZEN_TODAY 2026-07-02;
    v3 передаёт собственный frozen_today генератора: дедлайны относительные).
    """
    result = run_planning(
        income_total=portrait["income_total"],
        expense_total=portrait["expense_total"],
        obligations=portrait["obligations"],
        goals=portrait["goals"],
        bliq=portrait["bliq"],
        r_bench=portrait["r_bench"],
        risk_tolerance=portrait["risk_tolerance"],
        l_min=portrait["l_min"],
        today=today,
    )
    payments = sum(float(o.get("monthly_payment", 0)) for o in portrait["obligations"])
    rt = portrait["income_total"] - portrait["expense_total"] - payments
    best = result.get("best")

    if rt < -FLOW_EPS:  # R3-F1: полкопейки не делают кризис
        status = "deficit"
    elif best is None:
        status = "no_admissible_plan"
    else:
        status = "ok"

    xo = xr = xg = invest = 0.0
    dom = "none"
    if status == "ok" and best is not None:
        xo = float(best.get("x_obl_effective", best.get("x_obligations", 0)))
        xr = float(best.get("x_reserve", 0))
        xg = sum(float(v) for v in (best.get("goal_allocation", {}) or {}).values())
        # Инвестиционный транш (v3.1.0): в семантике экспертизы бакеты «цели»
        # и «инвестиции» объединены (goals+) — транш вычитается из резерва
        tranche = best.get("investment_tranche") or {}
        invest = float(tranche.get("amount", 0))
        xr -= invest
        xg += invest
        top = max(xo, xr, xg)
        if top > 0:
            dom = "debt" if top == xo else ("reserve" if top == xr else "goals+")

    crisis = result.get("crisis_plan")
    # model_lump — разовые ходы модели из накоплений (сопоставимо с lump
    # экспертов): преаллокация близких целей + surplus-ходы (G4) + балансовый
    # ход кризисного модуля.
    prealloc = float((result.get("bliq_preallocation") or {}).get("bliq_used", 0))
    surplus = sum(float(m.get("amount", 0))
                  for m in (result.get("surplus_plan") or {}).get("moves", []))
    balance_move = 0.0
    for act in (crisis or {}).get("actions", []):
        if act.get("type") == "close_debts_from_liquidity":
            balance_move += float(act.get("bliq_used", 0))
    return {
        "model_lump": round(prealloc + surplus + balance_move, 2),
        "status": status,
        "rt": rt,
        "lt": float(result["indicators"]["Lt"]),
        "dt": float(result["indicators"]["Dt"]),
        "xo": xo,
        "xr": xr,
        "xg": xg,
        "invest": invest,
        "dom": dom,
        "dt_alert": bool(result["indicators"].get("Dt_alert", False)),
        "crisis_actions": len((crisis or {}).get("actions", [])),
        "crisis_severity": (crisis or {}).get("severity"),
    }


def run_validation(
    rows: list[dict[str, str]], seed: int = 20260702, version: int = 1
) -> dict[str, Any]:
    # Регенерация строго тем генератором, которым построен эталонный joined:
    # раунд 1 — v1 (joined.csv.gz), раунд 2 — v2 (joined_v2.csv.gz)
    gen = PortraitGenerator(seed, version=version)
    stats: dict[str, Any] = {
        "n": len(rows),
        "status": Counter(),
        "selfcheck": {"status_match": 0, "dom_match": 0, "split_match": 0, "checked": 0},
        "agreement": {"with_consensus": 0, "agree": 0, "mismatch": Counter()},
        "g1_lt6": {"n": 0, "reserve_dom": 0, "reserve_share_sum": 0.0, "flow_sum": 0.0},
        "g3_positive_flow_silence": 0,
        "g6_floor": {"n": 0, "zero_reserve": 0},
        "crisis": {"deficit_n": 0, "with_actions": 0, "severity": Counter()},
        "examples": {},
    }

    for row in rows:
        idx = int(row["id"].split("-")[1])
        portrait = gen.generate(idx)
        out = model_outcome(portrait)
        stats["status"][out["status"]] += 1

        # ── Self-check против сохранённого выхода старой модели ────────────
        sc = stats["selfcheck"]
        sc["checked"] += 1
        sc["status_match"] += out["status"] == row["model_status"]
        sc["dom_match"] += out["dom"] == row["model_dom"]
        split_ok = all(
            abs(out[k] - float(row[f"model_x{k[-1]}"])) <= 0.06
            for k in ("xo", "xr", "xg")
        )
        sc["split_match"] += split_ok

        # ── Согласие с консенсусом (только платёжеспособные) ───────────────
        if out["status"] == "ok":
            cons = expert_consensus(row)
            if cons is not None:
                stats["agreement"]["with_consensus"] += 1
                if out["dom"] == cons:
                    stats["agreement"]["agree"] += 1
                else:
                    stats["agreement"]["mismatch"][(out["dom"], cons)] += 1

            flow = out["xo"] + out["xr"] + out["xg"]
            if out["lt"] >= LT_SURPLUS_THRESHOLD and flow > 0:
                g1 = stats["g1_lt6"]
                g1["n"] += 1
                g1["reserve_dom"] += out["dom"] == "reserve"
                g1["reserve_share_sum"] += out["xr"]
                g1["flow_sum"] += flow
            if out["lt"] < 1.0:
                stats["g6_floor"]["n"] += 1
                stats["g6_floor"]["zero_reserve"] += out["xr"] == 0.0

        if out["status"] == "no_admissible_plan" and out["rt"] >= 0:
            stats["g3_positive_flow_silence"] += 1

        if out["status"] == "deficit":
            c = stats["crisis"]
            c["deficit_n"] += 1
            c["with_actions"] += out["crisis_actions"] > 0
            if out["crisis_severity"]:
                c["severity"][out["crisis_severity"]] += 1

        if row["id"] in ("SP-00002", "SP-00044", "SP-00299", "SP-00003", "SP-00237"):
            stats["examples"][row["id"]] = {
                "dom": out["dom"], "status": out["status"],
                "xo": round(out["xo"], 2), "xr": round(out["xr"], 2),
                "xg": round(out["xg"], 2),
                "crisis_actions": out["crisis_actions"],
                "crisis_severity": out["crisis_severity"],
                "consensus": expert_consensus(row),
            }

    return stats


def render_report(stats: dict[str, Any], title_suffix: str) -> str:
    sc = stats["selfcheck"]
    ag = stats["agreement"]
    g1 = stats["g1_lt6"]
    g6 = stats["g6_floor"]
    cr = stats["crisis"]
    agree_pct = ag["agree"] / ag["with_consensus"] * 100 if ag["with_consensus"] else 0.0
    buf = io.StringIO()
    w = buf.write
    w(f"# Согласие мат-модели с экспертным консенсусом — {title_suffix}\n\n")
    w(f"> Портретов: **{stats['n']}** · дата прогона: 2026-07-10 · "
      f"инструмент: `tools/model_validation/expert_agreement.py` · "
      f"эталон: `knowledge/model_validation/joined.csv.gz` (4 независимых "
      f"экспертных движка, консенсус >=3/4)\n\n")
    w("## Статусы\n\n| Статус | Кол-во |\n|---|---|\n")
    for k, v in sorted(stats["status"].items()):
        w(f"| {k} | {v} |\n")
    w("\n## Self-check стенда (регенерация против сохранённого выхода)\n\n")
    w(f"- статус совпал: {sc['status_match']}/{sc['checked']}\n")
    w(f"- доминанта совпала: {sc['dom_match']}/{sc['checked']}\n")
    w(f"- сплит (xo/xr/xg, допуск 0.06 ₽) совпал: {sc['split_match']}/{sc['checked']}\n\n")
    w("## Ключевая метрика: согласие доминирующего направления с консенсусом\n\n")
    w(f"- портретов ok с консенсусом: **{ag['with_consensus']}**\n")
    w(f"- совпадений: **{ag['agree']}** = **{agree_pct:.1f}%**\n")
    if ag["mismatch"]:
        w("\n| Модель → Консенсус | Кол-во |\n|---|---|\n")
        for (md, cd), n in ag["mismatch"].most_common(8):
            w(f"| {md} → {cd} | {n} |\n")
    w("\n## Срезы по дефектам экспертизы\n\n")
    if g1["n"]:
        share = g1["reserve_share_sum"] / g1["flow_sum"] * 100 if g1["flow_sum"] else 0
        w(f"- **G1** (ok, Lt ≥ 6 мес): {g1['n']} портретов, доминанта «резерв» у "
          f"{g1['reserve_dom']} ({g1['reserve_dom'] / g1['n'] * 100:.1f}%), "
          f"доля потока в резерв {share:.1f}%\n")
    w(f"- **G3** (пустой план при Rt ≥ 0): {stats['g3_positive_flow_silence']} портретов\n")
    if g6["n"]:
        w(f"- **G6** (ok, Lt < 1 мес): {g6['n']} портретов, из них с нулевым резервом "
          f"{g6['zero_reserve']} ({g6['zero_reserve'] / g6['n'] * 100:.1f}%)\n")
    w(f"- **G2** (кризисный охват): дефицитных {cr['deficit_n']}, "
      f"с действиями кризисного плана {cr['with_actions']}")
    if cr["severity"]:
        sev = ", ".join(f"{k}: {v}" for k, v in sorted(cr["severity"].items()))
        w(f" ({sev})")
    w("\n\n## Контрольные кейсы экспертизы\n\n")
    w("| Кейс | Статус | Доминанта | xo/xr/xg | Кризис | Консенсус |\n|---|---|---|---|---|---|\n")
    for pid, e in sorted(stats["examples"].items()):
        crisis = f"{e['crisis_actions']} действ. ({e['crisis_severity']})" \
            if e["crisis_actions"] else "—"
        w(f"| {pid} | {e['status']} | {e['dom']} | "
          f"{e['xo']:.0f}/{e['xr']:.0f}/{e['xg']:.0f} | {crisis} | {e['consensus']} |\n")
    w("\n")
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Согласие модели с экспертным консенсусом")
    parser.add_argument("--joined", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--title", type=str, default="отчёт")
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--version", type=int, default=1,
                        help="версия генератора, которым построен joined")
    args = parser.parse_args(argv)

    rows = load_joined(args.joined)
    stats = run_validation(rows, seed=args.seed, version=args.version)
    ag = stats["agreement"]
    agree_pct = ag["agree"] / ag["with_consensus"] * 100 if ag["with_consensus"] else 0.0
    print(json.dumps({
        "n": stats["n"],
        "status": dict(stats["status"]),
        "selfcheck": stats["selfcheck"],
        "agreement_pct": round(agree_pct, 1),
        "g3_silence": stats["g3_positive_flow_silence"],
        "crisis": {k: (dict(v) if isinstance(v, Counter) else v)
                   for k, v in stats["crisis"].items()},
    }, ensure_ascii=False))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(stats, args.title), encoding="utf-8")
        print(f"report -> {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
