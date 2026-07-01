"""
Точка входа анализа исследования FINPILOT.

Запуск из корня проекта:
    python run_analysis.py [--data PATH] [--out DIR]

Результат:
    <out>/finpilot_report.html   — HTML-отчёт
    <out>/charts/*.png           — графики
    <out>/results.json           — машиночитаемые результаты
"""
from __future__ import annotations

import argparse

from finpilot_survey.data import DATA_PATH
from finpilot_survey.pipeline import AnalysisPipeline
from finpilot_survey.report import build_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Анализ исследования FINPILOT")
    parser.add_argument("--data", default=DATA_PATH, help="Путь к .xlsx выгрузке")
    parser.add_argument("--out", default="output", help="Каталог для результатов")
    args = parser.parse_args()

    pipeline = AnalysisPipeline(args.data, args.out)
    results = pipeline.run()
    json_path = pipeline.save_json()
    report_path = build_report(results, args.out)

    n = results["meta"]
    print(f"Валидных анкет: {n['n_valid']} из {n['n_total']}")
    print(f"Отчёт:     {report_path}")
    print(f"Результаты: {json_path}")
    print(f"Графиков:  {len(results['charts'])}")


if __name__ == "__main__":
    main()
