"""
Отбор 40 портретов для протокола проверки объяснимости (ROADMAP §6.5, после Волны 0).

Не раунд сертификации: раунды проверяли РЕШЕНИЯ модели против экспертного консенсуса
(5 раундов). Этот протокол впервые проверяет ТЕКСТ объяснения — «понятно ли, почему
именно так» — предложен владельцем в `docs/reports/testing/round5_owner_memo.md` п.6.3.
1 эксперт (не 4), 40 портретов (не 12 000), без статистики согласия.

Дисциплина слепой сессии сохраняется (сквозное правило §4 ROADMAP: тестирование
мат-модели строго вне сессии с памятью/инструкциями проекта). Эта сессия ИМЕЕТ полную
память проекта — не может сама быть «слепым экспертом». Задача скрипта — только
подготовить материал (портрет → текст объяснения) и протокол-вопросник; саму оценку
проводит отдельная чистая сессия/человек по `docs/model/explainability_protocol.md`.

Покрытие — 7 веток explain_alternative()/build_crisis_plan(), по которым явно ветвится
формулировка текста (не случайная выборка):
  1. Обычное распределение (типовой план)
  2. Кризисный режим (Rt < 0, §12)
  3. Токсичный долг (G8, floor 1 мес)
  4. Полоса тонкой подушки (Lt в [1; 2) — главная зона неопределённости раунда 5)
  5. Без целей (инвестиционный транш, §13)
  6. Насыщенная подушка (Lt >= Lt*, весь поток — либо транш, либо цели)
  7. Длинная цель, индексированная на инфляцию (> 36 мес, батч 0.1)

Запуск: python -m tools.model_validation.explainability_protocol_selection
Выход: docs/reports/testing/explainability_review_material.md
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core.ranking import RESERVE_FLOOR_MONTHS, TOXIC_FLOOR_MONTHS
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

OUTPUT = Path("docs/reports/testing/explainability_review_material.md")
FROZEN_TODAY = datetime(2026, 7, 2, 12, 0, 0)
GEN_TODAY = date(2026, 7, 2)
QUOTA_PER_BUCKET = {
    "plain": 8,
    "crisis": 6,
    "toxic_debt": 5,
    "thin_cushion": 6,
    "no_goals": 5,
    "saturated_cushion": 5,
    "long_goal_inflated": 5,
}


def _run(p: dict[str, Any]) -> dict[str, Any]:
    return run_planning(
        income_total=p["income_total"], expense_total=p["expense_total"],
        obligations=p["obligations"], goals=p["goals"], bliq=p["bliq"],
        r_bench=p["r_bench"], risk_tolerance=p["risk_tolerance"],
        l_min=p["l_min"], today=FROZEN_TODAY,
    )


def _classify(p: dict[str, Any], result: dict[str, Any]) -> str | None:
    rt = result["indicators"]["Rt"]
    lt = result["indicators"]["Lt"]
    if rt < 0:
        return "crisis"
    obligations = p.get("obligations") or []
    if any(
        float(o.get("interest_rate", 0)) >= max(0.30, p["r_bench"] + 0.15)
        and float(o.get("amount", 0)) > 0
        for o in obligations
    ):
        return "toxic_debt"
    if 1.0 <= lt < 2.0:
        return "thin_cushion"
    if not p.get("goals"):
        return "no_goals"
    if lt >= RESERVE_FLOOR_MONTHS and result.get("best", {}).get("investment_tranche"):
        return "saturated_cushion"
    for g in p.get("goals", []):
        dl = g.get("deadline")
        if dl and (dl - GEN_TODAY).days / 30.0 > 36.0:
            return "long_goal_inflated"
    if p.get("kind") == "plain":
        return "plain"
    return None


def _fmt_money(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def _render_case(idx: int, bucket: str, p: dict[str, Any], result: dict[str, Any]) -> str:
    ind = result["indicators"]
    lines = [
        f"## Портрет {idx} — ветка «{bucket}»",
        "",
        f"- Доход {_fmt_money(p['income_total'])} ₽, расходы {_fmt_money(p['expense_total'])} ₽, "
        f"обязательств: {len(p['obligations'])}, целей: {len(p['goals'])}, "
        f"ликвидная подушка {_fmt_money(p['bliq'])} ₽, риск-профиль {p['risk_tolerance']}/5",
        f"- Rt={ind['Rt']:.0f} ₽, Lt={ind['Lt']:.2f} мес, Dt={ind['Dt']*100:.0f}%",
        "",
    ]
    if bucket == "crisis":
        cp = result.get("crisis_plan") or {}
        lines.append("**Текст (кризисный режим):**")
        lines.append("")
        lines.append(f"> {cp.get('summary', '(нет текста)')}")
    else:
        best = result.get("best")
        if not best:
            lines.append("_(нет допустимой альтернативы — план не построен)_")
        else:
            expl = best.get("explanation", {})
            lines.append("**Текст (объяснение выбранного плана):**")
            lines.append("")
            for g in expl.get("gains", []):
                lines.append(f"> {g}")
            for c in expl.get("costs", []):
                lines.append(f"> {c}")
            lines.append(f"> {expl.get('insight', '')}")
            cf = expl.get("counterfactual")
            if cf and cf.get("available"):
                lines.append("")
                lines.append(f"> Контрфакт: {cf.get('text', '')}")
    lines.append("")
    lines.append(
        "**Вопрос:** понятно ли из этого текста, почему модель решила именно так? "
        "(да / отчасти / нет — и если не да, что именно неясно)"
    )
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


def select_and_render(seed: int = 20260812, pool: int = 4000) -> str:
    gen = PortraitGenerator(seed, version=2)
    buckets: dict[str, list[tuple[dict, dict]]] = {k: [] for k in QUOTA_PER_BUCKET}

    i = 0
    while i < pool and any(
        len(buckets[k]) < q for k, q in QUOTA_PER_BUCKET.items()
    ):
        p = gen.generate(i)
        i += 1
        if p["income_total"] <= 0:
            continue
        try:
            result = _run(p)
        except Exception:
            continue
        bucket = _classify(p, result)
        if bucket is None or len(buckets[bucket]) >= QUOTA_PER_BUCKET[bucket]:
            continue
        buckets[bucket].append((p, result))

    sections = [
        "# Материал для протокола проверки объяснимости",
        "",
        "> Подготовлено кодом (`tools/model_validation/"
        "explainability_protocol_selection.py`), не отобрано вручную — воспроизводимо по "
        "(seed, today). Инструкция для того, кто оценивает, — "
        "`docs/model/explainability_protocol.md`. **Эта сессия НЕ является слепым "
        "экспертом** (полная память проекта) — только подготовка материала.",
        "",
    ]
    idx = 1
    total_selected = 0
    for bucket, quota in QUOTA_PER_BUCKET.items():
        got = len(buckets[bucket])
        total_selected += got
        if got < quota:
            sections.append(
                f"> **[!] Ветка «{bucket}»: набрано {got} из {quota}** — не хватило "
                f"портретов в пуле {pool}, увеличить `pool` при перегенерации.\n"
            )
        for p, result in buckets[bucket]:
            sections.append(_render_case(idx, bucket, p, result))
            idx += 1

    total_quota = sum(QUOTA_PER_BUCKET.values())
    sections.insert(3, f"Портретов отобрано: {total_selected} из {total_quota} заявленных.\n")
    return "\n".join(sections)


def main() -> None:
    text = select_and_render()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Материал записан: {OUTPUT} ({len(text)} байт)")


if __name__ == "__main__":
    main()
