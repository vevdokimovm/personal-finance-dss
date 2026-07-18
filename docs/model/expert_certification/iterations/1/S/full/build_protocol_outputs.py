"""Protocol pipeline: run engine v2, validate invariants, cross-check cards,
emit summary.csv and aggregate_report.md."""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from finpilot_expert_engine import (
    CHEAP_CLOSE_RUNWAY, EPS, EXPENSIVE_SPREAD, FLOOR_MONTHS, TARGET_MONTHS, TODAY,
    ExpertEngine, band,
)

UPLOADS = Path("/mnt/user-data/uploads")
OUT = Path("/home/claude/out2")
TOL = 1.0


def run_engine(portraits: list[dict]) -> list[dict]:
    engine = ExpertEngine()
    return [engine.advise(p) for p in portraits]


def validate(p: dict, r: dict, errors: Counter) -> None:
    eng = p["engine"]
    bliq = eng["bliq"]
    lump_total = sum(x["amount"] for x in r["lump_sum_plan"])
    if abs(lump_total - bliq) > TOL:
        errors["lump_conservation"] += 1

    monthly_total = sum(x["amount"] for x in r["monthly_plan"])
    post_fcf = max(r["diagnostics"]["post"]["fcf"], 0.0)
    if abs(monthly_total - post_fcf) > TOL:
        errors["monthly_conservation"] += 1

    if r["status"] == "crisis":
        if monthly_total > TOL:
            errors["crisis_monthly_leak"] += 1
        if any(x["bucket"] in ("goal", "invest") for x in r["lump_sum_plan"]):
            errors["crisis_lump_leak"] += 1

    r_bench = eng["r_bench"]
    for d in r["debt_plan"]:
        if d["lump_amount"] > d["balance_start"] + TOL:
            errors["debt_overpaid"] += 1
        if (d["lump_amount"] > TOL and d["vs_bench"] == "cheap"
                and r["branch"] == "normal"):
            errors["cheap_prepaid_normal"] += 1

    invest_lump = sum(x["amount"] for x in r["lump_sum_plan"] if x["bucket"] == "invest")
    if invest_lump > TOL:
        for d in r["debt_plan"]:
            if (d["balance_start"] - d["lump_amount"] > TOL
                    and d["vs_bench"] == "expensive"):
                errors["invest_with_expensive_open"] += 1
                break

    for g in r["goal_plan"]:
        gap = max(g["target"] - g["current_start"], 0.0)
        if g["lump_allocation"] > gap + TOL:
            errors["goal_overfilled"] += 1
        if g["current_start"] >= g["target"] - EPS:
            if g["lump_allocation"] > TOL or g["allocated_monthly"] > TOL:
                errors["funded_goal_allocated"] += 1

    dated = sorted((g for g in r["goal_plan"] if g["deadline"]),
                   key=lambda g: (g["deadline"], g["id"]))
    flow_broken = False
    stock_broken = False
    for g in dated:
        if flow_broken and g["allocated_monthly"] > TOL:
            errors["flow_priority_violation"] += 1
        if stock_broken and g["lump_allocation"] > TOL:
            errors["stock_priority_violation"] += 1
        if g["status"] == "underfunded":
            flow_broken = True
        if g["current_start"] + g["lump_allocation"] < g["target"] - TOL:
            stock_broken = True


NUM = re.compile(r"[\d\s\u00a0]+")


def _num(s: str) -> float:
    return float(re.sub(r"[\s\u00a0]", "", s))


