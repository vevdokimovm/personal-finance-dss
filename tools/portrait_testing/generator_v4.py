"""Генератор портретов v4 — итерация 4 экспертной сертификации.

Независимый модуль: v3 (`generator_v3.py`) заморожен как канон итерации 3,
общего кода нет намеренно — изменение одного не может тихо сдвинуть другой.

Что нового против v3 (ТЗ раунда 3, `iterations/3/expert_feedback_aggregate.md` §6,
плюс невыполненные пункты методички тест-сетов):

  P1 **Продуктовая типизация кредитов** (главный дефект v3 — «ипотека 30.6% на
     3 года»): ставка × срок × остаток разыгрываются СОВМЕСТНО внутри спеки
     продукта, имя кредита выводится из продукта. Слой A строг по всем трём
     осям; слой B (DOE) держит ставку/срок в спеке, но допускает экстремальный
     остаток — экстремумы там и тестируются (зафиксировано в meta).
  P2 **k-целей = спека**: k — суммарный масштаб портрета (Σ target / годовой
     доход), enforced клампом каталога имён; заявленный диапазон совпадает с фактом.
  P4 **Потолок ПСК** 292% годовых — верхняя граница МФО (Закон 353-ФЗ).
  P5 **Реалистичные «киты»** (доход 5–10 млн) отделены от стресс-магнитуды 2e9:
     разные kind, гиганты не протекают в популяцию.
  P6 **Имя цели ↔ сумма**: каталог имён с диапазонами, непрерывно покрывающими
     5 тыс. – 100 млн; «Подушка безопасности» убрана (коллизия с bliq).
  P7 **Мощность страт**: выводы делаются по СЕМЕЙСТВАМ слоя C (>= 385 записей,
     ±5% при 95%), отдельный kind внутри семейства — детерминированная проба.
  P8 **Слой D v2**: составные и near-miss дефекты, рандомизированные объёмы;
     дубли id при ВАЛИДНЫХ данных вынесены в слой C (это не мусор, а проверка
     позиционного контракта).
  P9 **Точная арифметика границ** (источник находки R3-F1): нулевой поток и
     равенства строятся в целых рублях/Decimal — float-остатка нет по построению.
  E-слой: добавлены НЕРАВНОМЕРНЫЕ возмущения (одна ставка, один дедлайн) —
     равномерные сдвиги v3 модель не различала by design (раунд 3 §4).

Слои (n=12000): A 4800 популяция (копула) · B 3600 DOE (LHS 10 осей) ·
C 2400 каталог (6 семейств по 400) · D 600 adversarial · E 600 = 300 пар.

Детерминизм: только stdlib `random.Random` (кроссверсионный битовый поток);
всё воспроизводимо по (seed, index).
"""
from __future__ import annotations

import copy
import math
from datetime import date, timedelta
from decimal import Decimal
from random import Random

LAYER_QUOTAS: tuple[tuple[str, int], ...] = (
    ("A", 4800), ("B", 3600), ("C", 2400), ("D", 600), ("E", 600),
)

EXPERT_FIELDS_V4: tuple[str, ...] = (
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
)

# --- P1/P4: каталог кредитных продуктов РФ 2026 -----------------------------
# rate — годовая ставка; term — срок, мес; amount — остаток тела, ₽;
# weight — доля продукта в популяции. Диапазоны согласованы: платёж считается
# аннуитетом от (amount, rate, term), поэтому тройка всегда взаимно возможна.
LOAN_PRODUCTS: dict[str, dict] = {
    "mortgage": {"name": "Ипотека", "rate": (0.06, 0.19),
                 "term": (120, 360), "amount": (1_000_000, 30_000_000),
                 "weight": 12},
    "auto": {"name": "Автокредит", "rate": (0.10, 0.25),
             "term": (12, 84), "amount": (300_000, 5_000_000), "weight": 12},
    "consumer": {"name": "Потребительский кредит", "rate": (0.16, 0.35),
                 "term": (12, 84), "amount": (30_000, 3_000_000), "weight": 32},
    "card": {"name": "Кредитная карта", "rate": (0.20, 0.40),
             "term": (6, 36), "amount": (10_000, 500_000), "weight": 25},
    "installment": {"name": "Рассрочка", "rate": (0.0, 0.05),
                    "term": (3, 24), "amount": (5_000, 300_000), "weight": 13},
    "mfo": {"name": "Заём МФО", "rate": (0.50, 2.92),
            "term": (1, 12), "amount": (5_000, 100_000), "weight": 6},
}
PSK_RATE_CAP = 2.92  # 353-ФЗ: предельная ПСК микрозайма, ~0.8%/день


def products_for_rate(rate: float) -> list[str]:
    """Продукты, чья спека содержит ставку (кейсы «ставка == бенчмарку»)."""
    return [k for k, s in LOAN_PRODUCTS.items()
            if s["rate"][0] <= rate <= s["rate"][1]]


# --- P6: имена целей с диапазонами сумм (непрерывное покрытие 5e3..1e8) ------
GOAL_NAME_RANGES: dict[str, tuple[float, float]] = {
    "Техника": (5_000, 300_000),
    "Отпуск": (30_000, 500_000),
    "Лечение": (20_000, 1_500_000),
    "Переезд": (50_000, 1_500_000),
    "Свадьба": (200_000, 2_000_000),
    "Образование": (100_000, 2_500_000),
    "Ремонт": (150_000, 3_000_000),
    "Автомобиль": (400_000, 6_000_000),
    "Первый взнос по ипотеке": (500_000, 10_000_000),
    "Инвестиционный портфель": (300_000, 100_000_000),
    "Покупка недвижимости": (2_000_000, 50_000_000),
}
K_GOAL_MIN, K_GOAL_MAX = 0.2, 5.0
K_GOAL_TOLERANCE = 0.05  # допуск от клампа каталога имён (декларируется в meta)

