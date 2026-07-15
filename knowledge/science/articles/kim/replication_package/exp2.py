"""Computational study v2: three demo profiles x three L_min regimes."""
import json
import numpy as np
import model as m

def make_profiles():
    A = m.Profile(  # закредитованный: D > D_max -> допустимых нет
        income=90_000, expenses=40_000,
        loans=[m.Loan("Кредитная карта", 200_000, 0.27, 12),
               m.Loan("Потребительский кредит", 500_000, 0.22, 36)],
        goals=[m.Goal("Резерв", 100_000, 10_000, 12, 2.0)])
    B = m.Profile(  # типовой: L около порога
        income=135_000, expenses=60_000,
        loans=[m.Loan("Кредитная карта", 60_000, 0.27, 12),
               m.Loan("Потребительский кредит", 300_000, 0.22, 30),
               m.Loan("Ипотека", 1_500_000, 0.085, 180)],
        goals=[m.Goal("Резерв безопасности", 150_000, 30_000, 12, 2.0),
               m.Goal("Проф. переподготовка", 60_000, 10_000, 6, 3.0),
               m.Goal("Отпуск", 40_000, 5_000, 10, 0.5)])
    C = m.Profile(  # комфортный
        income=167_000, expenses=36_500,
        loans=[m.Loan("Потребительский кредит", 250_000, 0.19, 24),
               m.Loan("Ипотека", 1_800_000, 0.085, 180)],
        goals=[m.Goal("Резерв безопасности", 300_000, 90_000, 12, 2.0),
               m.Goal("Проф. переподготовка", 120_000, 30_000, 6, 3.0),
               m.Goal("Отпуск", 80_000, 20_000, 10, 0.5)])
    return {"A": A, "B": B, "C": C}

def study(profile, l_min):
    profile.l_min = l_min
    dm = m.DecisionModel(profile)
    base = dict(sum_p=dm.sum_payments, cf=dm.cash_flow, r=dm.resource,
                l=dm.liquidity(dm.resource, dm.sum_payments),
                d=dm.debt_load(dm.sum_payments))
    if dm.resource <= 0:
        return dict(base=base, status="fail_loud_R")
    rows = dm.evaluate()
    nf = sum(r["feasible"] for r in rows)
    if nf == 0:
        return dict(base=base, status="fail_loud_constraints", rows=rows)
    optima, u_matrix, alphas = {}, {}, None
    for name, w in m.RISK_PROFILES.items():
        feas, u, order = dm.rank(rows, w)
        optima[name] = feas[order[0]]["alpha"]
        u_matrix[name] = [float(x) for x in u]
        alphas = [f["alpha"] for f in feas]
    # sensitivity for Balanced
    base_w = np.array(m.RISK_PROFILES["Balanced"])
    feas, u0, o0 = dm.rank(rows, base_w)
    best0 = feas[o0[0]]["alpha"]
    stable = total = 0
    for k in range(4):
        for d in (-0.05, 0.05):
            w = base_w.copy(); w[k] = max(w[k]+d, 0); w = w/w.sum()
            _, u, o = dm.rank(rows, w)
            total += 1; stable += (feas[o[0]]["alpha"] == best0)
    return dict(base=base, status="ok", n_feasible=nf, rows=rows,
                optima=optima, u_matrix=u_matrix, alphas=alphas,
                sens=(stable, total))

profiles = make_profiles()
out = {}
for pname, prof in profiles.items():
    out[pname] = {}
    for lm in (0.0, 0.15, 0.30):
        res = study(prof, lm)
        key = f"lmin_{lm}"
        out[pname][key] = res
        s = res["status"]
        line = f"{pname} L_min={lm}: {s}"
        if s == "ok":
            opts = {k: "%.0f/%.0f/%.0f" % (v[0]*100, v[1]*100, v[2]*100)
                    for k, v in res["optima"].items()}
            line += f" feas={res['n_feasible']} distinct={len(set(res['optima'].values()))} sens={res['sens'][0]}/{res['sens'][1]} :: {opts}"
        print(line)
    b = out[pname]["lmin_0.3" if "lmin_0.3" in out[pname] else "lmin_0.30"] if False else None

# базовые показатели профилей
print()
for pname, prof in profiles.items():
    dm = m.DecisionModel(prof)
    print(f"{pname}: SumP={dm.sum_payments:,.0f} CF={dm.cash_flow:,.0f} R={dm.resource:,.0f} "
          f"L={dm.liquidity(dm.resource, dm.sum_payments):.3f} D={dm.debt_load(dm.sum_payments):.3f} "
          f"payments={[round(l.payment) for l in prof.loans]}")

def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
with open("results2.json", "w", encoding="utf-8") as f:
    json.dump(clean(out), f, ensure_ascii=False)
print("\nsaved results2.json")