def cross_check_cards(portraits: list[dict], n_samples: int = 5) -> list[dict]:
    text = (UPLOADS / "synthetic_portraits_12000_cards.md").read_text(
        encoding="utf-8", errors="replace")
    rng = random.Random(20260707)
    sample = rng.sample(portraits, n_samples)
    results = []
    for p in sample:
        sp = p["id"]
        m = re.search(rf"\n## {sp}[^\n]*\n", text)
        nxt = text.find("\n## SP-", m.end())
        block = text[m.start(): nxt if nxt != -1 else len(text)]
        card = {}
        mm = re.search(r"\*\*Доходы — ([\d\s\u00a0]+) ₽/мес\*\*", block)
        card["income"] = _num(mm.group(1))
        mm = re.search(r"\*\*Расходы — ([\d\s\u00a0]+) ₽/мес\*\*", block)
        card["expenses"] = _num(mm.group(1))
        mm = re.search(r"\*\*Ликвидная позиция — ([\d\s\u00a0]+) ₽\*\*", block)
        card["bliq"] = _num(mm.group(1))
        mm = re.search(r"\|\s*\*\*Итого\*\*\s*\|\s*\|\s*\*\*([\d\s\u00a0]+)\*\*\s*\|"
                       r"\s*\*\*([\d\s\u00a0]+)\*\*", block)
        if mm:
            card["debt_total"], card["pay_total"] = _num(mm.group(1)), _num(mm.group(2))
        else:
            card["debt_total"] = card["pay_total"] = 0.0
        goal_rows = re.findall(
            r"\|\s*\d+\s*\|[^|]+\|\s*([\d\s\u00a0]+)\s*\|\s*([\d\s\u00a0]+)\s*\|"
            r"\s*[\d\s\u00a0]+\s*\|\s*[\d.,]+\s*%", block)
        card["goal_target"] = sum(_num(a) for a, _ in goal_rows)
        card["goal_current"] = sum(_num(b) for _, b in goal_rows)

        e = p["engine"]
        checks = {
            "income": (card["income"], e["income_total"]),
            "expenses": (card["expenses"], e["expense_total"]),
            "bliq": (card["bliq"], e["bliq"]),
            "debt_total": (card["debt_total"], sum(o["amount"] for o in e["obligations"])),
            "pay_total": (card["pay_total"], sum(o["monthly_payment"] for o in e["obligations"])),
            "goal_target": (card["goal_target"], sum(g["target_amount"] for g in e["goals"])),
            "goal_current": (card["goal_current"], sum(g["current_amount"] for g in e["goals"])),
        }
        tol = 2.0
        results.append({
            "id": sp,
            "match": all(abs(a - b) <= tol for a, b in checks.values()),
            "max_diff": round(max(abs(a - b) for a, b in checks.values()), 2),
        })
    return results


