"""Тесты команды `run`: гарантированный нейминг выходных файлов прогона модели."""
from __future__ import annotations

import csv
import gzip

from tools.model_validation.dataset_export import (
    outcomes_filename,
    results_filename,
    run_model_over_dataset,
)


class TestNaming:
    def test_outcomes_name_encodes_model_and_dataset(self):
        assert (outcomes_filename("v3_4_0", 4)
                == "model_outcomes_v3_4_0_on_v4.csv.gz")
        assert (outcomes_filename("v3_1_0", 2)
                == "model_outcomes_v3_1_0_on_v2.csv.gz")

    def test_results_name_encodes_model_and_dataset(self):
        assert (results_filename("v3_4_0", 4)
                == "model_results_v3_4_0_on_v4.md")

    def test_model_version_normalised(self):
        # точки в версии модели приводятся к подчёркиваниям
        assert outcomes_filename("v3.4.0", 4).endswith("v3_4_0_on_v4.csv.gz")


class TestRun:
    N_SMALL = 600

    def test_run_emits_both_files_with_correct_names(self, tmp_path):
        result = run_model_over_dataset(
            dataset_version=4, seed=20260718, model_version="v3_4_0",
            out_dir=tmp_path, n=self.N_SMALL)
        csv_path = tmp_path / "model_outcomes_v3_4_0_on_v4.csv.gz"
        md_path = tmp_path / "model_results_v3_4_0_on_v4.md"
        assert csv_path.exists() and md_path.exists()
        assert result["outcomes_path"] == csv_path
        assert result["results_path"] == md_path

        with gzip.open(csv_path, "rt", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == self.N_SMALL
        assert all(r["id"].startswith("SP4-") for r in rows)

        summary = md_path.read_text(encoding="utf-8")
        assert "v3.4.0" in summary and "v4" in summary
        assert "invalid" in summary
        # сводка отражает фактические числа
        assert str(result["status_counts"]["invalid"]) in summary

    def test_summary_reports_d_layer_verdict(self, tmp_path):
        result = run_model_over_dataset(
            dataset_version=4, seed=20260718, model_version="v3_4_0",
            out_dir=tmp_path, n=self.N_SMALL)
        assert "false_positives_on_valid" in result
        assert result["false_positives_on_valid"] == 0
