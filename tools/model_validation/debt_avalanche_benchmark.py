"""
Стенд-замер помесячного графика погашения долга (ADR-016, канон v3.8.0, §10.5).

В отличие от ADR-013/015 (замер локализации смены победителя ранжирования),
`build_debt_amortization_schedule` — чистая ПОСЛЕДующая диагностика: вызывается
после того, как ranking/crisis уже отработали, ничего не читает и не пишет
обратно в решение. «0 изменений победителя без/с графиком» была бы тавтологией
по конструкции кода (amortization.py физически не импортируется ranking.py/
crisis.py) — красная линия уже доказана архитектурно и явным тестом
tests/test_crisis.py::test_crisis_plan_unaffected_by_debt_schedule_adr_016,
не этим бенчмарком.

Реальная цель замера — **терминация и адекватность чисел** на реалистичном
распределении портретов: 0 зависаний/исключений на N портретов (симуляция
имеет цикл до MAX_HORIZON_MONTHS — риск зависания при отсутствующем/
некорректном капе — прямая угроза, не гипотетическая), распределение
months_saved/interest_saved, доля horizon_capped/negative_amortization.

Генератор — обычный PortraitGenerator.generate() (не нужен отдельный
generate_with_*, обязательства уже синтезируются _gen_obligations_v2 с
amount/interest_rate/monthly_payment). Важный факт о покрытии: генератор НЕ
кладёт term в обязательства вообще — то есть 100% синтетических долгов идут
по пути "срок неизвестен", это основной путь данных бенчмарка, не редкий угол.

Запуск: python -m tools.model_validation.debt_avalanche_benchmark [N]
"""
from __future__ import annotations

import statistics
import sys
from datetime import datetime, timezone

from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

Y = "\033[93m"
G = "\033[92m"
R = "\033[91m"
C = "\033[96m"
X = "\033[0m"

DEFAULT_N = 2000
TODAY = datetime(2026, 8, 13, tzinfo=timezone.utc)


def run(n: int) -> None:
    gen = PortraitGenerator(seed=20260813, version=2)
    print(f"{Y}→ генерирую {n} портретов (seed 20260813){X}")

    considered = 0
    qualifying = 0
    scheduled = 0
    horizon_capped = 0
    negative_amort = 0
    months_saved_vals: list[float] = []
    interest_saved_vals: list[float] = []
    exceptions = 0

    for i in range(n):
        p = gen.generate(i)
        considered += 1
        try:
            result = run_planning(
                income_total=p["income_total"],
                expense_total=p["expense_total"],
                obligations=p["obligations"],
                goals=p["goals"],
                bliq=p["bliq"],
                r_bench=p["r_bench"],
                risk_tolerance=int(p.get("risk_tolerance", 3)),
                l_min=float(p.get("l_min", 0.0)),
                today=TODAY,
            )
        except Exception as exc:  # noqa: BLE001 — стенд-замер, ловим всё, считаем и печатаем
            exceptions += 1
            print(f"  {R}✗ портрет {i}: исключение {type(exc).__name__}: {exc}{X}")
            continue

        obligations = p["obligations"]
        if any(float(o.get("interest_rate", 0)) >= p["r_bench"] for o in obligations):
            qualifying += 1

        ds = result["indicators"].get("debt_schedule")
        if ds is None:
            continue
        scheduled += 1
        if ds["horizon_capped"]:
            horizon_capped += 1
        if ds["negative_amortization"]:
            negative_amort += 1
        months_saved_vals.append(ds["months_saved"])
        interest_saved_vals.append(ds["interest_saved"])

    def pct(a: int, b: int) -> str:
        return f"{(100.0 * a / b):.2f}%" if b else "n/a"

    def q(vals: list[float], perc: float) -> float:
        if not vals:
            return 0.0
        s = sorted(vals)
        return s[min(int(perc * len(s)), len(s) - 1)]

    print(f"\n{C}=== РЕЗУЛЬТАТ: помесячный график погашения (ADR-016) ==={X}")
    print(f"  портретов: {considered}")
    print(f"  {G if exceptions == 0 else R}исключений/зависаний: {exceptions} "
          f"(ожидается 0 — терминация подтверждена){X}")
    print(f"  с хотя бы одним долгом ≥ r_bench: {qualifying} ({pct(qualifying, considered)})")
    print(f"  график посчитан (best существует и x_obl_effective > 0): {scheduled} "
          f"({pct(scheduled, considered)})")
    print(f"  {G}✓ красная линия проверена архитектурно + tests/test_crisis.py "
          f"(не этим стендом){X}")
    if months_saved_vals:
        print(f"\n  {Y}Среди посчитанных ({scheduled}):{X}")
        print(f"    months_saved: медиана {statistics.median(months_saved_vals):.0f} · "
              f"p95 {q(months_saved_vals, 0.95):.0f} · макс {max(months_saved_vals):.0f}")
        print(f"    interest_saved: медиана {statistics.median(interest_saved_vals):,.0f} ₽ · "
              f"p95 {q(interest_saved_vals, 0.95):,.0f} ₽ · "
              f"макс {max(interest_saved_vals):,.0f} ₽")
        print(f"    horizon_capped (не уложился в горизонт): {horizon_capped} "
              f"({pct(horizon_capped, scheduled)})")
        print(f"    negative_amortization (проценты не покрываются платежом): "
              f"{negative_amort} ({pct(negative_amort, scheduled)})")
    print(f"\n{G}✓ замер завершён{X}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    run(n)
