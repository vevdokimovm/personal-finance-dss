"""Генератор портретов v3 — слоистый тест-сет A–E (итерация 3 сертификации).

Независимая генерация с нуля по архитектуре протокола
(`docs/model/expert_certification/iteration_protocol.md`) и консолидированному
ТЗ четырёх экспертов раунда 2
(`docs/model/expert_certification/iterations/2/expert_feedback_aggregate.md` §6).
Общего с v1/v2 (`generator.py`) — только схема полей экспертного пакета.

Слои (квоты на n=12000):
  A (population, 4800) — гауссова копула: лог-нормальный доход без клампа хвоста,
    Kumaraswamy-маргиналы долей, целевые ранговые связи (цели↔доход +0.3…0.5,
    расходы↔платежи +0.2…0.35), сегментация ставок по продуктам, 100% аннуитет.
  B (DOE, 3600) — латинский гиперкуб по 10 нормализованным осям решений
    (доход, exp/inc, ПДН, месяцы ликвидности, n_obl, спред к бенчмарку, n_goals
    0–8 без дыр, ближайший дедлайн 0–120 мес, готовность целей, риск).
  C (catalog, 2400) — детерминированный каталог граничных кейсов с джиттером;
    закрыты дыры раунда 2: target==current в копейку, bliq==0, FCF==0,
    дедлайн==дате среза, глубокая просрочка, 8 целей с единым дедлайном,
    5/6/7 целей, interest-only/растущий долг явными подслоями, МФО-токсичность
    при тонкой подушке, магнитудная страта ~1e9 с заявленной долей.
  D (adversarial, 600) — битые записи с манифестом ожидаемой причины отказа
    (`expected_error`); модель/эксперт обязаны отклонять, не падая.
  E (metamorphic, 600 = 300 пар) — пары (base, twin) с манифестом отношений
    M1 доход+1% / M2 ставка+1 п.п. / M3 дедлайн+6 мес / M4 подушка+1% /
    M5 все деньги ×10; `pair_id` восстанавливает пары без разметки решений.

Детерминизм: только stdlib `random.Random` (стабилен между версиями Python,
в отличие от битового потока numpy.Generator). Всё воспроизводимо по
(seed, index); межпортретные структуры (перестановки слоёв, LHS-страты,
квоты каталога, назначение пар) фиксируются мастер-ГСЧ в конструкторе.

Слепота: экспертам уходит проекция `expert_row(i)` (id + 8 полей брифа, без
kind/layer/pair_id); канонический размеченный файл и ключ координатора —
`tools/model_validation/dataset_export.py --version 3`.

r_bench непрерывный: усечённая нормаль вокруг якоря ключевой ставки,
коридор [0.08; 0.24] (D1 раунда 2). Дедлайны относительные: T+Δ от
`frozen_today`-параметра (D8), горизонты до 120 месяцев.
"""
from __future__ import annotations

import copy
import math
from datetime import date, timedelta
from random import Random

LAYER_QUOTAS: tuple[tuple[str, int], ...] = (
    ("A", 4800), ("B", 3600), ("C", 2400), ("D", 600), ("E", 600),
)

EXPERT_FIELDS_V3: tuple[str, ...] = (
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
)

# Целевые ранговые (Спирмен) связи слоя A — из ТЗ агрегата §6.4
SPEARMAN_TARGETS = {
    ("income", "k_goal"): -0.40,     # демпфер: цели ~ k × годовой доход
    ("exp_ratio", "pdn"): -0.50,     # демпфер общего доходного фактора
}

R_BENCH_ANCHOR, R_BENCH_SD = 0.15, 0.030
R_BENCH_LO, R_BENCH_HI = 0.08, 0.24

GOAL_NAMES = (
    "Подушка безопасности", "Отпуск", "Ремонт", "Автомобиль", "Первый взнос",
    "Образование", "Техника", "Переезд", "Лечение", "Свадьба",
)
OBL_NAMES = ("Ипотека", "Автокредит", "Потребкредит", "Кредитная карта", "Рассрочка", "Займ")

