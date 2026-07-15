"""
Оркестратор анализа: прогоняет все анализаторы, собирает единый результат,
генерирует графики и (через report) HTML-отчёт.
"""
from __future__ import annotations

import json
import os
from typing import Any

from finpilot_survey.data import SurveyData
from finpilot_survey.analyzers_quant import (
    AudienceProfiler, DescriptiveAnalyzer, HypothesisTester,
    PreferenceAnalyzer, RankingAnalyzer, SegmentAnalyzer)
from finpilot_survey.analyzers_product import (
    BehavioralValidator, BusinessAnalyzer, QualitativeCoder)
from finpilot_survey.visualization import ChartMaker


class AnalysisPipeline:
    def __init__(self, data_path: str, out_dir: str) -> None:
        self.data = SurveyData(data_path)
        self.out_dir = out_dir
        self.charts_dir = os.path.join(out_dir, "charts")
        os.makedirs(self.charts_dir, exist_ok=True)
        self.results: dict[str, Any] = {}

    def run(self) -> dict[str, Any]:
        d = self.data
        self.results = {
            "meta": {
                "n_total": d.n_total,
                "n_valid": d.n_valid,
                "n_dropped": d.n_dropped,
            },
            "descriptive": DescriptiveAnalyzer(d).run(),
            "audience": AudienceProfiler(d).run(),
            "segments": SegmentAnalyzer(d).run(),
            "hypotheses": HypothesisTester(d).run(),
            "preferences": PreferenceAnalyzer(d).run(),
            "rankings": RankingAnalyzer(d).run(),
            "behavioral": BehavioralValidator(d).run(),
            "business": BusinessAnalyzer(d).run(),
            "qualitative": QualitativeCoder(d).run(),
        }
        self.results["charts"] = ChartMaker(self.charts_dir).generate_all(
            self.results)
        return self.results

    def save_json(self, name: str = "results.json") -> str:
        path = os.path.join(self.out_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        return path
