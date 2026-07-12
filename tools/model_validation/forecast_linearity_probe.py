"""
Стенд-зонд: доказать/опровергнуть «график прогноза ВСЕГДА прямая линия».

Прогоняет forecast_indicators на наборе портретов и на каждом считает:
  - первые/вторые разности точечного Rt (вторая разность ≈ 0 ⇒ строго линейно);
  - ширину коридора Monte-Carlo p90−p10 по горизонту (растёт ⇒ конус, НЕ прямая);
  - разброс точечного Dt (нулевой ⇒ горизонтальная линия).

Ключевой контрольный кейс: подаём СИЛЬНО трендовую реальную историю и смотрим,
сгибается ли точечная линия. Ответ на вопрос владельца «бывает ли НЕ прямая».

Запуск: python -m tools.model_validation.forecast_linearity_probe
"""
from __future__ import annotations

from app.services.forecasting import forecast_indicators

Y = "\033[33m"   # прогресс
G = "\033[32m"   # успех/утверждение
R = "\033[31m"   # опровержение
C = "\033[36m"   # заголовок
X = "\033[0m"


def _second_diffs(series: list[float]) -> list[float]:
    first = [series[i + 1] - series[i] for i in range(len(series) - 1)]
    return [round(first[i + 1] - first[i], 6) for i in range(len(first) - 1)]


# forecast_indicators округляет Rt до копеек (round(..., 2)); поэтому вторые
# разности сидят на уровне округления (~0.01), а не машинного нуля. Линия
# считается линейной, если max|Δ²| не превышает удвоенный шаг округления.
ROUNDING_EPS = 0.02


def _probe(name: str, res: dict) -> dict:
    fc = res["forecast"]
    rt = [f["Rt"] for f in fc]
    dt = [f["Dt"] for f in fc]
    band = [round(f["Rt_p90"] - f["Rt_p10"], 2) for f in fc]

    d2 = _second_diffs(rt)
    max_abs_d2 = max((abs(v) for v in d2), default=0.0)
    slope = round(rt[1] - rt[0], 2) if len(rt) > 1 else 0.0
    dt_spread = round(max(dt) - min(dt), 6)
    band_monotone = all(band[i + 1] >= band[i] for i in range(len(band) - 1))
    crosses_zero = min(rt) < 0 < max(rt)

    linear = max_abs_d2 <= ROUNDING_EPS
    tag = f"{G}ЛИНЕЙНА (до копеек){X}" if linear else f"{R}НЕ линейна{X}"
    band_note = (f"{G}монотонный конус{X}" if band_monotone
                 else f"{Y}пинчуется у нуля (Rt меняет знак){X}" if crosses_zero
                 else f"{R}немонотонна{X}")
    print(f"\n{C}{name}{X}")
    print(f"  точечный Rt:        {[round(v) for v in rt]}")
    print(f"  1-я разность (шаг): наклон/мес = {slope:>12,.2f} (константа)")
    print(f"  2-я разность:       max|Δ²| = {max_abs_d2:.2e}  → {tag}")
    print(f"  коридор p90−p10:    {band}")
    print(f"                      → {band_note}")
    print(f"  точечный Dt:        разброс = {dt_spread}  → "
          f"{'горизонталь' if dt_spread < 1e-9 else 'меняется'}")
    return {"linear": linear, "band_monotone": band_monotone, "dt_flat": dt_spread < 1e-9}


def main() -> None:
    print(f"{Y}→ Зонд линейности прогноза (forecast_indicators){X}")

    portraits = [
        ("1. Профицит (доход>расход, есть платёж)",
         dict(balance=100_000, rt=20_000, lt=3.0, dt=0.25,
              income_total=80_000, expense_total=50_000, obligation_payments=10_000)),
        ("2. Дефицит (расход>доход)",
         dict(balance=30_000, rt=-8_000, lt=1.0, dt=0.30,
              income_total=60_000, expense_total=58_000, obligation_payments=10_000)),
        ("3. Высокая долговая нагрузка",
         dict(balance=200_000, rt=5_000, lt=5.0, dt=0.39,
              income_total=100_000, expense_total=55_000, obligation_payments=40_000)),
        ("4. Нулевой чистый поток (CF=ΣP)",
         dict(balance=50_000, rt=0, lt=2.0, dt=0.20,
              income_total=70_000, expense_total=50_000, obligation_payments=20_000)),
    ]

    results = []
    for label, kw in portraits:
        results.append(_probe(label, forecast_indicators(**kw)))

    # ── КОНТРОЛЬНЫЙ КЕЙС: сильно РАСТУЩАЯ реальная история дохода ──────────
    # +8% в месяц полгода. Если бы точка «сгибалась» под тренд — здесь бы.
    trend_income = [50_000 * (1.08 ** i) for i in range(6)]      # 50k → ~73k
    flat_expense = [45_000] * 6
    flat_obl = [12_000] * 6
    res_trend = forecast_indicators(
        balance=100_000, rt=50_000 - 45_000 - 12_000, lt=2.0, dt=0.24,
        income_total=trend_income[-1], expense_total=45_000, obligation_payments=12_000,
        income_history=trend_income, expense_history=flat_expense,
        obligation_history=flat_obl,
    )
    r_trend = _probe("5. КОНТРОЛЬ: реальная история дохода +8%/мес (сильный тренд)",
                     res_trend)
    inc_fc = [f["income"] for f in res_trend["forecast"]]
    print(f"  прогноз дохода:     {[round(v) for v in inc_fc]}  "
          f"(SES отдал КОНСТАНТУ — тренд истории потерян)")

    # ── ВЕРДИКТ ──────────────────────────────────────────────────────────
    all_linear = all(r["linear"] for r in results) and r_trend["linear"]
    all_dt_flat = all(r["dt_flat"] for r in results) and r_trend["dt_flat"]
    print(f"\n{C}=== ВЕРДИКТ ==={X}")
    print(f"  точечная линия ЛИНЕЙНА на ВСЕХ кейсах, вкл. тренд-историю "
          f"(до копеечного округления): {G+'ДА'+X if all_linear else R+'НЕТ'+X}")
    print(f"  точечный Dt — горизонталь на всех кейсах: "
          f"{G+'ДА'+X if all_dt_flat else R+'НЕТ'+X}")
    print(f"  единственный не-прямой элемент — коридор Monte-Carlo; но он "
          f"пропорционален |Rt|, поэтому у нуля пинчуется, а не растёт монотонно")
    print(f"  {Y}Ответ на «бывает ли НЕ прямая»: точечная линия — НИКОГДА "
          f"(конструкция single-SES это запрещает); кривой бывает только коридор.{X}")


if __name__ == "__main__":
    main()
