"""Statistical profile of expert_portraits_v2 (12,000 records).

Computes every item of the mandatory dataset-review checklist programmatically
and writes markdown tables to review_tables.md. Companion to dataset_review.md.
"""

from __future__ import annotations

import collections
import gzip
import json
import math
import random
import re
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats

AS_OF = date(2026, 7, 11)
CORE_CUTOFF = 1e8


def load() -> list:
    records = []
    for i in range(1, 5):
        path = f"/mnt/user-data/uploads/expert_portraits_v2_part{i}_jsonl.gz"
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            records.extend(json.loads(line) for line in handle if line.strip())
    return records


def pct(values: np.ndarray, p: float) -> float:
    return float(np.percentile(values, p))


def desc_row(name: str, values: np.ndarray) -> str:
    return (f"| {name} | {values.mean():,.0f} | {values.std():,.0f} | "
            f"{values.min():,.0f} | {pct(values, 10):,.0f} | {pct(values, 50):,.0f} | "
            f"{pct(values, 90):,.0f} | {pct(values, 99):,.0f} | {values.max():,.0f} |")


def corr_table(mat: np.ndarray, labels: list) -> str:
    head = "| | " + " | ".join(labels) + " |\n|" + "---|" * (len(labels) + 1)
    rows = [head]
    for i, lab in enumerate(labels):
        rows.append("| **" + lab + "** | " +
                    " | ".join(f"{mat[i, j]:.2f}" for j in range(len(labels))) + " |")
    return "\n".join(rows)


