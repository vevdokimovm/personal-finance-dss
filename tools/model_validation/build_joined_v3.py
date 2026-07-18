"""Сборка joined раунда 3: модель v3.4.0 + N экспертов на датасете v3.

Контракты (зафиксированы в `docs/reports/testing/round3_model_half.md` §1):
  * Сопоставление — СТРОГО ПО ПОРЯДКУ СТРОК. Слой D содержит дубли id, поэтому
    ключевое сопоставление по id невозможно; бриф v3 требовал «ровно одна
    строка ответа на входную строку, в порядке входа» — здесь это проверяется
    fail-loud: последовательность id каждого эксперта обязана побайтово
    совпасть с последовательностью слепого пакета (`expert_row`).
  * Enum статуса: ok | deficit | invalid. Для invalid-строк ожидаются
    dom=none и нулевые суммы — нарушения формы копятся в контекст (отчёту),
    не валят сборку: это сигнал о дисциплине эксперта, а не о битом файле.
  * Бюджет: для ok-строк res+debt+goal+inv <= max(0, FCF) + eps; FCF считается
    из регенерированного портрета; для невалидных по манифесту записей FCF
    не определён (None) — бюджет не проверяется.

Выход: knowledge/model_validation/joined_v3.csv.gz — модельная половина
(outcomes v3.4.0) + колонки экспертов + метки координатора (layer/kind/pair_*).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools.model_validation.portrait_validation import invalid_reason
from tools.portrait_testing.generator_v3 import PortraitGeneratorV3

EXPERT_STATUSES = frozenset({"ok", "deficit", "invalid"})
EXPERT_DOMS = frozenset({"debt", "reserve", "goals+", "none"})
NUM_FIELDS = ("res", "debt", "goal", "inv", "lump")
BUDGET_EPS = 1.0


@dataclass
class BudgetContext:
    violations: list[tuple] = field(default_factory=list)
    invalid_shape_violations: list[tuple] = field(default_factory=list)


def validate_id_sequence(tag: str, got: list[str], expected: list[str]) -> None:
    if len(got) != len(expected):
        raise ValueError(
            f"[{tag}] строк {len(got)}, ожидалось {len(expected)}")
    for pos, (g, e) in enumerate(zip(got, expected), 1):
        if g != e:
            raise ValueError(
                f"[{tag}] порядок нарушен: строка {pos}: {g!r} != {e!r}")


def check_expert_row(tag: str, pos: int, row: dict,
                     fcf: float | None, ctx: BudgetContext) -> dict:
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
    if status == "invalid":
        if dom != "none" or any(nums[f] != 0.0 for f in NUM_FIELDS):
            ctx.invalid_shape_violations.append((tag, pos, dom, dict(nums)))
    elif status == "ok" and fcf is not None:
        spent = nums["res"] + nums["debt"] + nums["goal"] + nums["inv"]
        if spent > max(0.0, fcf) + BUDGET_EPS:
            ctx.violations.append((tag, pos, round(spent, 2), round(fcf, 2)))
    return nums


def _read_expert_csv(path: Path) -> list[dict]:
    text = path.read_bytes().decode("utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def _fcf(portrait: dict) -> float:
    payments = sum(float(o.get("monthly_payment", 0))
                   for o in portrait.get("obligations") or ())
    return (float(portrait["income_total"])
            - float(portrait["expense_total"]) - payments)


def build(outcomes_path: Path, experts: dict[str, Path], out: Path,
          seed: int = 20260716, n: int = 12000) -> dict:
    gen = PortraitGeneratorV3(seed, n=n)
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

    ctx = BudgetContext()
    tags = sorted(experts)
    fields = (["index", "id", "layer", "kind", "pair_id", "pair_relation",
               "pair_role", "model_status", "model_dom", "rt", "lt", "dt",
               "model_xo", "model_xr", "model_xg", "model_invest",
               "model_lump", "invalid_reason"]
              + [f"{t}_{c}" for t in tags
                 for c in ("status", "dom", "res", "debt", "goal", "inv",
                           "lump")])
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
            rec = {
                "index": i, "id": f"SP3-{i:05d}",
                "layer": portrait["layer"], "kind": portrait["kind"],
                "pair_id": portrait.get("pair_id") or "",
                "pair_relation": portrait.get("pair_relation") or "",
                "pair_role": portrait.get("pair_role") or "",
                "model_status": mo["status"], "model_dom": mo["dom"],
                "rt": mo["rt"], "lt": mo["lt"], "dt": mo["dt"],
                "model_xo": mo["xo"], "model_xr": mo["xr"],
                "model_xg": mo["xg"], "model_invest": mo["invest"],
                "model_lump": mo.get("model_lump", ""),
                "invalid_reason": mo["invalid_reason"],
            }
            for t in tags:
                row = expert_rows[t][i]
                nums = check_expert_row(t, i + 1, row, fcf=fcf, ctx=ctx)
                st = row["status"]
                status_counts[t][st] = status_counts[t].get(st, 0) + 1
                rec[f"{t}_status"] = st
                rec[f"{t}_dom"] = row["dom"]
                for f in NUM_FIELDS:
                    rec[f"{t}_{f}"] = nums[f]
            writer.writerow(rec)
    return {
        "n": n,
        "experts": tags,
        "status_counts": status_counts,
        "budget_violations": len(ctx.violations),
        "budget_examples": ctx.violations[:5],
        "invalid_shape_violations": len(ctx.invalid_shape_violations),
        "invalid_shape_examples": ctx.invalid_shape_violations[:5],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--expert", action="append", required=True,
                        metavar="TAG=PATH")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=20260716)
    args = parser.parse_args(argv)
    experts = {}
    for spec in args.expert:
        tag, _, path = spec.partition("=")
        experts[tag] = Path(path)
    stats = build(args.outcomes, experts, args.out, seed=args.seed, n=args.n)
    print(f"joined -> {args.out}")
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
