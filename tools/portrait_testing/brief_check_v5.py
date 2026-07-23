"""Программная приёмка брифа v5 против фактического пакета (runbook C.12).

Урок сборки 1: датасет прошёл десять проверок, а бриф описывал несуществующий
вход (`portraits_v5.csv`), потерял правила чистоты и объявлял невыполненный
пункт ТЗ выполненным. Приёмка брифа — отдельный шаг, и он программный:
каждое имя файла, каждая обещанная доля сверяются с пакетом, а не глазами.

Запуск: `python3 -m tools.portrait_testing.brief_check_v5` из корня репо.
Выход 0 — бриф сходится с пакетом; ненулевой — печатает расхождения.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from pathlib import Path

BRIEF = Path("docs/model/expert_brief_v5.md")
PACK = Path("knowledge/model_validation/expert_pack_v5")
STATS = Path("docs/model/expert_certification/iterations/5/dataset_stats_v5.json")
CARDS_NAME = "portraits_v5_seed20260723_cards.md"

#: файлы, которые сдаёт эксперт, — упоминание в брифе законно без наличия в пакете
DELIVERABLE_RE = re.compile(
    r"(expert_allocations_v5\.csv|recommendations_v5\.jsonl\.gz|summary_v5\.csv"
    r"|expert_methodology_v5\.md|assumptions_log_v5\.md|dataset_review_v5\.(md|json)"
    r"|dataset_acceptance_v5\.(md|json)|self_validation_v5\.md"
    r"|expert_opinions_sample_v5\.md|sensitivity_v5\.(md|json)"
    r"|disagreement_forecast_v5\.md|run_metadata_v5\.md|engine_v5\.py"
    r"|dataset_stats_v5\.py|validate_answers_v5\.py|card_crosscheck_v5\.py"
    r"|sensitivity_runner_v5\.py|build_opinions_sample_v5\.py)")


def main() -> int:
    errors: list[str] = []
    text = BRIEF.read_text(encoding="utf-8")
    meta = json.loads(gzip.open(
        PACK / "expert_portraits_v5_part1.jsonl.gz", "rt",
        encoding="utf-8").readline())
    dec = meta["declarations"]
    stats = json.loads(STATS.read_text(encoding="utf-8"))

    # 1. Каждое имя файла из брифа существует в пакете или является сдаваемым
    package_names = {p.name for p in PACK.glob("*.jsonl.gz")}
    package_names |= {CARDS_NAME, "expert_brief_v5.md", "testset_methodology.md"}
    mentioned = set(re.findall(r"`([\w.]+\.[\w.]+(?:\.gz)?)`", text))
    for name in sorted(mentioned):
        expanded = {name}
        if "part1..4" in name:
            expanded = {name.replace("part1..4", f"part{i}") for i in range(1, 5)}
        for item in expanded:
            if item in package_names or DELIVERABLE_RE.fullmatch(item):
                continue
            if not item.endswith((".csv", ".md", ".gz", ".py", ".json")):
                continue
            errors.append(f"бриф упоминает файл, которого нет: {item}")

    # 2. Обещанные доли совпадают с декларациями слепой meta
    checks = [
        (f"{dec['stress_magnitude_share']*100:.2f}% портретов", "stress"),
        (f"{dec['realistic_whale_share']*100:.2f}%", "whale"),
        (f"{dec['loan_amount_outside_product_spec_share']*100:.2f}% кредитов",
         "loan oos"),
        (f"{dec['goal_amount_outside_name_band_share']*100:.2f}% целей",
         "goal band"),
        (f"[{dec['k_goal_actual_range'][0]:.4f}; "
         f"{dec['k_goal_actual_range'][1]:.4f}]", "k range"),
        (f"{dec['income_lognormal_ks_population']:.4f}", "KS"),
        (f"{stats['defect_layer']['composite_share']*100:.1f}% слоя",
         "composite"),
    ]
    for needle, tag in checks:
        if needle not in text:
            errors.append(f"доля в брифе разошлась с пакетом ({tag}): {needle}")

    # 3. Обязательные инструкции на месте
    musts = [
        ('{"__meta__": true', "инструкция про служебную строку __meta__"),
        (CARDS_NAME, "карточки с актуальным сидом"),
        ("Не используйте память, инструкции проекта",
         "правила чистоты сессии"),
        ("СТРОГО ПО ПОРЯДКУ СТРОК", "позиционный контракт"),
        ("part1 → part2 → part3 → part4", "порядок частей"),
        ("Дата среза — **" + meta["frozen_today"] + "**",
         "дата среза = frozen_today пакета"),
    ]
    for needle, tag in musts:
        if needle not in text:
            errors.append(f"в брифе нет: {tag}")

    # 4. Первый экран — требование чистой сессии до заголовка «Кому»
    if text.index("Не используйте память") > text.index("**Кому:**"):
        errors.append("требование чистой сессии не на первом экране")

    if errors:
        print("ПРИЁМКА БРИФА: РАСХОЖДЕНИЯ")
        for e in errors:
            print(" -", e)
        return 1
    print("приёмка брифа v5: все проверки сходятся с пакетом")
    return 0


if __name__ == "__main__":
    sys.exit(main())
