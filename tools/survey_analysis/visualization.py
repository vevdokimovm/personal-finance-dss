"""
Визуализация результатов: набор графиков (PNG) для HTML-отчёта.
Палитра сдержанная, шрифт с поддержкой кириллицы (DejaVu Sans).
"""
from __future__ import annotations

import os
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

INK = "#1e293b"
PRIMARY = "#2563eb"
TEAL = "#0d9488"
AMBER = "#f59e0b"
RED = "#dc2626"
GREY = "#94a3b8"
LIGHT = "#cbd5e1"

rcParams["font.family"] = "DejaVu Sans"
rcParams["font.size"] = 10
rcParams["axes.edgecolor"] = "#cbd5e1"
rcParams["axes.linewidth"] = 0.8
rcParams["figure.dpi"] = 110


class ChartMaker:
    def __init__(self, out_dir: str) -> None:
        self.out = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def _save(self, fig, name: str) -> str:
        path = os.path.join(self.out, name)
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return name

    @staticmethod
    def _despine(ax) -> None:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def generate_all(self, r: dict[str, Any]) -> dict[str, str]:
        charts = {}
        charts["bias"] = self.audience_bias(r["audience"]["bias"])
        charts["pain"] = self.hbar_multiselect(
            r["descriptive"]["multiselect"]["tool_lacks"],
            "Чего не умеет текущий инструмент", RED, "02a_pain.png")
        charts["must"] = self.hbar_multiselect(
            r["descriptive"]["multiselect"]["must_have"],
            "Что должно быть в инструменте", TEAL, "02b_must.png")
        charts["opportunity"] = self.opportunity(r["business"]["opportunity"])
        charts["hypotheses"] = self.hypotheses_forest(r["hypotheses"]["results"])
        charts["choice"] = self.choice_method(r["behavioral"]["stated_choice"])
        charts["gap"] = self.intention_action(r["behavioral"])
        charts["wtp"] = self.wtp(r["business"]["wtp"])
        charts["ai_trust"] = self.ai_trust(r["business"]["ai_trust"])
        charts["criteria"] = self.criteria_means(r["preferences"])
        charts["criteria_corr"] = self.criteria_corr(r["preferences"])
        charts["conf"] = self.confidence_hindsight(
            r["behavioral"]["confidence_vs_hindsight"])
        charts["qual"] = self.qualitative(r["qualitative"]["why_quit"])
        charts["rice"] = self.rice(r["business"]["feature_priority"])
        return charts

    # ── отдельные графики ───────────────────────────────────────────────
    def audience_bias(self, bias: list[dict]) -> str:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        labels = [f"{b['dimension']}: {b['label']}" for b in bias]
        shares = [b["share"] * 100 for b in bias]
        errs = [[(b["share"] - b["ci"][0]) * 100 for b in bias],
                [(b["ci"][1] - b["share"]) * 100 for b in bias]]
        colors = [RED if b["skewed"] else PRIMARY for b in bias]
        y = range(len(labels))
        ax.barh(list(y), shares, color=colors, xerr=errs,
                error_kw={"ecolor": INK, "capsize": 3, "lw": 1})
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels)
        ax.set_xlim(0, 100)
        ax.set_xlabel("% выборки (95% ДИ Уилсона)")
        ax.invert_yaxis()
        for i, s in enumerate(shares):
            ax.text(s + 2, i, f"{s:.0f}%", va="center", fontsize=9, color=INK)
        ax.set_title("Перекосы выборки: кто ответил", fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "01_bias.png")

    def hbar_multiselect(self, block: dict, title: str, color: str,
                         fname: str) -> str:
        items = block["items"][:7]
        fig, ax = plt.subplots(figsize=(7, 3.4))
        labels = [it["label"] for it in items][::-1]
        vals = [it["share"] * 100 for it in items][::-1]
        ax.barh(labels, vals, color=color)
        ax.set_xlabel(f"% (N={block['n']})")
        for i, v in enumerate(vals):
            ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=9, color=INK)
        ax.set_xlim(0, max(vals) * 1.18)
        ax.set_title(title, fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, fname)

    def opportunity(self, opp: list[dict]) -> str:
        fig, ax = plt.subplots(figsize=(7, 4.8))
        for o in opp:
            x, y = o["unmet_share"] * 100, o["want_share"] * 100
            ax.scatter(x, y, s=o["score"] * 1800, color=TEAL, alpha=0.55,
                       edgecolor=INK, linewidth=0.8, zorder=3)
            ax.annotate(o["opportunity"], (x, y), xytext=(0, 16),
                        textcoords="offset points", fontsize=8.5, color=INK,
                        ha="center", va="bottom", zorder=4)
        xs = [o["unmet_share"] * 100 for o in opp]
        ys = [o["want_share"] * 100 for o in opp]
        ax.set_xlim(min(xs) - 4, max(xs) + 4)
        ax.set_ylim(min(ys) - 5, max(ys) + 6)
        ax.set_xlabel("Неудовлетворённость, % (боль не закрыта)")
        ax.set_ylabel("Важность, % (хотят видеть)")
        ax.grid(True, ls=":", color=LIGHT, zorder=0)
        ax.set_title("Карта возможностей (важность × боль)",
                     fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "03_opportunity.png")

    def hypotheses_forest(self, results: list[dict]) -> str:
        fig, ax = plt.subplots(figsize=(7.4, 3.8))
        rows = results[::-1]
        labels = [f"{r['code']}  {r['effect_name']}" for r in rows]
        vals = [r["effect_value"] for r in rows]
        colors = [TEAL if r["significant_holm"] else GREY for r in rows]
        y = range(len(rows))
        ax.barh(list(y), vals, color=colors)
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels, fontsize=9)
        for i, (v, r) in enumerate(zip(vals, rows)):
            mark = "✓" if r["significant_holm"] else "—"
            ax.text(v + 0.01, i, f"{v:.2f} {mark}", va="center", fontsize=8.5,
                    color=INK)
        ax.axvspan(0, 0.1, color="#f1f5f9", zorder=0)
        ax.set_xlabel("Размер эффекта (|ρ| / V / r); ✓ — значимо после поправки Холма")
        ax.set_xlim(0, max(vals) * 1.25)
        ax.set_title("Проверка гипотез: сила связи", fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "04_hypotheses.png")

    def choice_method(self, stated: dict) -> str:
        dist = stated["distribution"]
        fig, ax = plt.subplots(figsize=(6.4, 3))
        labels = list(dist.keys())[::-1]
        vals = list(dist.values())[::-1]
        n = stated["n"]
        colors = [PRIMARY if "вручную" in l else AMBER if ("ощущению" in l or "лежат" in l)
                  else GREY for l in labels]
        ax.barh(labels, vals, color=colors)
        for i, v in enumerate(vals):
            ax.text(v + 1, i, f"{v} ({v/n*100:.0f}%)", va="center", fontsize=9, color=INK)
        ax.set_xlim(0, max(vals) * 1.22)
        ax.set_title("Как ГОВОРЯТ, что выбирают (заявленное)",
                     fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "05_choice.png")

    def intention_action(self, beh: dict) -> str:
        gap = beh["intention_action_gap"]
        basis = beh["case_basis"]["distribution"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.2),
                                       gridspec_kw={"width_ratios": [1, 1.3]})
        # слева — разрыв
        ax1.bar(["Заявляют\nрасчёт", "Реально\nрасчёт"],
                [gap["stated_manual_calc"] * 100, gap["revealed_calc"] * 100],
                color=[PRIMARY, RED])
        ax1.set_ylabel("%")
        ax1.set_ylim(0, 60)
        for i, v in enumerate([gap["stated_manual_calc"], gap["revealed_calc"]]):
            ax1.text(i, v * 100 + 1.5, f"{v*100:.0f}%", ha="center", fontsize=10,
                     fontweight="bold", color=INK)
        ax1.set_title("Intention–action gap", fontweight="bold", color=INK)
        self._despine(ax1)
        # справа — на что реально опирались
        labels = list(basis.keys())[::-1]
        vals = list(basis.values())[::-1]
        colors = [TEAL if "Расчёт" in l else RED if ("тревога" in l or "комфорт" in l)
                  else GREY for l in labels]
        ax2.barh(labels, vals, color=colors)
        ax2.set_title(f"На что опирались в кейсе (N={beh['case_basis']['n']}, предв.)",
                      fontweight="bold", color=INK, fontsize=10)
        for i, v in enumerate(vals):
            ax2.text(v + 0.1, i, str(v), va="center", fontsize=9, color=INK)
        ax2.set_xlim(0, max(vals) * 1.2)
        self._despine(ax2)
        return self._save(fig, "06_gap.png")

    def wtp(self, wtp: dict) -> str:
        dist = wtp["distribution"]
        order = ["До 200 ₽/мес", "200–500 ₽/мес", "500–1000 ₽/мес",
                 "Готов(а) заплатить разово (например 1500–3000 ₽)",
                 "Готов(а) платить процент от сэкономленного/заработанного"]
        short = {order[0]: "до 200/мес", order[1]: "200–500/мес",
                 order[2]: "500–1000/мес", order[3]: "разово 1.5–3k",
                 order[4]: "% от выгоды"}
        keys = [k for k in order if k in dist]
        vals = [dist[k] for k in keys]
        fig, ax = plt.subplots(figsize=(6.6, 3))
        colors = [RED, AMBER, TEAL, PRIMARY, GREY][:len(keys)]
        ax.bar([short[k] for k in keys], vals, color=colors)
        n = wtp["n"]
        for i, v in enumerate(vals):
            ax.text(i, v + 1, f"{v}\n{v/n*100:.0f}%", ha="center", fontsize=8.5,
                    color=INK)
        ax.set_ylim(0, max(vals) * 1.25)
        ax.set_title(f"Готовность платить (N={n})", fontweight="bold", color=INK)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right", fontsize=8.5)
        self._despine(ax)
        return self._save(fig, "07_wtp.png")

    def ai_trust(self, ai: dict) -> str:
        tasks = ai["tasks"]
        fig, ax = plt.subplots(figsize=(7, 3))
        labels = [t["task"] for t in tasks][::-1]
        vals = [t["yes_share"] * 100 for t in tasks][::-1]
        colors = [TEAL if v >= 50 else RED for v in vals]
        ax.barh(labels, vals, color=colors)
        for i, v in enumerate(vals):
            ax.text(v + 1.5, i, f"{v:.0f}%", va="center", fontsize=9, color=INK)
        ax.set_xlim(0, 100)
        ax.axvline(50, color=GREY, ls="--", lw=1)
        ax.set_xlabel(f'% ответивших «да» (N={ai["n"]}, предварительно)')
        ax.set_title("Доверие ИИ по задачам", fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "08_ai_trust.png")

    def criteria_means(self, pref: dict) -> str:
        means = pref["means"]
        fig, ax = plt.subplots(figsize=(6, 2.9))
        labels = list(means.keys())
        vals = list(means.values())
        ax.bar(labels, vals, color=[PRIMARY, TEAL, AMBER, "#8b5cf6"])
        ax.set_ylim(0, 5)
        ax.axhline(3, color=GREY, ls=":", lw=1)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.1, f"{v:.2f}", ha="center", fontsize=10,
                    fontweight="bold", color=INK)
        ax.set_ylabel("Средняя важность (1–5)")
        ax.set_title(f"Критерии распределения (N={pref['n_complete']}, предв.)",
                     fontweight="bold", color=INK, fontsize=10)
        self._despine(ax)
        return self._save(fig, "09_criteria.png")

    def criteria_corr(self, pref: dict) -> str:
        corr = pref["spearman_corr"]
        labels = list(corr.keys())
        mat = [[corr[r][c] for c in labels] for r in labels]
        fig, ax = plt.subplots(figsize=(4.6, 4))
        im = ax.imshow(mat, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8.5)
        ax.set_yticklabels(labels, fontsize=8.5)
        for i in range(len(labels)):
            for j in range(len(labels)):
                ax.text(j, i, f"{mat[i][j]:.2f}", ha="center", va="center",
                        fontsize=8.5,
                        color="white" if abs(mat[i][j]) > 0.5 else INK)
        ax.set_title("Корреляции критериев (Спирмен)", fontweight="bold",
                     color=INK, fontsize=10)
        fig.colorbar(im, fraction=0.046, pad=0.04)
        return self._save(fig, "10_criteria_corr.png")

    def confidence_hindsight(self, cvh: dict) -> str:
        if not cvh.get("available"):
            fig, ax = plt.subplots(figsize=(4, 2))
            ax.text(0.5, 0.5, "недостаточно данных", ha="center")
            ax.axis("off")
            return self._save(fig, "11_conf.png")
        fig, ax = plt.subplots(figsize=(4.6, 3))
        ax.bar(["В моменте", "Задним числом"],
               [cvh["confidence_mean"], cvh["hindsight_mean"]],
               color=[PRIMARY, AMBER])
        ax.set_ylim(0, 5)
        for i, v in enumerate([cvh["confidence_mean"], cvh["hindsight_mean"]]):
            ax.text(i, v + 0.1, f"{v:.2f}", ha="center", fontweight="bold",
                    fontsize=10, color=INK)
        ax.set_ylabel("Уверенность (1–5)")
        ax.set_title(f"Оценка решения падает\n(N={cvh['n']}, Wilcoxon p={cvh['wilcoxon_p']})",
                     fontweight="bold", color=INK, fontsize=10)
        self._despine(ax)
        return self._save(fig, "11_conf.png")

    def qualitative(self, wq: dict) -> str:
        themes = {"Не вижу пользы": wq["themes"]["no_value"],
                  "Всё ещё пользуюсь": wq["themes"]["still_using"],
                  "Не пробовал": wq["themes"]["never_tried"],
                  "Лень / муторно": wq["themes"]["too_tedious"],
                  "Только статистика": wq["themes"]["only_stats"]}
        fig, ax = plt.subplots(figsize=(6.4, 2.9))
        labels = list(themes.keys())[::-1]
        vals = list(themes.values())[::-1]
        colors = [RED if l in ("Не вижу пользы", "Только статистика") else GREY
                  for l in labels]
        ax.barh(labels, vals, color=colors)
        for i, v in enumerate(vals):
            ax.text(v + 1, i, str(v), va="center", fontsize=9, color=INK)
        ax.set_xlim(0, max(vals) * 1.18)
        ax.set_title(f"Почему забрасывают приложения (N={wq['n']})",
                     fontweight="bold", color=INK, fontsize=10)
        self._despine(ax)
        return self._save(fig, "12_qual.png")

    def rice(self, feats: list[dict]) -> str:
        fig, ax = plt.subplots(figsize=(7, 3))
        labels = [f["feature"] for f in feats][::-1]
        vals = [f["rice"] for f in feats][::-1]
        moscow = [f["moscow"] for f in feats][::-1]
        colors = [PRIMARY if m == "Must" else TEAL for m in moscow]
        ax.barh(labels, vals, color=colors)
        for i, (v, m) in enumerate(zip(vals, moscow)):
            ax.text(v + 0.02, i, f"{v:.2f} [{m}]", va="center", fontsize=8.5,
                    color=INK)
        ax.set_xlim(0, max(vals) * 1.3)
        ax.set_xlabel("RICE-балл (Reach × Impact / Effort)")
        ax.set_title("Приоритет фич", fontweight="bold", color=INK)
        self._despine(ax)
        return self._save(fig, "13_rice.png")
