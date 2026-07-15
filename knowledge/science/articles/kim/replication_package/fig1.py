import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "DejaVu Sans"})
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

TY, TH = 26, 12   # top row
BY, BH = 4, 12    # bottom row
W = 17.5
xs = [0, 20.5, 41, 61.5, 82]

box(xs[0], TY, W, TH, "Входные данные\n$X{=}\\{I_t,E_t,B_t,O,G,u\\}$", fc="0.92")
box(xs[1], TY, W, TH, "Показатели\nсостояния\n$CF_t,\\,R_t,\\,L_t,\\,D_t,\\,S_t$")
box(xs[2], TY, W, TH, "Прогноз потоков\nSES + Монте-Карло")
box(xs[3], TY, W, TH, "Генерация\nальтернатив\n(шаг 20 %)")
box(xs[4], TY, W, TH, "Фильтр ставок\nдосрочки\n$r_k \\geq r_{bench}$")

box(xs[4], BY, W, BH, "Фильтр\nдопустимости\n(каскад $D$, $L$, $R$)")
box(xs[3], BY, W, BH, "Нормативная\nнормализация\nкритериев")
box(xs[2], BY, W, BH, "Аддитивная свёртка\n$U(a)$ по профилю\nриска")
box(xs[1], BY, W, BH, "Выбор решения\n$a^*{=}\\arg\\max\\,U(a)$")
box(xs[0], BY, W, BH, "Рекомендация\nс объяснением", fc="0.92")

mid_t = TY + TH/2; mid_b = BY + BH/2
for i in range(4):
    arrow(xs[i] + W, mid_t, xs[i+1], mid_t)
arrow(xs[4] + W/2, TY, xs[4] + W/2, BY + BH)
for i in range(4, 0, -1):
    arrow(xs[i], mid_b, xs[i-1] + W, mid_b)
# прогноз -> свёртка (ключевая модификация)
arrow(xs[2] + W/2, TY, xs[2] + W/2, BY + BH, dashed=True)
ax.text(xs[2] + W/2 - 1.2, (TY + BY + BH)/2, "прогнозный критерий $\\hat{R}_{t+1}(a)$",
        fontsize=7.4, ha="right", va="center")
fig.savefig("fig1_pipeline.png", bbox_inches="tight")
print("ok")
