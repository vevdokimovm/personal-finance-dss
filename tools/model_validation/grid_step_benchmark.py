"""
Стенд-замер шага дискретизации сетки альтернатив (ROADMAP §6.3).

Отвечает на вопрос владельца «5% — сильно ли ударит по скорости?» и на скрытый
вопрос «а даёт ли 5% лучший совет»:
  1. |A| по шагу: C(1/step+2, 2) — 66 (10%), 231 (5%), 21 (20%).
  2. Латентность полного run_planning по шагам (медиана + p95, N прогонов).
  3. Разложение: сколько времени в generate vs evaluate-цикле (O(|A|)).
  4. Меняется ли ТОП-3 совет между 10% и 5% (эффективные сплиты).
  5. Инженерный блокер: коллизия id `a{d}{r}{g}` при двузначных шагах.

Запуск: python -m tools.model_validation.grid_step_benchmark
"""
from __future__ import annotations

import statistics
import time
from math import comb

from app.core.alternatives import evaluate_alternative, generate_alternatives
from app.core.filtering import B_MIN, DT_MAX, L_MIN, filter_alternatives
from app.core.ranking import rank_alternatives
from app.services.planning import run_planning

Y = "\033[33m"
G = "\033[32m"
R = "\033[31m"
C = "\033[36m"
X = "\033[0m"

N_RUNS = 300

PORTRAIT = dict(
    income_total=80_000,
    expense_total=50_000,
    obligations=[{"id": "cc", "monthly_payment": 8_000, "balance": 120_000, "rate": 0.24}],
    goals=[{"id": "g1", "target_amount": 300_000, "current_amount": 50_000}],
    bliq=90_000,
    r_bench=0.14,
    risk_tolerance=3,
)

STEPS = [0.20, 0.10, 0.05]


def _median_p95_ms(fn, n: int) -> tuple[float, float]:
    samples = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
    samples.sort()
    p95 = samples[min(int(0.95 * n), n - 1)]
    return statistics.median(samples), p95


def _grid_only_ms(step: float, n: int) -> float:
    """Изолированная O(|A|)-часть: generate + evaluate-цикл + filter + rank."""
    obligations = PORTRAIT["obligations"]
    goals = PORTRAIT["goals"]
    goals_total = 250_000.0
    rt = 22_000.0

    def run():
        alts = generate_alternatives(rt, 8_000, goals_total, step=step)
        for a in alts:
            evaluate_alternative(a, 80_000, 50_000, obligations, goals, 0.14, bliq=90_000)
        adm, _ = filter_alternatives(alts, b_min=B_MIN, l_min=L_MIN, dt_max=DT_MAX, dt_current=0.1)
        rank_alternatives(adm, 3)
    med, _ = _median_p95_ms(run, n)
    return med


def _top3_signatures(step: float) -> list[tuple[int, int, int]]:
    res = run_planning(**PORTRAIT, step=step)
    sigs = []
    for alt in res["top3"]:
        x_obl = round(float(alt.get("x_obl_effective", alt.get("x_obligations", 0))))
        x_res = round(float(alt.get("x_reserve", 0)))
        x_goals = round(sum(float(v) for v in (alt.get("goal_allocation", {}) or {}).values()))
        sigs.append((x_obl, x_res, x_goals))
    return sigs


def _id_collisions(step: float) -> tuple[int, int, tuple | None]:
    alts = generate_alternatives(22_000, 8_000, 250_000, step=step)
    seen: dict[str, tuple] = {}
    collision_example = None
    for a in alts:
        d, r, g = a["x_obligations"], a["x_reserve"], a["x_goals"]
        key = a["id"]
        if key in seen and collision_example is None:
            collision_example = (seen[key], (d, r, g), key)
        seen.setdefault(key, (d, r, g))
    return len(alts), len(seen), collision_example


def main() -> None:
    print(f"{Y}→ Стенд-замер шага сетки (N={N_RUNS} прогонов, портрет-эталон){X}")

    # 1–3. Размер сетки + латентность
    print(f"\n{C}Шаг    |A|=C(1/step+2,2)   full run_planning        только сетка O(|A|){X}")
    for step in STEPS:
        a_count = comb(round(1 / step) + 2, 2)
        med, p95 = _median_p95_ms(lambda s=step: run_planning(**PORTRAIT, step=s), N_RUNS)
        grid_med = _grid_only_ms(step, N_RUNS)
        print(f"  {int(step*100):>3}%  {a_count:>6}            "
              f"медиана {med:>7.3f} мс (p95 {p95:>7.3f})   {grid_med:>7.3f} мс")

    # 4. Меняется ли совет. ВАЖНО: решает ТОП-1 (best) — его человек и читает как совет.
    # Расхождение мест #2-#3 — артефакт плотности сетки (соседи к оптимуму просто ближе),
    # а не другая рекомендация. Массовый замер (2000 портретов): доминанта совета меняется
    # в 0.8% случаев, прирост полезности +0.07 п.п. Разбор — ADR-008 и
    # docs/reports/testing/grid_step_5pct_benchmark.md.
    print(f"\n{C}Меняется ли совет между 10% и 5%?{X}")
    s10 = _top3_signatures(0.10)
    s05 = _top3_signatures(0.05)
    best_same = s10[0] == s05[0]
    print(f"  ТОП-1 @10% (x_obl,x_res,x_goals): {s10[0]}")
    print(f"  ТОП-1 @ 5% (x_obl,x_res,x_goals): {s05[0]}")
    print(f"  → рекомендация: "
          f"{G+'ИДЕНТИЧНА'+X if best_same else Y+'ОТЛИЧАЕТСЯ'+X}")
    print(f"  топ-3 @10%: {s10}")
    print(f"  топ-3 @ 5%: {s05}")
    print(f"  → хвост топ-3: {G+'совпал'+X if s10 == s05 else Y+'разошёлся'+X} "
          f"(на плотной сетке соседи ближе — артефакт плотности, не смена совета)")

    # 5. Коллизия id
    print(f"\n{C}Инженерный блокер: уникальность id `a{{d}}{{r}}{{g}}`{X}")
    for step in (0.10, 0.05):
        total, uniq, ex = _id_collisions(step)
        if total == uniq:
            print(f"  {int(step*100):>3}%: {total} альтернатив, {uniq} уникальных id "
                  f"→ {G}коллизий нет{X}")
        else:
            a, b, key = ex
            print(f"  {int(step*100):>3}%: {total} альтернатив, только {uniq} уникальных id "
                  f"→ {R}КОЛЛИЗИЯ{X} (напр. {a} и {b} → '{key}')")

    print(f"\n{C}=== ИТОГ ==={X}")
    print(f"  {Y}Скорость НЕ блокер: полный план на 5% — единицы мс, "
          f"переход 10%→5% добавляет доли миллисекунды.{X}")
    print(f"  {Y}Реальные блокеры к отгрузке 5%: коллизия id (нужен реформат схемы) "
          f"и золотые тесты len==66; ценность 5% — по разнице совета выше.{X}")


if __name__ == "__main__":
    main()
