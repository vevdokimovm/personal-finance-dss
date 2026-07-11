"""Свип мат-модели: N синтетических портретов через run_planning + инварианты.

Запуск из корня репо (venv):
    python -m tools.portrait_testing.runner --n 2000 --seed 20260702 \
        --report docs/reports/testing/portrait_sweep_2026_07.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator
from tools.portrait_testing.invariants import (
    check_forecast_functions,
    check_result,
    check_static_profiles,
)

FROZEN_TODAY = datetime(2026, 7, 2, 12, 0, 0)


def run_one(portrait: dict[str, Any]) -> dict[str, Any]:
    return run_planning(
        income_total=portrait["income_total"],
        expense_total=portrait["expense_total"],
        obligations=portrait["obligations"],
        goals=portrait["goals"],
        bliq=portrait["bliq"],
        r_bench=portrait["r_bench"],
        risk_tolerance=portrait["risk_tolerance"],
        l_min=portrait["l_min"],
        today=FROZEN_TODAY,
    )


class SweepRunner:
    """Прогон N портретов с проверкой инвариантов и выборочным детерминизмом."""

    def __init__(
        self, n: int, seed: int, determinism_every: int = 50, gen_version: int = 2
    ) -> None:
        self.n = n
        self.seed = seed
        self.determinism_every = determinism_every
        self.gen_version = gen_version
        self.generator = PortraitGenerator(seed, version=gen_version)

    def run(self) -> dict[str, Any]:
        started = time.monotonic()
        violations: list[dict[str, Any]] = []
        crashes: list[dict[str, Any]] = []
        by_kind: Counter[str] = Counter()
        inv_counter: Counter[str] = Counter()

        static = check_static_profiles() + check_forecast_functions()
        for msg in static:
            inv_counter[msg.split(":", 1)[0]] += 1
            violations.append({"index": -1, "kind": "static", "msg": msg})

        for i in range(self.n):
            portrait = self.generator.generate(i)
            by_kind[portrait["kind"]] += 1
            try:
                result = run_one(portrait)
            except Exception:
                crashes.append({
                    "index": i, "kind": portrait["kind"],
                    "trace": traceback.format_exc(limit=4),
                })
                continue
            for msg in check_result(portrait, result):
                inv_counter[msg.split(":", 1)[0]] += 1
                violations.append({"index": i, "kind": portrait["kind"], "msg": msg})
            if i % self.determinism_every == 0:
                again = json.dumps(run_one(portrait), sort_keys=True, default=str)
                first = json.dumps(result, sort_keys=True, default=str)
                if again != first:
                    inv_counter["I8"] += 1
                    violations.append({
                        "index": i, "kind": portrait["kind"],
                        "msg": "I8: результат недетерминирован на повторном вызове",
                    })

        return {
            "n": self.n,
            "seed": self.seed,
            "gen_version": self.gen_version,
            "elapsed_sec": round(time.monotonic() - started, 2),
            "by_kind": dict(by_kind),
            "violations": violations,
            "violations_by_invariant": dict(inv_counter),
            "crashes": crashes,
        }


def write_report(stats: dict[str, Any], path: Path) -> None:
    ok = not stats["violations"] and not stats["crashes"]
    lines = [
        "# Портретный свип мат-модели v3.2.0 — отчёт",
        "",
        f"> Дата: 2026-07-10 · Портретов: **{stats['n']}** · seed: {stats['seed']} · "
        f"генератор: v{stats.get('gen_version', 2)} · "
        f"время: {stats['elapsed_sec']} с · Вердикт: "
        f"{'**ЧИСТО** — нарушений инвариантов нет' if ok else '**ЕСТЬ НАРУШЕНИЯ**'}",
        "",
        "Инструмент: `tools/portrait_testing/` (генератор + инварианты + раннер). "
        "Точка входа модели: `app.services.planning.run_planning` (чистая функция, "
        "время заморожено). Инварианты: I1 |A|=66/1-fail-loud · I2 счётчики · "
        "I3 жёсткие Rt'>=0, ПДН<=0.40 на допустимых · I4 суммы долей = R+ · "
        "I5 согласованность best/fail-loud · I6 веса профилей (суммы=1, нестрогая "
        "монотонность, плато 2–3) · I7 Avalanche (>= r_bench, убывание ставки) · "
        "I8 детерминизм · I9 SES + Monte-Carlo (p10<=p50<=p90, seed-детерминизм) · "
        "I10 сверка формул Lt (stock-based) и Dt · I11 конечность чисел · "
        "I12 кризисный охват (Rt<0 => план с действиями) · "
        "I13 floor-оптимальность best (стартовый месяц ликвидности) · "
        "I14 слой запаса: излишек сверх Lt*·Σe развёрнут, подушка цела (v3.2.0).",
        "",
        "## Распределение портретов по типам",
        "",
        "| Тип | Кол-во |",
        "|---|---|",
    ]
    for kind, cnt in sorted(stats["by_kind"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {kind} | {cnt} |")
    lines += ["", "## Нарушения по инвариантам", ""]
    if stats["violations_by_invariant"]:
        lines += ["| Инвариант | Кол-во |", "|---|---|"]
        for inv, cnt in sorted(stats["violations_by_invariant"].items()):
            lines.append(f"| {inv} | {cnt} |")
        lines += ["", "### Примеры (первые 10)", ""]
        for item in stats["violations"][:10]:
            lines.append(f"- портрет {item['index']} ({item['kind']}): {item['msg']}")
    else:
        lines.append("Нарушений нет.")
    lines += ["", "## Падения (crash)", ""]
    if stats["crashes"]:
        for c in stats["crashes"][:10]:
            lines.append(f"- портрет {c['index']} ({c['kind']}):")
            lines.append("```")
            lines.append(c["trace"].rstrip())
            lines.append("```")
    else:
        lines.append("Падений нет — включая граничные типы (нулевой доход/расход, "
                     "дефицитный CF, закредитованность, дешёвые долги, без целей, "
                     "профинансированная цель, огромная подушка, 8 целей).")
    lines += [
        "",
        "## Что дальше (веха 7)",
        "",
        "Свип покрывает синтетику и инварианты; веха 7 добавляет: прогон реальных "
        "эталонных портретов (6 user-cases), нагрузочное (Locust, бюджеты — `docs/slo.md`), "
        "мутационное тестирование ядра и **независимую экспертную оценку ВНЕ проекта** "
        "(правило: без памяти/инструкций, чтобы исключить bias).",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Портретный свип мат-модели")
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--gen-version", type=int, default=2, choices=(1, 2))
    args = parser.parse_args(argv)

    stats = SweepRunner(args.n, args.seed, gen_version=args.gen_version).run()
    print(json.dumps({k: v for k, v in stats.items() if k not in ("violations", "crashes")},
                     ensure_ascii=False))
    print(f"violations={len(stats['violations'])} crashes={len(stats['crashes'])}")
    if args.report:
        write_report(stats, args.report)
        print(f"report -> {args.report}")
    return 0 if not stats["violations"] and not stats["crashes"] else 1


if __name__ == "__main__":
    sys.exit(main())
