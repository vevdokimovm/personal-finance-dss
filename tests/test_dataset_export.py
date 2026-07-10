"""Тесты экспортера датасетов валидации (портреты + выход модели).

Датасеты кладутся в репо сжатыми (`knowledge/model_validation/`), чтобы
«один zip = полный контекст» работал и для данных: любой эксперт или вахта
получает и сами портреты, и ответ модели без регенерации. Экспорт обязан
быть детерминированным и байт-в-байт воспроизводимым из генератора.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from tools.model_validation.dataset_export import (
    export_model_outcomes,
    export_portraits,
)
from tools.portrait_testing.generator import PortraitGenerator

SEED = 20260702


class TestExportPortraits:
    def test_roundtrip_matches_generator(self, tmp_path: Path):
        out = tmp_path / "p.jsonl.gz"
        n = export_portraits(out, n=20, seed=SEED, version=2)
        assert n == 20
        gen = PortraitGenerator(SEED, version=2)
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh]
        assert len(rows) == 20
        p7 = gen.generate(7)
        assert rows[7]["id"] == "SP-00007"
        assert rows[7]["income_total"] == p7["income_total"]
        assert rows[7]["kind"] == p7["kind"]
        # даты сериализованы в ISO и восстановимы
        for g_row, g_gen in zip(rows[7]["goals"], p7["goals"]):
            if g_gen["deadline"] is None:
                assert g_row["deadline"] is None
            else:
                assert g_row["deadline"] == g_gen["deadline"].isoformat()

    def test_v1_export_pins_expert_dataset(self, tmp_path: Path):
        out = tmp_path / "v1.jsonl.gz"
        export_portraits(out, n=2, seed=SEED, version=1)
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh]
        payments = sum(o["monthly_payment"] for o in rows[1]["obligations"])
        rt = rows[1]["income_total"] - rows[1]["expense_total"] - payments
        assert round(rt, 2) == 9295.54  # SP-00001 эталона экспертизы


class TestExportOutcomes:
    def test_outcomes_csv_schema_and_values(self, tmp_path: Path):
        out = tmp_path / "o.csv.gz"
        n = export_model_outcomes(out, n=12, seed=SEED, version=2)
        assert n == 12
        import csv
        with gzip.open(out, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 12
        required = {"id", "kind", "risk", "status", "rt", "lt", "dt",
                    "xo", "xr", "xg", "invest", "dom",
                    "crisis_severity", "crisis_actions"}
        assert required <= set(rows[0])
        for r in rows:
            if r["status"] == "deficit":
                assert int(r["crisis_actions"]) >= 1  # I12: молчания нет
            if r["status"] == "ok":
                assert r["dom"] in ("debt", "reserve", "goals+", "none")
