"""Б-04: на сколько должна ошибиться оценка расходов, чтобы сменился совет."""
import sys, random, json
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core.alternatives import generate_alternatives, evaluate_alternative
from app.core.filtering import filter_alternatives
from app.core.ranking import rank_alternatives

R_BENCH = 0.14

def winner(income, expense, obls, goals, bliq, profile):
    pay = sum(o["monthly_payment"] for o in obls)
    rt = income - expense - pay
    goals_total = sum(g.get("target_amount", 0) for g in goals)
    alts = generate_alternatives(rt, pay, goals_total)
    ev = [evaluate_alternative(dict(a), income, expense, obls, goals, R_BENCH, bliq) for a in alts]
    dt_cur = pay / income if income else 0.0
    ok, _ = filter_alternatives(ev, dt_current=dt_cur)
    if not ok:
        return None
    ranked = rank_alternatives(ok, risk_tolerance=profile)
    best = max(ranked, key=lambda a: (a.get("floor_level", 0), a.get("utility", 0)))
    return best.get("id")   # альтернатива-ДОЛЯ, не рубли

def make_portrait(rng):
    income = rng.choice([45000, 70000, 95000, 130000, 180000, 250000])
    expense = income * rng.uniform(0.45, 0.80)
    n_obl = rng.randint(1, 3)
    obls = []
    for i in range(n_obl):
        amount = rng.uniform(40000, 900000)
        rate = rng.choice([0.055, 0.09, 0.12, 0.155, 0.19, 0.24, 0.35])
        obls.append({"id": f"o{i}", "name": f"Кредит {i}", "amount": round(amount, 2),
                     "interest_rate": rate,
                     "monthly_payment": round(amount * rng.uniform(0.02, 0.05), 2)})
    goals = [{"id": f"g{j}", "name": f"Цель {j}",
              "target_amount": round(rng.uniform(50000, 700000), 2),
              "current_amount": 0.0, "category": rng.choice(["safety","material","income","emotional"]),
              "deadline_months": rng.randint(4, 48)} for j in range(rng.randint(1, 2))]
    bliq = income * rng.uniform(0.2, 4.0)
    return income, round(expense, 2), obls, goals, round(bliq, 2)

def main():
    rng = random.Random(20260922)
    EPS = [0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.20]
    N = 400
    flipped_at = {e: 0 for e in EPS}
    valid = 0
    first_flip = []
    for _ in range(N):
        income, expense, obls, goals, bliq = make_portrait(rng)
        prof = rng.randint(1, 5)
        base = winner(income, expense, obls, goals, bliq, prof)
        if base is None:
            continue
        valid += 1
        ff = None
        for e in EPS:
            changed = False
            for sign in (+1, -1):
                w = winner(income, round(expense * (1 + sign * e), 2), obls, goals, bliq, prof)
                if w is not None and w != base:
                    changed = True
                    break
            if changed:
                flipped_at[e] += 1
                if ff is None:
                    ff = e
        first_flip.append(ff)
    print(f"портретов с допустимым решением: {valid} из {N}")
    print(f"{'возмущение расходов':>22} | {'сменился совет':>14}")
    for e in EPS:
        print(f"{e*100:>20.1f}% | {flipped_at[e]:>6} ({flipped_at[e]/valid*100:>5.1f}%)")
    never = sum(1 for f in first_flip if f is None)
    print(f"\nне сменился ни при одном возмущении до 20%: {never} ({never/valid*100:.1f}%)")
    small = sum(1 for f in first_flip if f is not None and f <= 0.02)
    print(f"сменился уже при ошибке ≤2%: {small} ({small/valid*100:.1f}%)")
main()