# --- P7: семейства слоя C (каждое >= 385 записей) ---------------------------
C_FAMILIES: dict[str, tuple[str, ...]] = {
    "flow_edges": ("zero_income", "zero_expenses", "fcf_zero_exact",
                   "deficit_flow"),
    "debt_edges": ("overleveraged", "cheap_debts_only", "rate_eq_bench_exact",
                   "rate_near_bench", "interest_only_block", "growing_debt",
                   "toxic_mfo_thin_cushion"),
    "goal_edges": ("target_eq_current_kopeck", "overfunded_goal",
                   "goal_at_minimum", "eight_goals_same_deadline",
                   "five_goals", "six_goals", "seven_goals"),
    "deadline_edges": ("deadline_today_exact", "deadline_tomorrow",
                       "deadline_deep_overdue", "horizon_10y"),
    "liquidity_edges": ("bliq_zero", "huge_bliq", "no_goals_no_debts",
                        "pdn_boundary"),
    "integrity_edges": ("duplicate_id_valid_pair", "magnitude_whale",
                        "magnitude_stress"),
}
_C_KIND_WEIGHTS: dict[str, int] = {
    # flow_edges = 400
    "zero_income": 100, "zero_expenses": 100, "fcf_zero_exact": 100,
    "deficit_flow": 100,
    # debt_edges = 400
    "overleveraged": 60, "cheap_debts_only": 60, "rate_eq_bench_exact": 60,
    "rate_near_bench": 60, "interest_only_block": 55, "growing_debt": 55,
    "toxic_mfo_thin_cushion": 50,
    # goal_edges = 400
    "target_eq_current_kopeck": 60, "overfunded_goal": 60,
    "goal_at_minimum": 55, "eight_goals_same_deadline": 55, "five_goals": 60,
    "six_goals": 55, "seven_goals": 55,
    # deadline_edges = 400
    "deadline_today_exact": 100, "deadline_tomorrow": 100,
    "deadline_deep_overdue": 100, "horizon_10y": 100,
    # liquidity_edges = 400
    "bliq_zero": 100, "huge_bliq": 100, "no_goals_no_debts": 100,
    "pdn_boundary": 100,
    # integrity_edges = 400
    "duplicate_id_valid_pair": 200, "magnitude_whale": 100,
    "magnitude_stress": 100,
}

# --- P8: слой D v2 — неравные объёмы, составные и near-miss ------------------
_D_KIND_WEIGHTS: dict[str, int] = {
    "negative_income": 45, "income_none": 40, "none_amount": 50,
    "broken_date_string": 55, "string_income": 35, "missing_income_field": 30,
    "negative_amount": 60, "negative_rate": 45, "absurd_rate_12": 40,
    "rate_string": 35, "goal_missing_deadline_key": 40,
    "duplicate_id_broken": 30,
    "near_rate_above_cap": 25, "near_empty_string_amount": 20,
    "near_bool_income": 20, "near_date_feb30": 15,
    "composite_negative_and_broken_date": 12, "composite_none_and_string": 13,
}

E_RELATIONS: tuple[str, ...] = (
    "M1_income", "M2_rate_all", "M2_rate_single", "M3_deadline_all",
    "M3_deadline_single", "M4_bliq", "M5_scale",
)

SPEARMAN_TARGETS = {
    ("income", "k_goal"): -0.40,
    ("exp_ratio", "pdn"): -0.50,
}
R_BENCH_ANCHOR, R_BENCH_SD = 0.15, 0.030
R_BENCH_LO, R_BENCH_HI = 0.08, 0.24

STATUS_TARGETS = {
    "A": {"deficit_pct": [12.0, 32.0]},   # популяция: калибровка по ЦБ/НБКИ
    "B": {"deficit_pct": [40.0, 70.0]},   # DOE: экстремумы по построению
}


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _kuma(u: float, a: float, b: float) -> float:
    u = min(max(u, 1e-12), 1.0 - 1e-12)
    return (1.0 - (1.0 - u) ** (1.0 / b)) ** (1.0 / a)


def _cholesky(m: list[list[float]]) -> list[list[float]]:
    n = len(m)
    low = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(low[i][k] * low[j][k] for k in range(j))
            low[i][j] = (math.sqrt(m[i][i] - s) if i == j
                         else (m[i][j] - s) / low[j][j])
    return low


def _round2(x: float) -> float:
    return float(Decimal(repr(x)).quantize(Decimal("0.01")))


def _annuity_amount(payment: float, rate: float, term: int) -> float:
    i = rate / 12.0
    if i <= 0:
        return payment * term
    return payment * (1.0 - (1.0 + i) ** (-term)) / i


def _annuity_payment(amount: float, rate: float, term: int) -> float:
    i = rate / 12.0
    if i <= 0:
        return amount / term
    return amount * i / (1.0 - (1.0 + i) ** (-term))


def _term_for_amount(payment: float, rate: float, amount: float) -> float:
    """Срок, при котором аннуитет с данным платежом даёт данный остаток."""
    i = rate / 12.0
    if i <= 0:
        return amount / payment
    ratio = amount * i / payment
    if ratio >= 1.0:
        return math.inf  # платёж не покрывает проценты такого тела
    return -math.log(1.0 - ratio) / math.log(1.0 + i)


def _payment_span(spec: dict) -> tuple[float, float]:
    lo = _annuity_payment(spec["amount"][0], spec["rate"][0], spec["term"][1])
    hi = _annuity_payment(spec["amount"][1], spec["rate"][1], spec["term"][0])
    return lo, hi


