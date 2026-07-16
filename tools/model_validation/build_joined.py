"""Сборка joined-файла сертификации: выход модели + CSV четырёх экспертов.

Вход:
  * `model_outcomes_*.csv.gz` — ответ модели (см. `dataset_export.py`);
  * четыре экспертных CSV формата брифа `id,status,dom,res,debt,goal,inv,lump`
    (`docs/model/expert_brief_v2.md`), кодировка UTF-8, LF или CRLF.

Выход — `joined_v2.csv.gz`: одна строка = один портрет, модельная половина
(`model_*` + диагностика) и колонки экспертов `{v,m,j,s}_*`. Семантика стенда
(`expert_agreement.py`): `model_xg` в joined ВКЛЮЧАЕТ инвест-транш (goals+),
`model_invest` хранится отдельно; у экспертов goals+ = goal + inv.

Принципы: структурные дефекты (дырки/дубли id, кривые enum, нечисла) —
ValueError, сборка невозможна; нарушения бюджета экспертами — считаем и
отдаём в сводке, но НЕ чиним (это находка сертификации, не ошибка сборки).

Запуск из корня репо:
    python -m tools.model_validation.build_joined \
        --outcomes knowledge/model_validation/model_outcomes_v3_3_0_on_v2.csv.gz \
        --expert v=path/to/v.csv --expert m=... --expert j=... --expert s=... \
        --portraits knowledge/model_validation/portraits_v2_seed20260702.jsonl.gz \
        --out knowledge/model_validation/joined_v2.csv.gz
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXPERT_TAGS = ("v", "m", "j", "s")
EXPERT_COLS = ("status", "dom", "res", "debt", "goal", "inv", "lump")
VALID_STATUS = {"ok", "deficit"}
VALID_DOM = {"debt", "reserve", "goals+", "none"}
MODEL_FIELDS = (
    "id", "kind", "risk", "model_status", "rt", "lt", "dt",
    "model_xo", "model_xr", "model_xg", "model_invest", "model_dom",
    "dt_alert", "crisis_severity", "crisis_actions",
)


@dataclass
class BudgetContext:
    """Свободный поток по id — для контроля res+debt+goal+inv <= поток."""

    flow_by_id: dict[str, float]
    tolerance: float = 1.0
    violations: dict[str, int] = field(default_factory=dict)

    def check(self, tag: str, pid: str, spent: float) -> None:
        flow = self.flow_by_id.get(pid)
        if flow is None:
            return
        if spent > max(flow, 0.0) + self.tolerance:
            self.violations[tag] = self.violations.get(tag, 0) + 1


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return open(path, "rt", encoding="utf-8", newline="")


def load_expert_csv(path: Path, tag: str) -> dict[str, dict[str, str]]:
    """Читает экспертный CSV, валидирует структуру, возвращает {id: строка}."""
    rows: dict[str, dict[str, str]] = {}
    with _open_text(path) as fh:
        reader = csv.DictReader(fh)
        expected = ["id", *EXPERT_COLS]
        if reader.fieldnames is None or [f.strip() for f in reader.fieldnames] != expected:
            raise ValueError(f"эксперт {tag}: шапка {reader.fieldnames} != {expected}")
        for line_no, row in enumerate(reader, start=2):
            pid = (row["id"] or "").strip()
            if pid in rows:
                raise ValueError(f"эксперт {tag}: дубль id {pid} (строка {line_no})")
            status = row["status"].strip()
            if status not in VALID_STATUS:
                raise ValueError(f"эксперт {tag}: status={status!r} у {pid}")
            dom = row["dom"].strip()
            if dom not in VALID_DOM:
                raise ValueError(f"эксперт {tag}: dom={dom!r} у {pid}")
            clean = {"status": status, "dom": dom}
            for col in ("res", "debt", "goal", "inv", "lump"):
                raw = row[col].strip()
                try:
                    val = float(raw)
                except ValueError as exc:
                    raise ValueError(f"эксперт {tag}: {col}={raw!r} у {pid}") from exc
                if val < 0:
                    raise ValueError(f"эксперт {tag}: {col}<0 у {pid}")
                clean[col] = raw
            rows[pid] = clean
    return rows


def load_flow_by_id(portraits_path: Path) -> dict[str, float]:
    """Свободный поток из jsonl-портретов: income - expense - Σ платежей."""
    flows: dict[str, float] = {}
    with gzip.open(portraits_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            payments = sum(float(o.get("monthly_payment", 0)) for o in p["obligations"])
            flows[p["id"]] = float(p["income_total"]) - float(p["expense_total"]) - payments
    return flows


def build_joined(
    outcomes_path: Path,
    expert_paths: dict[str, Path],
    out_path: Path,
    budget: BudgetContext | None = None,
) -> dict:
    """Собирает joined CSV; возвращает сводку (строки, нарушения бюджета)."""
    if sorted(expert_paths) != sorted(EXPERT_TAGS):
        raise ValueError(f"нужны эксперты {EXPERT_TAGS}, получены {sorted(expert_paths)}")
    experts = {tag: load_expert_csv(path, tag) for tag, path in expert_paths.items()}

    with gzip.open(outcomes_path, "rt", encoding="utf-8", newline="") as fh:
        model_rows = list(csv.DictReader(fh))
    model_ids = [r["id"] for r in model_rows]
    if len(set(model_ids)) != len(model_ids):
        raise ValueError("outcomes: дубли id")
    for tag, rows in experts.items():
        missing = set(model_ids) - set(rows)
        extra = set(rows) - set(model_ids)
        if missing or extra:
            raise ValueError(
                f"эксперт {tag}: покрытие id не сходится "
                f"(нет {len(missing)}, лишних {len(extra)})"
            )

    fields = list(MODEL_FIELDS) + [
        f"{tag}_{col}" for tag in EXPERT_TAGS for col in EXPERT_COLS
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out_path, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for m in model_rows:
            xg_plus = float(m["xg"]) + float(m["invest"])
            row = {
                "id": m["id"], "kind": m["kind"], "risk": m["risk"],
                "model_status": m["status"], "rt": m["rt"], "lt": m["lt"], "dt": m["dt"],
                "model_xo": m["xo"], "model_xr": m["xr"],
                "model_xg": f"{xg_plus:.2f}", "model_invest": m["invest"],
                "model_dom": m["dom"], "dt_alert": m["dt_alert"],
                "crisis_severity": m["crisis_severity"],
                "crisis_actions": m["crisis_actions"],
            }
            for tag in EXPERT_TAGS:
                e = experts[tag][m["id"]]
                for col in EXPERT_COLS:
                    row[f"{tag}_{col}"] = e[col]
                if budget is not None:
                    spent = sum(float(e[c]) for c in ("res", "debt", "goal", "inv"))
                    budget.check(tag, m["id"], spent)
            writer.writerow(row)
            written += 1

    return {
        "rows": written,
        "budget_violations": dict(budget.violations) if budget else {},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Сборка joined-файла сертификации")
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--expert", action="append", required=True,
                        metavar="TAG=PATH", help="v=..., m=..., j=..., s=...")
    parser.add_argument("--portraits", type=Path, default=None,
                        help="jsonl.gz портретов для контроля бюджета")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    expert_paths: dict[str, Path] = {}
    for item in args.expert:
        tag, _, raw = item.partition("=")
        expert_paths[tag.strip()] = Path(raw.strip())

    budget = None
    if args.portraits is not None:
        budget = BudgetContext(load_flow_by_id(args.portraits))

    summary = build_joined(args.outcomes, expert_paths, args.out, budget=budget)
    print(json.dumps(summary, ensure_ascii=False))
    print(f"joined -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
