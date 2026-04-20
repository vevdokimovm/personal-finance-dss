"""
Модуль планирования СППР — генерация, фильтрация и ранжирование
альтернатив распределения свободного ресурса Rt.

Реализует этапы 4–6 алгоритма из ВКР:
  4. Генерация альтернатив  →  A = {a₁, ..., aₙ}
  5. Фильтрация по ограничениям  →  A_доп ⊆ A
  6. Ранжирование по функции полезности  →  a* = argmax U(a)

Каждая альтернатива — вектор распределения:
  a_j = (x_обязат, x_резерв, x_цели)
  при: x_обязат + x_резерв + x_цели ≤ Rt
"""
from __future__ import annotations

from typing import Any


# ── Пороговые значения ───────────────────────────────────────
# Lt = Rt / (Расходы + Обязательства) — по формуле ВКР (табл.17)
# В тестовых сценариях ВКР Lt лежит в диапазоне 0.09–0.89,
# поэтому LT_CRIT = 0.0 (содержательный контроль — через B_MIN ≥ 0).

DT_MAX = 0.40        # максимально допустимая долговая нагрузка
LT_CRIT = 0.0        # минимально допустимая ликвидность (Lt ≥ 0)
LT_TARGET = 1.5      # целевой уровень ликвидности (для отображения)
B_MIN = 0.0          # минимально допустимый свободный ресурс


# ── Весовые коэффициенты функции полезности ───────────────────
# U(a) = w₁·Rt_norm + w₂·Lt_norm + w₃·Dt_norm + w₄·Goals_norm
# Веса по умолчанию — сбалансированная стратегия

DEFAULT_WEIGHTS = {
    "w_rt": 0.25,      # финансовая гибкость (доступный ресурс)
    "w_lt": 0.30,      # устойчивость (ликвидность)
    "w_dt": 0.25,      # финансовый риск (долговая нагрузка)
    "w_goals": 0.20,   # достижение целей
}

# Профили риска → веса
RISK_PROFILES = {
    1: {"w_rt": 0.15, "w_lt": 0.40, "w_dt": 0.35, "w_goals": 0.10, "label": "Консервативный"},
    2: {"w_rt": 0.20, "w_lt": 0.35, "w_dt": 0.30, "w_goals": 0.15, "label": "Умеренно-консервативный"},
    3: {"w_rt": 0.25, "w_lt": 0.30, "w_dt": 0.25, "w_goals": 0.20, "label": "Сбалансированный"},
    4: {"w_rt": 0.30, "w_lt": 0.20, "w_dt": 0.20, "w_goals": 0.30, "label": "Умеренно-агрессивный"},
    5: {"w_rt": 0.30, "w_lt": 0.15, "w_dt": 0.15, "w_goals": 0.40, "label": "Агрессивный"},
}


def _alt_name(d: int, r: int, g: int, steps: int) -> str:
    """Генерирует читаемое название альтернативы по долям (d, r, g)."""
    pct = lambda x: int(round(x / steps * 100))
    pd, pr, pg = pct(d), pct(r), pct(g)
    dominant = max((d, "обязательства"), (r, "резерв"), (g, "цели"), key=lambda x: x[0])
    if d == steps:
        return "Всё на погашение долга"
    if r == steps:
        return "Всё в резерв"
    if g == steps:
        return "Всё на цели"
    if dominant[0] / steps >= 0.6:
        return f"Акцент: {dominant[1]} ({pd}/{pr}/{pg})"
    if d == r == g:
        return f"Равное распределение ({pd}/{pr}/{pg})"
    return f"Распределение {pd}/{pr}/{pg}"