def write_summary_csv(portraits: list[dict], recs: list[dict]) -> None:
    cols = ["id", "kind", "status", "branch", "income", "expenses", "debt_service",
            "bliq", "r_bench", "risk", "fcf", "pdn", "cushion_months",
            "floor_reserve", "target_reserve", "lump_reserve", "lump_debt",
            "lump_goals", "lump_invest", "mon_reserve", "mon_debt", "mon_goals",
            "mon_invest", "n_debts", "n_debts_closed", "n_goals", "n_dated_goals",
            "n_goals_at_risk", "post_reserve_months", "flags"]
    with open(OUT / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for p, r in zip(portraits, recs):
            e = p["engine"]
            d = r["diagnostics"]
            lump = defaultdict(float)
            for x in r["lump_sum_plan"]:
                key = "debt" if x["bucket"].startswith("debt") else x["bucket"]
                lump[key] += x["amount"]
            mon = defaultdict(float)
            for x in r["monthly_plan"]:
                key = ("reserve" if x["bucket"] == "reserve_topup"
                       else "debt" if x["bucket"] == "debt_extra" else x["bucket"])
                mon[key] += x["amount"]
            w.writerow([
                r["id"], r["kind"], r["status"], r["branch"],
                round(e["income_total"], 2), round(e["expense_total"], 2),
                d["debt_service"], round(e["bliq"], 2), e["r_bench"],
                e["risk_tolerance"], d["fcf"], d["pdn"], d["cushion_months"],
                d["floor_reserve"], d["target_reserve"],
                round(lump["reserve"], 2), round(lump["debt"], 2),
                round(lump["goal"], 2), round(lump["invest"], 2),
                round(mon["reserve"], 2), round(mon["debt"], 2),
                round(mon["goal"], 2), round(mon["invest"], 2),
                len(e["obligations"]),
                sum(1 for x in r["debt_plan"] if x["closes"]),
                len(e["goals"]),
                sum(1 for g in r["goal_plan"] if g["deadline"]),
                sum(1 for g in r["goal_plan"] if g["status"] in ("underfunded", "frozen")),
                d["post"]["reserve_months"],
                "|".join(r["flags"]),
            ])


def write_aggregate_report(portraits: list[dict], recs: list[dict],
                           errors: Counter, cards: list[dict]) -> None:
    status_total = Counter(r["status"] for r in recs)
    status_by_kind = defaultdict(Counter)
    for r in recs:
        status_by_kind[r["kind"]][r["status"]] += 1
    closures = sum(1 for r in recs for d in r["debt_plan"] if d["closes"])
    restructure = sum(
        1 for r in recs if any(d["action"] == "restructure" for d in r["debt_plan"]))
    refinance = sum(
        1 for r in recs if any(d["action"] == "refinance" for d in r["debt_plan"]))
    goals_total = sum(len(r["goal_plan"]) for r in recs)
    dated_total = sum(1 for r in recs for g in r["goal_plan"] if g["deadline"])
    at_risk = sum(1 for r in recs for g in r["goal_plan"]
                  if g["status"] in ("underfunded", "frozen"))
    invest_any = sum(
        1 for r in recs
        if any(x["bucket"] == "invest" for x in r["lump_sum_plan"] + r["monthly_plan"]))

    statuses = ["crisis", "vulnerable", "stretched", "on_plan", "surplus"]
    lines = [
        "# FINPILOT · Экспертный прогон 12 000 портретов — сводный отчёт",
        "",
        f"Дата среза: {TODAY.isoformat()}. Датасет: `portraits_12000.jsonl` "
        "(поле `dataset_version` в файле отсутствует — см. dataset_review.md, P8).",
        "",
        "## 1. Методология и константы (зафиксированы до обработки)",
        "",
        "Методология и все константы были опубликованы в диалоге до запуска обработки "
        "и до получения координационной методички — подгонка под ожидания исключена "
        "по построению.",
        "",
        "| Константа | Значение | Обоснование |",
        "|---|---|---|",
        "| Пол резерва | 3 мес полного оттока (расходы + платежи) | стандарт финпланирования |",
        f"| Целевой резерв | {TARGET_MONTHS:.0f} мес оттока, плоско по риск-профилям | "
        "резерв — инструмент безопасности; риск-аппетит влияет на инвест-микс, не на подушку |",
        f"| Дорогой долг | ставка > r_bench + {EXPENSIVE_SPREAD * 100:.0f} п.п. | арбитраж ставок |",
        f"| Пограничный долг | r_bench … r_bench + {EXPENSIVE_SPREAD * 100:.0f} п.п., "
        "остаток 50/50 досрочка/инвест | зона безразличия |",
        "| Дешёвый долг | ставка < r_bench — не гасить вне кризиса | спред работает на клиента |",
        "| ПДН | 30% повышенная, 50% красная зона | макропруденциальная практика ЦБ |",
        "| Кризисное закрытие | только полное; после закрытия ≥ 1 мес нового оттока; "
        "остаток/платёж < текущий runway | закрытие должно удлинять выживание |",
        f"| Дешёвые в кризисе | закрывать только при runway < {CHEAP_CLOSE_RUNWAY:.0f} мес | "
        "иначе арбитраж важнее |",
        "| Взнос на цель | аннуитетная формула при r_bench, капитализация месячная | — |",
        "| Приоритет целей | ближайший дедлайн; бессрочные — остаточно | — |",
        "| Инструменты по горизонту | <12 мес накопительный счёт; 12-36 депозит/ОФЗ; "
        ">36 микс по риску (0/10/25-30/30-45/45-60% акций) | — |",
        "| Лимит АСВ | 1.4 млн ₽ на банк | страхование вкладов |",
        "| Допущение | целевые накопления обособлены от B_liq | иначе двойной счёт подушки |",
        "",
        "Каскад (lump): пол 3 мес → дорогой долг (лавина) → резерв до 6 мес → цели "
        "(дедлайн-приоритет) → пограничный 50/50 → инвест. Каскад (поток): пол → дорогой "
        "долг → взносы на цели → резерв до 6 мес → пограничный 50/50 → инвест. Асимметрия "
        "сознательная: разовый запас достраивает безопасность, поток не морозит дедлайны "
        "ради 4-6-го месяца подушки.",
        "",
        "## 2. Контроли",
        "",
        f"- Сохранение сумм и логические инварианты (10 проверок × 12 000 записей): "
        f"**{sum(errors.values())} нарушений**"
        + ("" if not errors else f" — {dict(errors)}"),
        "- Месячные бакеты = max(0, поток после lump-действий): закрытия кредитов меняют "
        "платежи, поэтому контроль ведётся против пост-lump потока.",
        f"- Сверка JSONL ↔ карточки ({len(cards)} случайных портретов, допуск ±2 ₽ "
        "на агрегат из-за построчного округления):",
        "",
        "| Портрет | Совпадение | Макс. расхождение, ₽ |",
        "|---|---|---:|",
    ]
    for c in cards:
        lines.append(f"| {c['id']} | {'да' if c['match'] else 'НЕТ'} | {c['max_diff']} |")
    lines += [
        "",
        "## 3. Распределение статусов",
        "",
        "| Статус | Всего | " + " | ".join(sorted(status_by_kind)) + " |",
        "|---|---:|" + "---:|" * len(status_by_kind),
    ]
    for s in statuses:
        row = [f"| {s} | {status_total.get(s, 0)}"]
        for k in sorted(status_by_kind):
            row.append(f" {status_by_kind[k].get(s, 0)}")
        lines.append(" |".join(row) + " |")
    lines += [
        "",
        "Статусы: crisis — дефицит не устранён; vulnerable — поток ≥ 0, но резерв ниже "
        "пола или открыт дорогой долг; stretched — база устойчива, часть целей с "
        "дедлайнами не успевает; on_plan — пол закрыт, цели по графику; surplus — резерв "
        "6 мес укомплектован, идут инвестиции. Флаг `cash_flow_repaired_by_closures` "
        "отмечает профили, где поток восстановлен закрытием кредитов из ликвидности.",
        "",
        "## 4. Ключевые агрегаты",
        "",
        f"- Кредитов закрыто из ликвидности: {closures}",
        f"- Профилей с рекомендацией реструктуризации: {restructure}",
        f"- Профилей с рекомендацией рефинансирования: {refinance}",
        f"- Целей всего {goals_total}, с дедлайнами {dated_total}, под риском "
        f"(underfunded/frozen): {at_risk} ({at_risk / max(dated_total, 1):.0%} дедлайновых)",
        f"- Профилей с ненулевой инвестиционной корзиной: {invest_any}",
        f"- Профилей с восстановленным потоком: "
        f"{sum(1 for r in recs if r['branch'] == 'crisis_repaired')}",
        "",
        "Интерпретация перекосов — в dataset_review.md: доминирование crisis-статусов "
        "отражает свойства генератора (платежи не согласованы с доходом), а не методику.",
    ]
    (OUT / "aggregate_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    portraits = [json.loads(l) for l in open(UPLOADS / "portraits_12000.jsonl")]
    recs = run_engine(portraits)

    errors: Counter = Counter()
    for p, r in zip(portraits, recs):
        validate(p, r, errors)
    print("invariant violations:", dict(errors) or "NONE")

    with open(OUT / "recommendations.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    cards = cross_check_cards(portraits)
    print("cards cross-check:", cards)

    write_summary_csv(portraits, recs)
    write_aggregate_report(portraits, recs, errors, cards)
    print("status distribution:", dict(Counter(r["status"] for r in recs)))


if __name__ == "__main__":
    main()
