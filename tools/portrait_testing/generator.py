"""Генератор синтетических портретов пользователя для свипа мат-модели.

Детерминирован по (seed, version, index): каждый портрет воспроизводим
независимо от порядка генерации. ~треть портретов — граничные случаи.

Две версии генерации:

  v1 (legacy, бит-в-бит) — на нём построен эталон независимой экспертизы
     `knowledge/model_validation/joined.csv.gz` (12 000 портретов, seed
     20260702). Дефект, подтверждённый пятью независимыми расчётами:
     тело кредита не связано с доходом (corr ~ 0.02), сроки аномально
     коротки → 80.8% сета в дефиците. Оставлен только для регенерации
     эталона; для новых прогонов НЕ использовать.

  v2 (актуальный канон) — долги через целевой ПДН (beta-распределение,
     медиана ~0.31, p90 ~0.55 — картина ЦБ/НБКИ после МПЛ), тело кредита
     из аннуитета с реалистичным сроком 12–84 мес, расходы от бюджета
     «после платежей» (дефицит у plain ~10–12%, по всему сету ≤ ~30%
     с учётом кризисных edge-типов), подушка с экспоненциальным профилем
     (медиана ~1.7 мес — реалистичнее равномерных 0–12), adversarial-слой
     граничных портретов (ПДН у гейта, ставка ровно на бенчмарке, дедлайн
     сегодня, копеечные и гигантские масштабы).
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

EDGE_KINDS_V1: tuple[str, ...] = (
    "zero_income",
    "zero_expenses",
    "deficit_cf",
    "overleveraged",
    "cheap_debts_only",
    "no_goals",
    "funded_goal",
    "huge_bliq",
    "many_goals",
)

ADVERSARIAL_KINDS: tuple[str, ...] = (
    "pdn_boundary",    # ПДН вплотную к регуляторному порогу 0.40
    "rate_at_bench",   # ставки всех долгов ровно равны r_bench (граница OCR-фильтра)
    "deadline_now",    # цель с дедлайном «сегодня»
    "kopeck_scale",    # копеечные величины — устойчивость к числовому шуму
    "giant_scale",     # величины ~1e9 — устойчивость float
)

EDGE_KINDS_V2: tuple[str, ...] = EDGE_KINDS_V1 + ADVERSARIAL_KINDS
EDGE_KINDS: tuple[str, ...] = EDGE_KINDS_V2  # актуальный канон

R_BENCH_CHOICES: tuple[float, ...] = (0.10, 0.1281, 0.14, 0.1596, 0.20)


class PortraitGenerator:
    """Фабрика синтетических портретов: доходы/расходы/долги/цели/подушка."""

    def __init__(self, seed: int = 20260702, version: int = 2) -> None:
        if version not in (1, 2):
            raise ValueError(f"неизвестная версия генератора: {version}")
        self.seed = seed
        self.version = version
        self._edge_kinds = EDGE_KINDS_V1 if version == 1 else EDGE_KINDS_V2

    def kind_for(self, index: int) -> str:
        if index % 3 == 0:
            return self._edge_kinds[(index // 3) % len(self._edge_kinds)]
        return "plain"

    def generate(self, index: int) -> dict[str, Any]:
        rng = random.Random(self.seed * 1_000_003 + index)
        if self.version == 1:
            return self._generate_v1(rng, index)
        return self._generate_v2(rng, index)

    # ── v1 (legacy, бит-в-бит: регенерация эталона экспертизы) ──────────

    def _generate_v1(self, rng: random.Random, index: int) -> dict[str, Any]:
        kind = self.kind_for(index)
        today = date(2026, 7, 2)

        income = round(rng.lognormvariate(11.2, 0.5), 2)
        expenses = round(income * rng.uniform(0.35, 1.15), 2)

        obligations = self._gen_obligations_v1(rng, income)
        goals = self._gen_goals(rng, today)
        bliq = round(expenses * rng.uniform(0.0, 12.0), 2)

        if kind == "zero_income":
            income = 0.0
        elif kind == "zero_expenses":
            expenses = 0.0
        elif kind == "deficit_cf":
            expenses = round(max(income, 1.0) * rng.uniform(1.05, 1.6), 2)
        elif kind == "overleveraged":
            obligations = self._gen_obligations_v1(rng, income, min_count=1)
            target_pdn = rng.uniform(0.45, 0.9)
            payments = sum(o["monthly_payment"] for o in obligations)
            scale = (target_pdn * max(income, 1.0)) / payments if payments > 0 else 1.0
            for o in obligations:
                o["monthly_payment"] = round(o["monthly_payment"] * scale, 2)
        elif kind == "cheap_debts_only":
            obligations = self._gen_obligations_v1(rng, income, min_count=1)
            for o in obligations:
                o["interest_rate"] = round(rng.uniform(0.01, 0.09), 4)
        elif kind == "no_goals":
            goals = []
        elif kind == "funded_goal":
            target = round(rng.uniform(50_000, 500_000), 2)
            goals = [{
                "id": 1, "name": "funded", "target_amount": target,
                "current_amount": round(target * rng.uniform(1.0, 1.2), 2),
                "deadline": today + timedelta(days=90),
            }]
        elif kind == "huge_bliq":
            bliq = round(max(expenses, 10_000.0) * rng.uniform(24.0, 60.0), 2)
        elif kind == "many_goals":
            goals = self._gen_goals(rng, today, count=8)

        return {
            "index": index,
            "kind": kind,
            "income_total": income,
            "expense_total": expenses,
            "obligations": obligations,
            "goals": goals,
            "bliq": bliq,
            "r_bench": rng.choice(R_BENCH_CHOICES),
            "risk_tolerance": rng.randint(1, 5),
            "l_min": 0.0,
        }

    def _gen_obligations_v1(
        self, rng: random.Random, income: float, min_count: int = 0
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for i in range(rng.randint(min_count, 4)):
            principal = round(rng.uniform(30_000, 3_000_000), 2)
            items.append({
                "id": i + 1,
                "name": f"loan_{i + 1}",
                "amount": principal,
                "interest_rate": round(rng.uniform(0.03, 0.35), 4),
                "monthly_payment": round(principal * rng.uniform(0.02, 0.06), 2),
            })
        return items

    # ── v2 (актуальный канон: калибровка + adversarial) ─────────────────

    def _generate_v2(self, rng: random.Random, index: int) -> dict[str, Any]:
        kind = self.kind_for(index)
        today = date(2026, 7, 2)
        r_bench = rng.choice(R_BENCH_CHOICES)

        income = round(rng.lognormvariate(11.2, 0.5), 2)
        has_debt = rng.random() < 0.55  # доля заёмщиков среди активного населения
        obligations = self._gen_obligations_v2(rng, income) if has_debt else []
        payments = sum(o["monthly_payment"] for o in obligations)

        # Расходы — от бюджета «после платежей»: даже перегруженный тратит на
        # жизнь минимум ~15% дохода; дефицит у plain возникает в хвосте (>1.0)
        living_budget = max(income - payments, income * 0.15)
        expenses = round(living_budget * rng.uniform(0.40, 1.08), 2)

        goals = self._gen_goals(rng, today)
        bliq_months = min(24.0, rng.expovariate(1 / 2.5))
        bliq = round(max(expenses, income * 0.3) * bliq_months, 2)

        if kind == "zero_income":
            income = 0.0
        elif kind == "zero_expenses":
            expenses = 0.0
        elif kind == "deficit_cf":
            expenses = round(max(income, 1.0) * rng.uniform(1.05, 1.6), 2)
        elif kind == "overleveraged":
            obligations = self._gen_obligations_v2(rng, income, min_count=1)
            target_pdn = rng.uniform(0.45, 0.9)
            payments = sum(o["monthly_payment"] for o in obligations)
            scale = (target_pdn * max(income, 1.0)) / payments if payments > 0 else 1.0
            for o in obligations:
                o["monthly_payment"] = round(o["monthly_payment"] * scale, 2)
        elif kind == "cheap_debts_only":
            obligations = self._gen_obligations_v2(rng, income, min_count=1)
            for o in obligations:
                o["interest_rate"] = round(rng.uniform(0.01, 0.09), 4)
        elif kind == "no_goals":
            goals = []
        elif kind == "funded_goal":
            target = round(rng.uniform(50_000, 500_000), 2)
            goals = [{
                "id": 1, "name": "funded", "target_amount": target,
                "current_amount": round(target * rng.uniform(1.0, 1.2), 2),
                "deadline": today + timedelta(days=90),
            }]
        elif kind == "huge_bliq":
            bliq = round(max(expenses, 10_000.0) * rng.uniform(24.0, 60.0), 2)
        elif kind == "many_goals":
            goals = self._gen_goals(rng, today, count=8)
        elif kind == "pdn_boundary":
            obligations = self._gen_obligations_v2(rng, income, min_count=1, n_max=1)
            obligations[0]["monthly_payment"] = round(
                income * rng.uniform(0.395, 0.405), 2
            )
            expenses = round(income * rng.uniform(0.40, 0.60), 2)
        elif kind == "rate_at_bench":
            obligations = self._gen_obligations_v2(rng, income, min_count=1, n_max=2)
            for o in obligations:
                o["interest_rate"] = r_bench
        elif kind == "deadline_now":
            goals = [{
                "id": 1, "name": "deadline_now",
                "target_amount": round(rng.uniform(50_000, 500_000), 2),
                "current_amount": 0.0,
                "deadline": today,
            }]
        elif kind == "kopeck_scale":
            income = round(rng.uniform(10.0, 500.0), 2)
            expenses = round(income * rng.uniform(0.40, 1.08), 2)
            obligations = []
            goals = [{
                "id": 1, "name": "tiny",
                "target_amount": round(rng.uniform(50.0, 500.0), 2),
                "current_amount": 0.0,
                "deadline": today + timedelta(days=180),
            }]
            bliq = round(rng.uniform(0.0, 1_000.0), 2)
        elif kind == "giant_scale":
            factor = rng.uniform(1e4, 5e4)
            income = round(income * factor, 2)
            expenses = round(expenses * factor, 2)
            for o in obligations:
                o["amount"] = round(o["amount"] * factor, 2)
                o["monthly_payment"] = round(o["monthly_payment"] * factor, 2)
            for g in goals:
                g["target_amount"] = round(g["target_amount"] * factor, 2)
                g["current_amount"] = round(g["current_amount"] * factor, 2)
            bliq = round(bliq * factor, 2)

        return {
            "index": index,
            "kind": kind,
            "income_total": income,
            "expense_total": expenses,
            "obligations": obligations,
            "goals": goals,
            "bliq": bliq,
            "r_bench": r_bench,
            "risk_tolerance": rng.randint(1, 5),
            "l_min": 0.0,
        }

    def _gen_obligations_v2(
        self,
        rng: random.Random,
        income: float,
        min_count: int = 1,
        n_max: int = 4,
    ) -> list[dict[str, Any]]:
        """Долги через целевой ПДН + аннуитетное тело с реалистичным сроком.

        ПДН ~ Beta(2.2, 4.4): медиана ~0.31, p90 ~0.55 — согласуется с картиной
        распределения долговой нагрузки заёмщиков ЦБ/НБКИ после введения МПЛ.
        Тело кредита восстанавливается из аннуитета по платежу, ставке и сроку
        12–84 мес — сумма долга связана с доходом через платёж (у v1 corr ~0.02).
        """
        n = rng.choices((1, 2, 3, 4), weights=(45, 30, 17, 8))[0]
        n = min(max(n, min_count), n_max)
        target_pdn = min(0.95, rng.betavariate(2.2, 4.4))
        payments_total = target_pdn * max(income, 1.0)
        shares = [rng.uniform(0.5, 1.5) for _ in range(n)]
        share_sum = sum(shares)

        items: list[dict[str, Any]] = []
        for i, share in enumerate(shares):
            payment = round(payments_total * share / share_sum, 2)
            rate = round(rng.uniform(0.06, 0.35), 4)
            term = rng.randint(12, 84)
            monthly_rate = rate / 12
            principal = payment * (1 - (1 + monthly_rate) ** (-term)) / monthly_rate
            items.append({
                "id": i + 1,
                "name": f"loan_{i + 1}",
                "amount": round(principal, 2),
                "interest_rate": rate,
                "monthly_payment": payment,
            })
        return items

    # ── общее ────────────────────────────────────────────────────────────

    def _gen_goals(
        self, rng: random.Random, today: date, count: int | None = None
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for i in range(count if count is not None else rng.randint(0, 4)):
            target = round(rng.uniform(50_000, 2_000_000), 2)
            deadline = (
                today + timedelta(days=30 * rng.randint(3, 60))
                if rng.random() > 0.25 else None
            )
            items.append({
                "id": i + 1,
                "name": f"goal_{i + 1}",
                "target_amount": target,
                "current_amount": round(rng.uniform(0, target * 0.9), 2),
                "deadline": deadline,
            })
        return items
