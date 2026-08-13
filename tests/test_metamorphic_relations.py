"""Метаморфические отношения (E-слой) поверх живого генератора v2.

M2_rate_all/M3_deadline_all из frozen-генераторов v4/v5 доказанно дают L1=0 на
всех парах (равномерный сдвиг сохраняет относительный порядок Avalanche/
срочности by design — `docs/model/model_quality_scorecard.md` ось 4). Фикс —
не правка frozen-файлов (сломала бы бит-в-бит воспроизводимость раундов 4/5),
а новые адресные отношения M2_rate_second/M3_deadline_second поверх живого
`tools/portrait_testing/generator.py`, тем же механизмом, что уже доказанно
информативен у *_single (раунды 4-5).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.core.goals_priority import goals_allocation_breakdown
from tools.portrait_testing.generator import (
    METAMORPHIC_RELATIONS,
    PortraitGenerator,
    build_metamorphic_twin,
)
from tools.portrait_testing.runner import run_one

TODAY = datetime(2026, 7, 2, 12, 0, 0)


def _base_portrait(**overrides: object) -> dict:
    portrait = {
        "index": 0,
        "kind": "plain",
        "income_total": 150_000.0,
        "expense_total": 60_000.0,
        "obligations": [
            {"id": 1, "name": "loan_1", "amount": 500_000.0,
             "interest_rate": 0.30, "monthly_payment": 15_000.0},
            {"id": 2, "name": "loan_2", "amount": 300_000.0,
             "interest_rate": 0.20, "monthly_payment": 8_000.0},
            {"id": 3, "name": "loan_3", "amount": 100_000.0,
             "interest_rate": 0.10, "monthly_payment": 3_000.0},
        ],
        "goals": [
            {"id": 1, "name": "goal_1", "target_amount": 200_000.0,
             "current_amount": 0.0, "deadline": TODAY + timedelta(days=30)},
            {"id": 2, "name": "goal_2", "target_amount": 300_000.0,
             "current_amount": 0.0, "deadline": TODAY + timedelta(days=60)},
            {"id": 3, "name": "goal_3", "target_amount": 400_000.0,
             "current_amount": 0.0, "deadline": TODAY + timedelta(days=90)},
        ],
        "bliq": 100_000.0,
        "r_bench": 0.14,
        "risk_tolerance": 3,
        "l_min": 0.0,
    }
    portrait.update(overrides)
    return portrait


class TestRelationSet:
    def test_vacuous_all_relations_removed(self) -> None:
        assert "M2_rate_all" not in METAMORPHIC_RELATIONS
        assert "M3_deadline_all" not in METAMORPHIC_RELATIONS

    def test_targeted_second_relations_present(self) -> None:
        assert "M2_rate_second" in METAMORPHIC_RELATIONS
        assert "M3_deadline_second" in METAMORPHIC_RELATIONS
        assert len(METAMORPHIC_RELATIONS) == 7  # тот же объём, что было в v4


class TestBuildTwinRate:
    def test_m2_rate_single_targets_top(self) -> None:
        base = _base_portrait()
        twin = build_metamorphic_twin(base, "M2_rate_single")
        rates = {o["id"]: o["interest_rate"] for o in twin["obligations"]}
        assert rates[1] == 0.31  # был самым дорогим (0.30)
        assert rates[2] == 0.20
        assert rates[3] == 0.10

    def test_m2_rate_second_targets_second_highest_not_top(self) -> None:
        base = _base_portrait()
        twin = build_metamorphic_twin(base, "M2_rate_second")
        rates = {o["id"]: o["interest_rate"] for o in twin["obligations"]}
        assert rates[1] == 0.30  # верхний не тронут
        assert rates[2] == 0.21  # второй по ставке — тронут
        assert rates[3] == 0.10

    def test_m2_rate_second_does_not_mutate_base(self) -> None:
        base = _base_portrait()
        build_metamorphic_twin(base, "M2_rate_second")
        assert base["obligations"][1]["interest_rate"] == 0.20

    def test_m2_rate_second_single_obligation_fallback(self) -> None:
        base = _base_portrait(obligations=[
            {"id": 1, "name": "loan_1", "amount": 500_000.0,
             "interest_rate": 0.30, "monthly_payment": 15_000.0},
        ])
        twin = build_metamorphic_twin(base, "M2_rate_second")
        assert twin["obligations"][0]["interest_rate"] == 0.31


class TestBuildTwinDeadline:
    def test_m3_deadline_single_targets_nearest(self) -> None:
        base = _base_portrait()
        twin = build_metamorphic_twin(base, "M3_deadline_single")
        deadlines = {g["id"]: g["deadline"] for g in twin["goals"]}
        assert deadlines[1] == TODAY + timedelta(days=30 + 183)
        assert deadlines[2] == TODAY + timedelta(days=60)
        assert deadlines[3] == TODAY + timedelta(days=90)

    def test_m3_deadline_second_targets_second_nearest_not_nearest(self) -> None:
        base = _base_portrait()
        twin = build_metamorphic_twin(base, "M3_deadline_second")
        deadlines = {g["id"]: g["deadline"] for g in twin["goals"]}
        assert deadlines[1] == TODAY + timedelta(days=30)  # ближайшая не тронута
        assert deadlines[2] == TODAY + timedelta(days=60 + 183)
        assert deadlines[3] == TODAY + timedelta(days=90)

    def test_m3_deadline_second_ignores_open_ended_goals(self) -> None:
        base = _base_portrait(goals=[
            {"id": 1, "name": "open", "target_amount": 100_000.0,
             "current_amount": 0.0, "deadline": None},
            {"id": 2, "name": "goal_2", "target_amount": 300_000.0,
             "current_amount": 0.0, "deadline": TODAY + timedelta(days=60)},
        ])
        twin = build_metamorphic_twin(base, "M3_deadline_second")
        deadlines = {g["id"]: g["deadline"] for g in twin["goals"]}
        assert deadlines[1] is None  # бессрочная не попадает в кандидаты
        # единственная датированная — деградация к поведению _single (как у
        # M2_rate_second с одним обязательством)
        assert deadlines[2] == TODAY + timedelta(days=60 + 183)


class TestOtherRelationsUnchangedBehaviour:
    def test_m1_income(self) -> None:
        twin = build_metamorphic_twin(_base_portrait(), "M1_income")
        assert twin["income_total"] == 151_500.0

    def test_m4_bliq(self) -> None:
        twin = build_metamorphic_twin(_base_portrait(), "M4_bliq")
        assert twin["bliq"] == 101_000.0

    def test_m5_scale(self) -> None:
        twin = build_metamorphic_twin(_base_portrait(), "M5_scale")
        assert twin["income_total"] == 1_500_000.0
        assert twin["obligations"][0]["amount"] == 5_000_000.0
        assert twin["goals"][0]["target_amount"] == 2_000_000.0

    def test_unknown_relation_raises(self) -> None:
        try:
            build_metamorphic_twin(_base_portrait(), "M9_bogus")
        except ValueError:
            return
        raise AssertionError("ожидался ValueError на неизвестном отношении")


class TestInformativenessAgainstModel:
    """Доказательство небесполезности: в отличие от *_all (L1=0 by design),
    адресные *_second меняют решение модели хотя бы на части выборки."""

    def _sample_bases(self, n: int = 80) -> list[dict]:
        gen = PortraitGenerator(seed=20260812, version=2)
        bases = []
        i = 0
        while len(bases) < n and i < n * 6:
            if gen.kind_for(i) == "plain":
                p = gen.generate(i)
                if len(p["obligations"]) >= 2 and p["income_total"] > 0:
                    bases.append(p)
            i += 1
        return bases

    def test_m2_rate_second_changes_decision_on_some_portraits(self) -> None:
        bases = self._sample_bases()
        changed = 0
        for base in bases:
            twin = build_metamorphic_twin(base, "M2_rate_second")
            r_base = run_one(base)
            r_twin = run_one(twin)
            id_base = r_base["best"]["id"] if r_base["best"] else None
            id_twin = r_twin["best"]["id"] if r_twin["best"] else None
            if id_base != id_twin:
                changed += 1
        assert changed > 0, "M2_rate_second не должен быть тождественно вырожден"

    def test_m3_deadline_second_changes_goal_allocation_within_urgency_window(
        self,
    ) -> None:
        """M3 воздействует не на верхний сплит (x_d,x_r,x_g) — срочность цели
        не входит в критерии R_t/L_t/D_t — а на распределение x_g МЕЖДУ
        целями (§11.4 канона, `goals_allocation_breakdown`). Правильный
        уровень проверки информативности — доля цели, не решение пайплайна.

        Случайная выборка из `PortraitGenerator` для этого теста непригодна:
        срочность $u_s = \\max(1, 12/\\tau_s)$ насыщается на горизонте >= 12
        мес (форм. §11.2) — если вторая по близости дедлайна цель уже вне
        12-месячного окна, сдвиг +183 дня оставляет $u_s=1$ и НИЧЕГО не
        меняет: это тот же класс вырожденности, что и у M3_deadline_all,
        просто зависящий от состава выборки, а не гарантированный by design.
        Поэтому здесь — детерминированная проверка на фикстуре с целями
        внутри окна (30/60/90 дней), где чувствительность гарантирована."""
        base = _base_portrait()
        twin = build_metamorphic_twin(base, "M3_deadline_second")
        breakdown_base = goals_allocation_breakdown(
            100_000.0, base["goals"], today=TODAY)
        breakdown_twin = goals_allocation_breakdown(
            100_000.0, twin["goals"], today=TODAY)
        shares_base = {g["id"]: g["share"] for g in breakdown_base}
        shares_twin = {g["id"]: g["share"] for g in breakdown_twin}
        assert shares_base != shares_twin, (
            "M3_deadline_second не должен быть тождественно вырожден "
            "внутри 12-месячного окна чувствительности срочности"
        )
