"""Independent statistical review of dataset v2 (12,000 portraits).

Computes the mandatory checklist: descriptive stats, correlations,
distribution shapes, categorical/count distributions, derived diagnostics,
annuity consistency, cap detection, pairwise-coverage approximation.
Writes markdown tables to /home/claude/analysis_out.md.
"""

import gzip
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

TODAY = date(2026, 7, 11)
UPLOADS = Path("/mnt/user-data/uploads")
OUT = Path("/home/claude/analysis_out.md")
FILES = [UPLOADS / f"expert_portraits_v2_part{i}_jsonl.gz" for i in range(1, 5)]
QUANTS = [0.10, 0.50, 0.90, 0.99]


class DatasetReviewer:
    def __init__(self) -> None:
        self.records: list[dict] = []
        self.obligations: list[dict] = []
        self.goals: list[dict] = []
        self.lines: list[str] = []

    def load(self) -> None:
        for path in FILES:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    obj = json.loads(line)
                    self.records.append(obj)
                    for o in obj.get("obligations", []):
                        self.obligations.append({**o, "pid": obj["id"],
                                                 "r_bench": obj["r_bench"],
                                                 "income": obj["income_total"]})
                    for g in obj.get("goals", []):
                        self.goals.append({**g, "pid": obj["id"],
                                           "income": obj["income_total"]})

    def build_frame(self) -> pd.DataFrame:
        rows = []
        for r in self.records:
            pay = sum(o.get("monthly_payment", 0) or 0
                      for o in r.get("obligations", []))
            tgt = sum(g.get("target_amount", 0) or 0 for g in r.get("goals", []))
            cur = sum(g.get("current_amount", 0) or 0 for g in r.get("goals", []))
            inc, exp = r["income_total"], r["expense_total"]
            burn = exp + pay
            rows.append({
                "id": r["id"], "income": inc, "expense": exp, "payments": pay,
                "bliq": r["bliq"], "r_bench": r["r_bench"],
                "risk": r["risk_tolerance"], "n_obl": len(r["obligations"]),
                "n_goals": len(r["goals"]), "goal_target_sum": tgt,
                "goal_current_sum": cur, "fcf": round(inc - exp - pay, 2),
                "dsti": pay / inc if inc > 0 else np.inf,
                "exp_ratio": exp / inc if inc > 0 else np.inf,
                "liq_months": r["bliq"] / burn if burn > 0 else np.inf,
            })
        return pd.DataFrame(rows)

    @staticmethod
    def describe(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        out = {}
        for c in cols:
            s = df[c].replace([np.inf, -np.inf], np.nan).dropna()
            q = s.quantile(QUANTS)
            out[c] = {"mean": s.mean(), "std": s.std(), "min": s.min(),
                      "p10": q[0.10], "p50": q[0.50], "p90": q[0.90],
                      "p99": q[0.99], "max": s.max()}
        return pd.DataFrame(out).T

    def annuity_check(self) -> dict:
        res = Counter()
        terms = []
        for o in self.obligations:
            a = o.get("amount") or 0
            p = o.get("monthly_payment") or 0
            r = o.get("interest_rate") or 0
            if a <= 0 or p <= 0 or r <= 0:
                res["degenerate"] += 1
                continue
            i = r / 12
            if p <= a * i + 1e-9:
                res["interest_only_or_less"] += 1
                continue
            n = math.log(p / (p - a * i)) / math.log(1 + i)
            terms.append(n)
            if 6 - 0.5 <= n <= 360 + 0.5:
                res["consistent_6_360"] += 1
            else:
                res["term_out_of_range"] += 1
        return {"counts": res, "terms": np.array(terms)}

    def deadline_mix(self) -> Counter:
        c = Counter()
        for g in self.goals:
            d = g.get("deadline")
            if not d:
                c["null"] += 1
                continue
            days = (date.fromisoformat(d[:10]) - TODAY).days
            if days < 0:
                c["overdue"] += 1
            elif days <= 92:
                c["<=3m"] += 1
            elif days <= 366:
                c["3-12m"] += 1
            elif days <= 1096:
                c["1-3y"] += 1
            elif days <= 3653:
                c["3-10y"] += 1
            else:
                c[">10y"] += 1
        return c

    def readiness_mix(self) -> Counter:
        c = Counter()
        for g in self.goals:
            t = g.get("target_amount") or 0
            cur = g.get("current_amount") or 0
            if t <= 0:
                c["target<=0"] += 1
                continue
            ratio = cur / t
            if cur > t:
                c["overfunded"] += 1
            elif abs(cur - t) < 0.01:
                c["exact_100%"] += 1
            elif ratio >= 0.75:
                c["75-100%"] += 1
            elif ratio >= 0.5:
                c["50-75%"] += 1
            elif ratio >= 0.25:
                c["25-50%"] += 1
            else:
                c["<25%"] += 1
        return c

    def pairwise_coverage(self, df: pd.DataFrame) -> tuple[int, int]:
        axes = {}
        axes["income"] = pd.qcut(df["income"].rank(method="first"), 3,
                                 labels=False)
        er = df["exp_ratio"].replace(np.inf, 9.9)
        axes["exp_ratio"] = pd.cut(er, [-0.1, 0.7, 1.0, 100], labels=False)
        ds = df["dsti"].replace(np.inf, 9.9)
        axes["dsti"] = pd.cut(ds, [-0.1, 0.3, 0.5, 100], labels=False)
        lm = df["liq_months"].replace(np.inf, 999)
        axes["liq"] = pd.cut(lm, [-0.1, 1, 6, 10000], labels=False)
        axes["n_obl"] = df["n_obl"].clip(0, 2)
        axes["n_goals"] = df["n_goals"].clip(0, 2)
        axes["risk"] = pd.cut(df["risk"], [0, 2, 3, 5], labels=False)
        names = list(axes)
        total, covered = 0, 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = axes[names[i]], axes[names[j]]
                seen = set(zip(a, b))
                la = a.nunique(dropna=True)
                lb = b.nunique(dropna=True)
                total += la * lb
                covered += len(seen)
        return covered, total

    def run(self) -> None:
        self.load()
        df = self.build_frame()
        obl = pd.DataFrame(self.obligations) if self.obligations else pd.DataFrame()
        gl = pd.DataFrame(self.goals) if self.goals else pd.DataFrame()
        parts = [f"# Программный отчёт по датасету v2 · {len(df)} портретов\n"]

        money_cols = ["income", "expense", "payments", "bliq",
                      "goal_target_sum", "goal_current_sum", "fcf",
                      "n_obl", "n_goals", "dsti", "liq_months"]
        desc = self.describe(df, money_cols).round(3)
        parts.append("## (а) Дескриптивные статистики\n" + desc.to_markdown())

        corr_cols = ["income", "expense", "payments", "bliq", "goal_target_sum"]
        pear = df[corr_cols].corr(method="pearson").round(3)
        spear = df[corr_cols].corr(method="spearman").round(3)
        parts.append("\n## (б) Корреляции Пирсона\n" + pear.to_markdown())
        parts.append("\n## (б) Корреляции Спирмена\n" + spear.to_markdown())

        pos_inc = df.loc[df["income"] > 0, "income"]
        log_inc = np.log(pos_inc)
        ks = stats.kstest(log_inc, "norm", args=(log_inc.mean(),
                                                 log_inc.std(ddof=0)))
        shapes = {c: (stats.skew(df[c].replace([np.inf], np.nan).dropna()),
                      stats.kurtosis(df[c].replace([np.inf], np.nan).dropna()))
                  for c in ["income", "expense", "bliq", "fcf"]}
        parts.append("\n## (в) Формы распределений\n" +
                     "\n".join(f"- {c}: skew={s:.2f}, kurtosis={k:.2f}"
                               for c, (s, k) in shapes.items()) +
                     f"\n- log(income>0): skew={stats.skew(log_inc):.3f}, "
                     f"kurt={stats.kurtosis(log_inc):.3f}, "
                     f"KS D={ks.statistic:.4f}, p={ks.pvalue:.2e} "
                     f"(n={len(log_inc)})")

        rb = df["r_bench"].value_counts().sort_index()
        parts.append("\n## (г) Категориальные распределения")
        parts.append("risk_tolerance:\n" +
                     df["risk"].value_counts().sort_index().to_markdown())
        parts.append(f"\nr_bench: {df['r_bench'].nunique()} уникальных значений\n"
                     + rb.to_markdown())
        parts.append("\nЧисло кредитов на портрет:\n" +
                     df["n_obl"].value_counts().sort_index().to_markdown())
        parts.append("\nЧисло целей на портрет:\n" +
                     df["n_goals"].value_counts().sort_index().to_markdown())
        dl = self.deadline_mix()
        parts.append("\nГоризонты дедлайнов (по целям, n=%d):\n" % len(self.goals)
                     + pd.Series(dl).to_markdown())
        rd = self.readiness_mix()
        parts.append("\nГотовность целей:\n" + pd.Series(rd).to_markdown())

        dsti_b = pd.cut(df["dsti"].replace(np.inf, 99),
                        [-0.001, 0, 0.3, 0.5, 0.8, 98, 1000],
                        labels=["0", "(0;0.3]", "(0.3;0.5]", "(0.5;0.8]",
                                ">0.8", "inf(inc=0)"])
        liq_b = pd.cut(df["liq_months"].replace(np.inf, 1e6),
                       [-0.001, 1, 3, 6, 12, 1e5, 1e9],
                       labels=["<1", "1-3", "3-6", "6-12", ">12", "inf(burn=0)"])
        fcf_sign = pd.cut(df["fcf"], [-1e18, -0.005, 0.005, 1e18],
                          labels=["FCF<0", "FCF=0", "FCF>0"])
        parts.append("\n## (д) Производные диагностики")
        parts.append("Бакеты ПДН:\n" + dsti_b.value_counts().sort_index().to_markdown())
        parts.append("\nМесяцы ликвидности:\n" +
                     liq_b.value_counts().sort_index().to_markdown())
        parts.append("\nЗнак свободного потока:\n" +
                     fcf_sign.value_counts().to_markdown())
        parts.append(f"\nДоля FCF<0: {(df['fcf'] < 0).mean():.4f}; "
                     f"медиана FCF: {df['fcf'].median():.0f}; "
                     f"медиана FCF среди FCF>0: "
                     f"{df.loc[df['fcf'] > 0, 'fcf'].median():.0f}")

        ann = self.annuity_check()
        n_obl_total = len(self.obligations)
        parts.append("\n## Аннуитетная согласованность кредитов "
                     f"(n={n_obl_total})\n" +
                     pd.Series(ann["counts"]).to_markdown())
        if len(ann["terms"]):
            t = ann["terms"]
            parts.append(f"\nСроки n (мес): min={t.min():.1f}, p50={np.median(t):.1f}, "
                         f"p90={np.percentile(t, 90):.1f}, max={t.max():.1f}")
        if not obl.empty:
            spread = obl["interest_rate"] - obl["r_bench"]
            parts.append(f"\nСтавки кредитов: min={obl['interest_rate'].min():.3f}, "
                         f"p50={obl['interest_rate'].median():.3f}, "
                         f"max={obl['interest_rate'].max():.3f}; "
                         f"доля ставка<r_bench: {(spread < 0).mean():.4f}; "
                         f"доля |спред|<=1п.п.: {(spread.abs() <= 0.01).mean():.4f}; "
                         f"точное равенство ставки бенчмарку: {(spread == 0).sum()}")

        parts.append("\n## Капы, хвосты, аномалии")
        for c in ["income", "expense", "bliq"]:
            top = df[c].value_counts().head(1)
            parts.append(f"- {c}: max={df[c].max():.2f}, самое частое значение "
                         f"{top.index[0]:.2f} × {top.iloc[0]}")
        if not gl.empty:
            tmax = gl["target_amount"].max()
            near_cap = (gl["target_amount"] > 0.95 * tmax).mean()
            parts.append(f"- goal target: min={gl['target_amount'].min():.2f}, "
                         f"max={tmax:.2f}, доля в верхних 5% от max: {near_cap:.4f}")
            k = gl.loc[gl["income"] > 0, "target_amount"] / \
                (12 * gl.loc[gl["income"] > 0, "income"])
            parts.append(f"- k = target/годовой доход: p10={k.quantile(0.1):.2f}, "
                         f"p50={k.median():.2f}, p90={k.quantile(0.9):.2f}, "
                         f"max={k.max():.2f}; corr(target, income) Пирсон = "
                         f"{gl['target_amount'].corr(gl['income']):.3f}")
        if not obl.empty:
            parts.append(f"- amount кредита: max={obl['amount'].max():.2f}; "
                         f"суммы >=1e8: {(obl['amount'] >= 1e8).sum()}")
        zero_inc = (df["income"] == 0).sum()
        zero_exp = (df["expense"] == 0).sum()
        parts.append(f"- нулевой доход: {zero_inc}; нулевые расходы: {zero_exp}; "
                     f"income==expense точно: "
                     f"{(df['income'] == df['expense']).sum()}")
        dupes = df["id"].duplicated().sum()
        neg = sum((df[c] < 0).sum() for c in
                  ["income", "expense", "bliq", "payments"])
        bad_dates = sum(1 for g in self.goals
                        if g.get("deadline") and not self._date_ok(g["deadline"]))
        parts.append(f"- дубликаты id: {dupes}; отрицательные денежные поля: {neg}; "
                     f"нечитаемые даты: {bad_dates}; NaN в скалярах: "
                     f"{int(df[['income', 'expense', 'bliq', 'r_bench']].isna().sum().sum())}")
        feat = df[["income", "expense", "payments", "bliq",
                   "goal_target_sum"]].round(2)
        parts.append(f"- полные дубликаты векторов признаков: "
                     f"{feat.duplicated().sum()}")

        cov, tot = self.pairwise_coverage(df)
        parts.append(f"\n## Pairwise-покрытие (аппроксимация, 3 уровня/ось): "
                     f"{cov}/{tot} пар уровней закрыто")

        near1 = ((df["income"].shift(-1) / df["income"]).sub(1).abs() < 0.011)
        parts.append(f"\n## Соседние id с доходом, отличающимся на ~1%: "
                     f"{int(near1.sum())} (грубый маркер метаморфических пар)")

        OUT.write_text("\n".join(str(p) for p in parts), encoding="utf-8")
        print(f"analysis written: {OUT}")

    @staticmethod
    def _date_ok(s: str) -> bool:
        try:
            date.fromisoformat(str(s)[:10])
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    DatasetReviewer().run()
