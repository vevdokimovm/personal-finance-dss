"""Part 2: refined criteria — forecast-aware resource + stock liquidity."""
import json
import numpy as np
import model as m

BT = {"A": 30_000.0, "B": 90_000.0, "C": 150_000.0}

def ses_point(series, alpha=0.3):
    s = series[0]
    for y in series[1:]:
        s = alpha * y + (1 - alpha) * s
    return s

def histories(mean_i, mean_e, seed):
    rng = np.random.default_rng(seed)
    hi = mean_i + rng.normal(0, 0.04 * mean_i, 18)
    he = mean_e + rng.normal(0, 0.06 * mean_e, 18)
    return hi, he

def refined_eval(dm, b_t, i_hat, e_hat):
    """Refined criteria over the same alternatives and same constraints."""
    r_plus = max(dm.resource, 0.0)
    rows = []
    for alpha in dm.alternatives():
        a_d, a_r, a_g = alpha
        x_d, x_g = a_d * r_plus, a_g * r_plus
        x_d_eff, new_payments = dm.apply_prepayment(x_d)
        x_g_eff = x_g + (x_d - x_d_eff)
        x_r = a_r * r_plus
        # constraints — как в исходной модели (защитный каскад не трогаем)
        r_flow = dm.resource - x_d_eff - x_g_eff
        l_flow = dm.liquidity(r_flow, new_payments)
        d_new = dm.debt_load(new_payments)
        feasible = (l_flow >= dm.p.l_min and d_new <= dm.p.d_max and r_flow >= 0)
        # refined criteria
        r_next = i_hat - e_hat - new_payments            # прогнозный ресурс t+1
        l_stock = (b_t + x_r) / (dm.p.expenses + new_payments)  # запас, мес.
        s_new = dm.goal_supply(x_g_eff)
        rows.append(dict(alpha=alpha, Rn=r_next, Ls=l_stock, D=d_new, S=s_new,
                         feasible=feasible))
    return rows

def rank(rows, weights):
    feas = [r for r in rows if r["feasible"]]
    def norm(key):
        v = np.array([r[key] for r in feas])
        lo, hi = v.min(), v.max()
        return np.zeros_like(v) if hi - lo < 1e-12 else (v - lo) / (hi - lo)
    rn, ln, dn, sn = norm("Rn"), norm("Ls"), norm("D"), norm("S")
    w1, w2, w3, w4 = weights
    u = w1 * rn + w2 * ln + w3 * (1 - dn) + w4 * sn
    return feas, u, np.argsort(-u)

import exp2 as base  # noqa: E402 — реиспользуем профили
profiles = base.make_profiles()

out = {}
for pname in ("B", "C"):
    prof = profiles[pname]
    prof.l_min = 0.30
    dm = m.DecisionModel(prof)
    hi, he = histories(prof.income, prof.expenses, seed=11)
    i_hat, e_hat = ses_point(list(hi)), ses_point(list(he))
    rows = refined_eval(dm, BT[pname], i_hat, e_hat)
    nf = sum(r["feasible"] for r in rows)
    optima, u_matrix = {}, {}
    for name, w in m.RISK_PROFILES.items():
        feas, u, order = rank(rows, w)
        optima[name] = feas[order[0]]["alpha"]
        u_matrix[name] = [float(x) for x in u]
    alphas = [f["alpha"] for f in feas]
    # sensitivity Balanced
    bw = np.array(m.RISK_PROFILES["Balanced"])
    feas, u0, o0 = rank(rows, bw)
    best0 = feas[o0[0]]["alpha"]
    stable = total = 0
    for k in range(4):
        for d in (-0.05, 0.05):
            w = bw.copy(); w[k] = max(w[k] + d, 0); w = w / w.sum()
            _, u, o = rank(rows, w)
            total += 1; stable += (feas[o[0]]["alpha"] == best0)
    print(f"{pname}: i_hat={i_hat:,.0f} e_hat={e_hat:,.0f} feas={nf} "
          f"distinct={len(set(optima.values()))} sens={stable}/{total}")
    for k, v in optima.items():
        print("   %-13s -> %3.0f/%3.0f/%3.0f" % (k, v[0]*100, v[1]*100, v[2]*100))
    out[pname] = dict(i_hat=i_hat, e_hat=e_hat, n_feasible=nf,
                      optima=optima, u_matrix=u_matrix, alphas=alphas,
                      sens=(stable, total),
                      rows=[{**r} for r in rows])

def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.bool_): return bool(o)
    return o
json.dump(clean(out), open("results3.json", "w", encoding="utf-8"), ensure_ascii=False)
print("saved results3.json")
