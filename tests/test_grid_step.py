"""
Параметр шага дискретизации сетки в оркестраторе (ROADMAP §6.3 замер 5%).

Замер: `docs/reports/testing/grid_step_5pct_benchmark.md`.
run_planning принимает step (по умолчанию 0.10 → 66); knob для стенд-замера
более мелкой сетки без правки боевого дефолта.
"""
import pytest

from app.core.alternatives import generate_alternatives
from app.services.planning import run_planning

PORTRAIT = dict(
    income_total=80_000,
    expense_total=50_000,
    obligations=[{"id": "cc", "monthly_payment": 8_000, "balance": 120_000, "rate": 0.24}],
    goals=[{"id": "g1", "target_amount": 300_000, "current_amount": 50_000}],
    bliq=90_000,
    r_bench=0.14,
    risk_tolerance=3,
)


class TestGridStep:
    def test_default_step_yields_66(self):
        res = run_planning(**PORTRAIT)
        assert res["alternatives_total"] == 66

    def test_step_5pct_yields_231(self):
        res = run_planning(**PORTRAIT, step=0.05)
        assert res["alternatives_total"] == 231

    def test_legacy_step_20pct_yields_21(self):
        res = run_planning(**PORTRAIT, step=0.20)
        assert res["alternatives_total"] == 21

    def test_finer_grid_produces_valid_plan(self):
        """Более мелкая сетка не ломает пайплайн: топ-3 остаётся непустым."""
        res = run_planning(**PORTRAIT, step=0.05)
        assert res["best"] is not None
        assert len(res["top3"]) >= 1


class TestAlternativeIdUniqueness:
    """Мина, вскрытая замером §6.1: id альтернативы обязан быть уникален при ЛЮБОМ шаге.

    Старый формат `f"a{d}{r}{g}"` — конкатенация без разделителя. На канонных 10% индексы
    однозначны и коллизий нет (66/66), но при 5% они двузначны: (0,1,19) и (0,11,9) → оба
    `a0119` — 29 коллизий из 231. Канон остался 10% (ADR-008), поэтому формат id на 10%
    НЕ менялся (golden-снапшоты живы), но решётка обязана быть корректной на любом шаге —
    иначе следующий эксперимент с сеткой молча потеряет альтернативы.
    """

    @pytest.mark.parametrize("step", [0.20, 0.10, 0.05, 0.04, 0.02])
    def test_ids_unique_for_any_step(self, step):
        alts = generate_alternatives(
            rt=22_000.0, obligation_payments=8_000.0, goals_total=300_000.0, step=step
        )
        ids = [a["id"] for a in alts]
        assert len(set(ids)) == len(ids), (
            f"шаг {step:.0%}: коллизия id — {len(ids) - len(set(ids))} дублей из {len(ids)}"
        )

    def test_canonical_id_format_unchanged(self):
        """Обратная совместимость: на канонных 10% формат id прежний (`a{d}{r}{g}`)."""
        alts = generate_alternatives(
            rt=22_000.0, obligation_payments=8_000.0, goals_total=300_000.0, step=0.10
        )
        ids = {a["id"] for a in alts}
        assert "a0100" in ids   # (0, 10, 0) — «всё в резерв»
        assert "a1000" in ids   # (10, 0, 0) — «всё в долги»
        assert "a0010" in ids   # (0, 0, 10) — «всё в цели»