def generate_alternatives(
    rt: float,
    obligation_payments: float,
    goals_total: float,
    step: float = 0.20,
) -> list[dict[str, Any]]:
    """
    Этап 4: Генерация множества A = {a₁, …, aₙ} через дискретизацию Rt.

    Дискретизация с шагом step=20% даёт ровно 21 комбинацию
    (x_обязат, x_резерв, x_цели) при x₁+x₂+x₃ = Rt (ВКР, форм. 38–39):
      C(1/step + 2, 2) = C(7, 2) = 21

    При Rt ≤ 0 возвращает единственную «дефицитную» альтернативу.
    """
    if rt <= 0:
        return [{
            "id": "deficit",
            "name": "Дефицитный бюджет",
            "description": "Расходы и обязательства превышают доходы. "
                           "Необходимо пересмотреть бюджет.",
            "x_obligations": 0,
            "x_reserve": 0,
            "x_goals": 0,
            "x_remain": rt,
        }]

    steps = round(1.0 / step)   # = 5 при step=0.20
    alternatives = []

    for d in range(steps + 1):          # доля на обязательства
        for r in range(steps + 1 - d):  # доля на резерв
            g = steps - d - r           # остаток — на цели

            # Пропускаем комбинации только с x_goals > 0, если целей нет
            if g > 0 and goals_total <= 0:
                continue
            # Пропускаем x_obligations > 0, если нет обязательств
            if d > 0 and obligation_payments <= 0:
                continue

            x_obl = round(rt * d * step, 2)
            x_res = round(rt * r * step, 2)
            x_goa = round(rt * g * step, 2)

            name = _alt_name(d, r, g, steps)
            pct = lambda x: int(round(x / steps * 100))
            pd, pr, pg = pct(d), pct(r), pct(g)
            desc_parts = []
            if x_obl > 0:
                desc_parts.append(f"погашение долга {pd}% ({x_obl:,.0f} ₽)")
            if x_res > 0:
                desc_parts.append(f"резерв {pr}% ({x_res:,.0f} ₽)")
            if x_goa > 0:
                desc_parts.append(f"цели {pg}% ({x_goa:,.0f} ₽)")

            alternatives.append({
                "id": f"a{d}{r}{g}",
                "name": name,
                "description": "; ".join(desc_parts) or "Все средства остаются в наличии.",
                "x_obligations": x_obl,
                "x_reserve": x_res,
                "x_goals": x_goa,
            })

    return alternatives


def evaluate_alternative(
    alt: dict,
    rt: float,
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    goals_total: float = 0.0,
) -> dict[str, Any]:
    """
    Этап 4b: Пересчёт Rt', Lt', Dt', Si для каждой альтернативы.

    Формулы соответствуют ВКР (табл. 17):
      Lt = Rt / (Расходы + Обязательства)
      Rt' = Rt + высвобожденные_обязательства   (досрочное погашение снижает будущий платёж)
      Lt' = Rt' / (Расходы + новые_обязательства)
      Dt' = новые_обязательства / Доходы
      Si  = x_goals / goals_total  — непрерывный показатель обеспеченности целей (ВКР, форм. 15)
    """
    x_obl = alt.get("x_obligations", 0)
    x_goals = alt.get("x_goals", 0)

    # Досрочное погашение снижает будущие ежемесячные обязательства
    new_obl = max(obligation_payments - x_obl, 0)

    # Rt' — новый ежемесячный профицит после снижения обязательств
    new_rt = rt + min(x_obl, obligation_payments)

    total_load = expense_total + new_obl
    # Lt' по формуле ВКР: Rt' / (Расходы + Обязательства')
    new_lt = new_rt / total_load if total_load > 0 else 0.0
    new_dt = new_obl / income_total if income_total > 0 else 0.0

    # Si — непрерывная обеспеченность целей: x_goals / goals_total (форм. 15 ВКР)
    if goals_total > 0:
        goals_coverage = min(1.0, x_goals / goals_total)
    else:
        goals_coverage = 1.0 if x_goals == 0 else 0.0

    alt["Rt_new"] = round(new_rt, 2)
    alt["Lt_new"] = round(new_lt, 4)
    alt["Dt_new"] = round(new_dt, 4)
    alt["goals_coverage"] = round(goals_coverage, 4)
    return alt


def filter_alternatives(
    alternatives: list[dict],
    b_min: float = B_MIN,
    lt_crit: float = LT_CRIT,
    dt_max: float = DT_MAX,
) -> tuple[list[dict], list[dict]]:
    """
    Этап 5a: Фильтрация — отсев альтернатив, нарушающих ограничения.
    
    Условия допустимости:
      Rt' ≥ B_min
      Lt' ≥ Lt_crit
      Dt' ≤ Dt_max
    
    Returns: (допустимые, отклонённые)
    """
    accepted = []
    rejected = []

    for alt in alternatives:
        violations = []
        if alt.get("Rt_new", 0) < b_min:
            violations.append(f"Rt' ({alt['Rt_new']:,.0f}) < B_min ({b_min})")
        if alt.get("Lt_new", 0) < lt_crit:
            violations.append(f"Lt' ({alt['Lt_new']:.2f}) < Lt_crit ({lt_crit})")
        if alt.get("Dt_new", 0) > dt_max:
            violations.append(f"Dt' ({alt['Dt_new']*100:.1f}%) > Dt_max ({dt_max*100:.0f}%)")

        alt["violations"] = violations
        alt["is_admissible"] = len(violations) == 0

        if alt["is_admissible"]:
            accepted.append(alt)
        else:
            rejected.append(alt)

    return accepted, rejected