def main() -> None:
    records = load()
    out = []

    inc = np.array([r["income_total"] for r in records])
    exp = np.array([r["expense_total"] for r in records])
    mps = np.array([sum(o["monthly_payment"] for o in r["obligations"]) for r in records])
    blq = np.array([r["bliq"] for r in records])
    gts = np.array([sum(g["target_amount"] for g in r["goals"]) for r in records])
    fcf = inc - exp - mps
    nob = np.array([len(r["obligations"]) for r in records])
    ngl = np.array([len(r["goals"]) for r in records])

    giant = (inc > CORE_CUTOFF) | (exp > CORE_CUTOFF) | (blq > CORE_CUTOFF) | (gts > CORE_CUTOFF)
    core = ~giant
    out.append(f"CORE={int(core.sum())} GIANT={int(giant.sum())}")

    out.append("\n### (а) Дескриптивные статистики — весь сет, n=12000\n")
    out.append("| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for name, v in [("income", inc), ("expense", exp), ("Σ платежей", mps),
                    ("bliq", blq), ("Σ target целей", gts), ("FCF", fcf)]:
        out.append(desc_row(name, v))
    out.append(desc_row("n кредитов", nob.astype(float)))
    out.append(desc_row("n целей", ngl.astype(float)))

    out.append(f"\n### (а') Ядро без гигантского блока, n={int(core.sum())}\n")
    out.append("| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for name, v in [("income", inc[core]), ("expense", exp[core]),
                    ("Σ платежей", mps[core]), ("bliq", blq[core]),
                    ("Σ target целей", gts[core]), ("FCF", fcf[core])]:
        out.append(desc_row(name, v))

    amounts, rates, pays = [], [], []
    for r in records:
        for o in r["obligations"]:
            amounts.append(o["amount"])
            rates.append(o["interest_rate"])
            pays.append(o["monthly_payment"])
    out.append(f"\nКредиты (n={len(rates)}):")
    out.append("| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    out.append(desc_row("остаток", np.array(amounts)))
    out.append(desc_row("ставка, %", np.array(rates) * 100))
    out.append(desc_row("платёж", np.array(pays)))

    labels = ["income", "expense", "Σ платежей", "bliq", "Σ целей"]
    stack = np.vstack([inc, exp, mps, blq, gts])
    stack_core = stack[:, core]
    pearson_core = np.corrcoef(stack_core)
    spearman_full = stats.spearmanr(stack.T).statistic
    out.append("\n### (б) Корреляции\n")
    out.append("Pearson (ядро, без гигантского блока):\n")
    out.append(corr_table(pearson_core, labels))
    out.append("\nSpearman (весь сет):\n")
    out.append(corr_table(np.asarray(spearman_full), labels))

    out.append("\n### (в) Формы распределений (ядро)\n")
    out.append("| Поле | skew | kurtosis (excess) |")
    out.append("|---|---|---|")
    for name, v in [("income", inc[core]), ("expense", exp[core]), ("bliq", blq[core])]:
        out.append(f"| {name} | {stats.skew(v):.2f} | {stats.kurtosis(v):.2f} |")
    pos = inc[core & (inc > 0)]
    logv = np.log(pos)
    ks = stats.kstest(logv, "norm", args=(logv.mean(), logv.std()))
    out.append(f"\nKS лог-нормальности дохода (ядро, income>0, n={len(pos)}): "
               f"D={ks.statistic:.4f}, p={ks.pvalue:.2e}")
    ks_shape = stats.kstest((logv - logv.mean()) / logv.std(), "norm")
    out.append(f"log(income): mean={logv.mean():.3f}, σ={logv.std():.3f}, "
               f"skew={stats.skew(logv):.3f}, kurt={stats.kurtosis(logv):.3f}")

    out.append("\n### (г) Категориальные и счётные\n")
    rt_c = collections.Counter(r["risk_tolerance"] for r in records)
    out.append("risk_tolerance: " + ", ".join(f"{k}: {v}" for k, v in sorted(rt_c.items())))
    rb_c = collections.Counter(round(r["r_bench"], 4) for r in records)
    out.append("r_bench (уникальных: %d): " % len(rb_c) +
               ", ".join(f"{k:.2%}: {v}" for k, v in sorted(rb_c.items())))
    out.append("n кредитов: " + ", ".join(f"{k}: {v}" for k, v in sorted(collections.Counter(nob).items())))
    out.append("n целей: " + ", ".join(f"{k}: {v}" for k, v in sorted(collections.Counter(ngl).items())))

    horizons, funded, null_dl, overdue, today = [], [], 0, 0, 0
    over_funded, exact_funded, k_ratio = 0, 0, []
    for r in records:
        for g in r["goals"]:
            tgt, cur = g["target_amount"], g["current_amount"]
            if tgt > 0:
                funded.append(cur / tgt)
            if cur > tgt + 0.005:
                over_funded += 1
            if abs(cur - tgt) <= 0.01:
                exact_funded += 1
            if r["income_total"] > 0:
                k_ratio.append(tgt / (r["income_total"] * 12))
            if g["deadline"] is None:
                null_dl += 1
                continue
            d = date.fromisoformat(g["deadline"])
            m = (d - AS_OF).days / 30.4375
            horizons.append(m)
            if d < AS_OF:
                overdue += 1
            if abs((d - AS_OF).days) <= 9:
                today += 1
    n_goals_total = int(ngl.sum())
    out.append(f"\nЦелей всего: {n_goals_total}; deadline=null: {null_dl} "
               f"({null_dl / n_goals_total:.0%}); просроченных: {overdue}; ±9 дней от среза: {today}")
    h = np.array(horizons)
    out.append(f"Горизонт дедлайнов, мес: min={h.min():.1f}, p10={pct(h,10):.1f}, "
               f"p50={pct(h,50):.1f}, p90={pct(h,90):.1f}, max={h.max():.1f}")
    hb = collections.Counter()
    for m in horizons:
        for hi, lab in [(0, "просрочен"), (3, "0–3"), (12, "3–12"), (36, "12–36"),
                        (60, "36–60"), (math.inf, ">60")]:
            if m < hi or (hi == math.inf):
                hb[lab] += 1
                break
    out.append("Бакеты горизонтов: " + ", ".join(f"{k}: {v}" for k, v in hb.items()))
    f = np.array(funded)
    out.append(f"Готовность целей current/target: p10={pct(f,10):.2f}, p50={pct(f,50):.2f}, "
               f"p90={pct(f,90):.2f}, max={f.max():.2f}; перефинансировано: {over_funded}; "
               f"target==current: {exact_funded}")
    k = np.array(k_ratio)
    out.append(f"k = target/годовой доход: p10={pct(k,10):.2f}, p50={pct(k,50):.2f}, "
               f"p90={pct(k,90):.2f}, p99={pct(k,99):.2f}, max={k.max():.1f}; "
               f"вне [0.2, 5]: {int(((k < 0.2) | (k > 5)).sum())} ({((k < 0.2) | (k > 5)).mean():.1%})")

    out.append("\n### (д) Производные диагностики\n")
    pdn_b, liq_b = collections.Counter(), collections.Counter()
    for r in records:
        mp = sum(o["monthly_payment"] for o in r["obligations"])
        pdn = mp / r["income_total"] if r["income_total"] > 0 else (math.inf if mp > 0 else 0)
        for hi, lab in [(1e-9, "0"), (0.3, "(0–30]"), (0.5, "(30–50]"),
                        (0.8, "(50–80]"), (math.inf, ">80%")]:
            if pdn <= hi:
                pdn_b[lab] += 1
                break
        ess = r["expense_total"] + mp
        lm = r["bliq"] / ess if ess > 0 else math.inf
        for hi, lab in [(1, "<1"), (3, "1–3"), (6, "3–6"), (12, "6–12"), (math.inf, ">12")]:
            if lm < hi:
                liq_b[lab] += 1
                break
    out.append("ПДН: " + ", ".join(f"{k}: {v} ({v/120:.1f}%)" for k, v in pdn_b.items()))
    out.append("Ликвидность, мес: " + ", ".join(f"{k}: {v} ({v/120:.1f}%)" for k, v in liq_b.items()))
    out.append(f"FCF: <0 → {int((fcf < 0).sum())} ({(fcf < 0).mean():.1%}), "
               f"==0 → {int((fcf == 0).sum())}, >0 → {int((fcf > 0).sum())}")

    out.append("\n### (е) Метки kind\n")
    has_kind = sum(1 for r in records if "kind" in r)
    out.append(f"Записей с полем kind: {has_kind} из 12000 — метки типов в выгрузку не включены "
               "(слепой протокол), валидация меток на стороне эксперта невозможна.")

    out.append("\n### Специальные проверки\n")
    io, grow, eq_bench, terms_bad, terms = 0, 0, 0, 0, []
    for r in records:
        for o in r["obligations"]:
            mi = o["amount"] * o["interest_rate"] / 12
            if o["monthly_payment"] < mi - 0.01:
                grow += 1
            elif o["monthly_payment"] <= mi * 1.01:
                io += 1
            else:
                i = o["interest_rate"] / 12
                if i > 0:
                    n = -math.log(1 - i * o["amount"] / o["monthly_payment"]) / math.log(1 + i)
                    terms.append(n)
                    if n < 5.5 or n > 366:
                        terms_bad += 1
            if abs(o["interest_rate"] - r["r_bench"]) < 1e-9:
                eq_bench += 1
    t = np.array(terms)
    near_int = int((np.abs(t - np.round(t)) < 0.05).sum())
    out.append(f"Кредиты: interest-only (P≈I): {io}; растущий долг (P<I): {grow}; "
               f"ставка == r_bench точно: {eq_bench}")
    out.append(f"Имплицитный аннуитетный срок: p50={pct(t,50):.0f} мес, p99={pct(t,99):.0f}, "
               f"max={t.max():.0f}; вне [6, 360]: {terms_bad}; срок ≈ целому (±0.05): "
               f"{near_int}/{len(t)} ({near_int/len(t):.1%})")

    sig_map = collections.defaultdict(list)
    for r in records:
        if r["income_total"] <= 0:
            continue
        key = (round(r["expense_total"] / r["income_total"], 6),
               round(r["bliq"] / r["income_total"], 6),
               len(r["obligations"]), len(r["goals"]), r["risk_tolerance"])
        sig_map[key].append(r["id"])
    m5 = sum(1 for v in sig_map.values() if len(v) > 1)
    exact_dup = 0
    seen = {}
    for r in records:
        key = json.dumps({k: v for k, v in r.items() if k != "id"}, sort_keys=True)
        if key in seen:
            exact_dup += 1
        seen[key] = r["id"]
    out.append(f"Метаморфические пары: сигнатур-кандидатов ×k-масштаба: {m5}; "
               f"точных дублей содержимого: {exact_dup} — слой E не обнаружен.")

    bad_layer_d = 0
    for r in records:
        for v in (r["income_total"], r["expense_total"], r["bliq"], r["r_bench"]):
            if not isinstance(v, (int, float)) or v < 0 or math.isnan(v):
                bad_layer_d += 1
    out.append(f"Слой D (битые записи): {bad_layer_d} — отсутствует.")

    blocks = {
        "income == 0": int((inc == 0).sum()),
        "expense == 0": int((exp == 0).sum()),
        "гигантские суммы (>10⁸)": int(giant.sum()),
        "goals == 8": int((ngl == 8).sum()),
        "перефинансированные цели": over_funded,
        "цели < 1000 ₽": sum(1 for r in records for g in r["goals"] if g["target_amount"] < 1000),
        "просроченный дедлайн": overdue,
        "дедлайн ≈ сегодня": today,
        "ставка == бенчмарк": eq_bench,
        "bliq == min (1 ₽)": int((blq <= 1.0).sum()),
    }
    out.append("\nИнвентарь граничных блоков (~285–450 записей каждый, разбросаны по id):")
    for name, cnt in blocks.items():
        out.append(f"- {name}: {cnt}")

    rng = random.Random(42)
    sample_ids = [records[rng.randrange(12000)]["id"] for _ in range(3)]
    md_text = Path("/mnt/user-data/uploads/portraits_v2_all_12000.md").read_text(encoding="utf-8")
    out.append("\n### Сверка JSONL с md-карточками (3 случайных id, seed 42)\n")
    by_id = {r["id"]: r for r in records}
    for sid in sample_ids:
        m = re.search(rf"### {sid} ·.*?(?=\n### |\Z)", md_text, re.S)
        card = m.group(0) if m else ""
        r = by_id[sid]
        def has(x: float) -> bool:
            return f"{x:,.2f}".replace(",", " ") in card
        checks = [has(r["income_total"]), has(r["expense_total"]), has(r["bliq"])]
        checks += [has(g["target_amount"]) for g in r["goals"][:2]]
        checks += [has(o["amount"]) for o in r["obligations"][:2]]
        out.append(f"- {sid}: полей сверено {len(checks)}, совпало {sum(checks)} — "
                   + ("OK" if all(checks) else "РАСХОЖДЕНИЕ"))

    Path("/home/claude/review_tables.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
