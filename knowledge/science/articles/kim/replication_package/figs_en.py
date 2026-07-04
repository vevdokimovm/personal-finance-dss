"""English versions of all three figures for the EN manuscript."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

import model as m
import exp2 as base
from exp3 import refined_eval, ses_point, histories, BT
from exp4 import rank_anchored

plt.rcParams.update({"font.family": "DejaVu Sans"})

# ---------- Fig 1 (pipeline, EN) ----------
fig, ax = plt.subplots(figsize=(9.0, 3.6), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 42); ax.axis("off")
FS = 8.2
def box(x, y, w, h, text, fc="white"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", linewidth=0.9))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=FS)
def arrow(x1, y1, x2, y2, dashed=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="black", linewidth=0.9,
                                linestyle=(0, (4, 3)) if dashed else "solid"))
TY, TH, BY, BH, W = 26, 12, 4, 12, 17.5
xs = [0, 20.5, 41, 61.5, 82]
box(xs[0], TY, W, TH, "Input data\n$X{=}\\{I_t,E_t,B_t,O,G,u\\}$", fc="0.92")
box(xs[1], TY, W, TH, "State metrics\n$CF_t,\\,R_t,\\,L_t,\\,D_t,\\,S_t$")
box(xs[2], TY, W, TH, "Cash-flow forecast\nSES + Monte-Carlo")
box(xs[3], TY, W, TH, "Alternative\ngeneration\n(step 20 %)")
box(xs[4], TY, W, TH, "Early-repayment\nrate filter\n$r_k \\geq r_{bench}$")
box(xs[4], BY, W, BH, "Feasibility\nfilter\n($D$, $L$, $R$ cascade)")
box(xs[3], BY, W, BH, "Norm-anchored\nnormalization\nof criteria")
box(xs[2], BY, W, BH, "Additive utility\n$U(a)$ by risk\nprofile")
box(xs[1], BY, W, BH, "Decision\n$a^*{=}\\arg\\max\\,U(a)$")
box(xs[0], BY, W, BH, "Recommendation\nwith explanation", fc="0.92")
mid_t, mid_b = TY + TH/2, BY + BH/2
for i in range(4): arrow(xs[i] + W, mid_t, xs[i+1], mid_t)
arrow(xs[4] + W/2, TY, xs[4] + W/2, BY + BH)
for i in range(4, 0, -1): arrow(xs[i], mid_b, xs[i-1] + W, mid_b)
arrow(xs[2] + W/2, TY, xs[2] + W/2, BY + BH, dashed=True)
ax.text(xs[2] + W/2 - 1.2, (TY + BY + BH)/2, "forecast criterion $\\hat{R}_{t+1}(a)$",
        fontsize=7.4, ha="right", va="center")
fig.savefig("fig1_pipeline_en.png", bbox_inches="tight")
print("fig1 EN ok")

# ---------- shared data for Fig 2/3 ----------
profiles = base.make_profiles()
prof = profiles["C"]; prof.l_min = 0.30
dm = m.DecisionModel(prof)
hi, he = histories(prof.income, prof.expenses, seed=11)
i_hat, e_hat = ses_point(list(hi)), ses_point(list(he))
cf_hat = i_hat - e_hat
rows = refined_eval(dm, BT["C"], i_hat, e_hat)
feas0, _, _ = rank_anchored(rows, np.array(m.RISK_PROFILES["Balanced"]), cf_hat, prof.d_max)
alphas = [f["alpha"] for f in feas0]
alabels = ["%.0f/%.0f/%.0f" % (a[0]*100, a[1]*100, a[2]*100) for a in alphas]
NAMES_EN = ["Conservative", "Moderate", "Balanced", "Active", "Aggressive"]

# ---------- Fig 2 (heatmap, EN) ----------
U = np.zeros((len(m.RISK_PROFILES), len(feas0)))
stars = []
for i, (name, w) in enumerate(m.RISK_PROFILES.items()):
    _, u, order = rank_anchored(rows, w, cf_hat, prof.d_max)
    U[i, :] = u
    stars.append(int(order[0]))
fig, ax = plt.subplots(figsize=(7.0, 2.9), dpi=300)
im = ax.imshow(U, aspect="auto", cmap="viridis")
ax.set_xticks(range(len(alabels)), alabels, rotation=90)
ax.set_yticks(range(5), NAMES_EN)
for i, j in enumerate(stars):
    ax.plot(j, i, marker="*", color="white", markersize=11,
            markeredgecolor="black", markeredgewidth=0.6)
ax.set_xlabel("Alternative (repayment/reserve/goals, % of $R_t$)")
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("$U(a)$")
fig.tight_layout()
fig.savefig("fig2_heatmap_en.png", bbox_inches="tight")
print("fig2 EN ok; stars:", [alabels[j] for j in stars])

# ---------- Fig 3 (forecast fan, EN) ----------
hist_R = hi - he - dm.sum_payments
smoothed, point, med, lo, hi95, sims = m.ses_mc_forecast(list(hist_R), alpha=0.3, horizon=3, n_iter=1000, seed=11)
fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=300)
t = np.arange(1, len(hist_R) + 1)
ax.plot(t, np.array(hist_R) / 1000, "o-", color="0.25", markersize=3, linewidth=0.9,
        label="Actual resource $R_t$")
ax.plot(t, np.array(smoothed) / 1000, "--", color="0.55", linewidth=1.0,
        label="Smoothed series (SES, $\\alpha=0.3$)")
th = np.arange(len(hist_R) + 1, len(hist_R) + 4)
ax.plot(th, med / 1000, "s-", color="black", markersize=4, linewidth=1.1, label="Median forecast")
ax.fill_between(th, lo / 1000, hi95 / 1000, color="0.8", label="95% interval (Monte-Carlo)")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlabel("Month"); ax.set_ylabel("Free resource, thousand rubles")
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig("fig3_forecast_en.png", bbox_inches="tight")
print("fig3 EN ok; CI95 h=3: [%.0f, %.0f]" % (lo[2], hi95[2]))
