"""Spec-3: norm-anchored normalization (final refined model)."""
import json
import numpy as np
import model as m
from exp3 import refined_eval, ses_point, histories, BT
import exp2 as base

L_STOCK_MAX = 6.0   # верхняя норма BLR (Greninger, 1996)

def rank_anchored(rows, weights, cf_hat, d_max):
    feas = [r for r in rows if r["feasible"]]
    rn = np.clip([r["Rn"] / cf_hat for r in feas], 0, 1)
    ln = np.clip([r["Ls"] / L_STOCK_MAX for r in feas], 0, 1)
    dn = np.clip([r["D"] / d_max for r in feas], 0, 1)
    sn = np.clip([r["S"] for r in feas], 0, 1)
    w1, w2, w3, w4 = weights
    u = w1 * rn + w2 * ln + w3 * (1 - dn) + w4 * sn
    return feas, u, np.argsort(-u)

profiles = base.make_profiles()
out = {}
for pname in ("B", "C"):
    prof = profiles[pname]; prof.l_min = 0.30
    dm = m.DecisionModel(prof)
    hi, he = histories(prof.income, prof.expenses, seed=11)
    i_hat, e_hat = ses_point(list(hi)), ses_point(list(he))
    cf_hat = i_hat - e_hat
    rows = refined_eval(dm, BT[pname], i_hat, e_hat)
    nf = sum(r["feasible"] for r in rows)
    optima, u_matrix = {}, {}
    for name, w in m.RISK_PROFILES.items():
        feas, u, order = rank_anchored(rows, w, cf_hat, prof.d_max)
        optima[name] = feas[order[0]]["alpha"]
        u_matrix[name] = [float(x) for x in u]
    alphas = [f["alpha"] for f in feas]
    bw = np.array(m.RISK_PROFILES["Balanced"])
    feas, u0, o0 = rank_anchored(rows, bw, cf_hat, prof.d_max)
    best0 = feas[o0[0]]["alpha"]
    stable = total = 0
    for k in range(4):
        for d in (-0.05, 0.05):
            w = bw.copy(); w[k] = max(w[k] + d, 0); w = w / w.sum()
            _, u, o = rank_anchored(rows, w, cf_hat, prof.d_max)
            total += 1; stable += (feas[o[0]]["alpha"] == best0)
    print(f"{pname}: feas={nf} distinct={len(set(optima.values()))} sens={stable}/{total}")
    for k, v in optima.items():
        print("   %-13s -> %3.0f/%3.0f/%3.0f" % (k, v[0]*100, v[1]*100, v[2]*100))
    out[pname] = dict(i_hat=float(i_hat), e_hat=float(e_hat), n_feasible=nf,
                      optima={k: list(v) for k, v in optima.items()},
                      u_matrix=u_matrix, alphas=[list(a) for a in alphas],
                      sens=[stable, total],
                      rows=[{k: (list(v) if isinstance(v, tuple) else (bool(v) if isinstance(v, (bool, np.bool_)) else float(v))) for k, v in r.items()} for r in rows])

json.dump(out, open("results4.json", "w", encoding="utf-8"), ensure_ascii=False)
print("saved results4.json")
