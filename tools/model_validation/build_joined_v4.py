"""Сборка joined раунда 4: модель v3.4.0 + N экспертов на датасете v4.

Контракты (наследуют раунд 3, `docs/reports/testing/round3_model_half.md` §1):
  * Сопоставление — СТРОГО ПО ПОРЯДКУ СТРОК (слой D содержит валидные дубли id);
  * enum статуса ok|deficit|invalid, доминанты debt|reserve|goals+|none;
  * бюджет: res+debt+goal+inv <= max(0, FCF)+eps для ok-строк.

Новое в раунде 4:
  * `confidence` 1-5 — обязательная колонка ответа (взвешивание консенсуса);
  * разбор `lump_sum_plan` из jsonl по НАПРАВЛЕНИЯМ: словари действий у
    экспертов разные, нормализуются `LUMP_ACTION_MAP` с fail-loud на
    неизвестном действии (молчаливый пропуск испортил бы метрику);
  * **action-vector** — свод месячного сплита и разовых ходов в один вектор
    через горизонт `ACTION_HORIZON_MONTHS`. Закрывает дефект раунда 3:
    на stock-данных сравнение по месячной доминанте частично невалидно
    (эксперт гасит долг разовым ходом, а месяц отдаёт целям — формально
    «расхождение», фактически то же действие).

Выход: knowledge/model_validation/joined_v4.csv.gz.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools.model_validation.portrait_validation import invalid_reason
from tools.portrait_testing.generator_v4 import PortraitGeneratorV4

EXPERT_STATUSES = frozenset({"ok", "deficit", "invalid"})
EXPERT_DOMS = frozenset({"debt", "reserve", "goals+", "none"})
NUM_FIELDS = ("res", "debt", "goal", "inv", "lump")
BUDGET_EPS = 1.0
CONFIDENCE_RANGE = range(1, 6)

# Горизонт свода разового хода и месячного потока в один вектор. Год —
# продуктовый горизонт плана: то, что модель распределяет за 12 месяцев,
# сопоставимо с разовым ходом того же размера.
ACTION_HORIZON_MONTHS = 12.0

DIRECTIONS = ("debt", "reserve", "goals+")
# Приоритет при точном равенстве компонент — детерминированность важнее
# «справедливости»: обе стороны метрики считаются одним правилом.
DIRECTION_PRIORITY = {"debt": 0, "reserve": 1, "goals+": 2}

# Словари разовых ходов четырёх экспертов раунда 4 + собственные типы модели
# (`app/core/surplus.py`, преаллокация целей, кризисное закрытие долгов).
LUMP_ACTION_MAP: dict[str, str] = {
    # --- долги ---
    "repay_debt": "debt",
    "close_debt": "debt",
    "partial_debt": "debt",
    "pay_toxic_debt": "debt",
    "pay_expensive_debt": "debt",
    "expensive_debt_payoff": "debt",
    "toxic_debt_payoff": "debt",
    "close_debts_from_liquidity": "debt",
    # --- цели и инвестиции (в семантике экспертизы это один бакет goals+) ---
    "close_goal": "goals+",
    "fund_goal": "goals+",
    "urgent_goal_funding": "goals+",
    "goal_prealloc": "goals+",
    "invest_surplus": "goals+",
    "invest_lump": "goals+",
    "place_excess": "goals+",
    "surplus_placement": "goals+",
    "deploy_surplus_invest": "goals+",
    "deploy_surplus_risk_free": "goals+",
    # --- резерв ---
    "top_up_reserve": "reserve",
    "fund_reserve": "reserve",
}


@dataclass
class BudgetContext:
    violations: list[tuple] = field(default_factory=list)
    invalid_shape_violations: list[tuple] = field(default_factory=list)
    lump_mismatch: list[tuple] = field(default_factory=list)


def validate_id_sequence(tag: str, got: list[str], expected: list[str]) -> None:
    if len(got) != len(expected):
        raise ValueError(f"[{tag}] строк {len(got)}, ожидалось {len(expected)}")
    for pos, (g, e) in enumerate(zip(got, expected), 1):
        if g != e:
            raise ValueError(
                f"[{tag}] порядок нарушен: строка {pos}: {g!r} != {e!r}")


def parse_confidence(tag: str, pos: int, raw: str) -> int:
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        raise ValueError(
            f"[{tag}] строка {pos}: confidence={raw!r} не число") from None
    if value not in CONFIDENCE_RANGE:
        raise ValueError(
            f"[{tag}] строка {pos}: confidence={value} вне 1..5")
    return value


def check_expert_row(tag: str, pos: int, row: dict, fcf: float | None,
                     ctx: BudgetContext) -> tuple[dict[str, float], int]:
    status = row.get("status")
    if status not in EXPERT_STATUSES:
        raise ValueError(f"[{tag}] строка {pos}: status {status!r} вне enum")
    dom = row.get("dom")
    if dom not in EXPERT_DOMS:
        raise ValueError(f"[{tag}] строка {pos}: dom {dom!r} вне enum")
    nums: dict[str, float] = {}
    for f in NUM_FIELDS:
        raw = row.get(f, "")
        try:
            nums[f] = float(raw)
        except (TypeError, ValueError):
            raise ValueError(
                f"[{tag}] строка {pos}: {f}={raw!r} не число") from None
    confidence = parse_confidence(tag, pos, row.get("confidence", ""))
    if status == "invalid":
        if dom != "none" or any(nums[f] != 0.0 for f in NUM_FIELDS):
            ctx.invalid_shape_violations.append((tag, pos, dom, dict(nums)))
    elif status == "ok" and fcf is not None:
        spent = nums["res"] + nums["debt"] + nums["goal"] + nums["inv"]
        if spent > max(0.0, fcf) + BUDGET_EPS:
            ctx.violations.append((tag, pos, round(spent, 2), round(fcf, 2)))
    return nums, confidence


def lump_by_direction(plan) -> dict[str, float]:
    """Разовые ходы -> вектор по направлениям. Неизвестное действие — ошибка.

    Тихий пропуск неизвестного ключа означал бы занижение чужого разового
    хода и перекос метрики в пользу модели — поэтому fail-loud.
    """
    out = {d: 0.0 for d in DIRECTIONS}
    for item in plan or ():
        action = item.get("action") or item.get("kind") or item.get("type")
        direction = LUMP_ACTION_MAP.get(action)
        if direction is None:
            raise ValueError(f"lump: неизвестное действие {action!r}")
        out[direction] += float(item.get("amount", 0) or 0)
    return out


def action_vector(monthly: dict[str, float],
                  lump: dict[str, float]) -> tuple[dict[str, float], str]:
    """Свод месячного плана и разовых ходов в один вектор + его доминанта."""
    vec = {d: monthly.get(d, 0.0) * ACTION_HORIZON_MONTHS + lump.get(d, 0.0)
           for d in DIRECTIONS}
    top = max(vec.values())
    if top <= 0:
        return vec, "none"
    winners = sorted((d for d in DIRECTIONS if vec[d] == top),
                     key=lambda d: DIRECTION_PRIORITY[d])
    return vec, winners[0]


def _read_expert_csv(path: Path) -> list[dict]:
    text = path.read_bytes().decode("utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def _read_jsonl(path: Path):
    """jsonl.gz экспертов; часть пакетов приходит дважды сжатой."""
    data = path.read_bytes()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    for line in io.StringIO(data.decode("utf-8")):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("__meta__"):
            continue
        yield rec


def _fcf(portrait: dict) -> float:
    payments = sum(float(o.get("monthly_payment", 0))
                   for o in portrait.get("obligations") or ())
    return (float(portrait["income_total"])
            - float(portrait["expense_total"]) - payments)


def _model_lump_vector(row: dict) -> dict[str, float]:
    """Разбор lump модели по направлениям из колонок outcomes."""
    return {
        "debt": float(row.get("model_lump_debt") or 0),
        "reserve": float(row.get("model_lump_reserve") or 0),
        "goals+": float(row.get("model_lump_goal") or 0),
    }


def build(outcomes_path: Path, experts: dict[str, Path],
          recommendations: dict[str, Path], out: Path,
          seed: int = 20260718, n: int = 12000) -> dict:
    gen = PortraitGeneratorV4(seed, n=n)
    expected_ids = [gen.expert_row(i)["id"] for i in range(n)]

    with gzip.open(outcomes_path, "rt", encoding="utf-8") as fh:
        model_rows = list(csv.DictReader(fh))
    if len(model_rows) != n:
        raise ValueError(f"outcomes: {len(model_rows)} строк, ожидалось {n}")

    expert_rows: dict[str, list[dict]] = {}
    for tag, path in experts.items():
        rows = _read_expert_csv(path)
        validate_id_sequence(tag, [r["id"] for r in rows], expected_ids)
        expert_rows[tag] = rows

    lump_vectors: dict[str, list[dict[str, float]]] = {}
    for tag, path in recommendations.items():
        vectors = [lump_by_direction(rec.get("lump_sum_plan"))
                   for rec in _read_jsonl(path)]
        if len(vectors) != n:
            raise ValueError(
                f"[{tag}] jsonl: {len(vectors)} записей, ожидалось {n}")
        lump_vectors[tag] = vectors

    ctx = BudgetContext()
    tags = sorted(experts)
    per_expert_cols = ("status", "dom", "res", "debt", "goal", "inv", "lump",
                       "confidence", "lump_debt", "lump_reserve", "lump_goal",
                       "act_dom")
    fields = (["index", "id", "layer", "kind", "family", "pair_id",
               "pair_relation", "pair_role", "model_status", "model_dom",
               "rt", "lt", "dt", "model_xo", "model_xr", "model_xg",
               "model_invest", "model_lump", "model_lump_debt",
               "model_lump_reserve", "model_lump_goal", "model_act_dom",
               "invalid_reason"]
              + [f"{t}_{c}" for t in tags for c in per_expert_cols])
    out.parent.mkdir(parents=True, exist_ok=True)
    status_counts: dict[str, dict] = {t: {} for t in tags}
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i in range(n):
            portrait = gen.generate(i)
            manifest_invalid = invalid_reason(portrait) is not None
            fcf = None if manifest_invalid else _fcf(portrait)
            mo = model_rows[i]
            m_lump = _model_lump_vector(mo)
            m_monthly = {
                "debt": float(mo["xo"] or 0),
                "reserve": float(mo["xr"] or 0),
                "goals+": float(mo["xg"] or 0) + float(mo["invest"] or 0),
            }
            _, m_act = action_vector(m_monthly, m_lump)
            rec = {
                "index": i, "id": f"SP4-{i:05d}",
                "layer": portrait["layer"], "kind": portrait["kind"],
                "family": portrait.get("family") or "",
                "pair_id": portrait.get("pair_id") or "",
                "pair_relation": portrait.get("pair_relation") or "",
                "pair_role": portrait.get("pair_role") or "",
                "model_status": mo["status"], "model_dom": mo["dom"],
                "rt": mo["rt"], "lt": mo["lt"], "dt": mo["dt"],
                "model_xo": mo["xo"], "model_xr": mo["xr"],
                "model_xg": mo["xg"], "model_invest": mo["invest"],
                "model_lump": mo.get("model_lump", ""),
                "model_lump_debt": round(m_lump["debt"], 2),
                "model_lump_reserve": round(m_lump["reserve"], 2),
                "model_lump_goal": round(m_lump["goals+"], 2),
                "model_act_dom": m_act,
                "invalid_reason": mo["invalid_reason"],
            }
            for t in tags:
                row = expert_rows[t][i]
                nums, conf = check_expert_row(t, i + 1, row, fcf=fcf, ctx=ctx)
                lv = lump_vectors[t][i]
                declared = nums["lump"]
                total = sum(lv.values())
                if abs(total - declared) > max(1.0, 0.01 * abs(declared)):
                    ctx.lump_mismatch.append(
                        (t, i + 1, round(total, 2), round(declared, 2)))
                monthly = {"debt": nums["debt"], "reserve": nums["res"],
                           "goals+": nums["goal"] + nums["inv"]}
                _, act = action_vector(monthly, lv)
                st = row["status"]
                status_counts[t][st] = status_counts[t].get(st, 0) + 1
                rec[f"{t}_status"] = st
                rec[f"{t}_dom"] = row["dom"]
                for f in NUM_FIELDS:
                    rec[f"{t}_{f}"] = nums[f]
                rec[f"{t}_confidence"] = conf
                rec[f"{t}_lump_debt"] = round(lv["debt"], 2)
                rec[f"{t}_lump_reserve"] = round(lv["reserve"], 2)
                rec[f"{t}_lump_goal"] = round(lv["goals+"], 2)
                rec[f"{t}_act_dom"] = act
            writer.writerow(rec)
    return {
        "n": n,
        "experts": tags,
        "status_counts": status_counts,
        "budget_violations": len(ctx.violations),
        "budget_examples": ctx.violations[:5],
        "invalid_shape_violations": len(ctx.invalid_shape_violations),
        "invalid_shape_examples": ctx.invalid_shape_violations[:5],
        "lump_mismatch": len(ctx.lump_mismatch),
        "lump_mismatch_examples": ctx.lump_mismatch[:5],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--expert", action="append", required=True,
                        metavar="TAG=PATH")
    parser.add_argument("--recommendations", action="append", required=True,
                        metavar="TAG=PATH")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=20260718)
    args = parser.parse_args(argv)
    experts = {}
    for spec in args.expert:
        tag, _, path = spec.partition("=")
        experts[tag] = Path(path)
    recs = {}
    for spec in args.recommendations:
        tag, _, path = spec.partition("=")
        recs[tag] = Path(path)
    stats = build(args.outcomes, experts, recs, args.out,
                  seed=args.seed, n=args.n)
    print(f"joined -> {args.out}")
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
