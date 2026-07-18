"""Statistical audit of dataset v3 for dataset_review.md (round 3)."""

import gzip
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

CUTOFF = date(2026, 7, 16)
UPLOADS = Path("/mnt/user-data/uploads")


def is_num(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def load_records() -> tuple:
    records, meta, broken = [], [], 0
    for part in sorted(UPLOADS.glob("expert_portraits_v3_part*_jsonl.gz")):
        for raw in gzip.open(part, "rt", encoding="utf-8"):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                broken += 1
                continue
            if isinstance(rec, dict) and rec.get("__meta__") is True:
                meta.append(rec)
            else:
                records.append(rec)
    return records, meta, broken


def clean_frame(records: list) -> pd.DataFrame:
    rows = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        base = {k: rec.get(k) for k in
                ("id", "income_total", "expense_total", "bliq",
                 "r_bench", "risk_tolerance")}
        if not all(is_num(base[k]) for k in
                   ("income_total", "expense_total", "bliq", "r_bench")):
            continue
        if any(base[k] < 0 for k in
               ("income_total", "expense_total", "bliq", "r_bench")):
            continue
        obligations = rec.get("obligations")
        goals = rec.get("goals")
        if not isinstance(obligations, list) or not isinstance(goals, list):
            continue
        pay, debt_amt, ok_obl = 0.0, 0.0, True
        for item in obligations:
            if not isinstance(item, dict) or not all(
                    is_num(item.get(k)) and item.get(k) >= 0
                    for k in ("amount", "interest_rate", "monthly_payment")):
                ok_obl = False
                break
            pay += item["monthly_payment"]
            debt_amt += item["amount"]
        if not ok_obl:
            continue
        tgt, cur, ok_goal = 0.0, 0.0, True
        for item in goals:
            if not isinstance(item, dict) or not all(
                    is_num(item.get(k)) and item.get(k) >= 0
                    for k in ("target_amount", "current_amount")):
                ok_goal = False
                break
            tgt += item["target_amount"]
            cur += item["current_amount"]
        if not ok_goal:
            continue
        base.update(pay_total=pay, debt_total=debt_amt, n_obl=len(obligations),
                    n_goals=len(goals), goal_target_total=tgt,
                    goal_current_total=cur)
        rows.append(base)
    frame = pd.DataFrame(rows)
    frame["flow"] = (frame.income_total - frame.expense_total
                     - frame.pay_total)
    frame["essentials"] = frame.expense_total + frame.pay_total
    frame["pdn"] = np.where(frame.income_total > 0,
                            frame.pay_total / frame.income_total, np.inf)
    frame["liq_months"] = np.where(frame.essentials > 0,
                                   frame.bliq / frame.essentials, np.inf)
    frame["exp_share"] = np.where(frame.income_total > 0,
                                  frame.expense_total / frame.income_total,
                                  np.inf)
    return frame


def describe(series: pd.Series) -> dict:
    values = series.replace([np.inf, -np.inf], np.nan).dropna()
    qs = values.quantile([0.10, 0.50, 0.90, 0.99])
    return {"mean": values.mean(), "std": values.std(), "min": values.min(),
            "p10": qs.iloc[0], "p50": qs.iloc[1], "p90": qs.iloc[2],
            "p99": qs.iloc[3], "max": values.max(), "n": len(values)}


def fmt_table(stats_map: dict) -> str:
    head = ("| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |\n"
            "|---|---|---|---|---|---|---|---|---|\n")
    lines = []
    for name, st in stats_map.items():
        cells = [f"{st[k]:,.0f}".replace(",", " ") if abs(st[k]) >= 100
                 else f"{st[k]:.4g}"
                 for k in ("mean", "std", "min", "p10", "p50", "p90",
                           "p99", "max")]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return head + "\n".join(lines)


def loans_frame(records: list) -> pd.DataFrame:
    rows = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        r_bench = rec.get("r_bench")
        for item in rec.get("obligations") or []:
            if not isinstance(item, dict):
                continue
            amount = item.get("amount")
            rate = item.get("interest_rate")
            payment = item.get("monthly_payment")
            if not all(is_num(v) and v >= 0
                       for v in (amount, rate, payment)):
                continue
            rows.append({"pid": rec.get("id"), "name": item.get("name"),
                         "amount": amount, "rate": rate, "payment": payment,
                         "r_bench": r_bench if is_num(r_bench) else np.nan})
    frame = pd.DataFrame(rows)
    i = frame.rate / 12.0
    with np.errstate(divide="ignore", invalid="ignore"):
        inner = 1.0 - frame.amount * i / frame.payment
        frame["n_implied"] = np.where(
            (frame.payment > 0) & (i > 0) & (inner > 0),
            -np.log(inner) / np.log1p(i), np.nan)
    frame["interest_only"] = ((frame.amount > 0) & (frame.rate > 0)
                              & (frame.payment <= frame.amount * i))
    frame["spread"] = frame.rate - frame.r_bench
    return frame


def goals_frame(records: list) -> pd.DataFrame:
    rows = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        income = rec.get("income_total")
        for item in rec.get("goals") or []:
            if not isinstance(item, dict):
                continue
            tgt = item.get("target_amount")
            cur = item.get("current_amount")
            if not (is_num(tgt) and is_num(cur) and tgt >= 0 and cur >= 0):
                continue
            deadline = item.get("deadline")
            parsed = None
            if isinstance(deadline, str):
                try:
                    parsed = date.fromisoformat(deadline)
                except ValueError:
                    parsed = "broken"
            rows.append({"pid": rec.get("id"), "name": item.get("name"),
                         "target": tgt, "current": cur,
                         "deadline": deadline, "parsed": parsed,
                         "income": income if is_num(income) else np.nan})
    frame = pd.DataFrame(rows)
    frame["funding"] = np.where(frame.target > 0,
                                frame.current / frame.target, np.nan)
    frame["k_income"] = np.where(frame.income > 0,
                                 frame.target / (frame.income * 12.0), np.nan)
    frame["horizon_m"] = [
        None if not isinstance(p, date) else (p - CUTOFF).days / 30.44
        for p in frame.parsed]
    return frame


def main() -> None:
    records, meta, broken = load_records()
    print("META:", json.dumps(meta, ensure_ascii=False))
    print("records:", len(records), "| unparseable JSON lines:", broken)

    ids = [r.get("id") for r in records if isinstance(r, dict)]
    dup = Counter(ids)
    dups = {k: v for k, v in dup.items() if v > 1 and k is not None}
    print("duplicate ids:", len(dups))

    frame = clean_frame(records)
    print("clean rows for stats:", len(frame))

    money = {
        "income_total": frame.income_total, "expense_total":
            frame.expense_total, "pay_total (Σ платежей)": frame.pay_total,
        "debt_total (Σ тел)": frame.debt_total, "bliq": frame.bliq,
        "goal_target_total": frame.goal_target_total,
        "goal_current_total": frame.goal_current_total, "flow": frame.flow,
    }
    print("\n=== (а) Дескриптивные статистики ===")
    print(fmt_table({k: describe(v) for k, v in money.items()}))
    counts = {"n_obligations": frame.n_obl, "n_goals": frame.n_goals,
              "r_bench": frame.r_bench, "risk_tolerance":
                  frame.risk_tolerance.astype(float)}
    print(fmt_table({k: describe(v) for k, v in counts.items()}))

    print("\n=== (б) Формы распределений ===")
    inc = frame.income_total[frame.income_total > 0]
    log_inc = np.log(inc)
    ks = sps.kstest(log_inc, "norm", args=(log_inc.mean(), log_inc.std()))
    print(f"income: skew={sps.skew(inc):.2f}, kurtosis="
          f"{sps.kurtosis(inc):.2f}; log-income skew="
          f"{sps.skew(log_inc):.3f}, kurt={sps.kurtosis(log_inc):.3f}; "
          f"KS(lognorm, оценённые параметры): D={ks.statistic:.4f}, "
          f"p={ks.pvalue:.3g} (Лиллиефорс-поправка не применялась)")
    for name, series in (("bliq", frame.bliq),
                         ("expense_total", frame.expense_total),
                         ("flow", frame.flow)):
        print(f"{name}: skew={sps.skew(series):.2f}, "
              f"kurtosis={sps.kurtosis(series):.2f}")

    print("\n=== (в) Корреляции (Pearson / Spearman) ===")
    cols = ["income_total", "expense_total", "pay_total", "bliq",
            "goal_target_total"]
    print("Pearson:\n", frame[cols].corr(method="pearson").round(3))
    print("Spearman:\n", frame[cols].corr(method="spearman").round(3))

    print("\n=== (г) Реалистичность кредитов и целей ===")
    loans = loans_frame(records)
    print("loans:", len(loans), "| типы:",
          dict(Counter(loans.name.fillna("<none>")).most_common()))
    print("ставки по типам (p50):")
    print(loans.groupby("name")["rate"].median().round(4))
    print("interest-only (payment ≤ месячному проценту):",
          int(loans.interest_only.sum()),
          f"({loans.interest_only.mean()*100:.2f}%)")
    n_ok = loans.n_implied.dropna()
    print(f"аннуитетный имплайд-срок: n={len(n_ok)}, "
          f"p10={n_ok.quantile(0.1):.0f}, p50={n_ok.median():.0f}, "
          f"p90={n_ok.quantile(0.9):.0f} мес.; вне [6,360]: "
          f"{int(((n_ok < 6) | (n_ok > 360)).sum())} "
          f"({((n_ok < 6) | (n_ok > 360)).mean()*100:.2f}%)")
    print("spread = rate − r_bench: p10/p50/p90 =",
          loans.spread.quantile([0.1, 0.5, 0.9]).round(3).tolist(),
          "| доля spread<0:", f"{(loans.spread < 0).mean()*100:.1f}%")

    goals = goals_frame(records)
    print("\ngoals:", len(goals), "| типы:",
          dict(Counter(goals.name.fillna("<none>")).most_common()))
    print("доля deadline=null:",
          f"{goals.deadline.isna().mean()*100:.1f}%",
          "| битые даты:", int((goals.parsed == "broken").sum()))
    hor = pd.Series([h for h in goals.horizon_m if h is not None])
    print(f"горизонты, мес.: p10={hor.quantile(0.1):.1f}, "
          f"p50={hor.median():.1f}, p90={hor.quantile(0.9):.1f}, "
          f"max={hor.max():.0f}; просроченных: {(hor <= 0).sum()} "
          f"({(hor <= 0).mean()*100:.2f}%)")
    print(f"funding=current/target: p50={goals.funding.median():.3f}, "
          f"доля ≥1 (перефинансированные): "
          f"{(goals.funding >= 1).mean()*100:.2f}%, "
          f"точных target==current: {(goals.current == goals.target).sum()}")
    print(f"k = target/годовой доход: p10={goals.k_income.quantile(.1):.2f}, "
          f"p50={goals.k_income.median():.2f}, "
          f"p90={goals.k_income.quantile(.9):.2f}, "
          f"max={goals.k_income.max():.1f}")

    print("\n=== (д) Граничные кейсы (по чистым записям) ===")
    flags = {
        "нулевой доход": (frame.income_total == 0).sum(),
        "нулевые расходы": (frame.expense_total == 0).sum(),
        "дефицит потока": (frame.flow < 0).sum(),
        "поток == 0 точно": (frame.flow == 0).sum(),
        "ПДН > 0.8": ((frame.pdn > 0.8) & np.isfinite(frame.pdn)).sum(),
        "ПДН > 0.4": ((frame.pdn > 0.4) & np.isfinite(frame.pdn)).sum(),
        "без кредитов": (frame.n_obl == 0).sum(),
        "без целей": (frame.n_goals == 0).sum(),
        "ликвидность > 24 мес.": ((frame.liq_months > 24)
                                  & np.isfinite(frame.liq_months)).sum(),
        "ликвидность < 1 мес.": (frame.liq_months < 1).sum(),
        "суммы ≥ 1e9 (любое поле)": int(
            ((frame.income_total >= 1e9) | (frame.bliq >= 1e9)
             | (frame.goal_target_total >= 1e9)
             | (frame.debt_total >= 1e9)).sum()),
    }
    for key, val in flags.items():
        print(f"{key}: {int(val)} ({int(val)/len(frame)*100:.2f}%)")
    print("бакеты ПДН (0/0-20/20-40/40-60/60-80/80+):",
          np.histogram(frame.pdn[np.isfinite(frame.pdn)].clip(0, 1.2),
                       bins=[0, 1e-9, .2, .4, .6, .8, 10])[0].tolist())
    print("бакеты ликвидности (<1/1-3/3-6/6-12/12-24/24+):",
          np.histogram(frame.liq_months[np.isfinite(frame.liq_months)]
                       .clip(0, 1000),
                       bins=[0, 1, 3, 6, 12, 24, 1e9])[0].tolist())
    print("риск-профили:", frame.risk_tolerance.value_counts()
          .sort_index().to_dict())
    print("r_bench: уникальных значений:", frame.r_bench.nunique(),
          "| min/max:", frame.r_bench.min(), frame.r_bench.max())

    print("\n=== (е) Целостность ===")
    expected = {f"SP3-{i:05d}" for i in range(12000)}
    got = set(i for i in ids if isinstance(i, str))
    print("дубли id:", len(dups), "| отсутствуют из диапазона:",
          len(expected - got))
    per_goal_curr_gt_tgt = (goals.current > goals.target).sum()
    print("целей с current > target:", int(per_goal_curr_gt_tgt))


if __name__ == "__main__":
    main()
