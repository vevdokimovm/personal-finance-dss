"""
Параметр шага дискретизации сетки в оркестраторе (ROADMAP §6.3 замер 5%).

Замер: `docs/reports/testing/grid_step_5pct_benchmark.md`.
run_planning принимает step (по умолчанию 0.10 → 66); knob для стенд-замера
более мелкой сетки без правки боевого дефолта.
"""
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