def normalize_value(value: float, v_min: float, v_max: float, minimize: bool = False) -> float:
    """
    Нормализация показателя к [0, 1].
    Для максимизации: (v - v_min) / (v_max - v_min)
    Для минимизации: (v_max - v) / (v_max - v_min)
    """
    if v_max == v_min:
        return 1.0
    if minimize:
        return (v_max - value) / (v_max - v_min)
    return (value - v_min) / (v_max - v_min)


def rank_alternatives(
    alternatives: list[dict],
    risk_tolerance: int = 3,
) -> list[dict]:
    """
    Этап 5b: Ранжирование через интегральную функцию полезности.
    
    U(a) = w₁·Rt_norm + w₂·Lt_norm + w₃·Dt_norm + w₄·Goals_norm
    a* = argmax U(a)
    """
    if not alternatives:
        return []

    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])
    w_rt = profile["w_rt"]
    w_lt = profile["w_lt"]
    w_dt = profile["w_dt"]
    w_goals = profile["w_goals"]

    # Находим min/max для нормализации
    rt_values = [a["Rt_new"] for a in alternatives]
    lt_values = [a["Lt_new"] for a in alternatives]
    dt_values = [a["Dt_new"] for a in alternatives]
    goal_values = [a["goals_coverage"] for a in alternatives]

    rt_min, rt_max = min(rt_values), max(rt_values)
    lt_min, lt_max = min(lt_values), max(lt_values)
    dt_min, dt_max = min(dt_values), max(dt_values)
    g_min, g_max = min(goal_values), max(goal_values)

    for alt in alternatives:
        rt_norm = normalize_value(alt["Rt_new"], rt_min, rt_max, minimize=False)
        lt_norm = normalize_value(alt["Lt_new"], lt_min, lt_max, minimize=False)
        dt_norm = normalize_value(alt["Dt_new"], dt_min, dt_max, minimize=True)
        g_norm = normalize_value(alt["goals_coverage"], g_min, g_max, minimize=False)

        utility = w_rt * rt_norm + w_lt * lt_norm + w_dt * dt_norm + w_goals * g_norm
        alt["utility"] = round(utility, 4)
        alt["scores"] = {
            "Rt_norm": round(rt_norm, 3),
            "Lt_norm": round(lt_norm, 3),
            "Dt_norm": round(dt_norm, 3),
            "Goals_norm": round(g_norm, 3),
        }

    # Сортировка по убыванию U(a)
    alternatives.sort(key=lambda a: a["utility"], reverse=True)

    # Помечаем лучшую
    if alternatives:
        alternatives[0]["is_optimal"] = True

    return alternatives


