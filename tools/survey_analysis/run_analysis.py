"""
Точка входа анализа исследования FINPILOT.

Запуск из корня проекта:
    python -m tools.survey_analysis.run_analysis [--data PATH] [--out DIR]

🔴 Именно модулем, а не файлом: после перевода импортов на `tools.survey_analysis`
прямой `python run_analysis.py` падает `ModuleNotFoundError` — каталог инструмента
не является корнем пакета. Прежняя строка обещала способ, который не работает.

Зависимости у конвейера свои — `tools/survey_analysis/requirements.txt`
(pandas, numpy, openpyxl, scipy, matplotlib, factor_analyzer); в основном окружении
проекта их нет, ставятся отдельно.

Результат:
    <out>/finpilot_report.html   — HTML-отчёт
    <out>/charts/*.png           — графики
    <out>/results.json           — машиночитаемые результаты
"""
from __future__ import annotations

import argparse

from tools.survey_analysis.data import DATA_PATH
from tools.survey_analysis.pipeline import AnalysisPipeline
from tools.survey_analysis.report import build_report


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
