"""Генератор синтетических портретов v5 — итерация 5 сертификации модели.

Наследует машинерию v4 (LHS, копула Спирмена, аннуитетная согласованность,
метаморфические пары) и правит ровно то, что назвали четыре эксперта раунда 4.
ТЗ: `docs/model/expert_certification/iterations/4/expert_feedback_aggregate.md` §5.

Что изменено против v4 (номера — пункты ТЗ):

  1. Слепая `meta` объявляет то, чего аудитор не может проверить изнутри
     файла: долю стресс-магнитуд, долю остатков вне продуктовой спеки,
     ФАКТИЧЕСКИЙ диапазон k, KS слоя A, природу `risk_tolerance`. Шесть
     консенсусных проблем раунда 4 из шести — про слепоту метаданных, а не
     про содержание данных.
  2. Кап 1e8 на суммах целей снят: хвост непрерывный, стресс-магнитуды живут
     отдельным kind.
  3. Джиттер объёмов: доля дефектов и объёмы граничных категорий перестали
     быть круглыми — слой больше не реверсится одним группировочным запросом.
  4. Длинные горизонты 10–30 лет (пенсия, образование детей) — не менее 5%
     датированных целей. В v4 такая цель была ровно одна на 12 000 портретов.
  5. Кромка ПСК: валидные 2.90–2.92 и дефектные 2.93–3.00 (в v4 между
     легальным потолком и дефектом был провал — самая спорная зона `invalid`
     осталась без проб).
  6. Формы дублей `id`: пары, ТРОЙНИК и пара invalid+invalid. Сборщик,
     выучивший «дубль = ровно два», обязан упасть на приёмке, а не в проде.
  7. Легальные лимиты продуктов: экстремум долговой нагрузки набирается
     ЧИСЛОМ кредитов, а не остатком МФО в 3.66 млн ₽.
  8. Имя-специфичные капы сумм целей («Отпуск» на 4.76 млн — след
     масштабирования доходом кита без натурального предела).
  9. k целей зажат в заявленную спеку [0.2; 5.0].
 10. Слой D расширен на `expense_total`, `bliq`, `risk_tolerance`, `r_bench`,
     `monthly_payment`, `target_amount`; доля составных дефектов поднята с
     4% до ~15% слоя.
 11. Карта: минимальный платёж 2–5% остатка вместо interest-only со сроком
     850 месяцев.

Сверх ТЗ — два семейства под ПРЕДЗАРЕГИСТРИРОВАННЫЕ гипотезы раунда 5
(`docs/reports/testing/expert_certification_round4.md` §10):

  * `floor_edge` — полоса L_t ∈ [1; 2), давшая 52.6% всех расхождений раунда 4,
    с разрезом по наличию цели с дедлайном < 6 месяцев (H5-1);
  * `whale_thin_cushion` — кит с тонкой подушкой для проверки относительного
    капа floor (H5-2).

Без этих семейств гипотезы проверить нечем.

СБОРКА 2 (seed 20260723). Ревизия сборки 1 нашла: ячейки H5-1 (231/241) и
H5-2 (120) не добирали порог мощности 385, державшийся только на семействе
(592); хелпер `_seed_goal` оставлял 18 целей ровно по 384 000 ₽. Решение
владельца — регенерация: итерация последняя, объявленная потеря точности
(±6.4%/±8.9% вместо ±5%) неприемлема. Изменения: фиксированные квоты ячеек
(400+джиттер на 12 000), слой C 0.28 -> 0.33 за счёт A (мощность шести
остальных семейств сохранена), пол и k хелпера целей дрожат.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal
from random import Random

from tools.portrait_testing.generator_v4 import (  # noqa: F401
    E_RELATIONS,
    EXPERT_FIELDS_V4 as EXPERT_FIELDS_V5,
    GOAL_NAME_RANGES,
    K_GOAL_MAX,
    K_GOAL_MIN,
    K_GOAL_TOLERANCE,
    LOAN_PRODUCTS,
    PSK_RATE_CAP,
    PortraitGeneratorV4,
    R_BENCH_ANCHOR,
    R_BENCH_SD,
    STATUS_TARGETS,
    _round2,
    products_for_rate,
)

DATASET_VERSION = 5
# Сборка 1 (seed 20260722) объявила недобор ячеек H5-1/H5-2; сборка 2
# добирает их фиксированными квотами (решение владельца: итерация
# последняя, второго захода не будет).
DATASET_BUILD = 2
ID_PREFIX = "SP5"

# Ячейки предзарегистрированных гипотез (H5-1 — разрез кромки floor по
# наличию близкой цели, H5-2 — кит с тонкой подушкой). Порог мощности 385
# должен держаться НА КАЖДОЙ ЯЧЕЙКЕ, а не только на семействе — урок ревизии
# сборки 1 (231/241/120 при семействе 592). Квота фиксированная с джиттером
# вверх: гарантия >= базы и не-круглые объёмы (круглые — отпечаток дизайна).
H5_CELL_QUOTA_BASE = 400  # на 12 000; масштабируется пропорционально n
H5_CELL_KINDS = ("floor_edge_with_near_goal", "floor_edge_no_near_goal",
                 "whale_thin_cushion")

# ТЗ-8: натуральные пределы сумм по имени цели. Верх поднят там, где это
# осмысленно (образование, недвижимость), и опущен там, где имя физически
# ограничивает сумму. Кап 1e8 снят: «Инвестиционный портфель» и «Покупка
# недвижимости» уходят в непрерывный хвост (ТЗ-2).
GOAL_NAME_RANGES_V5: dict[str, tuple[float, float]] = {
    "Техника": (5_000, 400_000),
    "Отпуск": (30_000, 1_500_000),
    "Лечение": (20_000, 5_000_000),
    "Переезд": (50_000, 2_000_000),
    "Свадьба": (200_000, 3_000_000),
    "Образование": (100_000, 4_000_000),
    "Ремонт": (150_000, 4_000_000),
    "Автомобиль": (400_000, 8_000_000),
    "Первый взнос по ипотеке": (500_000, 12_000_000),
    "Обучение детей": (300_000, 15_000_000),
    "Пенсионный капитал": (1_000_000, 60_000_000),
    "Инвестиционный портфель": (300_000, 250_000_000),
    "Покупка недвижимости": (2_000_000, 120_000_000),
}

# ТЗ-8 бьёт по БЫТОВЫМ именам: претензия экспертов была к «Технике» на 2.45 млн
# и «Отпуску» на 4.76 млн. Инвестпортфель, недвижимость и пенсионный капитал
# по своей природе верхнего предела не имеют — их диапазон в каталоге
# ориентировочный, и хвост им обрезать нельзя (это же ТЗ-2).
UNBOUNDED_GOAL_NAMES = ("Инвестиционный портфель", "Покупка недвижимости",
                        "Пенсионный капитал")

# ТЗ-4: имена, которым положен длинный горизонт.
LONG_HORIZON_NAMES = ("Пенсионный капитал", "Обучение детей")
LONG_HORIZON_YEARS = (10, 30)

# ТЗ-7: легальные потолки остатка по продукту (не размер выборки, а право).
# МФО — 1 млн ₽ по 151-ФЗ для займов юрлицам/ИП; бытовой микрозаём меньше,
# но верхняя граница держится законом, а не фантазией генератора.
PRODUCT_LEGAL_CAP: dict[str, float] = {
    "mfo": 1_000_000.0,
    "card": 3_000_000.0,
    "installment": 1_000_000.0,
    "consumer": 5_000_000.0,
    "auto": 10_000_000.0,
    "mortgage": 60_000_000.0,
}

# ТЗ-11: карта гасится минимальным платежом 2–5% остатка.
CARD_MIN_PAYMENT_SHARE = (0.02, 0.05)

# ТЗ-5: кромка предельной ПСК. Валидная сторона вплотную к потолку,
# дефектная — сразу за ним, с шагом, который человек различает глазом.
PSK_EDGE_VALID = (2.90, 2.915, 2.92)
PSK_EDGE_DEFECT = (2.93, 2.95, 3.00)

# ТЗ-3: доля дефектов — диапазон, а не константа 5.00%.
DEFECT_SHARE_RANGE = (0.042, 0.058)
QUOTA_JITTER = 0.20  # ±20% на объём вида внутри семейства

LAYER_SHARES: tuple[tuple[str, float], ...] = (
    ("A", 0.31), ("B", 0.26), ("C", 0.33), ("D", 0.05), ("E", 0.05),
)

C_FAMILIES_V5: dict[str, tuple[str, ...]] = {
    "flow_edges": ("zero_income", "zero_expenses", "fcf_zero_exact",
                   "deficit_flow"),
    "debt_edges": ("overleveraged", "cheap_debts_only", "rate_eq_bench_exact",
                   "rate_near_bench", "card_minimum_payment", "growing_debt",
                   "toxic_mfo_thin_cushion", "psk_edge_valid"),
    "goal_edges": ("target_eq_current_kopeck", "overfunded_goal",
                   "goal_at_minimum", "eight_goals_same_deadline",
                   "five_goals", "six_goals", "seven_goals"),
    "deadline_edges": ("deadline_today_exact", "deadline_tomorrow",
                       "deadline_deep_overdue", "horizon_10y",
                       "horizon_30y_retirement"),
    "liquidity_edges": ("bliq_zero", "huge_bliq", "no_goals_no_debts",
                        "pdn_boundary"),
    "integrity_edges": ("duplicate_id_valid_pair", "duplicate_id_triple",
                        "magnitude_whale", "magnitude_stress"),
    # H5-1 / H5-2: семейства под предзарегистрированные гипотезы
    "floor_edge": ("floor_edge_with_near_goal", "floor_edge_no_near_goal",
                   "whale_thin_cushion"),
}

_C_KIND_WEIGHTS_V5: dict[str, int] = {
    "zero_income": 85, "zero_expenses": 85, "fcf_zero_exact": 100,
    "deficit_flow": 95,
    "overleveraged": 55, "cheap_debts_only": 50, "rate_eq_bench_exact": 55,
    "rate_near_bench": 50, "card_minimum_payment": 60, "growing_debt": 45,
    "toxic_mfo_thin_cushion": 60, "psk_edge_valid": 45,
    "target_eq_current_kopeck": 62, "overfunded_goal": 58,
    "goal_at_minimum": 52, "eight_goals_same_deadline": 52, "five_goals": 62,
    "six_goals": 52, "seven_goals": 52,
    "deadline_today_exact": 80, "deadline_tomorrow": 75,
    "deadline_deep_overdue": 80, "horizon_10y": 85,
    "horizon_30y_retirement": 90,
    # сборка 2: веса семейства подняты 362 -> 410 — при доле C 0.33 и
    # фиксированных квотах H5 неудачный джиттер −10% ронял семейство до 374,
    # ниже порога 385 (замерено самоаудитом на 12 000, seed 20260723)
    "bliq_zero": 104, "huge_bliq": 100, "no_goals_no_debts": 94,
    "pdn_boundary": 112,
    "duplicate_id_valid_pair": 150, "duplicate_id_triple": 72,
    "magnitude_whale": 88, "magnitude_stress": 82,
    # ячейки floor_edge и whale_thin_cushion раздаются НЕ отсюда:
    # у них фиксированные квоты H5_CELL_QUOTA_BASE (см. _rebuild_v5_layout)
}

# ТЗ-10: дефекты на всех полях схемы + составные ~15% слоя.
_D_KIND_WEIGHTS_V5: dict[str, int] = {
    # доход
    "negative_income": 32, "income_none": 28, "string_income": 26,
    "missing_income_field": 22, "near_bool_income": 16,
    # расходы (в v4 не били вообще)
    "negative_expense": 28, "expense_none": 22, "expense_string": 20,
    # ликвидность (в v4 не били вообще)
    "negative_bliq": 26, "bliq_string": 20,
    # профиль риска и бенчмарк (в v4 не били вообще)
    "risk_out_of_range": 24, "risk_string": 18, "r_bench_negative": 20,
    "r_bench_absurd": 18,
    # обязательства
    "negative_amount": 34, "none_amount": 30, "negative_rate": 28,
    "absurd_rate_12": 24, "rate_string": 22,
    "negative_payment": 26, "payment_none": 20,
    "near_rate_above_cap": 28, "near_empty_string_amount": 18,
    # цели
    "goal_missing_deadline_key": 26, "broken_date_string": 30,
    "near_date_feb30": 16, "negative_target": 24, "target_none": 18,
    # целостность
    "duplicate_id_broken": 24, "duplicate_id_invalid_pair": 22,
    # составные — 15% слоя
    "composite_negative_and_broken_date": 30,
    "composite_none_and_string": 28,
    "composite_rate_and_payment": 26,
    "composite_triple_field": 24,
}

# Поле, по которому бьёт каждый вид дефекта — для покрытия схемы (ТЗ-10).
D_KIND_FIELD: dict[str, str] = {
    "negative_income": "income_total", "income_none": "income_total",
    "string_income": "income_total", "missing_income_field": "income_total",
    "near_bool_income": "income_total",
    "negative_expense": "expense_total", "expense_none": "expense_total",
    "expense_string": "expense_total",
    "negative_bliq": "bliq", "bliq_string": "bliq",
    "risk_out_of_range": "risk_tolerance", "risk_string": "risk_tolerance",
    "r_bench_negative": "r_bench", "r_bench_absurd": "r_bench",
    "negative_amount": "obligations.amount",
    "none_amount": "obligations.amount",
    "near_empty_string_amount": "obligations.amount",
    "negative_rate": "obligations.interest_rate",
    "absurd_rate_12": "obligations.interest_rate",
    "rate_string": "obligations.interest_rate",
    "near_rate_above_cap": "obligations.interest_rate",
    "negative_payment": "obligations.monthly_payment",
    "payment_none": "obligations.monthly_payment",
    "goal_missing_deadline_key": "goals.deadline",
    "broken_date_string": "goals.deadline",
    "near_date_feb30": "goals.deadline",
    "negative_target": "goals.target_amount",
    "target_none": "goals.target_amount",
    "duplicate_id_broken": "id", "duplicate_id_invalid_pair": "id",
    "composite_negative_and_broken_date": "composite",
    "composite_none_and_string": "composite",
    "composite_rate_and_payment": "composite",
    "composite_triple_field": "composite",
}


class PortraitGeneratorV5(PortraitGeneratorV4):
    """Датасет v5. Совместим по интерфейсу с v4 (generate/expert_row/meta)."""

    def __init__(self, seed: int = 20260723, n: int = 12000,
                 frozen_today: date | None = None):
        self._v5_seed = seed
        super().__init__(seed=seed, n=n,
                         frozen_today=frozen_today or date(2026, 7, 23))
        self._rebuild_v5_layout()

    # ------------------------------------------------------------- раскладка
    def _rebuild_v5_layout(self) -> None:
        """Пересборка раскладки слоёв и видов по правилам v5 (ТЗ-3, ТЗ-6)."""
        master = Random(f"v5:{self.seed}:layout")
        quotas = self._jittered_quotas(master, self.n)
        tags: list[str] = []
        for tag, q in quotas:
            tags.extend([tag] * q)
        master.shuffle(tags)
        self.layer_by_index = tags
        self.quotas = dict(quotas)

        by_layer: dict[str, list[int]] = {t: [] for t, _ in LAYER_SHARES}
        for idx, tag in enumerate(tags):
            by_layer[tag].append(idx)
        self._by_layer = by_layer

        self._kind_family = {k: fam for fam, kinds in C_FAMILIES_V5.items()
                             for k in kinds}
        cell_base = max(1, round(H5_CELL_QUOTA_BASE * self.n / 12000))
        cell_jit = max(3, cell_base // 12)
        fixed = {k: cell_base + master.randint(0, cell_jit)
                 for k in H5_CELL_KINDS}
        self._c_kind = self._deal_jittered(
            master, by_layer["C"], _C_KIND_WEIGHTS_V5,
            pair_kinds=("duplicate_id_valid_pair",),
            triple_kinds=("duplicate_id_triple",),
            fixed_quotas=fixed)
        self._d_kind = self._deal_jittered(
            master, by_layer["D"], _D_KIND_WEIGHTS_V5,
            pair_kinds=("duplicate_id_invalid_pair",))

        clean = by_layer["A"] + by_layer["B"]
        self._dup_target = {
            idx: master.choice(clean)
            for idx, kind in self._d_kind.items()
            if kind == "duplicate_id_broken"
        }

        # ТЗ-6: три формы дублей — пара валидных, тройник, пара invalid.
        self._valid_dup_pair = {}
        pairs = sorted(i for i, k in self._c_kind.items()
                       if k == "duplicate_id_valid_pair")
        for t in range(len(pairs) // 2):
            a, b = pairs[2 * t], pairs[2 * t + 1]
            shared = f"{ID_PREFIX}-{a:05d}"
            self._valid_dup_pair[a] = (t, shared)
            self._valid_dup_pair[b] = (t, shared)
        triples = sorted(i for i, k in self._c_kind.items()
                         if k == "duplicate_id_triple")
        base_t = len(pairs) // 2
        for t in range(len(triples) // 3):
            grp = triples[3 * t:3 * t + 3]
            shared = f"{ID_PREFIX}-{grp[0]:05d}"
            for i in grp:
                self._valid_dup_pair[i] = (base_t + t, shared)
        inv_pairs = sorted(i for i, k in self._d_kind.items()
                           if k == "duplicate_id_invalid_pair")
        base_i = base_t + len(triples) // 3
        for t in range(len(inv_pairs) // 2):
            a, b = inv_pairs[2 * t], inv_pairs[2 * t + 1]
            shared = f"{ID_PREFIX}-{a:05d}"
            self._valid_dup_pair[a] = (base_i + t, shared)
            self._valid_dup_pair[b] = (base_i + t, shared)

        self._pair_of = {}
        e_idx = by_layer["E"]
        for t in range(len(e_idx) // 2):
            base, twin = e_idx[2 * t], e_idx[2 * t + 1]
            rel = E_RELATIONS[t % len(E_RELATIONS)]
            pid = f"E5-{t:04d}"
            self._pair_of[base] = (pid, "base", rel, base)
            self._pair_of[twin] = (pid, "twin", rel, base)

        nb = len(by_layer["B"])
        self._b_order = {idx: pos for pos, idx in enumerate(by_layer["B"])}
        self._nb = nb
        self._lhs = {
            axis: master.sample(range(nb), nb) if nb else []
            for axis in ("income", "exp_ratio", "pdn", "liq", "n_obl",
                         "spread", "n_goals", "deadline", "readiness", "risk")
        }

    @staticmethod
    def _jittered_quotas(master: Random,
                         n: int) -> tuple[tuple[str, int], ...]:
        """ТЗ-3: объёмы слоёв дрожат, доля дефектов — диапазон 4.2-5.8%."""
        d_share = master.uniform(*DEFECT_SHARE_RANGE)
        e_share = master.uniform(0.045, 0.055)
        rest = 1.0 - d_share - e_share
        # Сборка 2: C вырос 0.28 -> 0.33 за счёт A (0.36 -> 0.31), чтобы
        # фиксированные квоты ячеек H5 (~1200) не отняли мощность у шести
        # остальных семейств слоя C (порог 385 у каждого).
        base = {"A": 0.31, "B": 0.26, "C": 0.33}
        norm = sum(base.values())
        out, acc = [], 0
        plan = [("A", rest * base["A"] / norm), ("B", rest * base["B"] / norm),
                ("C", rest * base["C"] / norm), ("D", d_share),
                ("E", e_share)]
        for i, (tag, share) in enumerate(plan):
            take = n - acc if i == len(plan) - 1 else int(round(n * share))
            if tag == "E":
                take -= take % 2
            out.append((tag, take))
            acc += take
        if acc != n:
            tag, take = out[0]
            out[0] = (tag, take + (n - acc))
        return tuple(out)

    @staticmethod
    def _deal_jittered(master: Random, indices: list[int],
                       weights: dict[str, int],
                       pair_kinds: tuple[str, ...] = (),
                       triple_kinds: tuple[str, ...] = (),
                       fixed_quotas: dict[str, int] | None = None,
                       ) -> dict[int, str]:
        """Раздача видов с дрожанием объёма ±20% (ТЗ-3).

        `fixed_quotas` — виды с гарантированным объёмом (ячейки
        предзарегистрированных гипотез): раздаются первыми ровно своей
        квотой, джиттер ±20% на них не действует — иначе порог мощности 385
        держится только в среднем, а не на каждой сборке.
        """
        fixed_quotas = dict(fixed_quotas or {})
        pool: list[str] = []
        for kind, quota in fixed_quotas.items():
            room = len(indices) - len(pool)
            if room <= 0:
                break
            pool.extend([kind] * min(quota, room))
        rest = {k: w for k, w in weights.items() if k not in fixed_quotas}
        jittered = {k: max(1, w * (1.0 + master.uniform(-QUOTA_JITTER,
                                                        QUOTA_JITTER)))
                    for k, w in rest.items()}
        total = sum(jittered.values())
        share = (len(indices) - len(pool)) / total if total else 0
        for kind, w in jittered.items():
            take = max(1, int(round(w * share)))
            if kind in pair_kinds and take % 2:
                take += 1
            if kind in triple_kinds and take % 3:
                take += 3 - take % 3
            pool.extend([kind] * take)
        grouped = {k: 2 for k in pair_kinds} | {k: 3 for k in triple_kinds}
        candidates = rest or weights
        loose = {k: w for k, w in candidates.items() if k not in grouped}
        fill = max(loose or candidates, key=(loose or candidates).get)
        while len(pool) < len(indices):
            pool.append(fill)
        del pool[len(indices):]
        # Обрезка и добивка могли порвать групповые виды (пара с нечётным
        # объёмом, тройник из четырёх) — тогда сборка групп молча теряет
        # хвостовой индекс и генерация падает KeyError. Ремонт: лишние
        # члены группы с хвоста демотируются в одиночный вид.
        for kind, m in grouped.items():
            extra = pool.count(kind) % m
            idx = len(pool) - 1
            while extra and idx >= 0:
                if pool[idx] == kind:
                    pool[idx] = fill
                    extra -= 1
                idx -= 1
        master.shuffle(pool)
        return dict(zip(indices, pool))

    def _rng(self, index: int, tag: str = "content") -> Random:
        return Random(f"v5:{self.seed}:{tag}:{index}")

    # ------------------------------------------------------------- продукты
    @staticmethod
    def _loan_record(product: str, rate: float, term: int, amount: float,
                     payment: float) -> dict:
        """ТЗ-7 и ТЗ-11: легальный потолок остатка + минимальный платёж карты.

        Потолок применяется к остатку, платёж пересчитывается пропорционально,
        чтобы аннуитетная согласованность (ставка-срок-остаток-платёж) не
        поехала — иначе приёмочный тест продуктовой типизации сломается.
        """
        cap = PRODUCT_LEGAL_CAP.get(product)
        if cap is not None and amount > cap > 0:
            payment *= cap / amount
            amount = cap
        if product == "card" and amount > 0:
            share = Random(f"card:{round(amount, 2)}:{round(rate, 4)}").uniform(
                *CARD_MIN_PAYMENT_SHARE)
            payment = amount * share
            term = max(1, int(math.ceil(amount / payment)))
        return PortraitGeneratorV4._loan_record(product, rate, term, amount,
                                                payment)

    # ---------------------------------------------------------------- цели
    @staticmethod
    def _goal_name(rng: Random, amount: float) -> tuple[str, float]:
        """ТЗ-8: имя выбирается под сумму, сумма зажимается натуральным капом.

        Если сумма выше всех бытовых пределов — имя меняется на подходящее
        крупное, а не остаётся «Отпуском» на 4.76 млн ₽ (находка S(P3)).
        """
        fits = [n for n, (lo, hi) in GOAL_NAME_RANGES_V5.items()
                if lo <= amount <= hi]
        if fits:
            return rng.choice(fits), amount
        widest = max(GOAL_NAME_RANGES_V5.items(), key=lambda kv: kv[1][1])
        if amount > widest[1][1]:
            # выше всех бытовых пределов — имя обязано быть безлимитным
            return rng.choice(UNBOUNDED_GOAL_NAMES), amount
        # Сумма ниже всех минимумов — берём самое «дешёвое» имя и НЕ
        # подтягиваем сумму к границе: снэп на минимум даёт кучу одинаковых
        # значений, то есть тот же обрезанный хвост, только снизу.
        name = min(GOAL_NAME_RANGES_V5.items(), key=lambda kv: kv[1][0])[0]
        hi = GOAL_NAME_RANGES_V5[name][1]
        return name, min(amount, hi)

    def _long_horizon_goal(self, rng: Random, income: float) -> dict:
        """ТЗ-4: пенсия и образование детей — горизонт 10-30 лет."""
        name = rng.choice(LONG_HORIZON_NAMES)
        lo, hi = GOAL_NAME_RANGES_V5[name]
        target = _round2(rng.uniform(lo, min(hi, max(lo * 1.5,
                                                     income * 12 * 4))))
        years = rng.randint(*LONG_HORIZON_YEARS)
        return {
            "name": name,
            "target_amount": target,
            "current_amount": _round2(target * rng.uniform(0.0, 0.25)),
            "deadline": self.frozen_today + timedelta(days=int(365.25 * years)),
        }

    def _seed_goal(self, p: dict, rng: Random) -> None:
        """Хелпер «портрету нужна хоть одна цель» — без следа-константы.

        Сборка 1 оставляла 18 целей ровно по 384 000.00 ₽: у v4-хелпера при
        доходе ниже пола сумма считалась как 40 000 x 0.8 x 12 — то же
        скопление одного значения, что и снэп на 5 000 ₽, только из другого
        угла. Пол дохода и k дрожат — совпадение до копейки исчезает.
        """
        if p["goals"]:
            return
        income = p.get("income_total")
        base = (float(income) if isinstance(income, (int, float))
                and not isinstance(income, bool) and income > 0 else 0.0)
        floor = rng.uniform(34_000.0, 56_000.0)
        p["goals"] = self._build_goals(rng, max(base, floor),
                                       rng.uniform(0.55, 1.05), 1)

    def _make_pdn_exact(self, p: dict, rng: Random) -> None:
        """Точная граница ПДН, переживающая конвейер v5.

        v4-конструкция ломалась дальше по конвейеру: карта пересобирает платёж
        от остатка (ТЗ-11), легальный кап рескейлит его пропорционально (ТЗ-7)
        — и точное отношение платежей к доходу исчезало. В сборке 1 из ~130
        записей вида доживало 11, в сборке 2 без починки — 5. Здесь: продукт
        выбирается без карты, want запоминается маркером, а generate()
        восстанавливает платёж ПОСЛЕ капов. Аннуитетная согласованность для
        слоя C по методичке не требуется (§3.4 — «кроме C/D by design»).
        Вес точного 0.40 удвоен: строгость «<= 0.40» проверяется на ~40
        записях, а не на пяти.
        """
        base = int(p["income_total"] or 100_000)
        base -= base % 5  # кратность 5 ₽: want целый, want/income даёт ровно
        income = float(base or 100_000)  # fl(0.40) без двойного округления
        target = Decimal(str(rng.choice((0.38, 0.395, 0.40, 0.40,
                                         0.405, 0.42))))
        want = float((Decimal(str(income)) * target).quantize(Decimal("0.01")))
        p["income_total"] = income
        keys = [k for k in LOAN_PRODUCTS if k != "card"]
        weights = [LOAN_PRODUCTS[k]["weight"] for k in keys]
        product = self._weighted_order(rng, keys, weights)[0]
        loan = self._loan_from_payment(rng, want, strict_amount=False,
                                       force_product=product)
        if loan is None:
            loan = self._loan_from_payment(rng, want, strict_amount=False)
        if loan:
            loan = dict(loan, id=1)
            loan["monthly_payment"] = want
            p["obligations"] = [loan]
            p["_pdn_exact_want"] = want
        else:
            p["obligations"] = []
        p["expense_total"] = _round2(min(p["expense_total"],
                                         max(income - want - 1.0, 0.0)))

    # ------------------------------------------------------- слой C: виды v5
    def _gen_c(self, index: int) -> dict:
        kind = self._c_kind[index]
        if kind in ("floor_edge_with_near_goal", "floor_edge_no_near_goal",
                    "whale_thin_cushion", "psk_edge_valid", "overleveraged",
                    "card_minimum_payment", "horizon_30y_retirement",
                    "duplicate_id_triple"):
            return self._gen_c_v5(index, kind)
        p = super()._gen_c(index)
        p["family"] = self._kind_family.get(p.get("kind"), p.get("family", ""))
        return p

    def _gen_c_v5(self, index: int, kind: str) -> dict:
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng)
        p["layer"] = "C"
        p["kind"] = kind
        p["family"] = self._kind_family[kind]
        if kind == "duplicate_id_triple":
            grp_no, shared = self._valid_dup_pair[index]
            p["id_override"] = shared
            p["pair_id"] = f"DUP3-{grp_no:04d}"
        elif kind == "overleveraged":
            # ТЗ-7: нагрузка набирается ЧИСЛОМ кредитов в легальных пределах,
            # а не одним займом МФО на 3.66 млн ₽.
            payments = p["income_total"] * rng.uniform(0.55, 0.85)
            p["obligations"] = self._build_obligations(
                rng, payments, rng.randint(5, 8), strict_amount=True)
        elif kind == "psk_edge_valid":
            self._seed_loan_at_rate(p, rng, rng.choice(PSK_EDGE_VALID))
        elif kind == "card_minimum_payment":
            self._seed_loan(p, rng, product="card")
        elif kind == "horizon_30y_retirement":
            p["goals"] = (p.get("goals") or [])[:2]
            p["goals"].append(self._long_horizon_goal(rng, p["income_total"]))
        elif kind == "whale_thin_cushion":
            # H5-2: доход реалистичного кита (ТЗ итерации 3 п.4 — 5-10 млн),
            # а подушка при этом в спорной полосе L_t in [1; 2). Смысл
            # семейства: при таком доходе «запас два месяца расходов» — это
            # десятки миллионов в кэше, и вопрос в том, остаётся ли правило
            # абсолютным или запас должен считаться от активов.
            self._make_whale(p, rng, rng.uniform(5_000_000, 10_000_000))
            self._seed_loan(p, rng, product="consumer")
            p["bliq"] = _round2(p["expense_total"] * rng.uniform(1.05, 1.95))
        else:  # кромка floor: L_t в [1; 2)
            p["bliq"] = _round2(max(p["expense_total"], 1.0)
                                * rng.uniform(1.02, 1.97))
            if not p["obligations"]:
                self._seed_loan(p, rng, product="consumer")
            near = kind == "floor_edge_with_near_goal"
            goals = p.get("goals") or []
            if not goals:
                self._seed_goal(p, rng)
                goals = p["goals"]
            if near:
                goals[0]["deadline"] = self.frozen_today + timedelta(
                    days=rng.randint(20, 170))
            else:
                for g in goals:
                    if g.get("deadline") is not None:
                        g["deadline"] = self.frozen_today + timedelta(
                            days=rng.randint(400, 1500))
        return p

    # ------------------------------------------------------- слой D: виды v5
    D_FIELD_FALLBACK = "unclassified"

    def _gen_d(self, index: int) -> dict:
        kind = self._d_kind[index]
        if kind in D_KIND_FIELD and not hasattr(
                self, f"_v4_has_{kind}") and kind in _D_KIND_WEIGHTS_V5:
            p = self._gen_d_v5(index, kind)
            if p is not None:
                return p
        p = super()._gen_d(index)
        # v4 писал в expected_error человеческую фразу («отрицательное тело
        # долга»). Для приёмки нужна машинная таксономия «поле:вид», иначе
        # мощность страт считается по видам и валится ниже порога.
        field = D_KIND_FIELD.get(p.get("kind"), self.D_FIELD_FALLBACK)
        p["expected_error"] = f"{field}:{p.get('kind')}"
        return p

    def _gen_d_v5(self, index: int, kind: str) -> dict | None:
        rng = self._rng(index)
        p = self._gen_a(index, rng=rng)
        p["layer"] = "D"
        p["kind"] = kind
        p["family"] = "defects"
        p["expected_error"] = f"{D_KIND_FIELD[kind]}:{kind}"
        if not p.get("obligations"):
            self._seed_loan(p, rng, product="consumer")
        if not p.get("goals"):
            self._seed_goal(p, rng)
        o, g = p["obligations"][0], p["goals"][0]

        if kind == "negative_expense":
            p["expense_total"] = -abs(p["expense_total"]) - 1000.0
        elif kind == "expense_none":
            p["expense_total"] = None
        elif kind == "expense_string":
            p["expense_total"] = "сорок тысяч"
        elif kind == "negative_bliq":
            p["bliq"] = -abs(p["bliq"]) - 500.0
        elif kind == "bliq_string":
            p["bliq"] = "нет данных"
        elif kind == "risk_out_of_range":
            p["risk_tolerance"] = rng.choice([0, 6, 9, -1])
        elif kind == "risk_string":
            p["risk_tolerance"] = "средний"
        elif kind == "r_bench_negative":
            p["r_bench"] = -0.05
        elif kind == "r_bench_absurd":
            p["r_bench"] = rng.choice([4.5, 12.0])
        elif kind == "negative_payment":
            o["monthly_payment"] = -abs(o["monthly_payment"])
        elif kind == "payment_none":
            o["monthly_payment"] = None
        elif kind == "negative_target":
            g["target_amount"] = -abs(g["target_amount"])
        elif kind == "target_none":
            g["target_amount"] = None
        elif kind == "near_rate_above_cap":
            o["interest_rate"] = rng.choice(PSK_EDGE_DEFECT)
        elif kind == "duplicate_id_invalid_pair":
            grp_no, shared = self._valid_dup_pair[index]
            p["id_override"] = shared
            p["pair_id"] = f"DUPI-{grp_no:04d}"
            p["income_total"] = None
            p["expected_error"] = "id:duplicate_id_invalid_pair+income_none"
        elif kind == "composite_rate_and_payment":
            o["interest_rate"] = "0,35"
            o["monthly_payment"] = -1.0
        elif kind == "composite_triple_field":
            p["expense_total"] = None
            o["amount"] = -50_000.0
            g["deadline"] = "2026-02-30"
        else:
            return None
        return p

    # ------------------------------------------------------------- фасады
    def blind_declarations(self) -> dict:
        """Агрегаты для усечённой `meta` слепого пакета — ТЗ п.1 раунда 4.

        Все четыре эксперта раунда 4 независимо написали одно и то же: по данным
        невозможно отличить НАМЕРЕННЫЙ дизайн от ДЕФЕКТА генератора, и ревью
        уходит в перечисление подозрений вместо финансовых решений. Здесь
        объявляются ровно те доли, которые снимают шесть консенсусных претензий,
        и ни одна из них не раскрывает, КАКАЯ запись к чему относится: слои,
        виды и пары по-прежнему скрыты.

        Считается один раз за прогон и кэшируется.
        """
        if getattr(self, "_declarations", None) is not None:
            return self._declarations

        def _num(x: object) -> bool:
            return isinstance(x, (int, float)) and not isinstance(x, bool)

        by_name = {spec["name"]: spec for spec in LOAN_PRODUCTS.values()}
        stress = whale = 0
        loans = oos = 0
        goals = out_of_band = 0
        ks: list[float] = []
        logs: list[float] = []
        risk: dict[int, int] = {}
        for i in range(self.n):
            p = self.generate(i)
            kind = p.get("kind")
            if kind == "magnitude_stress":
                stress += 1
            elif kind in ("magnitude_whale", "whale_thin_cushion"):
                whale += 1
            for o in p.get("obligations") or ():
                loans += 1
                spec = by_name.get(o.get("name"))
                if spec and _num(o.get("amount")) and not (
                        spec["amount"][0] * 0.999 <= o["amount"]
                        <= spec["amount"][1] * 1.001):
                    oos += 1
            for g in p.get("goals") or ():
                goals += 1
                band = GOAL_NAME_RANGES_V5.get(g.get("name"))
                if (p["layer"] != "D" and band and _num(g.get("target_amount"))
                        and not (band[0] * 0.999 <= g["target_amount"]
                                 <= band[1] * 1.001)):
                    out_of_band += 1
            inc = p.get("income_total")
            if _num(inc) and inc > 0:
                if p["layer"] == "A":
                    logs.append(math.log(inc))
                if p["layer"] != "D" and p.get("goals"):
                    ks.append(sum(g["target_amount"] for g in p["goals"]
                                  if _num(g.get("target_amount")))
                              / (12.0 * inc))
            rt = p.get("risk_tolerance")
            if isinstance(rt, int) and not isinstance(rt, bool) and 1 <= rt <= 5:
                risk[rt] = risk.get(rt, 0) + 1

        mu = sum(logs) / len(logs)
        sd = (sum((x - mu) ** 2 for x in logs) / len(logs)) ** 0.5
        ordered = sorted(logs)
        ks_stat = 0.0
        for idx, x in enumerate(ordered):
            cdf = 0.5 * (1.0 + math.erf((x - mu) / (sd * math.sqrt(2.0))))
            ks_stat = max(ks_stat, abs((idx + 1) / len(ordered) - cdf),
                          abs(cdf - idx / len(ordered)))

        self._declarations = {
            "stress_magnitude_share": round(stress / self.n, 4),
            "realistic_whale_share": round(whale / self.n, 4),
            "loan_amount_outside_product_spec_share": round(oos / loans, 4),
            "goal_amount_outside_name_band_share": round(out_of_band / goals, 4),
            "k_goal_actual_range": [round(min(ks), 4), round(max(ks), 4)],
            "k_goal_declared_range": [K_GOAL_MIN, K_GOAL_MAX],
            "income_lognormal_ks_population": round(ks_stat, 4),
            "risk_tolerance_note": (
                "равномерен by design (примерно по 1/5 на профиль) — это НЕ "
                "популяционная доля риск-профилей в России"
            ),
            "notes": (
                "Доли объявлены, чтобы отличать намеренный дизайн от дефекта "
                "генератора. Остаток кредита выходит за продуктовую спеку "
                "намеренно — так набирается экстремум долговой нагрузки; суммы "
                "целей выходят за диапазон имени у стресс-магнитуд и у части "
                "масштабированных портретов. Какая запись к чему относится — "
                "не раскрывается."
            ),
        }
        return self._declarations

    def expert_row(self, index: int) -> dict:
        p = self.generate(index)
        row = {"id": p.get("id_override", f"{ID_PREFIX}-{index:05d}")}
        for field in EXPERT_FIELDS_V5:
            if field != "id" and field in p:
                row[field] = p[field]
        return row

    def coordinator_key(self, index: int) -> dict:
        key = super().coordinator_key(index)
        key["id"] = f"{ID_PREFIX}-{index:05d}"
        return key

    def generate(self, index: int) -> dict:
        p = super().generate(index)
        # v4 зашивал префикс `SP4-` прямо в ветку `duplicate_id_broken`.
        # Унаследованный как есть, он помечал бы битые строки датасета v5
        # чужим префиксом — то есть выдавал бы слой дефектов одним grep.
        override = p.get("id_override")
        if isinstance(override, str) and not override.startswith(ID_PREFIX):
            p["id_override"] = ID_PREFIX + override[override.index("-"):]
        if p["layer"] not in ("D", "E"):
            rng = self._rng(index, "goalpolicy")
            self._inject_long_horizon(p, rng)
            self._apply_v5_goal_policy(p, rng)
            self._apply_legal_caps(p)
            self._renumber_goals(p)
        want = p.pop("_pdn_exact_want", None)
        if want is not None and p.get("obligations"):
            # капы могли рескейлить платёж — точная граница восстанавливается
            # последним шагом, это смысл вида pdn_boundary
            p["obligations"][0]["monthly_payment"] = want
        return p

    @staticmethod
    def _renumber_goals(p: dict) -> None:
        """Сквозная нумерация целей: новые виды v5 добавляют цели после
        сборки портрета, а планировщик адресует их по `id`."""
        for k, g in enumerate(p.get("goals") or (), start=1):
            g["id"] = k

    def _inject_long_horizon(self, p: dict, rng: Random) -> None:
        """ТЗ-4: пенсия и образование детей — не менее 5% датированных целей.

        В v4 длиннее 10 лет была РОВНО ОДНА цель на 12 000 портретов, то есть
        главный длинный кейс советника не тестировался вовсе.
        """
        goals = p.get("goals") or []
        if not goals or p.get("kind") in ("magnitude_stress", "no_goals_no_debts"):
            return
        dated = [g for g in goals if g.get("deadline") is not None]
        if not dated or rng.random() >= 0.17:
            return
        income = p.get("income_total")
        if not isinstance(income, (int, float)) or income <= 0:
            return
        victim = rng.choice(dated)
        long_goal = self._long_horizon_goal(rng, float(income))
        victim.update(long_goal)

    @staticmethod
    def _apply_legal_caps(p: dict) -> None:
        """ТЗ-7: остаток не выходит за правовой потолок продукта.

        DOE-ось нагрузки в v4 раздувала остаток МФО до 3.66 млн ₽ — это
        36 легальных лимитов; эксперты назвали это первым же запросом.
        """
        for o in p.get("obligations") or ():
            amount, rate = o.get("amount"), o.get("interest_rate")
            if not isinstance(amount, (int, float)) or \
                    not isinstance(rate, (int, float)) or amount <= 0:
                continue
            fits = products_for_rate(rate)
            if not fits:
                continue
            cap = max(PRODUCT_LEGAL_CAP.get(k, amount) for k in fits)
            if amount > cap:
                pay = o.get("monthly_payment")
                if isinstance(pay, (int, float)):
                    o["monthly_payment"] = _round2(pay * cap / amount)
                o["amount"] = _round2(cap)

    def _apply_v5_goal_policy(self, p: dict, rng: Random) -> None:
        """ТЗ-8 и ТЗ-9: натуральные капы имён и k в заявленной спеке."""
        goals = p.get("goals") or []
        if not goals:
            return
        for g in goals:
            amount = g.get("target_amount")
            if not isinstance(amount, (int, float)):
                continue
            name, fixed = self._goal_name(rng, float(amount))
            if p.get("kind") not in ("magnitude_stress", "magnitude_whale",
                                     "whale_thin_cushion"):
                g["name"], g["target_amount"] = name, _round2(fixed)
                if g.get("current_amount", 0) > g["target_amount"]:
                    g["current_amount"] = _round2(
                        g["target_amount"] * rng.uniform(0.0, 0.95))
        income = p.get("income_total")
        if not isinstance(income, (int, float)) or income <= 0:
            return
        annual = income * 12.0
        total = sum(g["target_amount"] for g in goals
                    if isinstance(g.get("target_amount"), (int, float)))
        if total <= 0:
            return
        k = total / annual
        if K_GOAL_MIN <= k <= K_GOAL_MAX:
            return
        # запас 0.5%: округление до копейки после масштабирования иначе
        # выносит фактический k за заявленную границу (было 5.0077 при 5.0)
        target_k = K_GOAL_MIN * 1.005 if k < K_GOAL_MIN else K_GOAL_MAX * 0.995
        factor = target_k / k
        stress = p.get("kind") in ("magnitude_stress", "magnitude_whale",
                                   "whale_thin_cushion")
        for g in goals:
            if not isinstance(g.get("target_amount"), (int, float)):
                continue
            g["target_amount"] = _round2(g["target_amount"] * factor)
            if not stress:
                # кламп k мог вывести сумму за натуральный предел имени —
                # имя пересогласуется повторно, иначе «Отпуск» уезжает в
                # миллионы (находка S(P3), из-за которой ТЗ-8 и появился)
                name, fixed = self._goal_name(rng, g["target_amount"])
                g["name"], g["target_amount"] = name, _round2(fixed)
            cur = g.get("current_amount") or 0
            if cur > g["target_amount"]:
                g["current_amount"] = _round2(g["target_amount"] * 0.9)

    # --------------------------------------------------------------- meta
    def meta(self) -> dict:
        """Слепая meta v5: объявляет то, что аудитор не проверит изнутри."""
        stress = out_of_spec = loans = 0
        ks: list[float] = []
        for i in range(self.n):
            p = self.generate(i)
            if p.get("kind") in ("magnitude_stress", "magnitude_whale",
                                 "whale_thin_cushion"):
                stress += 1
            for o in p.get("obligations") or ():
                amount, rate = o.get("amount"), o.get("interest_rate")
                if not isinstance(amount, (int, float)) or \
                        not isinstance(rate, (int, float)):
                    continue
                loans += 1
                fits = [k for k in products_for_rate(rate)
                        if LOAN_PRODUCTS[k]["amount"][0] <= amount
                        <= LOAN_PRODUCTS[k]["amount"][1]]
                if not fits:
                    out_of_spec += 1
            income = p.get("income_total")
            goals = p.get("goals") or []
            if isinstance(income, (int, float)) and income > 0 and goals:
                total = sum(g["target_amount"] for g in goals
                            if isinstance(g.get("target_amount"),
                                          (int, float)))
                if total > 0:
                    ks.append(total / (income * 12.0))
        base = super().meta()
        base.update({
            "dataset_version": DATASET_VERSION,
            "dataset_build": DATASET_BUILD,
            "generator": "tools/portrait_testing/generator_v5.py::"
                         "PortraitGeneratorV5",
            "id_prefix": ID_PREFIX,
            "goal_name_ranges": GOAL_NAME_RANGES_V5,
            "product_legal_cap": PRODUCT_LEGAL_CAP,
            "psk_edge": {"valid": list(PSK_EDGE_VALID),
                         "defect": list(PSK_EDGE_DEFECT)},
            "c_families": {f: list(k) for f, k in C_FAMILIES_V5.items()},
            "d_kinds": sorted(_D_KIND_WEIGHTS_V5),
            # --- декларации, которых требовали все четверо (ТЗ-1) ---
            "stress_magnitude_share": round(stress / self.n, 4),
            "loan_amount_out_of_spec_share": (round(out_of_spec / loans, 4)
                                              if loans else 0.0),
            "duplicate_id_shapes": ["pair_valid", "triple_valid",
                                    "pair_invalid", "broken_single"],
            "long_horizon_years": list(LONG_HORIZON_YEARS),
            "card_min_payment_share": list(CARD_MIN_PAYMENT_SHARE),
        })
        base["k_goal_spec"] = {
            "definition": "сумма target по портрету / годовой доход",
            "range": [K_GOAL_MIN, K_GOAL_MAX],
            "tolerance": K_GOAL_TOLERANCE,
            "enforced_by": "каталог имён + масштабирование + кламп на портрете",
            "actual_range": ([round(min(ks), 4), round(max(ks), 4)]
                             if ks else [0.0, 0.0]),
        }
        base["notes"] = dict(base.get("notes") or {})
        base["notes"].update({
            "risk_tolerance": "равномерен BY DESIGN (DOE-покрытие профилей), "
                              "НЕ популяционная доля — не использовать для "
                              "выводов о доле агрессивных инвесторов",
            "stress_magnitudes": "стресс-величины вынесены отдельными видами; "
                                 "популяционные агрегаты считать без них",
            "loan_amounts": "остаток вне продуктовой спеки допускается в DOE, "
                            "фактическая доля объявлена выше",
            "duplicate_ids": "дубли id бывают трёх форм: пара валидных, "
                             "тройник валидных, пара невалидных; "
                             "сопоставление СТРОГО ПО ПОРЯДКУ строк",
        })
        return base