class PortraitGeneratorV4:
    """Детерминированный слоистый генератор v4. `generate(i)` — портрет."""

    AXES = ("income", "exp_ratio", "pdn", "liq_months", "k_goal", "goals_prop")

    def __init__(self, seed: int = 20260718, n: int = 12000,
                 frozen_today: date = date(2026, 7, 18)) -> None:
        self.seed = seed
        self.n = n
        self.frozen_today = frozen_today
        master = Random(f"v4:{seed}:layout")

        quotas = self._scaled_quotas(n)
        tags: list[str] = []
        for tag, q in quotas:
            tags.extend([tag] * q)
        master.shuffle(tags)
        self.layer_by_index = tags
        self.quotas = dict(quotas)

        by_layer: dict[str, list[int]] = {t: [] for t, _ in LAYER_QUOTAS}
        for idx, tag in enumerate(tags):
            by_layer[tag].append(idx)

        self._kind_family = {k: fam for fam, kinds in C_FAMILIES.items()
                             for k in kinds}
        self._c_kind = self._deal(master, by_layer["C"], _C_KIND_WEIGHTS,
                                  pair_kinds=("duplicate_id_valid_pair",))
        self._d_kind = self._deal(master, by_layer["D"], _D_KIND_WEIGHTS)

        clean = by_layer["A"] + by_layer["B"]
        self._dup_target = {
            idx: master.choice(clean)
            for idx, kind in self._d_kind.items() if kind == "duplicate_id_broken"
        }
        # C: валидные дубли id — парами (позиционный контракт, не мусор)
        valid_dups = sorted(i for i, k in self._c_kind.items()
                            if k == "duplicate_id_valid_pair")
        self._valid_dup_pair: dict[int, tuple[int, str]] = {}
        for t in range(len(valid_dups) // 2):
            a, b = valid_dups[2 * t], valid_dups[2 * t + 1]
            shared = f"SP4-{a:05d}"
            self._valid_dup_pair[a] = (t, shared)
            self._valid_dup_pair[b] = (t, shared)

        # E: пары по 7 отношениям
        self._pair_of: dict[int, tuple[str, str, str, int]] = {}
        e_idx = by_layer["E"]
        for t in range(len(e_idx) // 2):
            base_i, twin_i = e_idx[2 * t], e_idx[2 * t + 1]
            rel = E_RELATIONS[t % len(E_RELATIONS)]
            pid = f"E4-{t:04d}"
            self._pair_of[base_i] = (pid, "base", rel, base_i)
            self._pair_of[twin_i] = (pid, "twin", rel, base_i)

        # B: LHS по 10 осям
        nb = len(by_layer["B"])
        self._b_order = {idx: pos for pos, idx in enumerate(by_layer["B"])}
        self._nb = nb
        self._lhs = {
            axis: master.sample(range(nb), nb) if nb else []
            for axis in ("income", "exp_ratio", "pdn", "liq", "n_obl", "spread",
                         "n_goals", "deadline", "readiness", "risk")
        }

        rho = [[1.0 if i == j else 0.0 for j in range(6)] for i in range(6)]
        ax = {name: k for k, name in enumerate(self.AXES)}
        for (a, b), rs in SPEARMAN_TARGETS.items():
            rp = 2.0 * math.sin(math.pi * rs / 6.0)
            rho[ax[a]][ax[b]] = rho[ax[b]][ax[a]] = rp
        self._chol = _cholesky(rho)

    # ------------------------------------------------------------------ utils
    @staticmethod
    def _scaled_quotas(n: int) -> tuple[tuple[str, int], ...]:
        base = sum(q for _, q in LAYER_QUOTAS)
        out, acc = [], 0
        for i, (tag, q) in enumerate(LAYER_QUOTAS):
            take = n - acc if i == len(LAYER_QUOTAS) - 1 else round(n * q / base)
            if tag == "E":
                take -= take % 2
            out.append((tag, take))
            acc += take
        return tuple(out)

    @staticmethod
    def _deal(master: Random, indices: list[int], weights: dict[str, int],
              pair_kinds: tuple[str, ...] = ()) -> dict[int, str]:
        total = sum(weights.values())
        share = len(indices) / total if total else 0
        pool: list[str] = []
        for kind, w in weights.items():
            take = max(1, round(w * share))
            if kind in pair_kinds and take % 2:
                take += 1
            pool.extend([kind] * take)
        fill = max(weights, key=weights.get)
        while len(pool) < len(indices):
            pool.append(fill)
        del pool[len(indices):]
        master.shuffle(pool)
        return dict(zip(indices, pool))

    def _rng(self, index: int, tag: str = "content") -> Random:
        return Random(f"v4:{self.seed}:{tag}:{index}")

    def _r_bench(self, rng: Random) -> float:
        while True:
            v = rng.gauss(R_BENCH_ANCHOR, R_BENCH_SD)
            if R_BENCH_LO <= v <= R_BENCH_HI:
                return round(v, 4)

    # ------------------------------------------------- P1: продуктовые кредиты
    def _loan_from_payment(self, rng: Random, payment: float,
                           strict_amount: bool = True,
                           force_product: str | None = None,
                           rate_override: float | None = None) -> dict | None:
        """Строит кредит под заданный платёж: (ставка, срок, остаток) в спеке."""
        if payment < 200.0:
            return None
        keys = [force_product] if force_product else list(LOAN_PRODUCTS)
        if not force_product:
            weights = [LOAN_PRODUCTS[k]["weight"] for k in keys]
            keys = self._weighted_order(rng, keys, weights)
        for key in keys:
            spec = LOAN_PRODUCTS[key]
            for _ in range(6):
                rate = (rate_override if rate_override is not None
                        else rng.uniform(*spec["rate"]))
                rate = min(max(rate, spec["rate"][0]), spec["rate"][1])
                a_lo, a_hi = spec["amount"]
                t_lo, t_hi = spec["term"]
                n_lo = _term_for_amount(payment, rate, a_lo)
                if n_lo == math.inf:
                    continue  # платёж не тянет даже нижнюю границу продукта
                n_hi = _term_for_amount(payment, rate, a_hi)
                lo = max(t_lo, math.ceil(n_lo))
                hi = min(t_hi, math.floor(n_hi)) if n_hi != math.inf else t_hi
                if lo <= hi:
                    term = rng.randint(int(lo), int(hi))
                    return self._loan_record(key, rate, term,
                                             _annuity_amount(payment, rate, term),
                                             payment)
                if not strict_amount:
                    term = rng.randint(t_lo, t_hi)
                    return self._loan_record(key, rate, term,
                                             _annuity_amount(payment, rate, term),
                                             payment)
        # последний рубеж: подгоняем платёж под спеку продукта
        key = force_product or ("consumer" if payment < 200_000 else "mortgage")
        spec = LOAN_PRODUCTS[key]
        rate = (rate_override if rate_override is not None
                and spec["rate"][0] <= rate_override <= spec["rate"][1]
                else rng.uniform(*spec["rate"]))
        term = rng.randint(*spec["term"])
        amount = min(max(_annuity_amount(payment, rate, term), spec["amount"][0]),
                     spec["amount"][1])
        return self._loan_record(key, rate, term, amount,
                                 _annuity_payment(amount, rate, term))

    @staticmethod
    def _weighted_order(rng: Random, keys: list[str],
                        weights: list[int]) -> list[str]:
        keys, weights = list(keys), list(weights)
        order = []
        while keys:
            pick = rng.choices(range(len(keys)), weights=weights)[0]
            order.append(keys.pop(pick))
            weights.pop(pick)
        return order

    @staticmethod
    def _loan_record(product: str, rate: float, term: int, amount: float,
                     payment: float) -> dict:
        return {
            "id": 0, "name": LOAN_PRODUCTS[product]["name"],
            "amount": _round2(amount),
            "interest_rate": round(rate, 4),
            "monthly_payment": _round2(payment),
            "_product": product, "_term": term,
        }

    def _build_obligations(self, rng: Random, total_payment: float, n_obl: int,
                           strict_amount: bool = True) -> list[dict]:
        if n_obl <= 0 or total_payment < 200.0:
            return []
        weights = [rng.gammavariate(2.0, 1.0) for _ in range(n_obl)]
        s = sum(weights)
        out: list[dict] = []
        for k in range(n_obl):
            loan = self._loan_from_payment(rng, total_payment * weights[k] / s,
                                           strict_amount=strict_amount)
            if loan:
                loan["id"] = len(out) + 1
                out.append(loan)
        return out

    # ---------------------------------------------------- P2/P6: цели и имена
    @staticmethod
    def _goal_name(rng: Random, amount: float) -> tuple[str, float]:
        fits = [n for n, (lo, hi) in GOAL_NAME_RANGES.items()
                if lo <= amount <= hi]
        if fits:
            return rng.choice(sorted(fits)), amount
        lows = min(lo for lo, _ in GOAL_NAME_RANGES.values())
        highs = max(hi for _, hi in GOAL_NAME_RANGES.values())
        if amount < lows:
            return "Техника", lows
        return "Инвестиционный портфель", highs

    def _build_goals(self, rng: Random, income: float, k_goal: float,
                     n_goals: int, readiness: float | None = None,
                     nearest_months: float | None = None) -> list[dict]:
        if n_goals <= 0:
            return []
        base_income = income if income > 0 else 40_000.0
        total = max(k_goal, K_GOAL_MIN) * 12.0 * base_income
        weights = [rng.gammavariate(2.0, 1.0) for _ in range(n_goals)]
        s = sum(weights)
        goals: list[dict] = []
        for k in range(n_goals):
            name, amount = self._goal_name(rng, total * weights[k] / s)
            ready = readiness if readiness is not None else _kuma(rng.random(),
                                                                  1.2, 2.5)
            if nearest_months is not None and k == 0:
                months = nearest_months
            else:
                months = 3.0 + 117.0 * _kuma(rng.random(), 1.1, 1.6)
            deadline = (None if rng.random() < 0.25
                        else self.frozen_today + timedelta(days=round(months * 30.44)))
            goals.append({
                "id": k + 1, "name": name,
                "target_amount": _round2(amount),
                "current_amount": _round2(min(amount * ready, amount)),
                "deadline": deadline,
            })
        return self._enforce_k(rng, goals, base_income)

    def _enforce_k(self, rng: Random, goals: list[dict],
                   income: float) -> list[dict]:
        """P2: суммарный k обязан лежать в заявленной спеке."""
        for _ in range(3):
            k_eff = sum(g["target_amount"] for g in goals) / (12.0 * income)
            if K_GOAL_MIN <= k_eff <= K_GOAL_MAX:
                return goals
            target = min(max(k_eff, K_GOAL_MIN), K_GOAL_MAX)
            factor = target / k_eff
            for g in goals:
                ratio = (g["current_amount"] / g["target_amount"]
                         if g["target_amount"] else 0.0)
                name, amount = self._goal_name(rng, g["target_amount"] * factor)
                g["name"] = name
                g["target_amount"] = _round2(amount)
                g["current_amount"] = _round2(amount * ratio)
        return goals

    # -------------------------------------------------------------- слой A
    def _gen_a(self, index: int, rng: Random | None = None,
               force_obl: bool = False, force_deadline: bool = False) -> dict:
        rng = rng or self._rng(index)
        g = [rng.gauss(0.0, 1.0) for _ in range(6)]
        z = [sum(self._chol[i][k] * g[k] for k in range(i + 1)) for i in range(6)]
        u = [_phi(v) for v in z]

        income = math.exp(math.log(72_000.0) + 0.75 * z[0])
        exp_ratio = 0.25 + 0.80 * _kuma(u[1], 2.2, 2.8)
        pdn = 0.85 * _kuma(u[2], 1.6, 4.5)
        liq_months = math.exp(math.log(2.0) + 0.9 * z[3])
        k_goal = math.exp(math.log(K_GOAL_MIN)
                          + u[4] * (math.log(K_GOAL_MAX) - math.log(K_GOAL_MIN)))

        acc, n_goals = 0.0, 8
        for lvl, w in enumerate((0.12, 0.18, 0.20, 0.16, 0.12, 0.09, 0.06,
                                 0.04, 0.03)):
            acc += w
            if u[5] <= acc:
                n_goals = lvl
                break

        expense = _round2(income * exp_ratio)
        n_obl = rng.choices((0, 1, 2, 3, 4), weights=(25, 30, 23, 14, 8))[0]
        if force_obl:
            n_obl = max(1, n_obl)
        obls = self._build_obligations(rng, income * pdn if n_obl else 0.0, n_obl)
        if force_obl and not obls:
            obls = self._build_obligations(rng, max(income * 0.12, 8_000.0), 1)
        pay = sum(o["monthly_payment"] for o in obls)
        bliq = _round2(max(liq_months * (expense + pay), 0.0))

        goals = self._build_goals(rng, income, k_goal, n_goals)
        if force_deadline:
            if not goals:
                goals = self._build_goals(rng, income, 0.8, 1)
            if all(x["deadline"] is None for x in goals):
                goals[0]["deadline"] = self.frozen_today + timedelta(days=365)

        return {
            "index": index, "layer": "A", "kind": "population", "family": "",
            "l_min": 0.0,
            "income_total": _round2(income), "expense_total": expense,
            "obligations": obls, "goals": goals, "bliq": bliq,
            "r_bench": self._r_bench(rng), "risk_tolerance": rng.randint(1, 5),
        }

    # -------------------------------------------------------------- слой B
    def _gen_b(self, index: int) -> dict:
        rng = self._rng(index)
        pos = self._b_order[index]
        ux = {axis: (self._lhs[axis][pos] + rng.random()) / self._nb
              for axis in self._lhs}

        income = math.exp(math.log(15_000.0)
                          + ux["income"] * (math.log(10_000_000.0)
                                            - math.log(15_000.0)))
        expense = _round2(income * (0.20 + 1.10 * ux["exp_ratio"]))
        pdn = 0.90 * ux["pdn"]
        n_obl = min(4, int(ux["n_obl"] * 5))
        r_bench = self._r_bench(rng)
        obls = self._build_obligations(rng, income * pdn if n_obl else 0.0,
                                       n_obl, strict_amount=False)
        # ось спреда: сдвигаем ставку самого дорогого внутри спеки его продукта
        if obls:
            spread = -0.10 + 0.35 * ux["spread"]
            top = max(obls, key=lambda o: o["interest_rate"])
            spec = LOAN_PRODUCTS[top["_product"]]
            rate = min(max(r_bench + spread, spec["rate"][0]), spec["rate"][1])
            top["interest_rate"] = round(rate, 4)
            top["amount"] = _round2(_annuity_amount(top["monthly_payment"],
                                                    rate, top["_term"]))
        pay = sum(o["monthly_payment"] for o in obls)
        bliq = _round2(24.0 * ux["liq"] * (expense + pay))
        k_goal = math.exp(math.log(K_GOAL_MIN)
                          + rng.random() * (math.log(K_GOAL_MAX)
                                            - math.log(K_GOAL_MIN)))
        goals = self._build_goals(rng, income, k_goal,
                                  min(8, int(ux["n_goals"] * 9)),
                                  readiness=ux["readiness"],
                                  nearest_months=max(120.0 * ux["deadline"], 0.5))
        return {
            "index": index, "layer": "B", "kind": "doe", "family": "",
            "l_min": 0.0,
            "income_total": _round2(income), "expense_total": expense,
            "obligations": obls, "goals": goals, "bliq": bliq,
            "r_bench": r_bench, "risk_tolerance": min(5, 1 + int(ux["risk"] * 5)),
        }

    # -------------------------------------------------------------- слой C
    def _gen_c(self, index: int) -> dict:
        kind = self._c_kind[index]
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng)
        p["layer"], p["kind"] = "C", kind
        p["family"] = self._kind_family[kind]
        t0 = self.frozen_today

        def pay_sum() -> float:
            return sum(o["monthly_payment"] for o in p["obligations"])

        if kind == "zero_income":
            p["income_total"] = 0.0
        elif kind == "zero_expenses":
            p["expense_total"] = 0.0
        elif kind == "deficit_flow":
            p["expense_total"] = _round2(p["income_total"] * rng.uniform(1.05, 1.6))
        elif kind == "fcf_zero_exact":
            self._make_flow_exactly_zero(p, rng)
        elif kind == "overleveraged":
            p["obligations"] = self._build_obligations(
                rng, p["income_total"] * rng.uniform(1.1, 1.8), 2)
        elif kind == "cheap_debts_only":
            self._retype_loans(p, rng, ("installment",))
        elif kind == "rate_eq_bench_exact":
            self._seed_loan_at_rate(p, rng, p["r_bench"])
        elif kind == "rate_near_bench":
            delta = rng.choice((-0.005, -0.001, 0.001, 0.005))
            self._seed_loan_at_rate(p, rng, round(p["r_bench"] + delta, 4))
        elif kind == "interest_only_block":
            self._seed_loan(p, rng, product="card")
            o = p["obligations"][0]
            o["monthly_payment"] = _round2(o["amount"] * o["interest_rate"] / 12.0)
        elif kind == "growing_debt":
            self._seed_loan(p, rng, product="card")
            o = p["obligations"][0]
            o["monthly_payment"] = _round2(o["amount"] * o["interest_rate"]
                                           / 12.0 * 0.6)
        elif kind == "toxic_mfo_thin_cushion":
            self._seed_loan(p, rng, product="mfo")
            p["bliq"] = _round2((p["expense_total"] + pay_sum())
                                * rng.uniform(0.1, 0.9))
        elif kind == "deadline_today_exact":
            self._seed_goal(p, rng)
            p["goals"][0]["deadline"] = t0
        elif kind == "deadline_tomorrow":
            self._seed_goal(p, rng)
            p["goals"][0]["deadline"] = t0 + timedelta(days=1)
        elif kind == "deadline_deep_overdue":
            self._seed_goal(p, rng)
            p["goals"][0]["deadline"] = t0 - timedelta(days=rng.randint(95, 720))
        elif kind == "horizon_10y":
            self._seed_goal(p, rng)
            p["goals"][0]["deadline"] = t0 + timedelta(days=rng.randint(1830, 3650))
        elif kind == "target_eq_current_kopeck":
            self._seed_goal(p, rng)
            g0 = p["goals"][0]
            g0["current_amount"] = g0["target_amount"]  # равенство по построению
        elif kind == "overfunded_goal":
            self._seed_goal(p, rng)
            g0 = p["goals"][0]
            g0["current_amount"] = _round2(g0["target_amount"]
                                           * rng.uniform(1.01, 1.4))
        elif kind == "goal_at_minimum":
            lo = GOAL_NAME_RANGES["Техника"][0]
            p["goals"] = [{"id": 1, "name": "Техника", "target_amount": lo,
                           "current_amount": 0.0,
                           "deadline": t0 + timedelta(days=90)}]
        elif kind in ("five_goals", "six_goals", "seven_goals",
                      "eight_goals_same_deadline"):
            n = {"five_goals": 5, "six_goals": 6, "seven_goals": 7,
                 "eight_goals_same_deadline": 8}[kind]
            p["goals"] = self._build_goals(rng, p["income_total"], 1.5, n)
            if kind == "eight_goals_same_deadline":
                common = t0 + timedelta(days=rng.randint(180, 1500))
                for g_ in p["goals"]:
                    g_["deadline"] = common
        elif kind == "bliq_zero":
            p["bliq"] = 0.0
        elif kind == "huge_bliq":
            p["bliq"] = _round2((p["expense_total"] + pay_sum() + 1.0)
                                * rng.uniform(30, 120))
        elif kind == "no_goals_no_debts":
            p["goals"], p["obligations"] = [], []
        elif kind == "pdn_boundary":
            self._make_pdn_exact(p, rng)
        elif kind == "magnitude_whale":
            self._make_whale(p, rng, income=rng.uniform(5e6, 10e6))
        elif kind == "magnitude_stress":
            self._make_whale(p, rng, income=rng.uniform(1e9, 2e9), stress=True)
        elif kind == "duplicate_id_valid_pair":
            pair_no, shared = self._valid_dup_pair[index]
            p["id_override"] = shared
            p["pair_id"] = f"DUP-{pair_no:04d}"
            # обе записи валидны, но данные конфликтуют — проверка позиционного
            # контракта: мержить по id нельзя, отвечать надо на обе строки
            p["income_total"] = _round2(p["income_total"]
                                        * (1.0 + 0.35 * (index % 2 or -1)))
        return p

    def _make_flow_exactly_zero(self, p: dict, rng: Random) -> None:
        """P9: нулевой поток в целых рублях — float-остатка нет (R3-F1)."""
        income = float(int(p["income_total"]))
        for o in p["obligations"]:
            o["monthly_payment"] = float(int(o["monthly_payment"]))
            o["amount"] = _round2(_annuity_amount(o["monthly_payment"],
                                                  o["interest_rate"], o["_term"]))
        pay = sum(o["monthly_payment"] for o in p["obligations"])
        if pay >= income:
            p["obligations"], pay = [], 0.0
        p["income_total"] = income
        p["expense_total"] = income - pay
        assert p["income_total"] - p["expense_total"] - pay == 0.0

    def _make_pdn_exact(self, p: dict, rng: Random) -> None:
        income = float(int(p["income_total"] or 100_000))
        target = Decimal(str(rng.choice((0.38, 0.395, 0.40, 0.405, 0.42))))
        want = float((Decimal(str(income)) * target).quantize(Decimal("0.01")))
        p["income_total"] = income
        loan = self._loan_from_payment(rng, want, strict_amount=False)
        p["obligations"] = [dict(loan, id=1)] if loan else []
        p["expense_total"] = _round2(min(p["expense_total"],
                                         max(income - want - 1.0, 0.0)))

    def _make_whale(self, p: dict, rng: Random, income: float,
                    stress: bool = False) -> None:
        p["income_total"] = _round2(income)
        p["expense_total"] = _round2(income * rng.uniform(0.3, 0.8))
        p["obligations"] = self._build_obligations(
            rng, income * rng.uniform(0.05, 0.3), 2, strict_amount=not stress)
        p["goals"] = self._build_goals(rng, income, 1.0, 2)
        p["bliq"] = _round2(income * rng.uniform(0.5, 6.0))

    def _retype_loans(self, p: dict, rng: Random,
                      products: tuple[str, ...]) -> None:
        self._seed_loan(p, rng, product=products[0])
        out = []
        for o in p["obligations"]:
            loan = self._loan_from_payment(rng, o["monthly_payment"],
                                           strict_amount=False,
                                           force_product=rng.choice(products))
            if loan:
                loan["id"] = len(out) + 1
                out.append(loan)
        p["obligations"] = out or p["obligations"]

    def _seed_loan_at_rate(self, p: dict, rng: Random, rate: float) -> None:
        """Кредит ровно с заданной ставкой: продукт подбирается ПОД ставку."""
        options = products_for_rate(rate)
        if not options:  # ставка ниже всех спек — рассрочка ближе всего
            options = ["installment"]
        payment = (p["obligations"][0]["monthly_payment"] if p["obligations"]
                   else max(p["income_total"] * 0.15, 6_000.0))
        loan = self._loan_from_payment(rng, payment, strict_amount=False,
                                       force_product=rng.choice(sorted(options)),
                                       rate_override=rate)
        if loan:
            p["obligations"] = [dict(loan, id=1)] + [
                dict(o, id=i + 2) for i, o in enumerate(p["obligations"][1:])]

    def _seed_loan(self, p: dict, rng: Random, product: str | None = None) -> None:
        if not p["obligations"]:
            payment = max(p["income_total"] * 0.15, 6_000.0)
            loan = self._loan_from_payment(rng, payment, strict_amount=False,
                                           force_product=product)
            p["obligations"] = [dict(loan, id=1)] if loan else []
        elif product:
            loan = self._loan_from_payment(rng, p["obligations"][0]["monthly_payment"],
                                           strict_amount=False,
                                           force_product=product)
            if loan:
                p["obligations"][0] = dict(loan, id=1)

    def _seed_goal(self, p: dict, rng: Random) -> None:
        if not p["goals"]:
            p["goals"] = self._build_goals(rng, max(p["income_total"], 40_000.0),
                                           0.8, 1)

    # -------------------------------------------------------------- слой D
    def _gen_d(self, index: int) -> dict:
        kind = self._d_kind[index]
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng, force_obl=True, force_deadline=True)
        p["layer"], p["kind"], p["family"] = "D", kind, ""
        errors = {
            "negative_income": "отрицательный income_total",
            "income_none": "income_total = null",
            "none_amount": "obligations[0].amount = null",
            "broken_date_string": "непарсящаяся дата дедлайна",
            "string_income": "income_total строкой прописью",
            "missing_income_field": "нет поля income_total",
            "negative_amount": "отрицательное тело долга",
            "negative_rate": "отрицательная ставка",
            "absurd_rate_12": "ставка 1200% годовых — выше потолка ПСК",
            "rate_string": "ставка строкой",
            "goal_missing_deadline_key": "у цели нет ключа deadline",
            "duplicate_id_broken": "дубль id + битая дата",
            "near_rate_above_cap": "ставка 301% — на волос выше порога мусора",
            "near_empty_string_amount": "пустая строка вместо суммы",
            "near_bool_income": "булево значение вместо дохода",
            "near_date_feb30": "30 февраля — синтаксис верен, даты нет",
            "composite_negative_and_broken_date": "два дефекта: знак и дата",
            "composite_none_and_string": "два дефекта: null и строка",
        }
        p["expected_error"] = errors[kind]
        o, g = p["obligations"][0], p["goals"][0]
        if kind == "negative_income":
            p["income_total"] = -abs(p["income_total"]) - 1.0
        elif kind == "income_none":
            p["income_total"] = None
        elif kind == "none_amount":
            o["amount"] = None
        elif kind == "broken_date_string":
            g["deadline"] = "2026-13-45"
        elif kind == "string_income":
            p["income_total"] = "сто тысяч"
        elif kind == "missing_income_field":
            del p["income_total"]
        elif kind == "negative_amount":
            o["amount"] = -abs(o["amount"])
        elif kind == "negative_rate":
            o["interest_rate"] = -0.15
        elif kind == "absurd_rate_12":
            o["interest_rate"] = 12.0
        elif kind == "rate_string":
            o["interest_rate"] = "двадцать"
        elif kind == "goal_missing_deadline_key":
            del g["deadline"]
        elif kind == "duplicate_id_broken":
            p["id_override"] = f"SP4-{self._dup_target[index]:05d}"
            g["deadline"] = "2026-02-30"
        elif kind == "near_rate_above_cap":
            o["interest_rate"] = 3.01
        elif kind == "near_empty_string_amount":
            o["amount"] = ""
        elif kind == "near_bool_income":
            p["income_total"] = True
        elif kind == "near_date_feb30":
            g["deadline"] = "2026-02-30"
        elif kind == "composite_negative_and_broken_date":
            p["income_total"] = -abs(p["income_total"])
            g["deadline"] = "не скажу"
        elif kind == "composite_none_and_string":
            o["amount"] = None
            o["interest_rate"] = "0,2"
        return p

    # -------------------------------------------------------------- слой E
    def _gen_e(self, index: int) -> dict:
        pid, role, rel, base_index = self._pair_of[index]
        base = self._gen_a(base_index, rng=self._rng(base_index, "epair"),
                           force_obl=True, force_deadline=True)
        base.update({"layer": "E", "kind": "metamorphic", "family": "",
                     "pair_id": pid, "pair_role": "base", "pair_relation": rel})
        # M2 двигает ставку на +1 п.п. — база не должна стоять вплотную к верху
        # спеки продукта (иначе твин вылезет за ПСК/каталог)
        for o in base["obligations"]:
            spec = LOAN_PRODUCTS[o["_product"]]
            ceiling = spec["rate"][1] - 0.01
            if o["interest_rate"] > ceiling:
                o["interest_rate"] = round(max(ceiling, spec["rate"][0]), 4)
                o["amount"] = _round2(_annuity_amount(o["monthly_payment"],
                                                      o["interest_rate"],
                                                      o["_term"]))
        if role == "base":
            base["index"] = index
            return base

        twin = copy.deepcopy(base)
        twin["index"] = index
        twin["pair_role"] = "twin"
        if rel == "M1_income":
            twin["income_total"] = _round2(base["income_total"] * 1.01)
        elif rel == "M2_rate_all":
            for o in twin["obligations"]:
                o["interest_rate"] = round(o["interest_rate"] + 0.01, 4)
        elif rel == "M2_rate_single":
            top = max(twin["obligations"], key=lambda o: o["interest_rate"])
            top["interest_rate"] = round(top["interest_rate"] + 0.01, 4)
        elif rel == "M3_deadline_all":
            for g_ in twin["goals"]:
                if g_["deadline"] is not None:
                    g_["deadline"] = g_["deadline"] + timedelta(days=183)
        elif rel == "M3_deadline_single":
            dated = [g_ for g_ in twin["goals"] if g_["deadline"] is not None]
            if dated:
                nearest = min(dated, key=lambda x: x["deadline"])
                nearest["deadline"] = nearest["deadline"] + timedelta(days=183)
        elif rel == "M4_bliq":
            twin["bliq"] = _round2(base["bliq"] * 1.01)
        elif rel == "M5_scale":
            twin["income_total"] = _round2(base["income_total"] * 10.0)
            twin["expense_total"] = _round2(base["expense_total"] * 10.0)
            twin["bliq"] = _round2(base["bliq"] * 10.0)
            for o in twin["obligations"]:
                o["amount"] = _round2(o["amount"] * 10.0)
                o["monthly_payment"] = _round2(o["monthly_payment"] * 10.0)
            for g_ in twin["goals"]:
                g_["target_amount"] = _round2(g_["target_amount"] * 10.0)
                g_["current_amount"] = _round2(g_["current_amount"] * 10.0)
        return twin

    # -------------------------------------------------------------- фасады
    def generate(self, index: int) -> dict:
        if not 0 <= index < self.n:
            raise IndexError(index)
        layer = self.layer_by_index[index]
        p = {"A": self._gen_a, "B": self._gen_b, "C": self._gen_c,
             "D": self._gen_d, "E": self._gen_e}[layer](index)
        for o in p.get("obligations") or ():
            o.pop("_product", None)
            o.pop("_term", None)
        return p

    def expert_row(self, index: int) -> dict:
        p = self.generate(index)
        row = {"id": p.get("id_override", f"SP4-{index:05d}")}
        for field in EXPERT_FIELDS_V4:
            if field != "id" and field in p:
                row[field] = p[field]
        return row

    def coordinator_key(self, index: int) -> dict:
        p = self.generate(index)
        return {
            "id": f"SP4-{index:05d}",
            "layer": p["layer"], "kind": p["kind"], "family": p.get("family", ""),
            "pair_id": p.get("pair_id"), "pair_role": p.get("pair_role"),
            "pair_relation": p.get("pair_relation"),
            "expected_error": p.get("expected_error"),
            "id_override": p.get("id_override"),
        }

    def meta(self) -> dict:
        return {
            "__meta__": True,
            "dataset_version": 4,
            "generator": "tools/portrait_testing/generator_v4.py::PortraitGeneratorV4",
            "seed": self.seed, "n": self.n,
            "frozen_today": self.frozen_today.isoformat(),
            "layers": dict(self.quotas),
            "loan_products": {k: {"name": v["name"], "rate": v["rate"],
                                  "term": v["term"], "amount": v["amount"],
                                  "weight": v["weight"]}
                              for k, v in LOAN_PRODUCTS.items()},
            "psk_rate_cap": PSK_RATE_CAP,
            "goal_name_ranges": GOAL_NAME_RANGES,
            "k_goal_spec": {"definition": "сумма target по портрету / годовой доход",
                            "range": [K_GOAL_MIN, K_GOAL_MAX],
                            "tolerance": K_GOAL_TOLERANCE,
                            "enforced_by": "каталог имён + масштабирование"},
            "c_families": {fam: list(kinds) for fam, kinds in C_FAMILIES.items()},
            "c_family_min_n": 385,
            "d_kinds": sorted(_D_KIND_WEIGHTS),
            "e_relations": list(E_RELATIONS),
            "status_targets": STATUS_TARGETS,
            "spearman_targets": {"goals_sum~income": "+0.30…0.50",
                                 "expenses~payments": "+0.20…0.35"},
            "r_bench": {"law": "truncnorm", "anchor": R_BENCH_ANCHOR,
                        "sd": R_BENCH_SD, "range": [R_BENCH_LO, R_BENCH_HI]},
            "notes": {
                "layer_b_amounts": "DOE допускает остаток вне спеки продукта: "
                                   "ставка и срок в спеке, экстремум — по оси",
                "duplicate_ids": "слой C содержит валидные дубли id (парами), "
                                 "слой D — битые; сопоставление ПО ПОРЯДКУ строк",
                "metamorphic_twins": "у твинов M2_* аннуитет намеренно "
                                     "расходится (ставка растёт при том же "
                                     "платеже), у твинов M5_scale суммы целей "
                                     "выходят за натуральные диапазоны имён — "
                                     "это дизайн возмущения, а не дефект",
            },
        }
