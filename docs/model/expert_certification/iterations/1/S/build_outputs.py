"""Run the expert engine over all portraits, validate invariants, aggregate
statistics and build a stratified 40-case audit file with card excerpts."""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from expert_engine import EPS, EXPENSIVE_SPREAD, ExpertEngine

UPLOADS = Path("/mnt/user-data/uploads")
OUT = Path("/home/claude/out")
TOL = 1.0


def load_portraits() -> list[dict]:
    with open(UPLOADS / "portraits_12000.jsonl") as f:
        return [json.loads(line) for line in f]


def validate(profile: dict, rec: dict, errors: Counter) -> None:
    eng = profile["engine"]
    bliq = eng["bliq"]
    stock = rec["stock_allocation"]
    prepay_total = sum(p["amount"] for p in stock["debt_prepay"])
    goals_stock = sum(g["amount"] for g in stock["goals"])
    total_stock = stock["reserve"] + prepay_total + goals_stock + stock["invest"]
    if abs(total_stock - bliq) > TOL:
        errors["stock_sum"] += 1

    flow = rec["flow_allocation"]
    flow_total = (flow["reserve_topup"] + sum(d["monthly"] for d in flow["debt_extra"])
                  + sum(g["monthly"] for g in flow["goals"]) + flow["invest"])
    post_fcf = max(rec["post_allocation"]["fcf"], 0.0)
    if abs(flow_total - post_fcf) > TOL:
        errors["flow_sum"] += 1

    if rec["branch"] == "crisis":
        if flow_total > TOL or goals_stock > TOL or stock["invest"] > TOL:
            errors["crisis_leak"] += 1

    prepaid = {p["id"]: p["amount"] for p in stock["debt_prepay"]}
    r_bench = eng["r_bench"]
    for o in eng["obligations"]:
        pre = prepaid.get(o["id"], 0.0)
        if pre > o["amount"] + TOL:
            errors["overpaid_debt"] += 1
        if pre > TOL and o["interest_rate"] < r_bench and rec["branch"] == "normal":
            errors["cheap_prepaid_normal"] += 1

    if stock["invest"] > TOL and rec["branch"] != "crisis":
        for o in eng["obligations"]:
            open_bal = o["amount"] - prepaid.get(o["id"], 0.0)
            if open_bal > TOL and o["interest_rate"] > r_bench + EXPENSIVE_SPREAD:
                errors["invest_with_expensive_open"] += 1
                break

    by_id = {g["id"]: g for g in eng["goals"]}
    for gs in rec["goal_status"]:
        orig = by_id[gs["id"]]
        gap = max(orig["target_amount"] - orig["current_amount"], 0.0)
        if gs["from_stock"] > gap + TOL:
            errors["goal_overfilled"] += 1
        if orig["current_amount"] >= orig["target_amount"] - EPS:
            if gs["from_stock"] > TOL or gs["allocated_monthly"] > TOL:
                errors["funded_goal_allocated"] += 1

    dated = sorted(
        (gs for gs in rec["goal_status"] if gs["deadline"]),
        key=lambda g: (g["deadline"], g["id"]),
    )
    seen_underfunded_flow = False
    seen_unfilled_stock = False
    for gs in dated:
        if seen_underfunded_flow and gs["allocated_monthly"] > TOL:
            errors["flow_priority_violation"] += 1
        if seen_unfilled_stock and gs["from_stock"] > TOL:
            errors["stock_priority_violation"] += 1
        if gs["status"] == "underfunded" and gs["allocated_monthly"] > TOL:
            seen_underfunded_flow = True
        if gs["status"] == "underfunded" and gs["allocated_monthly"] <= TOL:
            seen_underfunded_flow = True
        if gs["status"] != "funded" and gs["current"] < gs["target"] - TOL:
            seen_unfilled_stock = True


