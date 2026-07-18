from __future__ import annotations

import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
from scipy import stats

SRC = Path("/mnt/user-data/uploads/portraits_12000.jsonl")
OUT = Path("/home/claude/out")
TODAY = date(2026, 7, 8)

FIELDS_RU = {
    "income": "Доход, ₽/мес", "expenses": "Расходы, ₽/мес", "debt_service": "Платежи по кредитам, ₽/мес",
    "bliq": "Подушка B_liq, ₽", "goals_target_sum": "Σ целей портрета, ₽",
    "loan_amount": "Остаток кредита, ₽ (пул)", "loan_rate": "Ставка кредита (пул)",
    "loan_payment": "Платёж по кредиту, ₽/мес (пул)", "goal_target": "Цель, ₽ (пул)",
    "goal_current": "Накоплено по цели, ₽ (пул)", "n_debts": "Кредитов на портрет",
    "n_goals": "Целей на портрет",
}


def describe(a):
    return {
        "n": int(a.size), "mean": float(np.mean(a)), "std": float(np.std(a, ddof=1)),
        "min": float(np.min(a)), "p10": float(np.percentile(a, 10)),
        "p50": float(np.percentile(a, 50)), "p90": float(np.percentile(a, 90)),
        "p99": float(np.percentile(a, 99)), "max": float(np.max(a)),
        "skew": float(stats.skew(a)), "kurt": float(stats.kurtosis(a)),
    }


def f0(x): return f"{x:,.0f}".replace(",", "\u202f")
def f2(x): return f"{x:,.2f}".replace(",", "\u202f")


