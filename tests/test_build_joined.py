"""Тесты сборщика joined-файла второй сертификации (модель + 4 эксперта).

Joined v2 — «одна строка = один портрет»: диагностика и ответ модели из
`model_outcomes_*.csv.gz` плюс колонки четырёх экспертов из их CSV
(формат брифа `id,status,dom,res,debt,goal,inv,lump`). Сборка обязана быть
детерминированной, фиксировать нарушения бюджета экспертами (не чинить их)
и падать громко на структурных дефектах (дырки/дубли id, кривые статусы).
"""
from __future__ import annotations

import csv
import gzip
from pathlib import Path

import pytest

from tools.model_validation.build_joined import BudgetContext, build_joined
from tools.model_validation.expert_agreement import model_outcome, run_validation
from tools.portrait_testing.generator import PortraitGenerator

SEED = 20260702


def _write_outcomes(path: Path, rows: list[dict]) -> None:
    fields = (
        "id", "kind", "risk", "status", "rt", "lt", "dt",
        "xo", "xr", "xg", "invest", "dom",
        "dt_alert", "crisis_severity", "crisis_actions",
    )
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_expert(path: Path, rows: list[dict], line_ending: str = "\n") -> None:
    header = "id,status,dom,res,debt,goal,inv,lump"
    lines = [header] + [
        ",".join(str(r[k]) for k in header.split(",")) for r in rows
    ]
    path.write_bytes((line_ending.join(lines) + line_ending).encode("utf-8"))


def _outcome_row(pid: str, status: str = "ok", dom: str = "reserve") -> dict:
    return {
        "id": pid, "kind": "plain", "risk": 3, "status": status,
        "rt": "1000.00", "lt": "2.0", "dt": "0.1",
        "xo": "0.00", "xr": "700.00", "xg": "200.00", "invest": "100.00",
        "dom": dom, "dt_alert": 0, "crisis_severity": "", "crisis_actions": 0,
    }


def _expert_row(pid: str, **over) -> dict:
    row = {"id": pid, "status": "ok", "dom": "reserve",
           "res": 700, "debt": 0, "goal": 200, "inv": 100, "lump": 0}
    row.update(over)
    return row


class TestBuildJoined:
    def _paths(self, tmp_path: Path, pids: list[str]) -> tuple[Path, dict[str, Path]]:
        outcomes = tmp_path / "outcomes.csv.gz"
        _write_outcomes(outcomes, [_outcome_row(p) for p in pids])
        experts = {}
        for tag in ("v", "m", "j", "s"):
            path = tmp_path / f"{tag}.csv"
            ending = "\r\n" if tag == "s" else "\n"
            _write_expert(path, [_expert_row(p) for p in pids], line_ending=ending)
            experts[tag] = path
        return outcomes, experts

    def test_joined_schema_and_values(self, tmp_path: Path):
        pids = ["SP-00000", "SP-00001"]
        outcomes, experts = self._paths(tmp_path, pids)
        out = tmp_path / "joined.csv.gz"
        summary = build_joined(outcomes, experts, out)
        assert summary["rows"] == 2
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert [r["id"] for r in rows] == pids
        first = rows[0]
        # модельная половина: xg в joined включает инвест-транш (семантика стенда)
        assert first["model_status"] == "ok"
        assert first["model_dom"] == "reserve"
        assert float(first["model_xg"]) == pytest.approx(300.0)
        assert float(first["model_xr"]) == pytest.approx(700.0)
        assert float(first["model_invest"]) == pytest.approx(100.0)
        # экспертная половина, включая CRLF-источник s
        for tag in ("v", "m", "j", "s"):
            assert first[f"{tag}_status"] == "ok"
            assert first[f"{tag}_dom"] == "reserve"
            assert float(first[f"{tag}_res"]) == pytest.approx(700.0)

    def test_fails_loud_on_missing_and_duplicate_ids(self, tmp_path: Path):
        pids = ["SP-00000", "SP-00001"]
        outcomes, experts = self._paths(tmp_path, pids)
        broken = tmp_path / "broken.csv"
        _write_expert(broken, [_expert_row("SP-00000"), _expert_row("SP-00000")])
        experts["m"] = broken
        with pytest.raises(ValueError, match="id"):
            build_joined(outcomes, experts, tmp_path / "j.csv.gz")

    def test_fails_loud_on_bad_enum(self, tmp_path: Path):
        pids = ["SP-00000"]
        outcomes, experts = self._paths(tmp_path, pids)
        bad = tmp_path / "bad.csv"
        _write_expert(bad, [_expert_row("SP-00000", dom="cash")])
        experts["j"] = bad
        with pytest.raises(ValueError, match="dom"):
            build_joined(outcomes, experts, tmp_path / "j.csv.gz")

    def test_budget_violations_counted_not_fixed(self, tmp_path: Path):
        pids = ["SP-00000"]
        outcomes, experts = self._paths(tmp_path, pids)
        greedy = tmp_path / "greedy.csv"
        _write_expert(greedy, [_expert_row("SP-00000", res=900, goal=200)])
        experts["v"] = greedy
        ctx = BudgetContext({"SP-00000": 1000.0}, tolerance=1.0)
        out = tmp_path / "joined.csv.gz"
        summary = build_joined(outcomes, experts, out, budget=ctx)
        assert summary["budget_violations"]["v"] == 1
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            row = next(csv.DictReader(fh))
        assert float(row["v_res"]) == pytest.approx(900.0)  # не чиним


class TestValidationVersioned:
    def test_run_validation_regenerates_with_requested_version(self):
        """Self-check на v2-строке сходится только генератором v2."""
        gen = PortraitGenerator(SEED, version=2)
        out = model_outcome(gen.generate(1))
        assert out["status"] == "ok"
        row = {
            "id": "SP-00001",
            "model_status": out["status"], "model_dom": out["dom"],
            "model_xo": f"{out['xo']:.2f}", "model_xr": f"{out['xr']:.2f}",
            "model_xg": f"{out['xg']:.2f}",
        }
        for tag in ("v", "m", "j", "s"):
            row[f"{tag}_dom"] = out["dom"]
            row[f"{tag}_status"] = "ok"
        stats = run_validation([row], seed=SEED, version=2)
        assert stats["selfcheck"]["dom_match"] == 1
        assert stats["selfcheck"]["split_match"] == 1