def aggregates(portraits: list[dict], recs: list[dict]) -> dict:
    by_kind = defaultdict(Counter)
    underfunded = 0
    dated_total = 0
    refi = 0
    invest_share = defaultdict(list)
    for p, r in zip(portraits, recs):
        by_kind[p["kind"]][r["branch"]] += 1
        for gs in r["goal_status"]:
            if gs["deadline"]:
                dated_total += 1
                if gs["status"] in ("underfunded", "frozen"):
                    underfunded += 1
        if any("ефинансир" in a or "еструктур" in a for a in r["actions"]):
            refi += 1
        bliq = p["engine"]["bliq"]
        if bliq > 0:
            invest_share[p["kind"]].append(r["stock_allocation"]["invest"] / bliq)
    med_invest = {
        k: round(sorted(v)[len(v) // 2], 3) for k, v in invest_share.items()
    }
    return {
        "branches_by_kind": {k: dict(v) for k, v in sorted(by_kind.items())},
        "dated_goals_total": dated_total,
        "dated_goals_at_risk": underfunded,
        "profiles_with_restructuring_action": refi,
        "median_invest_share_of_bliq": med_invest,
    }


def extract_cards(sample_ids: set[str]) -> dict[str, str]:
    text = (UPLOADS / "synthetic_portraits_12000_cards.md").read_text(
        encoding="utf-8", errors="replace"
    )
    blocks = {}
    for m in re.finditer(r"\n## (SP-\d{5})[^\n]*\n", text):
        sp = m.group(1)
        if sp not in sample_ids:
            continue
        start = m.start() + 1
        nxt = text.find("\n## SP-", m.end())
        blocks[sp] = text[start: nxt if nxt != -1 else len(text)].strip()
    return blocks


def fmt(x: float) -> str:
    return f"{round(x):,}".replace(",", " ")


def render_recommendation(rec: dict) -> str:
    d = rec["diagnosis"]
    p = rec["post_allocation"]
    lines = [f"### Экспертное распределение — {rec['id']} · ветка: `{rec['branch']}`", ""]
    pdn = f"{d['pdn']:.0%}" if d["pdn"] is not None else "н/п (нет дохода)"
    cush = f"{d['cushion_months']:.1f} мес" if d["cushion_months"] is not None else "∞"
    lines.append(
        f"**Диагноз:** FCF {fmt(d['fcf'])} ₽/мес · ПДН {pdn} · подушка {cush} · "
        f"флаги: {', '.join(d['flags']) or '—'}"
    )
    lines.append("")
    s = rec["stock_allocation"]
    lines.append("**Распределение запаса (B_liq):**")
    lines.append("")
    lines.append("| Корзина | Сумма (₽) |")
    lines.append("|---|---:|")
    lines.append(f"| Резерв | {fmt(s['reserve'])} |")
    for pr in s["debt_prepay"]:
        tag = "закрыт" if pr["closes"] else "частично"
        lines.append(f"| Досрочка {pr['name']} ({tag}) | {fmt(pr['amount'])} |")
    for g in s["goals"]:
        lines.append(f"| Цель #{g['id']} | {fmt(g['amount'])} |")
    lines.append(f"| Инвестиции | {fmt(s['invest'])} |")
    lines.append("")
    f = rec["flow_allocation"]
    lines.append("**Распределение потока (₽/мес):**")
    lines.append("")
    lines.append("| Корзина | Сумма (₽/мес) |")
    lines.append("|---|---:|")
    lines.append(f"| Пополнение резерва | {fmt(f['reserve_topup'])} |")
    for de in f["debt_extra"]:
        lines.append(f"| Досрочка {de['name']} | {fmt(de['monthly'])} |")
    for g in f["goals"]:
        lines.append(f"| Цель #{g['id']} | {fmt(g['monthly'])} |")
    lines.append(f"| Инвестиции | {fmt(f['invest'])} |")
    lines.append("")
    if rec["goal_status"]:
        lines.append("**Цели:**")
        lines.append("")
        lines.append("| # | Дедлайн | Нужно ₽/мес | Выделено ₽/мес | Из запаса | Статус | Сдвиг |")
        lines.append("|---|---|---:|---:|---:|---|---:|")
        for gs in rec["goal_status"]:
            req = fmt(gs["required_monthly"]) if gs["required_monthly"] is not None else "—"
            delay = f"{gs['delay_months']} мес" if gs["delay_months"] else "—"
            lines.append(
                f"| {gs['id']} | {gs['deadline'] or 'без срока'} | {req} | "
                f"{fmt(gs['allocated_monthly'])} | {fmt(gs['from_stock'])} | "
                f"{gs['status']} | {delay} |"
            )
        lines.append("")
    lines.append("**Действия:**")
    lines.append("")
    for a in rec["actions"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append(
        f"**После распределения:** FCF {fmt(p['fcf'])} ₽/мес · резерв "
        f"{p['reserve_months'] if p['reserve_months'] is not None else '∞'} мес оттока · "
        f"инструменты: резерв — {rec['instruments']['reserve']}; "
        f"инвестиции — {rec['instruments']['invest']}"
    )
    return "\n".join(lines)


AUDIT_HEADER = """# Аудит-выборка: 40 портретов (по 4 на каждый структурный тип)

Независимая экспертная разметка. Методика — стандартный каскад финансового
планирования, без использования клиентской методологии.

**Каскад (запас):** пол резерва 3 мес полного оттока → дорогой долг
(ставка > r_bench + 3 п.п., лавина) → резерв до 6 мес → цели (ближайший
дедлайн первым, бессрочные — по наименьшему остатку) → пограничный долг
(r_bench…r_bench+3 п.п.) 50/50 с инвестициями → инвестиции по риск-профилю.

**Каскад (поток):** пол резерва → досрочка дорогого долга → взносы на цели
с дедлайнами → резерв до 6 мес → пограничный долг 50/50 → инвестиции.
Асимметрия сознательная: разовый запас сначала достраивает безопасность,
регулярный поток не должен морозить цели с дедлайнами ради 4-6-го месяца подушки.

**Кризисная ветка (FCF < 0):** полное закрытие кредитов из ликвидности,
если после закрытия остаётся ≥ 1 мес оттока и запас прочности растёт
(остаток/платёж < текущий runway); дешёвые ставки (< r_bench) закрываются
только при runway < 12 мес. Если поток не восстановлен: весь остаток — в
резерв, цели заморожены, реструктуризация и сокращение расходов.

**Допущения:** целевые накопления обособлены от B_liq; дата расчёта
2026-07-07; ставка на накопления = r_bench профиля, капитализация месячная;
частичная досрочка — с сокращением срока; ПДН > 50% — красная зона;
лимит АСВ 1.4 млн ₽ на банк.

---
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    portraits = load_portraits()
    engine = ExpertEngine()
    recs = [engine.advise(p) for p in portraits]

    errors: Counter = Counter()
    for p, r in zip(portraits, recs):
        validate(p, r, errors)
    print("validation errors:", dict(errors) or "NONE")

    with open(OUT / "recommendations_12000.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    agg = aggregates(portraits, recs)
    print(json.dumps(agg, ensure_ascii=False, indent=1))

    rng = random.Random(20260707)
    by_kind = defaultdict(list)
    for p in portraits:
        by_kind[p["kind"]].append(p["id"])
    sample_ids = []
    for kind in sorted(by_kind):
        sample_ids.extend(rng.sample(by_kind[kind], 4))
    id_set = set(sample_ids)
    cards = extract_cards(id_set)
    rec_by_id = {r["id"]: r for r in recs}

    parts = [AUDIT_HEADER]
    for sp in sorted(sample_ids):
        parts.append(cards.get(sp, f"## {sp} (карточка не найдена)"))
        parts.append("")
        parts.append(render_recommendation(rec_by_id[sp]))
        parts.append("\n---\n")
    (OUT / "audit_sample_40.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"audit file: {len(sample_ids)} cases")


if __name__ == "__main__":
    main()