_C_KINDS: tuple[tuple[str, int], ...] = (
    ("zero_income", 120), ("zero_expenses", 100), ("deficit_flow", 150),
    ("fcf_zero_exact", 100), ("overleveraged", 100), ("cheap_debts_only", 120),
    ("rate_eq_bench_exact", 100), ("rate_near_bench", 100),
    ("interest_only_block", 60), ("growing_debt", 60),
    ("toxic_mfo_thin_cushion", 80), ("deadline_today_exact", 80),
    ("deadline_deep_overdue", 80), ("deadline_tomorrow", 60),
    ("target_eq_current_kopeck", 80), ("overfunded_goal", 80),
    ("goal_at_minimum", 60), ("bliq_zero", 80), ("huge_bliq", 80),
    ("eight_goals_same_deadline", 80), ("five_goals", 60), ("six_goals", 60),
    ("seven_goals", 60), ("no_goals_no_debts", 90), ("magnitude_1e9", 100),
    ("pdn_boundary", 140), ("horizon_10y", 120),
)

_D_KINDS: tuple[str, ...] = (
    "negative_income", "income_none", "none_amount", "broken_date_string",
    "string_income", "missing_income_field", "negative_amount", "negative_rate",
    "absurd_rate_12", "rate_string", "goal_missing_deadline_key", "duplicate_id",
)

_E_RELATIONS: tuple[str, ...] = (
    "M1_income", "M2_rate", "M3_deadline", "M4_bliq", "M5_scale",
)