def _explain_alternative(
    alt: dict,
    rt: float,
    lt: float,
    dt: float,
    expense_total: float,
    obligation_payments: float,
    goals_total: float,
    risk_profile_label: str,
) -> dict[str, Any]:
    """
    Формирует структурированное объяснение: почему эта альтернатива
    рекомендуется, что конкретно улучшается и какой есть компромисс.
    """
    delta_rt = alt["Rt_new"] - rt
    delta_lt = alt["Lt_new"] - lt
    delta_dt = alt["Dt_new"] - dt

    x_obl   = alt.get("x_obligations", 0)
    x_res   = alt.get("x_reserve", 0)
    x_goals = alt.get("x_goals", 0)

    gains   = []   # что улучшается
    costs   = []   # чем жертвуем
    insight = []   # ключевой вывод для пользователя

    # — Обязательства ——————————————————————————————
    if x_obl > 0:
        freed_monthly = min(x_obl, obligation_payments)
        gains.append(
            f"Долговая нагрузка снижается с {dt*100:.1f}% до {alt['Dt_new']*100:.1f}% "
            f"(−{abs(delta_dt)*100:.1f} п.п.). "
            f"Досрочное погашение на {x_obl:,.0f} ₽ освободит "
            f"≈{freed_monthly:,.0f} ₽/мес в будущих периодах."
        )
        if x_goals == 0 and x_res == 0:
            costs.append("Средства на цели и резерв в этом периоде не направляются.")

    # — Резерв ——————————————————————————————————————
    if x_res > 0:
        months_cover = x_res / expense_total if expense_total > 0 else 0
        gains.append(
            f"Резервный фонд пополняется на {x_res:,.0f} ₽ "
            f"(≈{months_cover:.1f} мес. расходов). "
            f"Ликвидность: {lt:.3f} → {alt['Lt_new']:.3f} "
            f"({'↑' if delta_lt >= 0 else '↓'}{abs(delta_lt):.3f})."
        )

    # — Цели ————————————————————————————————————————
    if x_goals > 0 and goals_total > 0:
        pct_goals = alt["goals_coverage"] * 100
        gains.append(
            f"На финансовые цели направляется {x_goals:,.0f} ₽ "
            f"— покрывается {pct_goals:.0f}% от суммарной потребности."
        )
        if x_obl == 0:
            costs.append("Досрочное погашение обязательств в этом периоде не производится.")

    # — Rt всегда растёт при погашении долга ————————
    if delta_rt > 0:
        gains.append(
            f"Свободный ресурс будущего периода вырастет: "
            f"{rt:,.0f} → {alt['Rt_new']:,.0f} ₽ (+{delta_rt:,.0f} ₽/мес)."
        )

    # — Ключевой вывод ——————————————————————————————
    if alt.get("is_optimal"):
        insight.append(
            f"Лучший вариант для профиля «{risk_profile_label}»: "
            f"максимальный U(a) = {alt['utility']} из всех допустимых альтернатив."
        )
    else:
        insight.append(
            f"U(a) = {alt['utility']} — "
            + ("высокая полезность, акцент на ликвидности."
               if alt["Lt_new"] == max(alt["Lt_new"], alt["Dt_new"]) else
               "высокая полезность, акцент на достижении целей.")
        )

    if not gains:
        gains.append("Все средства остаются в распоряжении на следующий период.")

    return {
        "gains": gains,
        "costs": costs,
        "insight": " ".join(insight),
        "delta": {
            "Rt": round(delta_rt, 2),
            "Lt": round(delta_lt, 4),
            "Dt": round(delta_dt, 4),
        },
    }


def run_planning(
    rt: float,
    lt: float,
    dt: float,
    income_total: float,
    expense_total: float,
    obligation_payments: float,
    goals_total: float,
    risk_tolerance: int = 3,
    l_min: float = LT_CRIT,
) -> dict[str, Any]:
    """
    Полный цикл планирования:
    генерация → оценка → фильтрация → ранжирование → рекомендация.

    l_min — минимально допустимый уровень Lt' (параметр пользователя U.L_min из ВКР).
    """
    profile = RISK_PROFILES.get(risk_tolerance, RISK_PROFILES[3])

    # 1. Генерация (21 альтернатива при шаге 20%)
    alternatives = generate_alternatives(
        rt=rt,
        obligation_payments=obligation_payments,
        goals_total=goals_total,
    )

    # 2. Оценка (пересчёт Rt', Lt', Dt', Si для каждой)
    for alt in alternatives:
        evaluate_alternative(
            alt, rt,
            income_total, expense_total, obligation_payments,
            goals_total=goals_total,
        )

    # 3. Фильтрация с пользовательским порогом L_min
    admissible, rejected = filter_alternatives(alternatives, lt_crit=l_min)

    # 4. Ранжирование допустимых
    ranked = rank_alternatives(admissible, risk_tolerance)

    # 5. Топ-3 с объяснением «почему именно это»
    top3 = []
    for alt in ranked[:3]:
        explanation = _explain_alternative(
            alt=alt,
            rt=rt, lt=lt, dt=dt,
            expense_total=expense_total,
            obligation_payments=obligation_payments,
            goals_total=goals_total,
            risk_profile_label=profile["label"],
        )
        top3.append({**alt, "explanation": explanation})

    optimal = ranked[0] if ranked else None

    return {
        "indicators": {"Rt": rt, "Lt": lt, "Dt": dt},
        "risk_profile": profile["label"],
        "weights": {
            "w_rt": profile["w_rt"],
            "w_lt": profile["w_lt"],
            "w_dt": profile["w_dt"],
            "w_goals": profile["w_goals"],
        },
        "alternatives_total": len(alternatives),
        "admissible_count": len(admissible),
        "rejected_count": len(rejected),
        "top3": top3,
        "ranked": ranked,
        "rejected": rejected,
        "optimal": optimal,
    }
