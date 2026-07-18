"""Reproducible statistics for the FINPILOT 12k portrait dataset.

Recomputes every number cited in dataset_review_and_prompt.md:
headline figures of sections 1-2 (correlations, annuity terms,
interest-only loans, deadline checks, plain DSR buckets) and the
full appendix A (A.1-A.6). Stdlib only.

Usage: python3 dataset_stats.py <portraits.jsonl>
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter
from datetime import date
from typing import Any, Callable

REF_DATE = date(2026, 7, 7)


class DatasetProfiler:
    def __init__(self, path: str) -> None:
        self.rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        self.loans = [o for r in self.rows for o in r["engine"]["obligations"]]
        self.goals = [g for r in self.rows for g in r["engine"]["goals"]]
        self.per = [self._derive(r["engine"]) for r in self.rows]
        self.plain = [p for p, r in zip(self.per, self.rows) if r["kind"] == "plain"]

    @staticmethod
    def _derive(e: dict[str, Any]) -> dict[str, float]:
        pays = sum(o["monthly_payment"] for o in e["obligations"])
        return {
            "inc": e["income_total"], "exp": e["expense_total"], "pays": pays,
            "bliq": e["bliq"], "outflow": e["expense_total"] + pays,
            "fcf": e["income_total"] - e["expense_total"] - pays,
            "nloans": len(e["obligations"]), "ngoals": len(e["goals"]),
            "risk": e["risk_tolerance"], "rb": e["r_bench"],
            "tgt": sum(g["target_amount"] for g in e["goals"]),
            "cur": sum(g["current_amount"] for g in e["goals"]),
        }

    # -- math helpers (population moments, index percentiles) ----------------
    @staticmethod
    def _q(sorted_a: list[float], p: float) -> float:
        return sorted_a[min(len(sorted_a) - 1, int(p * (len(sorted_a) - 1)))]

    def _desc(self, vals: list[float]) -> dict[str, float]:
        a = sorted(vals)
        return {"n": len(a), "mean": statistics.fmean(a), "std": statistics.pstdev(a),
                "mn": a[0], "p10": self._q(a, .1), "p50": self._q(a, .5),
                "p90": self._q(a, .9), "p99": self._q(a, .99), "mx": a[-1]}

    @staticmethod
    def _skew_kurt(vals: list[float]) -> tuple[float, float]:
        m, s = statistics.fmean(vals), statistics.pstdev(vals)
        m3 = statistics.fmean([(x - m) ** 3 for x in vals])
        m4 = statistics.fmean([(x - m) ** 4 for x in vals])
        return m3 / s ** 3, m4 / s ** 4 - 3

    @staticmethod
    def _pearson(x: list[float], y: list[float]) -> float:
        mx, my = statistics.fmean(x), statistics.fmean(y)
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
        return num / den

    def _spearman(self, x: list[float], y: list[float]) -> float:
        def rank(v: list[float]) -> list[float]:
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v)
            for pos, i in enumerate(order):
                r[i] = pos
            return r
        return self._pearson(rank(x), rank(y))

    # -- headline numbers for sections 1-2 ------------------------------------
    def annuity(self) -> dict[str, float]:
        interest_only, weird, terms = 0, 0, []
        for o in self.loans:
            i = o["interest_rate"] / 12
            share = o["amount"] * i / o["monthly_payment"]
            if share >= 1:
                interest_only += 1
                continue
            n = -math.log(1 - share) / math.log(1 + i)
            terms.append(n)
            weird += n < 3 or n > 420
        return {"interest_only": interest_only, "weird_term": weird,
                "term_med": statistics.median(terms),
                "term_p90": self._q(sorted(terms), .9)}

    def goal_deadlines(self) -> dict[str, Any]:
        horizon: Counter = Counter()
        overdue = near = 0
        for g in self.goals:
            if not g["deadline"]:
                horizon["null"] += 1
                continue
            m = (date.fromisoformat(g["deadline"]) - REF_DATE).days / 30.4375
            gap = g["target_amount"] - g["current_amount"]
            overdue += m <= 0 and gap > 0
            near += 0 < m <= 3
            horizon["<=0" if m <= 0 else "0-3m" if m <= 3 else "3-12m" if m <= 12
                    else "1-3y" if m <= 36 else "3-5y" if m <= 60 else ">5y"] += 1
        return {"overdue_unfunded": overdue, "within_90d": near, "horizon": horizon}

    def plain_dsr_buckets(self) -> Counter:
        buckets: Counter = Counter()
        for p in self.plain:
            if p["pays"] == 0:
                buckets["0"] += 1
                continue
            d = p["pays"] / p["inc"]
            buckets["<0.3" if d < .3 else "<0.5" if d < .5 else "<0.8" if d < .8
                    else "<1.5" if d < 1.5 else ">=1.5"] += 1
        return buckets

    # -- appendix A -------------------------------------------------------------
    def descriptives(self) -> dict[str, dict[str, float]]:
        f = {
            "income (все)": [p["inc"] for p in self.per],
            "income (>0)": [p["inc"] for p in self.per if p["inc"] > 0],
            "expenses (все)": [p["exp"] for p in self.per],
            "debt payments (порт.)": [p["pays"] for p in self.per],
            "bliq": [p["bliq"] for p in self.per],
            "FCF": [p["fcf"] for p in self.per],
            "loan amount": [o["amount"] for o in self.loans],
            "loan rate": [o["interest_rate"] for o in self.loans],
            "loan payment": [o["monthly_payment"] for o in self.loans],
            "goal target": [g["target_amount"] for g in self.goals],
            "goal current": [g["current_amount"] for g in self.goals],
        }
        return {k: self._desc(v) for k, v in f.items()}

    def correlations_plain(self) -> tuple[list[str], dict, dict]:
        axes = ["inc", "exp", "pays", "bliq", "tgt"]
        cols = {a: [p[a] for p in self.plain] for a in axes}
        pear = {(a, b): self._pearson(cols[a], cols[b]) for a in axes for b in axes}
        spear = {(a, b): self._spearman(cols[a], cols[b]) for a in axes for b in axes}
        return axes, pear, spear

    def shapes(self) -> dict[str, float]:
        inc = [p["inc"] for p in self.per if p["inc"] > 0]
        sk_i, ku_i = self._skew_kurt(inc)
        logs = [math.log(x) for x in inc]
        sk_l, ku_l = self._skew_kurt(logs)
        mu, sg = statistics.fmean(logs), statistics.pstdev(logs)
        srt, n = sorted(inc), len(inc)
        d = max(abs((i + 1) / n - 0.5 * (1 + math.erf((math.log(x) - mu) / (sg * math.sqrt(2)))))
                for i, x in enumerate(srt))
        sk_b, ku_b = self._skew_kurt([p["bliq"] for p in self.per if p["bliq"] > 0])
        return {"inc_skew": sk_i, "inc_kurt": ku_i, "log_skew": sk_l, "log_kurt": ku_l,
                "ks_d": d, "ks_crit": 1.36 / math.sqrt(n), "bliq_skew": sk_b, "bliq_kurt": ku_b}

    def categoricals(self) -> dict[str, Counter]:
        ready: Counter = Counter()
        for g in self.goals:
            r = g["current_amount"] / g["target_amount"] if g["target_amount"] > 0 else 9
            ready["0-25%" if r < .25 else "25-50%" if r < .5 else "50-75%" if r < .75
                  else "75-100%" if r < 1 else ">=100%"] += 1
        return {"risk": Counter(p["risk"] for p in self.per),
                "r_bench": Counter(p["rb"] for p in self.per),
                "n_loans": Counter(p["nloans"] for p in self.per),
                "n_goals": Counter(p["ngoals"] for p in self.per),
                "readiness": ready}

    def diagnostics(self) -> dict[str, Counter]:
        dsr: Counter = Counter()
        liq: Counter = Counter()
        fcf: Counter = Counter()
        for p in self.per:
            if p["inc"] <= 0:
                dsr["доход=0"] += 1
            elif p["pays"] == 0:
                dsr["0"] += 1
            else:
                d = p["pays"] / p["inc"]
                dsr["<30%" if d < .3 else "30-50%" if d < .5 else "50-80%" if d < .8
                    else "80-150%" if d < 1.5 else ">=150%"] += 1
            if p["outflow"] <= 0:
                liq["отток=0"] += 1
            else:
                m = p["bliq"] / p["outflow"]
                liq["<1" if m < 1 else "1-3" if m < 3 else "3-6" if m < 6
                    else "6-12" if m < 12 else ">=12"] += 1
            fcf["FCF>0" if p["fcf"] > 0 else "FCF=0" if p["fcf"] == 0 else "FCF<0"] += 1
        return {"dsr": dsr, "liq_months": liq, "fcf_sign": fcf}

    def kind_validation(self) -> list[tuple[str, float, float, float, float]]:
        by_kind: dict[str, list[dict]] = {}
        for p, r in zip(self.per, self.rows):
            by_kind.setdefault(r["kind"], []).append(p)
        med: Callable[[list[float]], float] = lambda v: statistics.median(v) if v else 0.0
        out = []
        for k in sorted(by_kind):
            g = by_kind[k]
            out.append((k, med([x["inc"] for x in g]),
                        med([x["pays"] / x["inc"] for x in g if x["inc"] > 0]),
                        med([x["bliq"] / x["outflow"] for x in g if x["outflow"] > 0]),
                        100 * sum(1 for x in g if x["fcf"] < 0) / len(g)))
        return out

    # -- report ------------------------------------------------------------------
    def report(self) -> str:
        axes, pear, _ = self.correlations_plain()
        ann, dl, sh = self.annuity(), self.goal_deadlines(), self.shapes()
        lines = [
            "=== HEADLINE (секции 1-2 ревью) ===",
            f"corr plain: inc~exp={pear[('inc','exp')]:.3f} inc~pays={pear[('inc','pays')]:.3f} "
            f"inc~bliq={pear[('inc','bliq')]:.3f} inc~goals={pear[('inc','tgt')]:.3f}",
            f"annuity: interest_only={ann['interest_only']} weird_term={ann['weird_term']} "
            f"term_med={ann['term_med']:.0f} p90={ann['term_p90']:.0f}",
            f"deadlines: overdue_unfunded={dl['overdue_unfunded']} within_90d={dl['within_90d']}",
            f"plain DSR buckets: {dict(self.plain_dsr_buckets())}",
            f"r_bench values: {dict(sorted(self.categoricals()['r_bench'].items()))}",
            "", "=== APPENDIX A ===",
            "A.1 " + json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()}
                                 for k, v in self.descriptives().items()}, ensure_ascii=False),
            "A.3 " + json.dumps({k: round(v, 4) for k, v in sh.items()}),
            "A.4 horizon " + json.dumps(dict(dl["horizon"]), ensure_ascii=False),
            "A.5 " + json.dumps({k: dict(v) for k, v in self.diagnostics().items()},
                                ensure_ascii=False),
            "A.6 " + json.dumps([(k, round(i), round(d, 2), round(l, 1), round(f))
                                 for k, i, d, l, f in self.kind_validation()],
                                ensure_ascii=False),
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/portraits_12000.jsonl"
    print(DatasetProfiler(src).report())
