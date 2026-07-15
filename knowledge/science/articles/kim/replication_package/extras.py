import time
import numpy as np
import model as m
import exp2 as base
from exp3 import refined_eval, ses_point, histories, BT
from exp4 import rank_anchored

profiles = base.make_profiles()
for pname in ("B", "C"):
    prof = profiles[pname]; prof.l_min = 0.30
    dm = m.DecisionModel(prof)
    rows = dm.evaluate()
    R = np.array([r["R"] for r in rows]); L = np.array([r["L"] for r in rows])
    print(pname, "corr(R,L) over 21 alts:", round(float(np.corrcoef(R, L)[0, 1]), 5))

# timing: full cycle (alternatives + avalanche + constraints + 5 rankings) on C
prof = profiles["C"]; prof.l_min = 0.30
dm = m.DecisionModel(prof)
hi, he = histories(prof.income, prof.expenses, seed=11)
i_hat, e_hat = ses_point(list(hi)), ses_point(list(he))
def cycle():
    rows = refined_eval(dm, BT["C"], i_hat, e_hat)
    for name, w in m.RISK_PROFILES.items():
        rank_anchored(rows, w, i_hat - e_hat, prof.d_max)
n = 200
t0 = time.perf_counter()
for _ in range(n): cycle()
dt = (time.perf_counter() - t0) / n * 1000
print(f"full cycle: {dt:.2f} ms")
# + SES/MC forecast timing
t0 = time.perf_counter()
for _ in range(50):
    m.ses_mc_forecast(list(hi - he - dm.sum_payments), alpha=0.3, horizon=3, n_iter=1000, seed=1)
dt2 = (time.perf_counter() - t0) / 50 * 1000
print(f"SES+MC (N=1000, h=3): {dt2:.2f} ms")
