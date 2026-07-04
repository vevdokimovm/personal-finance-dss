"""Computational experiment for the KIM paper.

Implements the full decision model: alternative generation (stars-and-bars,
step 0.2), Avalanche filter with opportunity-cost rate, weighted goal supply,
feasibility constraints, min-max normalization, SAW ranking for five risk
profiles, and weight-sensitivity analysis.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field

import numpy as np


def annuity_payment(balance: float, annual_rate: float, term_months: int) -> float:
    r = annual_rate / 12.0
    if r == 0:
        return balance / term_months
    return balance * r / (1.0 - (1.0 + r) ** (-term_months))


@dataclass
class Loan:
    name: str
    balance: float
    rate: float
    term: int

    @property
    def payment(self) -> float:
        return annuity_payment(self.balance, self.rate, self.term)


@dataclass
class Goal:
    name: str
    target: float
    current: float
    months_to_deadline: int
    category_weight: float  # income_growth=3.0 safety=2.0 material=1.0 emotional=0.5

    @property
    def urgency(self) -> float:
        return max(1.0, 12.0 / max(self.months_to_deadline, 1))


@dataclass
class Profile:
    income: float
    expenses: float
    loans: list[Loan]
    goals: list[Goal]
    l_min: float = 0.30
    d_max: float = 0.40
    r_bench: float = 0.14


RISK_PROFILES = {
    "Conservative": (0.20, 0.45, 0.25, 0.10),
    "Moderate": (0.20, 0.35, 0.25, 0.20),
    "Balanced": (0.25, 0.30, 0.25, 0.20),
    "Active": (0.30, 0.20, 0.20, 0.30),
    "Aggressive": (0.35, 0.10, 0.15, 0.40),
}


class DecisionModel:
    def __init__(self, profile: Profile) -> None:
        self.p = profile

    # --- base metrics -------------------------------------------------
    @property
    def sum_payments(self) -> float:
        return sum(loan.payment for loan in self.p.loans)

    @property
    def cash_flow(self) -> float:
        return self.p.income - self.p.expenses

    @property
    def resource(self) -> float:
        return self.cash_flow - self.sum_payments

    def liquidity(self, resource: float, payments: float) -> float:
        return resource / (self.p.expenses + payments)

    def debt_load(self, payments: float) -> float:
        return payments / self.p.income

    # --- avalanche with opportunity-cost rate -------------------------
    def apply_prepayment(self, x_d: float) -> tuple[float, float]:
        """Return (effective prepayment, new total monthly payment)."""
        targets = sorted(
            (l for l in self.p.loans if l.rate >= self.p.r_bench),
            key=lambda l: l.rate,
            reverse=True,
        )
        if not targets:
            return 0.0, self.sum_payments
        remaining = x_d
        new_total = 0.0
        target_names = {l.name for l in targets}
        for loan in self.p.loans:
            if loan.name not in target_names:
                new_total += loan.payment
        for loan in targets:
            pay_down = min(remaining, loan.balance)
            remaining -= pay_down
            new_balance = loan.balance - pay_down
            if new_balance > 1e-9:
                new_total += annuity_payment(new_balance, loan.rate, loan.term)
        return x_d - remaining, new_total

    # --- weighted goal supply ------------------------------------------
    def goal_supply(self, x_g: float) -> float:
        goals = self.p.goals
        weights = np.array([g.category_weight * g.urgency for g in goals])
        room = np.array([g.target - g.current for g in goals])
        add = np.zeros(len(goals))
        rest = x_g
        active = room > 1e-9
        while rest > 1e-9 and active.any():
            share = weights * active
            share = share / share.sum()
            alloc = np.minimum(rest * share, room - add)
            add += alloc
            rest -= alloc.sum()
            active = (room - add) > 1e-9
            if alloc.sum() < 1e-9:
                break
        num = sum(
            (g.current + a) * g.category_weight * g.urgency
            for g, a in zip(goals, add)
        )
        den = sum(g.target * g.category_weight * g.urgency for g in goals)
        return num / den

    # --- alternatives ---------------------------------------------------
    def alternatives(self, step: float = 0.2):
        n = round(1.0 / step)
        for i, j in itertools.product(range(n + 1), repeat=2):
            if i + j <= n:
                yield (i * step, j * step, (n - i - j) * step)

    def evaluate(self):
        r_plus = max(self.resource, 0.0)
        rows = []
        for alpha in self.alternatives():
            a_d, a_r, a_g = alpha
            x_d, x_g = a_d * r_plus, a_g * r_plus
            x_d_eff, new_payments = self.apply_prepayment(x_d)
            # unspent prepayment is redirected to goals (OCR rule)
            x_g_eff = x_g + (x_d - x_d_eff)
            r_new = self.resource - x_d_eff - x_g_eff
            l_new = self.liquidity(r_new, new_payments)
            d_new = self.debt_load(new_payments)
            s_new = self.goal_supply(x_g_eff)
            feasible = (
                l_new >= self.p.l_min and d_new <= self.p.d_max and r_new >= 0.0
            )
            rows.append(
                dict(
                    alpha=alpha,
                    x_d=x_d_eff,
                    x_r=a_r * r_plus,
                    x_g=x_g_eff,
                    R=r_new,
                    L=l_new,
                    D=d_new,
                    S=s_new,
                    feasible=feasible,
                )
            )
        return rows

    @staticmethod
    def rank(rows, weights):
        feas = [r for r in rows if r["feasible"]]
        def norm(key):
            vals = np.array([r[key] for r in feas])
            lo, hi = vals.min(), vals.max()
            return np.zeros_like(vals) if hi - lo < 1e-12 else (vals - lo) / (hi - lo)
        rn, ln, dn, sn = norm("R"), norm("L"), norm("D"), norm("S")
        w1, w2, w3, w4 = weights
        u = w1 * rn + w2 * ln + w3 * (1.0 - dn) + w4 * sn
        order = np.argsort(-u)
        return feas, u, order


def ses_mc_forecast(series, alpha=0.3, horizon=3, n_iter=1000, seed=42):
    rng = np.random.default_rng(seed)
    smoothed = [series[0]]
    for y in series[1:]:
        smoothed.append(alpha * y + (1 - alpha) * smoothed[-1])
    residuals = np.array(series[1:]) - np.array(smoothed[:-1])
    sigma = residuals.std(ddof=1)
    point = smoothed[-1]
    sims = point + rng.normal(0.0, sigma, size=(n_iter, horizon)).cumsum(axis=1) * 0
    # i.i.d. noise per horizon step (no random walk): regenerate properly
    sims = point + rng.normal(0.0, sigma, size=(n_iter, horizon))
    med = np.median(sims, axis=0)
    lo = np.percentile(sims, 2.5, axis=0)
    hi = np.percentile(sims, 97.5, axis=0)
    return smoothed, point, med, lo, hi, sims


def main() -> None:
    profile = Profile(
        income=167_000.0,
        expenses=36_500.0,
        loans=[
            Loan("Потребительский кредит", 250_000.0, 0.19, 24),
            Loan("Ипотека", 1_800_000.0, 0.085, 180),
        ],
        goals=[
            Goal("Резерв безопасности", 300_000.0, 90_000.0, 12, 2.0),
            Goal("Проф. переподготовка", 120_000.0, 30_000.0, 6, 3.0),
            Goal("Отпуск", 80_000.0, 20_000.0, 10, 0.5),
        ],
    )
    model = DecisionModel(profile)

    print("=== BASE METRICS ===")
    print(f"Payments: {[round(l.payment, 2) for l in profile.loans]}")
    print(f"Sum P = {model.sum_payments:.2f}")
    print(f"CF = {model.cash_flow:.2f}, R = {model.resource:.2f}")
    print(f"L = {model.liquidity(model.resource, model.sum_payments):.4f}")
    print(f"D = {model.debt_load(model.sum_payments):.4f}")
    s0 = model.goal_supply(0.0)
    print(f"S (no allocation) = {s0:.4f}")

    rows = model.evaluate()
    n_feasible = sum(r["feasible"] for r in rows)
    print(f"\nAlternatives: {len(rows)}, feasible: {n_feasible}")

    results = {}
    for name, w in RISK_PROFILES.items():
        feas, u, order = model.rank(rows, w)
        best = feas[order[0]]
        results[name] = dict(
            best_alpha=best["alpha"], best_u=float(u[order[0]]),
            u=[float(x) for x in u],
            alphas=[f["alpha"] for f in feas],
        )
        a = best["alpha"]
        print(
            f"{name:13s} -> a*=({a[0]:.0%}/{a[1]:.0%}/{a[2]:.0%}) "
            f"U={u[order[0]]:.4f}"
        )

    # sensitivity: perturb each weight of Balanced by +-0.05, renormalize
    base_w = np.array(RISK_PROFILES["Balanced"])
    feas, u_base, order_base = model.rank(rows, base_w)
    best_base = feas[order_base[0]]["alpha"]
    stable, total = 0, 0
    changes = []
    for k in range(4):
        for delta in (-0.05, 0.05):
            w = base_w.copy()
            w[k] = max(w[k] + delta, 0.0)
            w = w / w.sum()
            _, u, order = model.rank(rows, w)
            total += 1
            if feas[order[0]]["alpha"] == best_base:
                stable += 1
            else:
                changes.append((k, delta, feas[order[0]]["alpha"]))
    print(f"\nSensitivity: top-1 stable in {stable}/{total} perturbations")
    if changes:
        print("Changes:", changes)

    # SES + MC forecast on synthetic 18-month income history
    rng = np.random.default_rng(7)
    history = list(167_000 + rng.normal(0, 6_000, size=18))
    smoothed, point, med, lo, hi, sims = ses_mc_forecast(history)
    print(f"\nForecast point={point:.0f}, h=1..3 median={np.round(med)}")
    print(f"95% CI h=3: [{lo[2]:.0f}, {hi[2]:.0f}]")

    table_rows = []
    for r in rows:
        a = r["alpha"]
        table_rows.append(
            dict(
                alpha=f"{a[0]:.0%}/{a[1]:.0%}/{a[2]:.0%}",
                R=round(r["R"]), L=round(r["L"], 3), D=round(r["D"], 3),
                S=round(r["S"], 3), feasible=bool(r["feasible"]),
            )
        )
    out = dict(
        base=dict(
            payments=[round(l.payment, 2) for l in profile.loans],
            sum_p=round(model.sum_payments, 2),
            cf=round(model.cash_flow, 2),
            r=round(model.resource, 2),
            l=round(model.liquidity(model.resource, model.sum_payments), 4),
            d=round(model.debt_load(model.sum_payments), 4),
            s0=round(s0, 4),
        ),
        n_feasible=n_feasible,
        table=table_rows,
        ranking={k: dict(best=v["best_alpha"], u=v["best_u"]) for k, v in results.items()},
        sensitivity=dict(stable=stable, total=total, changes=changes),
        forecast=dict(point=round(point), median=[round(x) for x in med],
                      lo=[round(x) for x in lo], hi=[round(x) for x in hi]),
        history=[round(x) for x in history],
        results_full=results,
    )
    with open("/home/claude/experiment/results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\nSaved results.json")


if __name__ == "__main__":
    main()
