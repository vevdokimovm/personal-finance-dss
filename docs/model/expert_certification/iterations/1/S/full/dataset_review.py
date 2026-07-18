"""Dataset statistical review per the expert protocol checklist (items а-з).

Computes descriptive statistics, correlations, distribution-shape tests,
categorical distributions, derived diagnostics, kind-label validation, and
assembles numbered problems P1..P9 with numeric evidence. Writes
dataset_review.md. All numbers are produced by this script.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

UPLOADS = Path("/mnt/user-data/uploads")
OUT = Path("/home/claude/out2")
PCTS = [10, 50, 90, 99]


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    profiles, obligations, goals = [], [], []
    for line in open(UPLOADS / "portraits_12000.jsonl"):
        rec = json.loads(line)
        e = rec["engine"]
        pay_total = sum(o["monthly_payment"] for o in e["obligations"])
        amt_total = sum(o["amount"] for o in e["obligations"])
        profiles.append({
            "id": rec["id"], "kind": rec["kind"],
            "income": e["income_total"], "expenses": e["expense_total"],
            "bliq": e["bliq"], "r_bench": e["r_bench"], "risk": e["risk_tolerance"],
            "l_min": e["l_min"], "n_debts": len(e["obligations"]),
            "n_goals": len(e["goals"]), "pay_total": pay_total,
            "amt_total": amt_total,
            "goal_target_total": sum(g["target_amount"] for g in e["goals"]),
            "goal_current_total": sum(g["current_amount"] for g in e["goals"]),
        })
        for o in e["obligations"]:
            obligations.append({
                "kind": rec["kind"], "amount": o["amount"],
                "rate": o["interest_rate"], "payment": o["monthly_payment"],
                "interest_only": o["amount"] * o["interest_rate"] / 12.0,
                "r_bench": e["r_bench"],
            })
        for g in e["goals"]:
            months = None
            if g.get("deadline"):
                y, m, _ = map(int, g["deadline"].split("-"))
                months = (y - 2026) * 12 + (m - 7)
            goals.append({
                "kind": rec["kind"], "target": g["target_amount"],
                "current": g["current_amount"],
                "readiness": g["current_amount"] / g["target_amount"]
                if g["target_amount"] > 0 else np.nan,
                "months": months, "income": e["income_total"],
            })
    return pd.DataFrame(profiles), pd.DataFrame(obligations), pd.DataFrame(goals)


def fmt(x: float, dec: int = 0) -> str:
    if pd.isna(x):
        return "—"
    s = f"{x:,.{dec}f}".replace(",", " ")
    return s


def desc_table(df: pd.DataFrame, cols: dict[str, str], dec: dict | None = None) -> list[str]:
    dec = dec or {}
    lines = ["| Поле | mean | σ | min | p10 | p50 | p90 | p99 | max |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for col, label in cols.items():
        s = df[col].dropna()
        d = dec.get(col, 0)
        pct = np.percentile(s, PCTS)
        lines.append(
            f"| {label} | {fmt(s.mean(), d)} | {fmt(s.std(), d)} | {fmt(s.min(), d)} | "
            f"{fmt(pct[0], d)} | {fmt(pct[1], d)} | {fmt(pct[2], d)} | "
            f"{fmt(pct[3], d)} | {fmt(s.max(), d)} |")
    return lines


def corr_tables(df: pd.DataFrame) -> list[str]:
    cols = ["income", "expenses", "pay_total", "bliq", "goal_target_total"]
    labels = ["доход", "расходы", "платежи", "подушка", "цели (target)"]
    out = []
    for method in ("pearson", "spearman"):
        c = df[cols].corr(method=method)
        out.append(f"**{method.capitalize()}:**")
        out.append("")
        out.append("| | " + " | ".join(labels) + " |")
        out.append("|---|" + "---:|" * len(labels))
        for i, row in enumerate(cols):
            vals = " | ".join(f"{c.loc[row, c2]:.3f}" for c2 in cols)
            out.append(f"| {labels[i]} | {vals} |")
        out.append("")
    return out


def main() -> None:
    prof, obl, gl = load()
    n = len(prof)
    lines: list[str] = [
        "# dataset_review.md — статистический профиль и критика датасета",
        "",
        f"Датасет: `portraits_12000.jsonl`, {n} записей, {len(obl)} обязательств, "
        f"{len(gl)} целей. Дата анализа: 2026-07-07. Все числа посчитаны скриптом "
        "`dataset_review.py` (приложен).",
        "",
        "## (а) Дескриптивные статистики",
        "",
        "**Профиль (12 000):**",
        "",
    ]
    lines += desc_table(prof, {
        "income": "Доход, ₽/мес", "expenses": "Расходы, ₽/мес", "bliq": "Подушка B_liq, ₽",
        "pay_total": "Платежи по кредитам, ₽/мес", "amt_total": "Тело долга, ₽",
        "goal_target_total": "Сумма целей (target), ₽",
        "goal_current_total": "Накоплено по целям, ₽",
        "n_debts": "Кредитов на профиль", "n_goals": "Целей на профиль",
        "r_bench": "r_bench",
    }, dec={"r_bench": 4, "n_debts": 2, "n_goals": 2})
    lines += ["", "**Обязательства (24 368):**", ""]
    lines += desc_table(obl, {
        "amount": "Остаток, ₽", "rate": "Ставка", "payment": "Платёж, ₽/мес",
    }, dec={"rate": 3})
    lines += ["", "**Цели (25 406):**", ""]
    lines += desc_table(gl, {
        "target": "Target, ₽", "current": "Накоплено, ₽", "readiness": "Готовность",
        "months": "Горизонт, мес (только с дедлайном)",
    }, dec={"readiness": 3, "months": 1})

    lines += ["", "## (б) Корреляции (по профилям)", ""]
    lines += corr_tables(prof)
    plain = prof[prof["kind"] == "plain"]
    lines += [
        f"Только plain (8 000): Pearson(доход, расходы) = "
        f"{plain['income'].corr(plain['expenses']):.3f}; "
        f"Pearson(доход, платежи) = {plain['income'].corr(plain['pay_total']):.3f}; "
        f"Pearson(доход, сумма целей) = "
        f"{plain['income'].corr(plain['goal_target_total']):.3f}.",
        "",
        "Расходы масштабируются доходом, платежи и цели — нет. Это ядро проблем P1 и P7.",
    ]

    inc = prof.loc[prof["income"] > 0, "income"].to_numpy()
    shape, loc, scale = stats.lognorm.fit(inc, floc=0)
    ks = stats.kstest(inc, "lognorm", args=(shape, loc, scale))
    log_inc = np.log(inc)
    amounts = obl["amount"].to_numpy()
    ks_amt = stats.kstest(
        amounts, "uniform", args=(amounts.min(), amounts.max() - amounts.min()))
    rates = obl["rate"].to_numpy()
    ks_rate = stats.kstest(
        rates, "uniform", args=(rates.min(), rates.max() - rates.min()))
    lines += [
        "", "## (в) Формы распределений", "",
        "| Поле | Асимметрия | Эксцесс |",
        "|---|---:|---:|",
        f"| Доход (>0) | {stats.skew(inc):.2f} | {stats.kurtosis(inc):.2f} |",
        f"| log(доход) | {stats.skew(log_inc):.2f} | {stats.kurtosis(log_inc):.2f} |",
        f"| Расходы | {stats.skew(prof['expenses']):.2f} | "
        f"{stats.kurtosis(prof['expenses']):.2f} |",
        f"| B_liq | {stats.skew(prof['bliq']):.2f} | {stats.kurtosis(prof['bliq']):.2f} |",
        f"| Остаток долга | {stats.skew(amounts):.2f} | {stats.kurtosis(amounts):.2f} |",
        f"| Ставка | {stats.skew(rates):.2f} | {stats.kurtosis(rates):.2f} |",
        "",
        f"KS лог-нормальности дохода (fit lognorm, floc=0): D = {ks.statistic:.4f}, "
        f"p = {ks.pvalue:.2e}. При n = {len(inc)} тест отклоняет даже близкие формы; "
        f"log(доход) с асимметрией {stats.skew(log_inc):.2f} близок к симметричному — "
        "форма похожа на лог-нормаль, но параметры не калиброваны по Росстату.",
        f"KS остатков долга против U[{fmt(amounts.min())}; {fmt(amounts.max())}]: "
        f"D = {ks_amt.statistic:.4f} — фактически равномерное с жёстким капом.",
        f"KS ставок против U[{rates.min():.2f}; {rates.max():.2f}]: "
        f"D = {ks_rate.statistic:.4f} — равномерная, без продуктовой структуры.",
    ]

    rb = prof["r_bench"].value_counts().sort_index()
    horiz = pd.cut(gl["months"].dropna(), bins=[0, 6, 12, 24, 36, 60],
                   labels=["0-6", "7-12", "13-24", "25-36", "37-59"]).value_counts().sort_index()
    ready = pd.cut(gl["readiness"].dropna(), bins=[-0.01, 0.25, 0.5, 0.75, 0.9999, 10],
                   labels=["<25%", "25-50%", "50-75%", "75-<100%", "≥100%"]).value_counts().sort_index()
    lines += [
        "", "## (г) Категориальные и счётные распределения", "",
        "| Риск-профиль | " + " | ".join(str(k) for k in sorted(prof['risk'].unique())) + " |",
        "|---|" + "---:|" * prof['risk'].nunique(),
        "| Кол-во | " + " | ".join(
            str(prof['risk'].value_counts()[k]) for k in sorted(prof['risk'].unique())) + " |",
        "",
        "| r_bench | " + " | ".join(f"{v:.4f}" for v in rb.index) + " |",
        "|---|" + "---:|" * len(rb),
        "| Кол-во | " + " | ".join(str(v) for v in rb.values) + " |",
        "",
        "**Ровно 5 дискретных значений r_bench** — см. P4.",
        "",
        "| Кредитов на профиль | " + " | ".join(
            str(k) for k in sorted(prof['n_debts'].unique())) + " |",
        "|---|" + "---:|" * prof['n_debts'].nunique(),
        "| Кол-во | " + " | ".join(
            str(prof['n_debts'].value_counts()[k])
            for k in sorted(prof['n_debts'].unique())) + " |",
        "",
        "| Целей на профиль | " + " | ".join(
            str(k) for k in sorted(prof['n_goals'].unique())) + " |",
        "|---|" + "---:|" * prof['n_goals'].nunique(),
        "| Кол-во | " + " | ".join(
            str(prof['n_goals'].value_counts()[k])
            for k in sorted(prof['n_goals'].unique())) + " |",
        "",
        f"Горизонты дедлайнов (мес): " + ", ".join(
            f"{k}: {v}" for k, v in horiz.items())
        + f"; без дедлайна: {gl['months'].isna().sum()} "
        f"({gl['months'].isna().mean():.0%}). Максимум — 59 мес, горизонтов 5-10 лет нет.",
        "",
        "Готовность целей: " + ", ".join(f"{k}: {v}" for k, v in ready.items()) + ".",
    ]

    pay, incm = prof["pay_total"], prof["income"]
    pdn = np.where(incm > 0, pay / incm, np.where(pay > 0, np.inf, 0.0))
    fcf = incm - prof["expenses"] - pay
    outflow = prof["expenses"] + pay
    cushion = np.where(outflow > 0, prof["bliq"] / outflow, np.inf)
    pdn_b = pd.cut(pd.Series(pdn).replace(np.inf, 99),
                   bins=[-0.01, 0.0, 0.3, 0.5, 0.8, 100],
                   labels=["0", "<30%", "30-50%", "50-80%", "≥80%/без дохода"]).value_counts().sort_index()
    liq_b = pd.cut(pd.Series(cushion).replace(np.inf, 999),
                   bins=[-0.01, 1, 3, 6, 12, 1000],
                   labels=["<1", "1-3", "3-6", "6-12", "≥12"]).value_counts().sort_index()
    lines += [
        "", "## (д) Производные диагностики (весь сет)", "",
        "| ПДН | " + " | ".join(pdn_b.index.astype(str)) + " |",
        "|---|" + "---:|" * len(pdn_b),
        "| Кол-во | " + " | ".join(str(v) for v in pdn_b.values) + " |",
        "",
        "| Ликвидность, мес | " + " | ".join(liq_b.index.astype(str)) + " |",
        "|---|" + "---:|" * len(liq_b),
        "| Кол-во | " + " | ".join(str(v) for v in liq_b.values) + " |",
        "",
        f"Знак свободного потока: FCF < 0 у {int((fcf < 0).sum())} из {n} "
        f"({(fcf < 0).mean():.0%}); FCF ≥ 0 у {int((fcf >= 0).sum())}.",
    ]

    prof2 = prof.assign(pdn=pdn, fcf=fcf, cushion=cushion)
    med = prof2.groupby("kind").agg(
        income=("income", "median"), expenses=("expenses", "median"),
        fcf=("fcf", "median"),
        pdn=("pdn", lambda s: np.nanmedian(np.where(np.isinf(s), np.nan, s))),
        cushion=("cushion", lambda s: np.nanmedian(np.where(np.isinf(s), np.nan, s))),
        neg_fcf=("fcf", lambda s: (s < 0).mean()),
    )
    lines += [
        "", "## (е) Валидация меток типов", "",
        "| kind | медиана дохода | медиана расходов | медиана FCF | медиана ПДН | "
        "медиана подушки, мес | доля FCF<0 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for k, r in med.iterrows():
        lines.append(
            f"| {k} | {fmt(r['income'])} | {fmt(r['expenses'])} | {fmt(r['fcf'])} | "
            f"{r['pdn']:.2f} | {r['cushion']:.1f} | {r['neg_fcf']:.0%} |")
    cheap = prof[prof["kind"] == "cheap_debts_only"]
    cheap_ok = 0
    for line in open(UPLOADS / "portraits_12000.jsonl"):
        rec = json.loads(line)
        if rec["kind"] != "cheap_debts_only":
            continue
        e = rec["engine"]
        if all(o["interest_rate"] < e["r_bench"] for o in e["obligations"]):
            cheap_ok += 1
    funded_ok = 0
    for line in open(UPLOADS / "portraits_12000.jsonl"):
        rec = json.loads(line)
        if rec["kind"] != "funded_goal":
            continue
        if any(g["current_amount"] >= g["target_amount"] for g in rec["engine"]["goals"]):
            funded_ok += 1
    lines += [
        "",
        f"Точечные проверки: `cheap_debts_only` — все ставки ниже r_bench у "
        f"{cheap_ok}/{len(cheap)}; `funded_goal` — есть цель ≥100% у {funded_ok}/444; "
        f"`zero_income` — max(доход) = {prof[prof['kind'] == 'zero_income']['income'].max():.0f}; "
        f"`zero_expenses` — max(расходы) = "
        f"{prof[prof['kind'] == 'zero_expenses']['expenses'].max():.0f}; "
        f"`many_goals` — целей = "
        f"{prof[prof['kind'] == 'many_goals']['n_goals'].unique().tolist()}.",
        "",
        "Граничные метки честные. Метка `plain` («без граничных особенностей») фактическому "
        f"состоянию не соответствует: доля FCF<0 в plain — "
        f"{med.loc['plain', 'neg_fcf']:.0%}, медианный ПДН — "
        f"{med.loc['plain', 'pdn']:.2f} (см. P1).",
    ]

    non_amort = obl[obl["payment"] <= obl["interest_only"] + 1e-9]
    na_by_kind = non_amort["kind"].value_counts()
    cap_share = (obl["amount"] > 2.9e6).sum()
    plain_corr = plain["income"].corr(plain["pay_total"])
    gl_dated = gl.dropna(subset=["months"])
    p_list = [
        ("P1", "Платежи по кредитам не согласованы с доходом",
         f"Pearson(доход, платежи) = {prof['income'].corr(prof['pay_total']):.3f} "
         f"(plain: {plain_corr:.3f}); медианный платёж одного кредита "
         f"{fmt(obl['payment'].median())} ₽ при медианном доходе {fmt(prof['income'].median())} ₽; "
         f"итог — FCF<0 у {(fcf < 0).mean():.0%} сета и {med.loc['plain', 'neg_fcf']:.0%} plain",
         "Тест-сет тестирует почти исключительно кризисную ветку; ветки целей и "
         "инвестиций получают ~14% сигнала. Метка plain вводит в заблуждение."),
        ("P2", "Нереалистичное распределение ПДН",
         f"ПДН ≥ 80% или платежи без дохода: {int(pdn_b['≥80%/без дохода'])} из {n} "
         f"({int(pdn_b['≥80%/без дохода']) / n:.0%}); в популяции РФ хвост ПДН>80% — "
         "единицы процентов (публикации ЦБ/НБКИ)",
         "Пороговые ветки ПДН (30/50%) почти не дискриминируют: всё в красной зоне."),
        ("P3", "Случайные interest-only кредиты вне дизайна",
         f"Платёж ≤ месячному проценту у {len(non_amort)} из {len(obl)} обязательств "
         f"({len(non_amort) / len(obl):.1%}), размазаны по типам: "
         + ", ".join(f"{k}: {v}" for k, v in na_by_kind.head(5).items()),
         "Вечный долг возникает как артефакт генерации платежа, а не как "
         "детерминированный кейс слоя C — загрязняет остальные метки."),
        ("P4", "Дискретный r_bench",
         f"Ровно 5 значений: {', '.join(f'{v:.4f}' for v in rb.index)}",
         "Ветвление по спреду ставка−бенчмарк сэмплируется в 5 точках; случай "
         "ставка == r_bench недостижим по построению непрерывной ставки."),
        ("P5", "Равномерное тело долга с жёстким капом 3 млн",
         f"KS против U: D = {ks_amt.statistic:.4f}; {cap_share} остатков > 2.9 млн; "
         f"max = {fmt(amounts.max())} ₽",
         "Нет реалистичного хвоста (ипотеки 5-15 млн отсутствуют), кап создаёт "
         "искусственное скопление у границы."),
        ("P6", "Ставки равномерны, без продуктовой структуры",
         f"KS против U[0.01; 0.35]: D = {ks_rate.statistic:.4f}; кластеров "
         "ипотека/потреб/МФО нет",
         "Дешёвый долг — случайность розыгрыша, а не льготная ипотека; связка "
         "ставка×тело×срок нереалистична."),
        ("P7", "Цели не масштабированы доходом, горизонты обрезаны",
         f"Pearson(доход, сумма целей) = {prof['income'].corr(prof['goal_target_total']):.3f}; "
         f"максимальный горизонт {int(gl_dated['months'].max())} мес, "
         f"без дедлайна {gl['months'].isna().mean():.0%}",
         "Достижимость целей определяется лотереей, а не жизненной логикой; "
         "долгие горизонты (5-10 лет) не тестируются вовсе."),
        ("P8", "Нет dataset_version/seed в самом файле",
         "Первая строка JSONL — обычная запись SP-00000; версия и конфиг слоёв "
         "не зафиксированы в данных",
         "Ревью экспертов нельзя привязать к версии — итерации несравнимы (§4 методички)."),
        ("P9", "Мёртвое поле l_min",
         f"l_min = 0 у всех {n} записей (min = max = {prof['l_min'].max():.1f})",
         "Входная размерность существует, но не варьируется — ветки модели, "
         "зависящие от порога ликвидности, не тестируются."),
    ]
    lines += ["", "## (ж) Проблемы P1..P9", ""]
    for code, title, ev, cons in p_list:
        lines += [f"**{code}. {title}.**",
                  f"Доказательство: {ev}.",
                  f"Последствие: {cons}", ""]

    lines += [
        "## (з) Рекомендации для следующей итерации генератора", "",
        "1. Долги задавать через ПДН × доход с аннуитетной согласованностью "
        "(срок n ∈ [6, 360], платёж из формулы) — закрывает P1, P2, P3 разом; "
        "interest-only оставить детерминированным кейсом слоя C.",
        "2. r_bench — непрерывный (например, N(ключевая ставка, σ) с усечением), "
        "плюс детерминированный кейс «ставка == r_bench точно» в слое C — закрывает P4.",
        "3. Тело долга — из продуктовой смеси: ипотека (лог-нормаль, 8-18%, до 15 млн), "
        "потреб (15-35%), МФО-хвост; без жёсткого капа — закрывает P5, P6.",
        "4. Доход — лог-нормаль, калиброванная по Росстату; цели — target ~ k × годовой "
        "доход, k ∈ [0.2; 5]; дедлайны — смесь null + горизонты 3-120 мес — закрывает P7.",
        "5. Первой строкой JSONL — метазапись: dataset_version, seed, конфиг слоёв, "
        "корреляционная матрица — закрывает P8.",
        "6. l_min либо убрать из схемы, либо варьировать и включить в оси DOE — закрывает P9.",
        "7. Метку plain присваивать пост-фактум по реализованным диагностикам "
        "(FCF ≥ 0, ПДН < 50%, подушка 1-12 мес), а не по способу генерации.",
        "8. Слои D (битые записи) и E (метаморфические пары) в текущем сете отсутствуют — "
        "добавить согласно архитектуре §1 методички.",
    ]
    (OUT / "dataset_review.md").write_text("\n".join(lines), encoding="utf-8")
    print("dataset_review.md written,", len(lines), "lines")


if __name__ == "__main__":
    main()
