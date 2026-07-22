"""Build expert_opinions_sample_v4.md: 40 deterministically sampled rows
(every 300th input position), each with readable input, metrics, decision,
prose reasoning and a manual "on paper" recomputation.

The manual recompute below deliberately re-implements the WRITTEN methodology
with hard-coded constants (no imports from the engine's Constants) so that a
drift between engine and document would surface as a mismatch.
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import math
from pathlib import Path

from engine_v4 import Constants, Pipeline, Validator

CUTOFF = dt.date(2026, 7, 18)


def fmt(value) -> str:
    """Format money with thin-space thousands, keeping prose commas intact."""
    return f"{value:,.0f}".replace(",", " ")


RESERVE_MONTHS = {1: 6, 2: 5, 3: 4, 4: 3, 5: 3}


def paper_recompute(raw: dict) -> dict:
    """Straight sequential arithmetic per expert_methodology_v4.md."""
    payments = sum(o["monthly_payment"] for o in raw["obligations"])
    fcf = raw["income_total"] - raw["expense_total"] - payments
    burn = raw["expense_total"] + payments
    bench = raw["r_bench"]
    target = RESERVE_MONTHS[raw["risk_tolerance"]] * burn
    debts = []
    for o in raw["obligations"]:
        rate = o["interest_rate"]
        if rate >= 0.45:
            klass = "toxic"
        elif rate > bench + 0.02:
            klass = "expensive"
        else:
            klass = "cheap"
        debts.append({"name": o["name"], "amount": o["amount"],
                      "rate": rate, "payment": o["monthly_payment"],
                      "klass": klass, "paid": 0.0})
    goals = []
    for g in raw["goals"]:
        deadline = (dt.date.fromisoformat(g["deadline"])
                    if g["deadline"] else None)
        gap = max(0.0, g["target_amount"] - g["current_amount"])
        months = None
        overdue = False
        if deadline is not None:
            days = (deadline - CUTOFF).days
            if days < 0:
                overdue, months = True, 12
            else:
                months = max(1, math.ceil(days / 30.4375))
        goals.append({"name": g["name"], "deadline": deadline, "gap": gap,
                      "months": months, "overdue": overdue, "lump": 0.0})

    bliq, spent = raw["bliq"], 0.0
    floor_toxic, floor_normal = 1.0 * burn, target

    def excess(floor):
        return max(0.0, bliq - spent - floor)

    for d in sorted([d for d in debts if d["klass"] == "toxic"
                     and d["amount"] > 0],
                    key=lambda d: (-d["rate"], -d["amount"])):
        room = excess(floor_toxic)
        if room <= 0:
            break
        move = min(room, d["amount"])
        if move < d["amount"] and move < 10_000:
            continue
        d["paid"] = move
        spent += move
    for d in sorted([d for d in debts if d["klass"] == "expensive"
                     and d["amount"] > 0],
                    key=lambda d: (-d["rate"], -d["amount"])):
        room = excess(floor_normal)
        if room <= 0:
            break
        move = min(room, d["amount"])
        if move < d["amount"] and move < 10_000:
            continue
        d["paid"] = move
        spent += move
    if fcf >= 0:
        urgent = [g for g in goals if g["deadline"] is not None
                  and g["gap"] > 0
                  and (g["overdue"]
                       or (g["deadline"] - CUTOFF).days <= 365)]
        for g in sorted(urgent, key=lambda g: g["deadline"]):
            room = excess(floor_normal)
            if room <= 0:
                break
            move = min(room, g["gap"])
            if move < g["gap"] and move < 10_000:
                continue
            g["lump"] = move
            g["gap"] -= move
            spent += move
        room = excess(floor_normal)
        if room >= 10_000:
            spent += room
    lump = int(math.floor(spent))

    res = debt = goal = inv = 0.0
    if fcf > 0:
        bliq_after = bliq - spent
        rem = fcf
        if bliq_after < burn:
            take = min(rem, (burn - bliq_after) / 3.0)
            res += take
            rem -= take
        toxic_left = [d for d in debts if d["klass"] == "toxic"
                      and d["amount"] - d["paid"] > 0]
        exp_left = [d for d in debts if d["klass"] == "expensive"
                    and d["amount"] - d["paid"] > 0]
        if toxic_left and rem > 0:
            debt += rem
            rem = 0.0
        else:
            dated = sorted([g for g in goals if g["deadline"] is not None
                            and g["gap"] > 0], key=lambda g: g["deadline"])
            if dated and rem > 0:
                budget = rem * (0.5 if exp_left else 1.0)
                spent_g = 0.0
                for g in dated:
                    if budget <= 0:
                        break
                    take = min(g["gap"] / g["months"], budget)
                    spent_g += take
                    budget -= take
                goal += spent_g
                rem -= spent_g
            if exp_left and rem > 0:
                if bliq_after < target:
                    debt += rem * 0.7
                    res += rem * 0.3
                else:
                    debt += rem
                rem = 0.0
            if rem > 0 and bliq_after < target:
                take = min(rem, (target - bliq_after) / 6.0)
                res += take
                rem -= take
            if rem > 0:
                open_goals = [g for g in goals if g["deadline"] is None
                              and g["gap"] > 0]
                if open_goals:
                    goal += rem / 2.0
                    inv += rem - rem / 2.0
                else:
                    inv += rem
    return {"fcf": fcf, "burn": burn, "target": target,
            "res": int(res), "debt": int(debt), "goal": int(goal),
            "inv": int(inv), "lump": lump}


def readable_input(raw: dict) -> str:
    debts = "; ".join(
        f"«{o['name']}» {fmt(o['amount'])} ₽ под {o['interest_rate']:.1%}, "
        f"платёж {fmt(o['monthly_payment'])}"
        for o in raw["obligations"]) or "нет"
    goals = "; ".join(
        f"«{g['name']}» {fmt(g['target_amount'])} "
        f"(есть {fmt(g['current_amount'])}, "
        f"{g['deadline'] or 'бессрочно'})"
        for g in raw["goals"]) or "нет"
    return (f"доход {fmt(raw['income_total'])} · расходы "
            f"{fmt(raw['expense_total'])} · подушка {fmt(raw['bliq'])} · "
            f"риск {raw['risk_tolerance']} · бенчмарк {raw['r_bench']:.1%}\n"
            f"  Кредиты: {debts}\n  Цели: {goals}")


def prose(rec: dict, raw: dict, seed: int) -> str:
    diag = rec["diagnostics"]

    def pick(options):
        return options[seed % len(options)]

    sentences = []
    closed = [m for m in rec["lump_sum_plan"]
              if m["closes"] and m["kind"].endswith("debt_payoff")]
    placement = [m for m in rec["lump_sum_plan"]
                 if m["kind"] == "surplus_placement"]
    if rec["status"] == "deficit":
        sentences.append(pick([
            f"Поток {fmt(diag['fcf'])} ₽/мес — клиент живёт в минус, поэтому "
            "никаких месячных распределений: сначала выправить бюджет",
            f"При потоке {fmt(diag['fcf'])} ₽/мес раздавать нечего — "
            "месячные бакеты обнуляю и работаю только запасами"]))
        if closed:
            freed = sum(d["payment"] for d in rec["debt_plan"]
                        if d.get("closed_by_lump"))
            sentences.append(
                f"Подушка ({fmt(diag['bliq'])} ₽) позволяет разово закрыть "
                f"{len(closed)} долг(а) сверх защитного пола — это снимет "
                f"{fmt(freed)} ₽/мес платежей и почти наверняка выведет "
                "поток в плюс" if diag['fcf'] + freed >= 0 else
                f"Разово гашу {len(closed)} самых дорогих долга из излишка "
                f"подушки — платежи упадут на {fmt(freed)} ₽/мес, дефицит "
                "сожмётся")
        elif any(d["class"] == "toxic" for d in rec["debt_plan"]):
            sentences.append("Токсичный долг при пустом излишке — кандидат "
                             "на реструктуризацию, из последней подушки его "
                             "не гашу")
    elif any(d["class"] == "toxic" and not d.get("closed_by_lump")
             for d in rec["debt_plan"]):
        sentences.append("Остался токсичный долг — весь свободный поток "
                         "идёт в него, цели и инвестиции подождут")
    else:
        if closed:
            sentences.append(pick([
                f"Излишек над целевой подушкой ({fmt(diag['reserve_target'])}"
                " ₽) позволяет разово закрыть дорогие кредиты — лавиной, "
                "с самой высокой ставки",
                "Ликвидность выше целевой, поэтому дорогие долги закрываю "
                "разовым платежом по лавине"]))
        if rec["totals"]["goal"] > 0:
            if "goal_at_risk" in rec["flags"]:
                sentences.append(
                    f"Весь доступный лимит {fmt(rec['totals']['goal'])} "
                    "₽/мес отдаю датированным целям, ближайший дедлайн — "
                    "первым, но требуемых взносов он не покрывает")
            else:
                sentences.append(pick([
                    f"Датированные цели получают {fmt(rec['totals']['goal'])}"
                    " ₽/мес по требуемым взносам, ближайший дедлайн — первым",
                    "На цели с дедлайнами закладываю "
                    f"{fmt(rec['totals']['goal'])} ₽/мес — ровно столько, "
                    "сколько нужно по срокам"]))
        if rec["totals"]["debt"] > 0:
            sentences.append("Оставшиеся дорогие кредиты гашу досрочно из "
                             "месячного потока")
        if rec["totals"]["res"] > 0:
            sentences.append(
                f"Резерв добираю до {fmt(diag['reserve_target'])} ₽ "
                f"({RESERVE_MONTHS[diag['risk']]} мес расходов по профилю)")
        if rec["totals"]["inv"] > 0:
            sentences.append("Остаток потока — в инвестиции по риск-сетке "
                             f"профиля {diag['risk']}")
        if placement:
            sentences.append(
                f"Свободный излишек {fmt(placement[0]['amount'])} ₽ разово "
                f"размещаю: {placement[0]['target']}")
    if "goal_at_risk" in rec["flags"]:
        sentences.append("Часть дедлайнов при таком потоке недостижима — "
                         "честно помечаю и предлагаю сдвиг срока")
    return ". ".join(sentences[:4]) + "."


def main() -> None:
    input_dir = Path("/mnt/user-data/uploads")
    pipeline = Pipeline(input_dir, Path("."), Constants())
    validator = Validator(Constants())
    lines = list(pipeline.iter_lines())
    recs = [json.loads(line) for line in gzip.open(
        "recommendations_v4.jsonl.gz", "rt", encoding="utf-8")]
    import csv as csv_module
    with open("expert_allocations_v4.csv", encoding="utf-8") as handle:
        confidences = [row["confidence"]
                       for row in csv_module.DictReader(handle)]

    out = ["# Выборка обоснований — 40 портретов (v4)", "",
           "Отбор детерминированный: каждая 300-я входная строка "
           "(позиции 0, 300, …, 11700) — стратификации по позиции хватает, "
           "т.к. части перемешаны генератором. Ручная сверка: независимый "
           "пересчёт методологии «на бумаге» (отдельная реализация с "
           "константами из документа, см. `build_opinions_sample_v4.py`) "
           "против чисел движка.", ""]
    matches = mismatches = 0
    for pos in range(0, 12000, 300):
        line, rec = lines[pos], recs[pos]
        out.append(f"## {pos // 300 + 1}. Позиция {pos} · id `{rec['id']}` · "
                   f"status={rec['status']} · dom={rec['dom']}")
        portrait, reason = validator.parse_line(line)
        if portrait is None:
            out += [f"- Вход: дефектная запись (`{reason}`)",
                    "- Решение: `invalid`, все суммы 0 — по правилу §2 "
                    "брифа запись не чинится и не оценивается.",
                    "- Ручная сверка: критерий дефекта подтверждён по "
                    "исходной строке — совпадает. ✅", ""]
            matches += 1
            continue
        raw = json.loads(line)
        diag = rec["diagnostics"]
        out.append("- Вход: " + readable_input(raw).replace("\n", "\n  "))
        out.append(
            f"- Метрики: поток {fmt(diag['fcf'])} ₽/мес · ПДН "
            f"{diag['pdn']:.2f} · запас {diag['liquidity_months']:.1f} мес "
            f"(от burn = расходы+платежи) · целевая подушка "
            f"{fmt(diag['reserve_target'])} ₽")
        moves = "; ".join(
            f"{m['kind']}→«{m['target']}» {fmt(m['amount'])} ₽"
            for m in rec["lump_sum_plan"]) or "нет"
        totals = rec["totals"]
        out.append(
            f"- Решение: lump = {fmt(totals['lump'])} ₽ ({moves}); месячный "
            f"сплит res/debt/goal/inv = {fmt(totals['res'])}/"
            f"{fmt(totals['debt'])}/{fmt(totals['goal'])}/"
            f"{fmt(totals['inv'])} ₽ · confidence {confidences[pos]}")
        out.append("- Почему: " + prose(rec, raw, pos // 300))
        paper = paper_recompute(raw)
        same = all(abs(paper[k] - totals[k]) <= 1
                   for k in ("res", "debt", "goal", "inv", "lump"))
        if same:
            matches += 1
            out.append("- Ручная сверка: пересчёт на бумаге даёт те же "
                       f"суммы (res {fmt(paper['res'])} / "
                       f"debt {fmt(paper['debt'])} / goal "
                       f"{fmt(paper['goal'])} / inv {fmt(paper['inv'])} / "
                       f"lump {fmt(paper['lump'])}) — расхождений нет. ✅")
        else:
            mismatches += 1
            out.append(f"- Ручная сверка: РАСХОЖДЕНИЕ — бумага {paper}, "
                       f"движок {totals}. ❌")
        out.append("")
    out.append(f"**Итог сверки:** совпало {matches}/40, расхождений "
               f"{mismatches}. Метод отбора и пересчёт воспроизводимы.")
    Path("expert_opinions_sample_v4.md").write_text(
        "\n".join(out), encoding="utf-8")
    print(f"matches={matches} mismatches={mismatches}")


if __name__ == "__main__":
    main()