def _phi(z: float) -> float:
    """Стандартная нормальная CDF."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _kuma(u: float, a: float, b: float) -> float:
    """Обратная CDF Kumaraswamy — Beta-подобный маргинал в закрытой форме."""
    u = min(max(u, 1e-12), 1.0 - 1e-12)
    return (1.0 - (1.0 - u) ** (1.0 / b)) ** (1.0 / a)


def _cholesky(m: list[list[float]]) -> list[list[float]]:
    n = len(m)
    low = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(low[i][k] * low[j][k] for k in range(j))
            if i == j:
                low[i][j] = math.sqrt(m[i][i] - s)
            else:
                low[i][j] = (m[i][j] - s) / low[j][j]
    return low


def _annuity_amount(payment: float, annual_rate: float, term_months: int) -> float:
    i = annual_rate / 12.0
    if i <= 0:
        return payment * term_months
    return payment * (1.0 - (1.0 + i) ** (-term_months)) / i


def _round2(x: float) -> float:
    return round(x + 1e-9, 2)


class PortraitGeneratorV3:
    """Детерминированный слоистый генератор. `generate(i)` — портрет по индексу."""

    AXES = ("income", "exp_ratio", "pdn", "liq_months", "k_goal", "goals_prop")

    def __init__(self, seed: int = 20260716, n: int = 12000,
                 frozen_today: date = date(2026, 7, 16)) -> None:
        self.seed = seed
        self.n = n
        self.frozen_today = frozen_today
        master = Random(f"v3:{seed}:layout")

        quotas = self._scaled_quotas(n)
        tags: list[str] = []
        for tag, q in quotas:
            tags.extend([tag] * q)
        master.shuffle(tags)
        self.layer_by_index: list[str] = tags
        self.quotas = dict(quotas)

        by_layer: dict[str, list[int]] = {t: [] for t, _ in LAYER_QUOTAS}
        for idx, tag in enumerate(tags):
            by_layer[tag].append(idx)

        # C: раздача kind по квотам (масштабируются пропорционально)
        c_share = self.quotas["C"] / 2400.0
        c_pool: list[str] = []
        for kind, q in _C_KINDS:
            c_pool.extend([kind] * max(1, round(q * c_share)))
        while len(c_pool) < len(by_layer["C"]):
            c_pool.append("pdn_boundary")
        del c_pool[len(by_layer["C"]):]
        master.shuffle(c_pool)
        self._c_kind = dict(zip(by_layer["C"], c_pool))

        # D: 12 kinds равными долями; duplicate_id получает цель дубля
        d_pool: list[str] = []
        per = max(1, len(by_layer["D"]) // len(_D_KINDS))
        for kind in _D_KINDS:
            d_pool.extend([kind] * per)
        while len(d_pool) < len(by_layer["D"]):
            d_pool.append("negative_amount")
        del d_pool[len(by_layer["D"]):]
        master.shuffle(d_pool)
        self._d_kind = dict(zip(by_layer["D"], d_pool))
        clean = by_layer["A"] + by_layer["B"]
        self._dup_target = {
            idx: master.choice(clean)
            for idx, kind in self._d_kind.items() if kind == "duplicate_id"
        }

        # E: последовательные пары по глобально перемешанным индексам слоя
        self._pair_of: dict[int, tuple[str, str, str, int]] = {}
        e_idx = by_layer["E"]
        for t in range(len(e_idx) // 2):
            base_i, twin_i = e_idx[2 * t], e_idx[2 * t + 1]
            rel = _E_RELATIONS[t % len(_E_RELATIONS)]
            pid = f"E-{t:04d}"
            self._pair_of[base_i] = (pid, "base", rel, base_i)
            self._pair_of[twin_i] = (pid, "twin", rel, base_i)

        # B: LHS — независимая перестановка страт по каждой из 10 осей
        nb = len(by_layer["B"])
        self._b_order = {idx: pos for pos, idx in enumerate(by_layer["B"])}
        self._lhs = {
            axis: master.sample(range(nb), nb) if nb else []
            for axis in ("income", "exp_ratio", "pdn", "liq", "n_obl",
                         "spread", "n_goals", "deadline", "readiness", "risk")
        }
        self._nb = nb

        # Копула слоя A: Спирмен -> Пирсон -> Холецкий
        rho = [[1.0 if i == j else 0.0 for j in range(6)] for i in range(6)]
        ax = {name: k for k, name in enumerate(self.AXES)}
        for (a, b), rs in SPEARMAN_TARGETS.items():
            rp = 2.0 * math.sin(math.pi * rs / 6.0)
            rho[ax[a]][ax[b]] = rho[ax[b]][ax[a]] = rp
        self._chol = _cholesky(rho)

    # ------------------------------------------------------------------ util
    @staticmethod
    def _scaled_quotas(n: int) -> tuple[tuple[str, int], ...]:
        base = sum(q for _, q in LAYER_QUOTAS)
        out = []
        acc = 0
        for i, (tag, q) in enumerate(LAYER_QUOTAS):
            if i == len(LAYER_QUOTAS) - 1:
                take = n - acc
            else:
                take = round(n * q / base)
                if tag == "E":
                    take -= take % 2
            out.append((tag, take))
            acc += take
        return tuple(out)

    def _rng(self, index: int, tag: str = "content") -> Random:
        return Random(f"v3:{self.seed}:{tag}:{index}")

    def _r_bench(self, rng: Random) -> float:
        while True:
            v = rng.gauss(R_BENCH_ANCHOR, R_BENCH_SD)
            if R_BENCH_LO <= v <= R_BENCH_HI:
                return round(v, 4)

    def _risk(self, rng: Random) -> int:
        return rng.randint(1, 5)

    # ------------------------------------------------------------ строители
    def _build_obligations(self, rng: Random, total_payment: float,
                           n_obl: int, max_rate: float | None = None) -> list[dict]:
        if n_obl <= 0 or total_payment < 500.0:
            return []
        weights = [rng.gammavariate(2.0, 1.0) for _ in range(n_obl)]
        s = sum(weights)
        obls: list[dict] = []
        for k in range(n_obl):
            payment = _round2(total_payment * weights[k] / s)
            if payment < 300.0:
                continue
            if max_rate is not None and k == 0:
                rate = max_rate
                term = rng.randint(12, 84)
            else:
                seg = rng.random()
                if seg < 0.22 and payment > 12000:
                    rate = round(rng.uniform(0.08, 0.18), 4)
                    term = rng.randint(120, 360)
                elif seg < 0.97 or max_rate is not None:
                    rate = round(rng.uniform(0.16, 0.35), 4)
                    term = rng.randint(12, 84)
                else:
                    rate = round(rng.uniform(0.36, 0.59), 4)
                    term = rng.randint(6, 12)
            obls.append({
                "id": k + 1,
                "name": rng.choice(OBL_NAMES),
                "amount": _round2(_annuity_amount(payment, rate, term)),
                "interest_rate": rate,
                "monthly_payment": payment,
            })
        return obls

    def _build_goals(self, rng: Random, income: float, k_goal: float,
                     n_goals: int, readiness: float | None = None,
                     nearest_months: float | None = None) -> list[dict]:
        if n_goals <= 0:
            return []
        total_target = max(k_goal * 12.0 * income, 5000.0 * n_goals)
        weights = [rng.gammavariate(2.0, 1.0) for _ in range(n_goals)]
        s = sum(weights)
        goals: list[dict] = []
        for k in range(n_goals):
            target = _round2(max(total_target * weights[k] / s, 3000.0))
            ready = readiness if readiness is not None else _kuma(rng.random(), 1.2, 2.5)
            current = _round2(min(target * ready, target))
            if rng.random() < 0.25:
                deadline = None
            else:
                if nearest_months is not None and k == 0:
                    months = nearest_months
                else:
                    months = 3.0 + 117.0 * _kuma(rng.random(), 1.1, 1.6)
                deadline = self.frozen_today + timedelta(days=round(months * 30.44))
            goals.append({
                "id": k + 1,
                "name": rng.choice(GOAL_NAMES),
                "target_amount": target,
                "current_amount": current,
                "deadline": deadline,
            })
        return goals

    def _base_common(self, index: int, layer: str, kind: str) -> dict:
        return {
            "index": index,
            "layer": layer,
            "kind": kind,
            "l_min": 0.0,
        }

    # ---------------------------------------------------------------- слой A
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
        k_goal = math.exp(math.log(0.2) + u[4] * (math.log(5.0) - math.log(0.2)))

        goal_weights = (0.12, 0.18, 0.20, 0.16, 0.12, 0.09, 0.06, 0.04, 0.03)
        acc, n_goals = 0.0, 8
        for lvl, w in enumerate(goal_weights):
            acc += w
            if u[5] <= acc:
                n_goals = lvl
                break

        expense = _round2(income * exp_ratio)
        n_obl = rng.choices((0, 1, 2, 3, 4), weights=(25, 30, 23, 14, 8))[0]
        if force_obl:
            n_obl = max(1, n_obl)
        payments_total = income * pdn if n_obl else 0.0
        obls = self._build_obligations(rng, payments_total, n_obl)
        if force_obl and not obls:
            obls = self._build_obligations(rng, max(income * 0.12, 6_000.0), 1)
        pay = sum(o["monthly_payment"] for o in obls)
        bliq = _round2(max(liq_months * (expense + pay), 0.0))

        goals = self._build_goals(rng, income, k_goal, n_goals)
        if force_deadline:
            if not goals:
                goals = self._build_goals(rng, max(income, 40_000.0), 0.8, 1)
            if all(g_["deadline"] is None for g_ in goals):
                goals[0]["deadline"] = self.frozen_today + timedelta(days=365)

        p = self._base_common(index, "A", "population")
        p.update({
            "income_total": _round2(income),
            "expense_total": expense,
            "obligations": obls,
            "goals": goals,
            "bliq": bliq,
            "r_bench": self._r_bench(rng),
            "risk_tolerance": self._risk(rng),
        })
        return p

    # ---------------------------------------------------------------- слой B
    def _lhs_u(self, axis: str, pos: int, rng: Random) -> float:
        stratum = self._lhs[axis][pos]
        return (stratum + rng.random()) / self._nb

    def _gen_b(self, index: int) -> dict:
        rng = self._rng(index)
        pos = self._b_order[index]
        ux = {axis: self._lhs_u(axis, pos, rng) for axis in self._lhs}

        income = math.exp(math.log(15_000.0)
                          + ux["income"] * (math.log(1_500_000.0) - math.log(15_000.0)))
        exp_ratio = 0.20 + 1.10 * ux["exp_ratio"]
        pdn = 0.90 * ux["pdn"]
        liq_months = 24.0 * ux["liq"]
        n_obl = min(4, int(ux["n_obl"] * 5))
        spread = -0.10 + 0.35 * ux["spread"]
        n_goals = min(8, int(ux["n_goals"] * 9))
        nearest = 120.0 * ux["deadline"]
        readiness = ux["readiness"]
        risk = min(5, 1 + int(ux["risk"] * 5))

        r_bench = self._r_bench(rng)
        max_rate = round(max(r_bench + spread, 0.015), 4)
        expense = _round2(income * exp_ratio)
        payments_total = income * pdn if n_obl else 0.0
        obls = self._build_obligations(rng, payments_total, n_obl, max_rate=max_rate)
        pay = sum(o["monthly_payment"] for o in obls)
        bliq = _round2(liq_months * (expense + pay))
        k_goal = math.exp(math.log(0.2) + rng.random() * (math.log(5.0) - math.log(0.2)))
        goals = self._build_goals(rng, income, k_goal, n_goals,
                                  readiness=readiness, nearest_months=max(nearest, 0.5))

        p = self._base_common(index, "B", "doe")
        p.update({
            "income_total": _round2(income),
            "expense_total": expense,
            "obligations": obls,
            "goals": goals,
            "bliq": bliq,
            "r_bench": r_bench,
            "risk_tolerance": risk,
        })
        return p

    # ---------------------------------------------------------------- слой C
    def _gen_c(self, index: int) -> dict:
        kind = self._c_kind[index]
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng)
        p["layer"], p["kind"] = "C", kind
        income = p["income_total"]
        expense = p["expense_total"]
        r_bench = p["r_bench"]
        t0 = self.frozen_today

        def pay_sum() -> float:
            return sum(o["monthly_payment"] for o in p["obligations"])

        if kind == "zero_income":
            p["income_total"] = 0.0
        elif kind == "zero_expenses":
            p["expense_total"] = 0.0
        elif kind == "deficit_flow":
            p["expense_total"] = _round2(income * rng.uniform(1.05, 1.6))
        elif kind == "fcf_zero_exact":
            p["expense_total"] = _round2(income - pay_sum())
            if p["expense_total"] < 0:
                p["obligations"], p["expense_total"] = [], _round2(income)
        elif kind == "overleveraged":
            p["obligations"] = self._build_obligations(
                rng, income * rng.uniform(1.1, 1.8), max(2, len(p["obligations"]) or 2))
        elif kind == "cheap_debts_only":
            for o in p["obligations"] or self._seed_one_loan(p, rng):
                o["interest_rate"] = round(rng.uniform(0.03, max(r_bench - 0.02, 0.035)), 4)
        elif kind == "rate_eq_bench_exact":
            for o in p["obligations"] or self._seed_one_loan(p, rng):
                pass
            p["obligations"][0]["interest_rate"] = r_bench
        elif kind == "rate_near_bench":
            self._seed_one_loan(p, rng)
            delta = rng.choice((-0.005, -0.001, 0.001, 0.005))
            p["obligations"][0]["interest_rate"] = round(r_bench + delta, 4)
        elif kind == "interest_only_block":
            self._seed_one_loan(p, rng)
            o = p["obligations"][0]
            o["monthly_payment"] = _round2(o["amount"] * o["interest_rate"] / 12.0)
        elif kind == "growing_debt":
            self._seed_one_loan(p, rng)
            o = p["obligations"][0]
            o["monthly_payment"] = _round2(o["amount"] * o["interest_rate"] / 12.0 * 0.6)
        elif kind == "toxic_mfo_thin_cushion":
            self._seed_one_loan(p, rng)
            o = p["obligations"][0]
            o["interest_rate"] = round(rng.uniform(0.36, 0.60), 4)
            o["amount"] = _round2(_annuity_amount(o["monthly_payment"],
                                                  o["interest_rate"], rng.randint(6, 12)))
            p["bliq"] = _round2((expense + pay_sum()) * rng.uniform(0.1, 0.9))
        elif kind == "deadline_today_exact":
            self._seed_one_goal(p, rng)
            p["goals"][0]["deadline"] = t0
        elif kind == "deadline_tomorrow":
            self._seed_one_goal(p, rng)
            p["goals"][0]["deadline"] = t0 + timedelta(days=1)
        elif kind == "deadline_deep_overdue":
            self._seed_one_goal(p, rng)
            p["goals"][0]["deadline"] = t0 - timedelta(days=rng.randint(95, 720))
        elif kind == "target_eq_current_kopeck":
            self._seed_one_goal(p, rng)
            g0 = p["goals"][0]
            g0["current_amount"] = g0["target_amount"]
        elif kind == "overfunded_goal":
            self._seed_one_goal(p, rng)
            g0 = p["goals"][0]
            g0["current_amount"] = _round2(g0["target_amount"] * rng.uniform(1.01, 1.4))
        elif kind == "goal_at_minimum":
            p["goals"] = [{
                "id": 1, "name": rng.choice(GOAL_NAMES),
                "target_amount": 3000.0, "current_amount": 0.0,
                "deadline": t0 + timedelta(days=90),
            }]
        elif kind == "bliq_zero":
            p["bliq"] = 0.0
        elif kind == "huge_bliq":
            p["bliq"] = _round2((expense + pay_sum() + 1.0) * rng.uniform(30, 120))
        elif kind == "eight_goals_same_deadline":
            common = t0 + timedelta(days=rng.randint(180, 1500))
            p["goals"] = self._build_goals(rng, max(income, 30000.0), 1.5, 8)
            for g_ in p["goals"]:
                g_["deadline"] = common
        elif kind in ("five_goals", "six_goals", "seven_goals"):
            n = {"five_goals": 5, "six_goals": 6, "seven_goals": 7}[kind]
            p["goals"] = self._build_goals(rng, max(income, 30000.0), 1.2, n)
        elif kind == "no_goals_no_debts":
            p["goals"], p["obligations"] = [], []
        elif kind == "magnitude_1e9":
            scale = rng.uniform(3e3, 2e4)
            p["income_total"] = _round2(min(income * scale, 2e9))
            p["expense_total"] = _round2(p["income_total"] * rng.uniform(0.3, 0.8))
            p["obligations"] = self._build_obligations(
                rng, p["income_total"] * rng.uniform(0.05, 0.3), 2)
            p["goals"] = self._build_goals(rng, p["income_total"], 1.0, 2)
            p["bliq"] = _round2(p["income_total"] * rng.uniform(0.5, 6.0))
        elif kind == "pdn_boundary":
            target_pdn = rng.choice((0.38, 0.395, 0.40, 0.405, 0.42))
            p["obligations"] = self._build_obligations(
                rng, income * target_pdn, max(1, len(p["obligations"]) or 1))
        elif kind == "horizon_10y":
            self._seed_one_goal(p, rng)
            p["goals"][0]["deadline"] = t0 + timedelta(days=rng.randint(1830, 3650))
        return p

    def _seed_one_loan(self, p: dict, rng: Random) -> list[dict]:
        if not p["obligations"]:
            p["obligations"] = self._build_obligations(
                rng, max(p["income_total"], 40_000.0) * 0.15, 1)
        return p["obligations"]

    def _seed_one_goal(self, p: dict, rng: Random) -> list[dict]:
        if not p["goals"]:
            p["goals"] = self._build_goals(
                rng, max(p["income_total"], 40_000.0), 0.8, 1)
        return p["goals"]

    # ---------------------------------------------------------------- слой D
    def _gen_d(self, index: int) -> dict:
        kind = self._d_kind[index]
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng, force_obl=True, force_deadline=True)
        p["layer"], p["kind"] = "D", kind
        err = {
            "negative_income": "отрицательный income_total",
            "income_none": "income_total = null",
            "none_amount": "obligations[0].amount = null",
            "broken_date_string": "непарсящаяся дата дедлайна",
            "string_income": "income_total строкой",
            "missing_income_field": "нет поля income_total",
            "negative_amount": "отрицательное тело долга",
            "negative_rate": "отрицательная ставка",
            "absurd_rate_12": "ставка 1200% годовых",
            "rate_string": "ставка строкой",
            "goal_missing_deadline_key": "у цели нет ключа deadline",
            "duplicate_id": "дубль id в выгрузке (+битая дата как маркер)",
        }[kind]
        p["expected_error"] = err
        if kind == "negative_income":
            p["income_total"] = -abs(p["income_total"]) - 1.0
        elif kind == "income_none":
            p["income_total"] = None
        elif kind == "none_amount":
            p["obligations"][0]["amount"] = None
        elif kind == "broken_date_string":
            p["goals"][0]["deadline"] = "2026-13-45"
        elif kind == "string_income":
            p["income_total"] = "сто тысяч"
        elif kind == "missing_income_field":
            del p["income_total"]
        elif kind == "negative_amount":
            p["obligations"][0]["amount"] = -abs(p["obligations"][0]["amount"])
        elif kind == "negative_rate":
            p["obligations"][0]["interest_rate"] = -0.15
        elif kind == "absurd_rate_12":
            p["obligations"][0]["interest_rate"] = 12.0
        elif kind == "rate_string":
            p["obligations"][0]["interest_rate"] = "двадцать"
        elif kind == "goal_missing_deadline_key":
            del p["goals"][0]["deadline"]
        elif kind == "duplicate_id":
            p["id_override"] = f"SP3-{self._dup_target[index]:05d}"
            p["goals"][0]["deadline"] = "2026-02-30"
        return p

    # ---------------------------------------------------------------- слой E
    def _gen_e(self, index: int) -> dict:
        pid, role, rel, base_index = self._pair_of[index]
        base = self._gen_a(base_index, rng=self._rng(base_index, "epair"),
                           force_obl=True, force_deadline=True)
        base["layer"], base["kind"] = "E", "metamorphic"
        base.update({"pair_id": pid, "pair_role": "base", "pair_relation": rel})
        if role == "base":
            base["index"] = index
            return base

        twin = copy.deepcopy(base)
        twin["index"] = index
        twin["pair_role"] = "twin"
        if rel == "M1_income":
            twin["income_total"] = _round2(base["income_total"] * 1.01)
        elif rel == "M2_rate":
            for o in twin["obligations"]:
                o["interest_rate"] = round(o["interest_rate"] + 0.01, 4)
        elif rel == "M3_deadline":
            for g_ in twin["goals"]:
                if g_["deadline"] is not None:
                    g_["deadline"] = g_["deadline"] + timedelta(days=183)
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

    # --------------------------------------------------------------- фасады
    def generate(self, index: int) -> dict:
        if not 0 <= index < self.n:
            raise IndexError(index)
        layer = self.layer_by_index[index]
        if layer == "A":
            return self._gen_a(index)
        if layer == "B":
            return self._gen_b(index)
        if layer == "C":
            return self._gen_c(index)
        if layer == "D":
            return self._gen_d(index)
        return self._gen_e(index)

    def expert_row(self, index: int) -> dict:
        """Слепая проекция для экспертного пакета: id + 8 полей брифа."""
        p = self.generate(index)
        row = {"id": p.get("id_override", f"SP3-{index:05d}")}
        for field in EXPERT_FIELDS_V3:
            if field != "id" and field in p:
                row[field] = p[field]
        return row

    def coordinator_key(self, index: int) -> dict:
        """Ключ координатора: id -> метки (слепота экспертов сохраняется)."""
        p = self.generate(index)
        return {
            "id": f"SP3-{index:05d}",
            "layer": p["layer"],
            "kind": p["kind"],
            "pair_id": p.get("pair_id"),
            "pair_role": p.get("pair_role"),
            "pair_relation": p.get("pair_relation"),
            "expected_error": p.get("expected_error"),
            "id_override": p.get("id_override"),
        }

    def meta(self) -> dict:
        return {
            "__meta__": True,
            "dataset_version": 3,
            "generator": "tools/portrait_testing/generator_v3.py::PortraitGeneratorV3",
            "seed": self.seed,
            "n": self.n,
            "frozen_today": self.frozen_today.isoformat(),
            "layers": dict(self.quotas),
            "spearman_targets": {
                "goals_sum~income": "+0.30…0.50 (через демпфер income~k_goal "
                                    f"{SPEARMAN_TARGETS[('income', 'k_goal')]})",
                "expenses~payments": "+0.20…0.35",
            },
            "r_bench": {"law": "truncnorm", "anchor": R_BENCH_ANCHOR,
                        "sd": R_BENCH_SD, "range": [R_BENCH_LO, R_BENCH_HI]},
            "c_catalog": dict(_C_KINDS),
            "d_kinds": list(_D_KINDS),
            "e_relations": list(_E_RELATIONS),
            "deadlines": "относительные T+Δ от frozen_today; Δ ∈ [3; 120] мес; null ≈ 25%",
        }