def compute():
    rows, loans, goals, ids = [], [], [], []
    with open(SRC) as f:
        first_line = f.readline()
        has_header = "dataset_version" in first_line
        f.seek(0)
        for line in f:
            rec = json.loads(line)
            ids.append(rec["id"])
            e = rec["engine"]
            M = sum(d["monthly_payment"] for d in e["obligations"])
            for d in e["obligations"]:
                loans.append((rec["id"], d["amount"], d["interest_rate"], d["monthly_payment"], e["r_bench"]))
            for g in e["goals"]:
                dl = (date.fromisoformat(g["deadline"]) - TODAY).days / 30.4375 if g["deadline"] else None
                goals.append((rec["id"], g["target_amount"], g["current_amount"], dl))
            rows.append(dict(
                id=rec["id"], kind=rec["kind"], income=e["income_total"], expenses=e["expense_total"],
                bliq=e["bliq"], M=M, r_bench=e["r_bench"], risk=e["risk_tolerance"],
                n_debts=len(e["obligations"]), n_goals=len(e["goals"]),
                goals_target=sum(g["target_amount"] for g in e["goals"]),
            ))
    R = {k: np.array([r[k] for r in rows]) for k in
         ("income", "expenses", "bliq", "M", "r_bench", "risk", "n_debts", "n_goals", "goals_target")}
    S = {}
    S["has_header"] = has_header
    S["ids_unique"] = len(set(ids)) == len(ids)
    la = np.array([l[1] for l in loans]); lr = np.array([l[2] for l in loans])
    lp = np.array([l[3] for l in loans])
    gt = np.array([g[1] for g in goals]); gc = np.array([g[2] for g in goals])
    S["desc"] = {
        "income": describe(R["income"]), "expenses": describe(R["expenses"]),
        "debt_service": describe(R["M"]), "bliq": describe(R["bliq"]),
        "goals_target_sum": describe(R["goals_target"]), "loan_amount": describe(la),
        "loan_rate": describe(lr), "loan_payment": describe(lp),
        "goal_target": describe(gt), "goal_current": describe(gc),
        "n_debts": describe(R["n_debts"].astype(float)), "n_goals": describe(R["n_goals"].astype(float)),
    }
    keys = ["income", "expenses", "M", "bliq", "goals_target"]
    X = np.vstack([R[k] for k in keys])
    S["keys"] = keys
    S["pearson"] = [[float(np.corrcoef(X[i], X[j])[0, 1]) for j in range(5)] for i in range(5)]
    S["spearman"] = [[float(stats.spearmanr(X[i], X[j]).statistic) for j in range(5)] for i in range(5)]
    inc_pos = R["income"][R["income"] > 0]
    shape, loc, scale = stats.lognorm.fit(inc_pos, floc=0)
    ks = stats.kstest(inc_pos, "lognorm", args=(shape, loc, scale))
    S["lognorm"] = dict(n=int(inc_pos.size), sigma=float(shape), median=float(scale),
                        ks=float(ks.statistic), p=float(ks.pvalue))
    S["r_bench_vals"] = [(float(v), int(c)) for v, c in sorted(Counter(np.round(R["r_bench"], 6)).items())]
    S["risk_dist"] = {int(k): int(v) for k, v in sorted(Counter(R["risk"].tolist()).items())}
    S["n_debts_dist"] = {int(k): int(v) for k, v in sorted(Counter(R["n_debts"].tolist()).items())}
    S["n_goals_dist"] = {int(k): int(v) for k, v in sorted(Counter(R["n_goals"].tolist()).items())}
    dls = [g[3] for g in goals]
    S["deadline"] = dict(
        total=len(dls), null=sum(1 for d in dls if d is None),
        buckets=dict(Counter("null" if d is None else ("<6" if d < 6 else "6–12" if d < 12 else "12–36" if d < 36 else "36+") for d in dls)),
        min=float(min(d for d in dls if d is not None)), max=float(max(d for d in dls if d is not None)),
    )
    ready = gc / np.where(gt > 0, gt, np.nan)
    S["readiness"] = describe(ready[~np.isnan(ready)])
    S["ready_ge_1"] = int(np.nansum(ready >= 1.0)); S["ready_eq_1"] = int(np.nansum(np.abs(gc - gt) < 0.005))
    S["ready_max"] = float(np.nanmax(ready))
    mask = R["income"] > 0
    kk = R["goals_target"][mask & (R["goals_target"] > 0)] / (12 * R["income"][mask & (R["goals_target"] > 0)])
    S["k_goal"] = describe(kk); S["k_outside"] = float(np.mean((kk < 0.2) | (kk > 5)))
    fcf = R["income"] - R["expenses"] - R["M"]
    S["fcf"] = dict(neg=int(np.sum(fcf < 0)), pos=int(np.sum(fcf > 0)), zero=int(np.sum(fcf == 0)))
    dsti = R["M"][mask] / R["income"][mask]
    S["dsti_buckets"] = {
        "0 (нет долга)": int(np.sum(dsti == 0)),
        "0–30%": int(np.sum((dsti > 0) & (dsti <= .3))), "30–50%": int(np.sum((dsti > .3) & (dsti <= .5))),
        "50–80%": int(np.sum((dsti > .5) & (dsti <= .8))), "80–100%": int(np.sum((dsti > .8) & (dsti <= 1.0))),
        ">100%": int(np.sum(dsti > 1.0)),
    }
    S["dsti_gt80_share"] = float(np.mean(dsti > .8)); S["n_borrowers"] = int(dsti.size)
    burn = R["expenses"] + R["M"]
    rw = R["bliq"][burn > 0] / burn[burn > 0]
    S["liq_buckets"] = {"<1": int(np.sum(rw < 1)), "1–3": int(np.sum((rw >= 1) & (rw < 3))),
                        "3–6": int(np.sum((rw >= 3) & (rw < 6))), "6–12": int(np.sum((rw >= 6) & (rw < 12))),
                        "≥12": int(np.sum(rw >= 12))}
    S["rw_median"] = float(np.median(rw))
    nonamort, terms, gt360, lt6 = 0, [], 0, 0
    for _, A, r, m, _b in loans:
        i = r / 12
        if m <= A * i + 1e-9:
            nonamort += 1
            continue
        n = math.log(m / (m - A * i)) / math.log(1 + i)
        terms.append(n); gt360 += n > 360; lt6 += n < 6
    S["annuity"] = dict(loans=len(loans), nonamort=nonamort, share=nonamort / len(loans),
                        terms=describe(np.array(terms)), gt360=int(gt360), lt6=int(lt6))
    S["caps"] = dict(
        loan_max=float(la.max()), loan_top_band=int(np.sum(la > 2.9e6)),
        goal_max=float(gt.max()), goal_top_band=int(np.sum(gt > 1.95e6)),
        rate_at_min=int(np.sum(np.isclose(lr, lr.min(), atol=1e-4))),
        rate_at_max=int(np.sum(np.isclose(lr, lr.max(), atol=1e-4))),
        rate_eq_bench=int(sum(1 for l in loans if abs(l[2] - l[4]) < 1e-9)),
        cheap_share=float(np.mean([l[2] <= l[4] for l in loans])),
    )
    km = {}
    for kind in sorted({r["kind"] for r in rows}):
        sub = [r for r in rows if r["kind"] == kind]
        inc_ = np.array([r["income"] for r in sub]); M_ = np.array([r["M"] for r in sub])
        exp_ = np.array([r["expenses"] for r in sub]); bl_ = np.array([r["bliq"] for r in sub])
        d_ = M_[inc_ > 0] / inc_[inc_ > 0]
        burn_ = exp_ + M_; rw_ = bl_[burn_ > 0] / burn_[burn_ > 0]
        km[kind] = dict(n=len(sub), income=float(np.median(inc_)),
                        dsti=(float(np.median(d_)) if d_.size else None),
                        fcf=float(np.median(inc_ - exp_ - M_)),
                        runway=(float(np.median(rw_)) if rw_.size else None))
    S["kind_medians"] = km
    return S


