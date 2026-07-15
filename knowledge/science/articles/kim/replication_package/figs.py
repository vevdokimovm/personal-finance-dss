"""Sensitivity details + 3 monochrome-safe figures for the paper."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle

import model as m
import exp2 as base
from exp3 import refined_eval, ses_point, histories, BT
from exp4 import rank_anchored

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

profiles = base.make_profiles()

# ---- sensitivity detail for C / Balanced ----
prof = profiles["C"]; prof.l_min = 0.30
dm = m.DecisionModel(prof)
hi, he = histories(prof.income, prof.expenses, seed=11)
i_hat, e_hat = ses_point(list(hi)), ses_point(list(he))
cf_hat = i_hat - e_hat
rows = refined_eval(dm, BT["C"], i_hat, e_hat)
bw = np.array(m.RISK_PROFILES["Balanced"])
feas, u0, o0 = rank_anchored(rows, bw, cf_hat, prof.d_max)
best0 = feas[o0[0]]["alpha"]
print("C Balanced base a* =", best0, "U=", round(float(u0[o0[0]]), 4))
labels = ["w_R", "w_L", "w_D", "w_S"]
for k in range(4):
    for d in (-0.05, 0.05):
        w = bw.copy(); w[k] = max(w[k] + d, 0); w = w / w.sum()
        _, u, o = rank_anchored(rows, w, cf_hat, prof.d_max)
        b = feas[o[0]]["alpha"]
        flag = "" if b == best0 else "  <-- FLIP to %s (dU=%.4f)" % (b, float(u[o[0]] - u[list(map(lambda f: f['alpha'], feas)).index(best0)]))
        print(f"  {labels[k]} {d:+.2f}: a*={b}{flag}")

# ---- Fig 2: heatmap U(a) for C, Spec-3 ----
alphas = [f["alpha"] for f in feas]
alabels = ["%.0f/%.0f/%.0f" % (a[0]*100, a[1]*100, a[2]*100) for a in alphas]
U = np.zeros((len(m.RISK_PROFILES), len(feas)))
stars = []
for i, (name, w) in enumerate(m.RISK_PROFILES.items()):
    f2, u, order = rank_anchored(rows, w, cf_hat, prof.d_max)
    U[i, :] = u
    stars.append(int(order[0]))
fig, ax = plt.subplots(figsize=(7.0, 2.9), dpi=300)
im = ax.imshow(U, aspect="auto", cmap="viridis")
ax.set_xticks(range(len(alabels)), alabels, rotation=90)
ax.set_yticks(range(len(m.RISK_PROFILES)),
              ["Консервативный", "Умеренный", "Сбалансированный", "Активный", "Агрессивный"])
for i, j in enumerate(stars):
    ax.plot(j, i, marker="*", color="white", markersize=11, markeredgecolor="black", markeredgewidth=0.6)
ax.set_xlabel("Альтернатива (досрочка/резерв/цели, % от $R_t$)")
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("$U(a)$")
fig.tight_layout()
fig.savefig("fig2_heatmap.png", bbox_inches="tight")
print("fig2 saved")

# ---- Fig 3: SES + MC fan chart for resource of C ----
rng = np.random.default_rng(11)
hist_R = hi - he - dm.sum_payments
smoothed, point, med, lo, hi95, sims = m.ses_mc_forecast(list(hist_R), alpha=0.3, horizon=3, n_iter=1000, seed=11)
fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=300)
t = np.arange(1, len(hist_R) + 1)
ax.plot(t, np.array(hist_R) / 1000, "o-", color="0.25", markersize=3, linewidth=0.9, label="Фактический ресурс $R_t$")
ax.plot(t, np.array(smoothed) / 1000, "--", color="0.55", linewidth=1.0, label="Сглаженный ряд (SES, $\\alpha=0{,}3$)")
th = np.arange(len(hist_R) + 1, len(hist_R) + 4)
ax.plot(th, med / 1000, "s-", color="black", markersize=4, linewidth=1.1, label="Медианный прогноз")
ax.fill_between(th, lo / 1000, hi95 / 1000, color="0.8", label="95% интервал (Монте-Карло)")
from matplotlib.ticker import MaxNLocator
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlabel("Месяц"); ax.set_ylabel("Свободный ресурс, тыс. руб.")
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig("fig3_forecast.png", bbox_inches="tight")
print("fig3 saved; CI95 h=3: [%.0f, %.0f], med=%.0f" % (lo[2], hi95[2], med[2]))

# ---- Fig 1: pipeline scheme ----
fig, ax = plt.subplots(figsize=(7.0, 3.3), dpi=300)
ax.axis("off")
def box(x, y, w, h, text, fc="white"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", linewidth=0.9))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="black", linewidth=0.9))
# top row
box(0.0, 0.62, 0.16, 0.26, "Входные данные\n$X=\\{I_t,E_t,B_t,O,G,u\\}$", fc="0.92")
box(0.21, 0.62, 0.17, 0.26, "Показатели состояния\n$CF_t,R_t,L_t,D_t,S_t$")
box(0.43, 0.62, 0.17, 0.26, "Прогноз потоков\nSES + Монте-Карло")
box(0.65, 0.62, 0.16, 0.26, "Генерация\nальтернатив\n(шаг 20 %)")
box(0.86, 0.62, 0.14, 0.26, "Фильтр ставок\n($r_k \\geq r_{bench}$)")
# bottom row (right to left)
box(0.86, 0.10, 0.14, 0.26, "Фильтр\nдопустимости\n$L,D,R$-каскад")
box(0.63, 0.10, 0.18, 0.26, "Нормативная нормализация\n(ПДН, нормы запаса)")
box(0.40, 0.10, 0.18, 0.26, "Аддитивная свёртка\n$U(a)$, профиль риска")
box(0.21, 0.10, 0.14, 0.26, "$a^*=\\arg\\max U$")
box(0.0, 0.10, 0.16, 0.26, "Рекомендация\n+ объяснение", fc="0.92")
arrow(0.16, 0.75, 0.21, 0.75); arrow(0.38, 0.75, 0.43, 0.75)
arrow(0.60, 0.75, 0.65, 0.75); arrow(0.81, 0.75, 0.86, 0.75)
arrow(0.93, 0.62, 0.93, 0.36)
arrow(0.86, 0.23, 0.81, 0.23); arrow(0.63, 0.23, 0.58, 0.23)
arrow(0.40, 0.23, 0.35, 0.23); arrow(0.21, 0.23, 0.16, 0.23)
# forecast feeds utility (key refinement) — vertical dashed
ax.annotate("", xy=(0.49, 0.36), xytext=(0.515, 0.62),
            arrowprops=dict(arrowstyle="-|>", color="black", linewidth=0.9, linestyle=(0, (4, 3))))
ax.text(0.485, 0.47, "прогнозный критерий $\\hat{R}_{t+1}(a)$", fontsize=7.5, rotation=0, ha="right")
fig.savefig("fig1_pipeline.png", bbox_inches="tight")
print("fig1 saved")
