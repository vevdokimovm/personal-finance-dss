"""Экспорт датасетов валидации: портреты и выход модели (веха 6).

Назначение — материализовать в репо сжатые датасеты, чтобы принцип
«один zip = полный контекст» работал и для данных:

  * `portraits_*.jsonl.gz` — сами портреты (вход): один JSON-объект на строку,
    id формата SP-XXXXX, даты в ISO. Эксперту для независимой оценки не нужен
    ни код, ни генератор — только этот файл.
  * `model_outcomes_*.csv.gz` — ответ модели v3.1.0 по каждому портрету:
    статус, показатели, эффективный сплит, доминанта, инвест-транш, кризис.
    Это половина будущего joined-файла второй сертификации (вторую половину —
    колонки экспертов — добавляют внешние экспертные движки).

Запуск из корня репо:
    python -m tools.model_validation.dataset_export portraits \
        --out knowledge/model_validation/portraits_v2_seed20260702.jsonl.gz \
        --n 12000 --seed 20260702 --version 2
    python -m tools.model_validation.dataset_export outcomes \
        --out knowledge/model_validation/model_outcomes_v3_1_0_on_v2.csv.gz \
        --n 12000 --seed 20260702 --version 2
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from tools.model_validation.expert_agreement import FROZEN_TODAY, model_outcome
from tools.portrait_testing.generator import PortraitGenerator


def _jsonable(node: Any) -> Any:
    if isinstance(node, (datetime, date)):
        return node.isoformat()
    if isinstance(node, dict):
        return {k: _jsonable(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_jsonable(x) for x in node]
    return node


def export_portraits(out: Path, n: int, seed: int, version: int) -> int:
    """Пишет n портретов в jsonl.gz; возвращает число записанных строк."""
    gen = PortraitGenerator(seed, version=version)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        for i in range(n):
            portrait = _jsonable(gen.generate(i))
            portrait["id"] = f"SP-{i:05d}"
            fh.write(json.dumps(portrait, ensure_ascii=False) + "\n")
            written += 1
    return written


OUTCOME_FIELDS = (
    "id", "kind", "risk", "status", "rt", "lt", "dt",
    "xo", "xr", "xg", "invest", "dom",
    "dt_alert", "crisis_severity", "crisis_actions",
)


def export_model_outcomes(out: Path, n: int, seed: int, version: int) -> int:
    """Прогоняет n портретов через run_planning и пишет выход модели в csv.gz.

    xo/xr/xg — эффективный сплит лучшего плана; invest — инвестиционный транш
    (в xg НЕ включён: колонки независимы, семантику goals+inv собирает
    потребитель). Кризисные поля — охват G2.
    """
    gen = PortraitGenerator(seed, version=version)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTCOME_FIELDS)
        writer.writeheader()
        for i in range(n):
            portrait = gen.generate(i)
            o = model_outcome(portrait)
            writer.writerow({
                "id": f"SP-{i:05d}",
                "kind": portrait["kind"],
                "risk": portrait["risk_tolerance"],
                "status": o["status"],
                "rt": round(o["rt"], 2),
                "lt": round(o["lt"], 4),
                "dt": round(o["dt"], 4),
                "xo": round(o["xo"], 2),
                "xr": round(o["xr"], 2),
                "xg": round(o["xg"] - o["invest"], 2),
                "invest": round(o["invest"], 2),
                "dom": o["dom"],
                "dt_alert": int(o["dt_alert"]),
                "crisis_severity": o["crisis_severity"] or "",
                "crisis_actions": o["crisis_actions"],
            })
            written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт датасетов валидации")
    parser.add_argument("what", choices=("portraits", "outcomes"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--version", type=int, default=2, choices=(1, 2))
    args = parser.parse_args(argv)

    fn = export_portraits if args.what == "portraits" else export_model_outcomes
    written = fn(args.out, n=args.n, seed=args.seed, version=args.version)
    print(f"{args.what}: {written} строк -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