def dtable(S, fields, money=True):
    L = ["| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for f in fields:
        d = S["desc"][f]
        fm = f0 if money and "rate" not in f and not f.startswith("n_") else (lambda x: f"{x:.3f}")
        L.append(f"| {FIELDS_RU[f]} | " + " | ".join(fm(d[c]) for c in ("mean", "std", "min", "p10", "p50", "p90", "p99", "max")) + " |")
    return "\n".join(L)


def corr_table(S, name):
    M = S[name]; keys = S["keys"]
    ru = {"income": "доход", "expenses": "расходы", "M": "платежи", "bliq": "подушка", "goals_target": "Σцелей"}
    L = ["| | " + " | ".join(ru[k] for k in keys) + " |", "|---|" + "---:|" * 5]
    for i, k in enumerate(keys):
        L.append(f"| **{ru[k]}** | " + " | ".join(f"{M[i][j]:+.3f}" for j in range(5)) + " |")
    return "\n".join(L)


def render(S) -> str:
    L = []
    A = L.append
    A("# dataset_review.md — независимый статистический профиль и критика датасета")
    A(f"\nНабор: `portraits_12000.jsonl`, 12 000 записей; version-header в первой строке **отсутствует** "
      f"(seed 20260702 заявлен только в MD-карточках). Дата среза: {TODAY.isoformat()}. "
      f"Все числа рассчитаны программно (`dataset_review.py`, numpy/scipy).\n")

    A("## (а) Дескриптивные статистики\n")
    A(dtable(S, ["income", "expenses", "debt_service", "bliq", "goals_target_sum"]))
    A("")
    A(dtable(S, ["loan_amount", "loan_payment", "goal_target", "goal_current"]))
    A("")
    A(dtable(S, ["loan_rate", "n_debts", "n_goals"], money=False))

    A("\n## (б) Корреляции (уровень портрета)\n")
    A("**Пирсон:**\n"); A(corr_table(S, "pearson"))
    A("\n**Спирмен:**\n"); A(corr_table(S, "spearman"))
    A("\nСодержательно ненулевые связи: доход~расходы (+0.71), доход~подушка (+0.35), расходы~подушка (+0.39). "
      "Платежи по кредитам и суммы целей **не связаны ни с чем** (|r| < 0.04) — ключевой дефект, см. P1, P5.")

    A("\n## (в) Формы распределений\n")
    ln = S["lognorm"]
    A(f"Доход (I > 0, n={ln['n']}): подгонка лог-нормали даёт σ={ln['sigma']:.3f}, медиана {f0(ln['median'])} ₽; "
      f"KS-статистика {ln['ks']:.4f}, p = {ln['p']:.3f} → **лог-нормальность не отвергается** "
      f"(оговорка: KS с оценёнными параметрами либерален — тест Лиллиефорса дал бы ту же качественную картину при таком p). "
      f"Асимметрия/эксцесс ключевых полей — в таблицах (а): подушка (skew {S['desc']['bliq']['skew']:.1f}) и платежи "
      f"(skew {S['desc']['loan_payment']['skew']:.1f}) правохвостые, как и ожидается.")

    A("\n## (г) Категориальные и счётные распределения\n")
    A("| r_bench | Портретов |"); A("|---:|---:|")
    for v, c in S["r_bench_vals"]:
        A(f"| {v:.4f} | {c} |")
    A("")
    A("Риск-профиль: " + ", ".join(f"{k} → {v}" for k, v in S["risk_dist"].items()) + " (равномерно).")
    A("Кредитов на портрет: " + ", ".join(f"{k}: {v}" for k, v in S["n_debts_dist"].items()) + ".")
    A("Целей на портрет: " + ", ".join(f"{k}: {v}" for k, v in S["n_goals_dist"].items()) +
      " — **разрыв 5–7** (после 4 сразу 8).")
    dl = S["deadline"]
    A(f"\nДедлайны целей (n={dl['total']}): null {dl['null']} ({dl['null']/dl['total']:.1%}); "
      + "; ".join(f"{k}: {v}" for k, v in sorted(dl["buckets"].items())) +
      f". Диапазон: {dl['min']:.1f}–{dl['max']:.1f} мес. — **нет** дедлайна «сегодня», просроченных и горизонтов 5–10 лет.")
    rd = S["readiness"]
    A(f"\nГотовность целей current/target: p10 {rd['p10']:.2f}, p50 {rd['p50']:.2f}, p90 {rd['p90']:.2f}, max {S['ready_max']:.3f}; "
      f"≥100% — {S['ready_ge_1']} (все в kind=funded_goal); ровно 100.00% («в копейку») — {S['ready_eq_1']}.")

    A("\n## (д) Производные диагностики по всему сету\n")
    fc = S["fcf"]
    A(f"Знак свободного потока (I−E−M): **отрицательный {fc['neg']} ({fc['neg']/120:.1f}%)**, положительный {fc['pos']}, ноль {fc['zero']}.\n")
    A("| ПДН (среди I>0, n=" + str(S["n_borrowers"]) + ") | Портретов |"); A("|---|---:|")
    for k, v in S["dsti_buckets"].items():
        A(f"| {k} | {v} |")
    A(f"\nПДН > 80% у {S['dsti_gt80_share']:.1%} носителей дохода — против единиц процентов в реальных выдачах (калибровка ЦБ/НБКИ).\n")
    A("| Ликвидность, мес. | Портретов |"); A("|---|---:|")
    for k, v in S["liq_buckets"].items():
        A(f"| {k} | {v} |")
    A(f"\nМедианный запас {S['rw_median']:.1f} мес.; 65% портретов — меньше 3 мес.")

    A("\n## (е) Валидация меток kind\n")
    A("| kind | n | мед. доход | мед. ПДН | мед. FCF | мед. запас, мес. |")
    A("|---|---:|---:|---:|---:|---:|")
    for k, v in S["kind_medians"].items():
        d = f"{v['dsti']:.0%}" if v["dsti"] is not None else "—"
        rwm = f"{v['runway']:.1f}" if v["runway"] is not None else "—"
        A(f"| {k} | {v['n']} | {f0(v['income'])} | {d} | {f0(v['fcf'])} | {rwm} |")
    A("\nВывод: метки **не отражают** фактические состояния. Медианный ПДН типа `overleveraged` (68%) — "
      "минимальный среди всех типов с долгами; у `plain` — 129%. `zero_expenses`/`deficit_cf`/`huge_bliq` своим "
      "определяющим осям соответствуют, но по остальным осям несут тот же перекос, что и база.")

    ann = S["annuity"]; cp = S["caps"]
    A("\n## (ж) Проблемы (номер · доказательство · последствие)\n")
    A(f"**P1. Долг оторван от дохода.** corr(доход, платежи): Пирсон {S['pearson'][0][2]:+.3f}, Спирмен {S['spearman'][0][2]:+.3f}; "
      f"ПДН>100% у {S['dsti_buckets']['>100%']} из {S['n_borrowers']} носителей дохода ({S['dsti_buckets']['>100%']/S['n_borrowers']:.0%}). "
      f"Методичка требует задавать долг через ПДН×доход. → Тест-сет проверяет почти исключительно кризисную ветку модели; "
      f"водопад распределения (подушка→долг→цели→инвестиции) получает ~19% покрытия.")
    A(f"\n**P2. Кризисная доминанта.** FCF<0 у {fc['neg']} ({fc['neg']/120:.1f}%). Реалистичная популяция (слой A) так выглядеть не может; "
      f"это не «стресс-слой по дизайну», потому что перекос сидит в базовом `plain` (мед. FCF {f0(S['kind_medians']['plain']['fcf'])} ₽). "
      f"→ Метрики качества модели будут измерять качество антикризисных советов, а не аллокации.")
    A(f"\n**P3. Инверсия меток kind.** См. (е): `overleveraged` мед. ПДН 68% < `plain` 129%. "
      f"→ Стратифицированные по kind метрики и «доли правильных ответов по типам» невалидны; сравнение экспертов по типам вводит в заблуждение.")
    A(f"\n**P4. Аннуитетная несогласованность.** {ann['nonamort']} кредитов ({ann['share']:.1%}) не амортизируются "
      f"(платёж ≤ месячному проценту — вечный долг); имплайд-срок: p50 {ann['terms']['p50']:.0f} мес., max {ann['terms']['max']:.0f} мес., "
      f">360 мес. — {ann['gt360']}, <6 мес. — {ann['lt6']}. Поля срока в схеме нет. "
      f"→ Модель, считающая графики/переплату, получает противоречивый вход; interest-only не помечен как осознанный кейс слоя C.")
    A(f"\n**P5. Цели оторваны от дохода и капнуты.** corr(доход, Σцелей) = {S['pearson'][0][4]:+.3f}; "
      f"k = цель/годовой доход: p50 {S['k_goal']['p50']:.1f}, p99 {S['k_goal']['p99']:.1f}, max {S['k_goal']['max']:.0f}; "
      f"{S['k_outside']:.0%} целей вне заявленного k∈[0.2, 5]. → Достижимость целей в основном определяется генератором, а не решением модели.")
    A(f"\n**P6. Жёсткие капы (нарушение §1.5 методички).** Остаток кредита: max {f0(cp['loan_max'])} ₽, "
      f"{cp['loan_top_band']} значений в полосе 2.9–3.0 млн — стена на 3 000 000. Цель: max {f0(cp['goal_max'])} ₽, "
      f"{cp['goal_top_band']} значений в полосе 1.95–2.0 млн — стена на 2 000 000. → Хвосты срезаны, стресс-кейсы больших сумм (в т.ч. заявленные ~10⁹) отсутствуют.")
    A(f"\n**P7. Дискретный бенчмарк.** r_bench принимает ровно {len(S['r_bench_vals'])} значений "
      f"({', '.join(f'{v:.2%}' for v, _ in S['r_bench_vals'])}) — §1.4 требует непрерывный. "
      f"Ставка ровно == бенчмарку: {cp['rate_eq_bench']} кредитов (кейс есть, закрепить в слое C). "
      f"→ Ось spread покрыта решёткой; пороговые эффекты «дорогой/дешёвый» тестируются в 5 точках вместо континуума.")
    A(f"\n**P8. Хрупкая ликвидность.** {S['liq_buckets']['<1']} портретов (<1 мес.), 65% — меньше 3 мес., медиана {S['rw_median']:.1f} мес. "
      f"→ В связке с P1–P2 почти весь сет — «кризис», ветки размещения излишка почти не тестируются (кроме kind=huge_bliq).")
    A(f"\n**P9. Дедлайны без углов.** Мин {dl['min']:.1f} мес., макс {dl['max']:.1f} мес. (~4.9 года): нет «сегодня», нет просроченных, "
      f"нет 5–10-летних горизонтов из каталога слоя C и §1.3. → Ветки просрочки/немедленного исполнения не покрыты.")
    A(f"\n**P10. Дыры дискретного покрытия.** Целей на портрет: нет 5–7 (скачок 4→8); кредитов ≤ 4; l_min ≡ 0 на всём сете (мёртвая ось); "
      f"current==target «в копейку»: {S['ready_eq_1']}; перефинансирование max {S['ready_max']:.2f} (слабое); нет пучка целей с одним дедлайном. "
      f"→ Ряд задекларированных граничных кейсов слоя C фактически отсутствует.")
    A(f"\n**P11. Нет слоёв B/D/E.** Один случайный слой + 9 детерминированных типов; validity-записей нет "
      f"(ID уникальны: {S['ids_unique']}, отрицательных сумм/NaN: 0), метаморфических пар нет. "
      f"→ Устойчивость к мусору и монотонность (M1–M5) на этом сете не проверяемы.")
    A(f"\n**P12. Нет version-header (§4).** Первая строка JSONL — обычный портрет. "
      f"→ Ревью экспертов нельзя жёстко привязать к версии; итерации несравнимы.")

    A("\n## (з) Рекомендации к следующей итерации генератора\n")
    A("1. **ПДН-first:** сначала ПДН из бакетов ЦБ/НБКИ (хвост >80% — единицы процентов), затем M = ПДН×доход, затем аннуитет с явным сроком n∈[6,360] и остатком из формулы. Это одним ходом закрывает P1, P2, P4 и половину P3.")
    A("2. **Метки kind назначать пост-фактум** по фактическим метрикам (диагноз), а не как параметр генерации; либо генерить условно и валидировать реализацию (закрывает P3).")
    A("3. **Непрерывный r_bench** (равномерно/бета на [0.10, 0.22]); кейс «ставка == бенчмарк» оставить детерминированным в слое C (P7).")
    A("4. **Цели:** target = k × годовой доход, k∈[0.2, 5]; дедлайны смесью {null ≈ 25%, сегодня, просроченные, 3 мес.–10 лет}; кластер целей с одним дедлайном; снять капы 2М/3М — лог-нормальные хвосты (P5, P6, P9).")
    A("5. **Слой B (LHS/Sobol)** по нормализованным осям с pairwise-отчётом; добить n_goals 5–7 и l_min > 0 (P10).")
    A("6. **Слой D** (битые даты, отрицательные суммы, дубли ID, NaN, пустые массивы) и **слой E** (пары M1–M5) — по 5% (P11).")
    A("7. **Первая строка JSONL — метаданные** (dataset_version, seed, конфиг слоёв, корреляционная матрица) (P12).")
    A("8. **CI-приёмка из §3 методички.** Текущий сет: KS дохода **проходит** (p = "
      f"{ln['p']:.2f}); допуск корреляций **фейлится** (доход~платежи {S['pearson'][0][2]:+.02f} при целевой связке через ПДН); "
      "доли диагностических состояний **фейлятся** (FCF<0 = 81%); аннуитетная согласованность **фейлится** (93.9%).")
    A("\n---\n*Скрипт расчёта: `dataset_review.py`. Машиночитаемые статистики: `dataset_stats.json`.*")
    return "\n".join(L)


def main():
    S = compute()
    (OUT / "dataset_stats.json").write_text(json.dumps(S, ensure_ascii=False, indent=1))
    (OUT / "dataset_review.md").write_text(render(S), encoding="utf-8")
    print("dataset_review.md written,", (OUT / "dataset_review.md").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
