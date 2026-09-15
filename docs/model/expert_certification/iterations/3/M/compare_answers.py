#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_answers.py — сверка CSV-ответов сравниваемого решения ("кандидата")
с эталонным CSV независимого эксперта на портретах v3.

Вход:
  --portraits  4 файла expert_portraits_v3_part*.jsonl.gz (для признаков и аудита)
  --reference  эталонный CSV эксперта (id,status,dom,res,debt,goal,inv,lump)
  --candidate  CSV кандидата в том же формате (одна строка на входную строку,
               в порядке входа; дубликаты id — обе строки)
  --out        каталог для отчёта

Выход в --out:
  comparison_report.md   — человекочитаемый отчёт
  comparison_metrics.json — все числа машинно
  worst_mismatches.csv   — топ-200 худших расхождений для разбора

Самопроверка:
  python3 compare_answers.py --portraits ... --reference ... --selftest --out DIR
  (identity-прогон 100% + посаженные возмущения с точным пересчётом)

Только stdlib, детерминированно.
"""
import argparse, csv, gzip, json, math, os, random, re, sys, time
from collections import Counter, defaultdict, deque
from datetime import date

ASOF = date(2026, 7, 16)
STATUSES = ("ok", "deficit", "invalid")
DOMS = ("debt", "reserve", "goals+", "none")
AMT_COLS = ("res", "debt", "goal", "inv", "lump")
HDR = ["id", "status", "dom", "res", "debt", "goal", "inv", "lump"]
ID_RE = re.compile(r'"id"\s*:\s*"([^"]*)"')
TOX_ABS, TOX_SPREAD = 0.25, 0.10
EPS = 0.5          # допуск сравнения/инвариантов, ₽
TOP_WORST = 200

# ---------------------------------------------------------------- валидатор
# Копия валидатора эксперта (process_v3.py) — критерии invalid идентичны.

def num_chk(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None, "type"
    if not math.isfinite(x):
        return None, "nan"
    if x < 0:
        return None, "neg"
    return float(x), None


def validate(rec):
    if not isinstance(rec, dict):
        return None, "not_object"
    for k in ("id", "income_total", "expense_total", "obligations", "goals",
              "bliq", "r_bench", "risk_tolerance"):
        if k not in rec:
            return None, f"missing:{k}"
    if not isinstance(rec["id"], str) or not rec["id"]:
        return None, "type:id"
    vals = {}
    for k in ("income_total", "expense_total", "bliq", "r_bench"):
        v, err = num_chk(rec[k])
        if err:
            return None, f"{err}:{k}"
        vals[k] = v
    rt = rec["risk_tolerance"]
    if isinstance(rt, bool):
        return None, "type:risk_tolerance"
    if isinstance(rt, float) and rt.is_integer():
        rt = int(rt)
    if not isinstance(rt, int):
        return None, "type:risk_tolerance"
    if not (1 <= rt <= 5):
        return None, "domain:risk_tolerance"
    if not isinstance(rec["obligations"], list):
        return None, "type:obligations"
    if not isinstance(rec["goals"], list):
        return None, "type:goals"
    O = []
    for o in rec["obligations"]:
        if not isinstance(o, dict):
            return None, "type:obligation"
        for k in ("name", "amount", "interest_rate", "monthly_payment"):
            if k not in o:
                return None, f"missing:obligation.{k}"
        if not isinstance(o["name"], str):
            return None, "type:obligation.name"
        a, e1 = num_chk(o["amount"])
        r, e2 = num_chk(o["interest_rate"])
        p, e3 = num_chk(o["monthly_payment"])
        for e, f in ((e1, "amount"), (e2, "interest_rate"), (e3, "monthly_payment")):
            if e:
                return None, f"{e}:obligation.{f}"
        O.append({"name": o["name"], "a": a, "r": r, "p": p})
    G = []
    for g in rec["goals"]:
        if not isinstance(g, dict):
            return None, "type:goal"
        for k in ("name", "target_amount", "current_amount", "deadline"):
            if k not in g:
                return None, f"missing:goal.{k}"
        if not isinstance(g["name"], str):
            return None, "type:goal.name"
        t, e1 = num_chk(g["target_amount"])
        c, e2 = num_chk(g["current_amount"])
        for e, f in ((e1, "target_amount"), (e2, "current_amount")):
            if e:
                return None, f"{e}:goal.{f}"
        d = g["deadline"]
        if d is not None:
            if not isinstance(d, str):
                return None, "type:goal.deadline"
            try:
                date.fromisoformat(d)
            except ValueError:
                return None, "date:goal.deadline"
        G.append(None)
    return {"id": rec["id"], "inc": vals["income_total"], "exp": vals["expense_total"],
            "bliq": vals["bliq"], "rb": vals["r_bench"], "rt": rt, "O": O,
            "n_goal": len(G)}, None


# ---------------------------------------------------------------- загрузка

def load_portraits(paths):
    """Список по строкам данных: {'id','valid','feat'|None}. Мета-строки пропускаются."""
    out = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    m = ID_RE.search(line)
                    out.append({"id": m.group(1) if m else "", "valid": False, "feat": None})
                    continue
                if ln == 1 and isinstance(rec, dict) and rec.get("__meta__") is True:
                    continue
                rid = str(rec.get("id", "")) if isinstance(rec, dict) else ""
                v, _ = validate(rec)
                if v is None:
                    out.append({"id": rid, "valid": False, "feat": None})
                    continue
                pay = sum(o["p"] for o in v["O"])
                fcf = v["inc"] - v["exp"] - pay
                tox_thr = max(TOX_ABS, v["rb"] + TOX_SPREAD)
                out.append({"id": v["id"], "valid": True, "feat": {
                    "inc": v["inc"], "fcf": fcf, "bliq": v["bliq"], "rt": v["rt"],
                    "pdn": (pay / v["inc"]) if v["inc"] > 0 else None,
                    "has_tox": any(o["a"] > 0 and o["r"] >= tox_thr for o in v["O"]),
                }})
    return out


def load_answers(path, label):
    rows, problems = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        try:
            header = [h.strip() for h in next(rd)]
        except StopIteration:
            return [], [f"{label}: пустой файл"]
        if header != HDR:
            problems.append(f"{label}: шапка {header} != {HDR}")
        for i, r in enumerate(rd):
            if len(r) != 8:
                problems.append(f"{label}: строка {i + 2}: {len(r)} полей вместо 8")
                r = (r + [""] * 8)[:8]
            st, dom = r[1].strip(), r[2].strip()
            if st not in STATUSES:
                problems.append(f"{label}: строка {i + 2}: status вне словаря: {st!r}")
            if dom not in DOMS:
                problems.append(f"{label}: строка {i + 2}: dom вне словаря: {dom!r}")
            amts = []
            for c, x in zip(AMT_COLS, r[3:8]):
                try:
                    amts.append(float(x))
                except ValueError:
                    problems.append(f"{label}: строка {i + 2}: {c} не число: {x!r}")
                    amts.append(math.nan)
            rows.append({"id": r[0].strip(), "st": st, "dom": dom,
                         "a": dict(zip(AMT_COLS, amts))})
    return rows, problems


def align(ref, cand):
    """[(ref_row, cand_row, idx_ref)], режим, missing, extra."""
    if len(ref) == len(cand) and all(a["id"] == b["id"] for a, b in zip(ref, cand)):
        return [(r, c, i) for i, (r, c) in enumerate(zip(ref, cand))], "positional", 0, 0
    pool = defaultdict(deque)
    for c in cand:
        pool[c["id"]].append(c)
    pairs, missing = [], 0
    for i, r in enumerate(ref):
        q = pool.get(r["id"])
        if q:
            pairs.append((r, q.popleft(), i))
        else:
            missing += 1
    extra = sum(len(q) for q in pool.values())
    return pairs, "id-join", missing, extra


# ---------------------------------------------------------------- статистика

def med(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def pctl(xs, p):
    if not xs:
        return None
    s = sorted(xs)
    k = (len(s) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] if lo == hi else s[lo] + (s[hi] - s[lo]) * (k - lo)


def compute(pairs, portraits):
    m = {}
    st_conf = Counter()
    dom_conf = Counter()
    st_match = dom_pairs = dom_match = 0
    amt = {c: {"d": [], "n_cmp": 0, "exact": 0, "w1": 0, "w100": 0,
               "sum_ref": 0.0, "sum_cand": 0.0, "rel": []} for c in AMT_COLS}
    row_detail = []          # (idx_ref, id, st_mism, dom_mism, dmap, total_abs)
    full_exact = 0
    n_amt_rows = 0

    for r, c, i in pairs:
        st_r = r["st"] if r["st"] in STATUSES else "other"
        st_c = c["st"] if c["st"] in STATUSES else "other"
        st_conf[(st_r, st_c)] += 1
        s_ok = st_r == st_c
        st_match += s_ok

        both_val = r["st"] != "invalid" and c["st"] != "invalid"
        d_ok = True
        if both_val:
            dom_pairs += 1
            dom_r = r["dom"] if r["dom"] in DOMS else "other"
            dom_c = c["dom"] if c["dom"] in DOMS else "other"
            dom_conf[(dom_r, dom_c)] += 1
            d_ok = dom_r == dom_c
            dom_match += d_ok

        dmap, total_abs = {}, 0.0
        if both_val:
            n_amt_rows += 1
            for col in AMT_COLS:
                rv, cv = r["a"][col], c["a"][col]
                if math.isnan(rv) or math.isnan(cv):
                    dmap[col] = math.nan
                    continue
                d = cv - rv
                a = amt[col]
                a["d"].append(d)
                a["n_cmp"] += 1
                a["exact"] += abs(d) <= EPS
                a["w1"] += abs(d) <= 1
                a["w100"] += abs(d) <= 100
                a["sum_ref"] += rv
                a["sum_cand"] += cv
                if rv > 0:
                    a["rel"].append(abs(d) / rv)
                dmap[col] = d
                total_abs += abs(d)
            if s_ok and d_ok and total_abs <= EPS * len(AMT_COLS):
                full_exact += 1
        row_detail.append((i, r["id"], not s_ok, both_val and not d_ok, dmap, total_abs))

    n = len(pairs)
    m["n_pairs"] = n
    m["status"] = {
        "match": st_match, "rate": st_match / n if n else None,
        "confusion": {f"{a}->{b}": v for (a, b), v in sorted(st_conf.items())},
    }
    m["dom"] = {
        "pairs_both_non_invalid": dom_pairs, "match": dom_match,
        "rate": dom_match / dom_pairs if dom_pairs else None,
        "confusion": {f"{a}->{b}": v for (a, b), v in sorted(dom_conf.items())},
    }
    acols = {}
    for col in AMT_COLS:
        a = amt[col]
        ab = [abs(x) for x in a["d"]]
        acols[col] = {
            "n": a["n_cmp"], "exact": a["exact"], "mismatch": a["n_cmp"] - a["exact"],
            "within_1": a["w1"], "within_100": a["w100"],
            "mae": (sum(ab) / a["n_cmp"]) if a["n_cmp"] else None,
            "median_abs": med(ab), "p95_abs": pctl(ab, 0.95),
            "max_abs": max(ab) if ab else None,
            "sum_ref": a["sum_ref"], "sum_cand": a["sum_cand"],
            "sum_diff": a["sum_cand"] - a["sum_ref"],
            "median_rel_where_ref_pos": med(a["rel"]),
        }
    m["amounts"] = acols
    m["rows"] = {"amount_compared": n_amt_rows, "full_exact": full_exact,
                 "full_exact_rate": full_exact / n_amt_rows if n_amt_rows else None}
    return m, row_detail


def bucketize(pairs, portraits, row_detail):
    """Разрезы: n, доля совпадения status, dom, полностью точных строк, медиана Σ|Δ|."""
    det = {d[0]: d for d in row_detail}
    incs = sorted(p["feat"]["inc"] for p in portraits if p["valid"])
    qs = [pctl(incs, q) for q in (0.2, 0.4, 0.6, 0.8)] if incs else []

    def inc_bucket(x):
        for j, c in enumerate(qs):
            if x <= c:
                return f"income_q{j + 1}"
        return "income_q5"

    def pdn_bucket(x):
        if x is None:
            return "pdn_undef"
        if x == 0:
            return "pdn_0"
        if x <= 0.2:
            return "pdn_(0,0.2]"
        if x <= 0.4:
            return "pdn_(0.2,0.4]"
        return "pdn_>0.4"

    groups = defaultdict(list)
    for r, c, i in pairs:
        groups[("ref_status", r["st"])].append(i)
        p = portraits[i] if i < len(portraits) else None
        if p and p["valid"]:
            f = p["feat"]
            groups[("risk", str(f["rt"]))].append(i)
            groups[("income", inc_bucket(f["inc"]))].append(i)
            groups[("pdn", pdn_bucket(f["pdn"]))].append(i)
            groups[("toxic_debt", "yes" if f["has_tox"] else "no")].append(i)
        groups[("ref_lump", "gt0" if (r["a"]["lump"] or 0) > 0 else "eq0")].append(i)

    out = {}
    for (fam, key), idxs in sorted(groups.items()):
        st_ok = dom_ok = dom_n = fx = 0
        tabs = []
        for i in idxs:
            _, _, st_m, dom_m, dmap, ta = det[i]
            st_ok += not st_m
            if dmap:
                dom_n += 1
                dom_ok += not dom_m
                tabs.append(ta)
                if not st_m and not dom_m and ta <= EPS * len(AMT_COLS):
                    fx += 1
        out.setdefault(fam, {})[key] = {
            "n": len(idxs), "status_rate": st_ok / len(idxs),
            "dom_rate": dom_ok / dom_n if dom_n else None,
            "full_exact_rate": fx / dom_n if dom_n else None,
            "median_total_abs": med(tabs),
        }
    return out


def audit_candidate(pairs, portraits):
    """Проверки кандидата, не зависящие от эталона (кроме валидности портрета)."""
    a = {"neg_or_nan_amounts": 0, "missed_invalid": 0, "false_invalid": 0,
         "ok_sum_gt_fcf": 0, "ok_but_fcf_neg": 0, "deficit_but_fcf_nonneg": 0,
         "deficit_positive_monthly": 0, "lump_gt_bliq": 0}
    ex = defaultdict(list)
    for r, c, i in pairs:
        vals = [c["a"][k] for k in AMT_COLS]
        if any(math.isnan(v) or v < -EPS for v in vals):
            a["neg_or_nan_amounts"] += 1
            _keep(ex, "neg_or_nan_amounts", c["id"])
        p = portraits[i] if i < len(portraits) else None
        if p is None:
            continue
        if not p["valid"]:
            if c["st"] != "invalid":
                a["missed_invalid"] += 1
                _keep(ex, "missed_invalid", c["id"])
            continue
        if c["st"] == "invalid":
            a["false_invalid"] += 1
            _keep(ex, "false_invalid", c["id"])
            continue
        f = p["feat"]
        s4 = sum(0 if math.isnan(c["a"][k]) else c["a"][k]
                 for k in ("res", "debt", "goal", "inv"))
        if c["st"] == "ok":
            if s4 > f["fcf"] + EPS:
                a["ok_sum_gt_fcf"] += 1
                _keep(ex, "ok_sum_gt_fcf", c["id"])
            if f["fcf"] < 0:
                a["ok_but_fcf_neg"] += 1
                _keep(ex, "ok_but_fcf_neg", c["id"])
        elif c["st"] == "deficit":
            if f["fcf"] >= 0:
                a["deficit_but_fcf_nonneg"] += 1
                _keep(ex, "deficit_but_fcf_nonneg", c["id"])
            if s4 > EPS:
                a["deficit_positive_monthly"] += 1
                _keep(ex, "deficit_positive_monthly", c["id"])
        lump = c["a"]["lump"]
        if not math.isnan(lump) and lump > f["bliq"] + EPS:
            a["lump_gt_bliq"] += 1
            _keep(ex, "lump_gt_bliq", c["id"])
    return a, {k: v for k, v in ex.items()}


def _keep(ex, key, rid, cap=5):
    if len(ex[key]) < cap:
        ex[key].append(rid)


# ---------------------------------------------------------------- отчёт

def fmt(x):
    if x is None:
        return "—"
    if isinstance(x, float):
        if x != x:
            return "nan"
        if abs(x) >= 1000:
            return f"{x:,.0f}".replace(",", " ")
        return f"{x:.4g}"
    if isinstance(x, int) and abs(x) >= 1000:
        return f"{x:,}".replace(",", " ")
    return str(x)


def pct(x):
    return "—" if x is None else f"{100 * x:.2f}%"


def write_report(path, meta, m, buckets, audit, audit_ex, problems, worst_path):
    L = []
    A = L.append
    A("# Отчёт сравнения: кандидат vs эталон эксперта (portraits v3)\n")
    A(f"- Эталон: `{meta['reference']}`")
    A(f"- Кандидат: `{meta['candidate']}`")
    A(f"- Выравнивание: **{meta['align_mode']}**"
      + (f" (нет в кандидате: {meta['missing']}, лишних: {meta['extra']})"
         if meta["align_mode"] != "positional" else ""))
    A(f"- Пар сравнено: **{fmt(m['n_pairs'])}**\n")

    if problems:
        A("## ⚠ Проблемы формата")
        for p in problems[:30]:
            A(f"- {p}")
        if len(problems) > 30:
            A(f"- … и ещё {len(problems) - 30}")
        A("")

    A("## Вердикт")
    A(f"- Совпадение `status`: **{pct(m['status']['rate'])}** "
      f"({fmt(m['status']['match'])}/{fmt(m['n_pairs'])})")
    A(f"- Совпадение `dom` (обе стороны не invalid): **{pct(m['dom']['rate'])}** "
      f"({fmt(m['dom']['match'])}/{fmt(m['dom']['pairs_both_non_invalid'])})")
    A(f"- Полностью точных строк (status+dom+все суммы до ₽): "
      f"**{pct(m['rows']['full_exact_rate'])}** "
      f"({fmt(m['rows']['full_exact'])}/{fmt(m['rows']['amount_compared'])})")
    viol = sum(audit[k] for k in ("neg_or_nan_amounts", "ok_sum_gt_fcf", "lump_gt_bliq",
                                  "missed_invalid", "false_invalid"))
    A(f"- Жёстких нарушений у кандидата (аудит): **{fmt(viol)}**\n")

    A("## Матрица `status` (эталон → кандидат)")
    A("| | " + " | ".join(f"cand {s}" for s in STATUSES + ("other",)) + " |")
    A("|---" * 5 + "|")
    conf = m["status"]["confusion"]
    for a_ in STATUSES + ("other",):
        row = [str(conf.get(f"{a_}->{b}", 0)) for b in STATUSES + ("other",)]
        if a_ == "other" and all(x == "0" for x in row):
            continue
        A(f"| ref {a_} | " + " | ".join(row) + " |")
    A("")

    A("## Матрица `dom` (обе стороны не invalid)")
    A("| | " + " | ".join(f"cand {d}" for d in DOMS + ("other",)) + " |")
    A("|---" * 6 + "|")
    dconf = m["dom"]["confusion"]
    for a_ in DOMS + ("other",):
        row = [str(dconf.get(f"{a_}->{b}", 0)) for b in DOMS + ("other",)]
        if a_ == "other" and all(x == "0" for x in row):
            continue
        A(f"| ref {a_} | " + " | ".join(row) + " |")
    A("")

    A("## Суммы (₽), по строкам, где обе стороны не invalid")
    A("| колонка | n | точных (≤0.5₽) | расхожд. | MAE | медиана \\|Δ\\| | p95 \\|Δ\\| "
      "| max \\|Δ\\| | Σ эталон | Σ кандидат | Σ Δ |")
    A("|---" * 11 + "|")
    for col in AMT_COLS:
        c = m["amounts"][col]
        A(f"| {col} | {fmt(c['n'])} | {fmt(c['exact'])} | {fmt(c['mismatch'])} "
          f"| {fmt(c['mae'])} | {fmt(c['median_abs'])} | {fmt(c['p95_abs'])} "
          f"| {fmt(c['max_abs'])} | {fmt(c['sum_ref'])} | {fmt(c['sum_cand'])} "
          f"| {fmt(c['sum_diff'])} |")
    A("")

    A("## Разрезы")
    titles = {"ref_status": "По статусу эталона", "risk": "По риск-профилю",
              "income": "По квинтилям дохода (валидные портреты)",
              "pdn": "По ПДН", "toxic_debt": "Есть токсичный долг",
              "ref_lump": "Эталонный lump > 0"}
    for fam in ("ref_status", "risk", "income", "pdn", "toxic_debt", "ref_lump"):
        if fam not in buckets:
            continue
        A(f"### {titles[fam]}")
        A("| срез | n | status | dom | строки точь-в-точь | медиана Σ\\|Δ\\| |")
        A("|---" * 6 + "|")
        for key, b in buckets[fam].items():
            A(f"| {key} | {fmt(b['n'])} | {pct(b['status_rate'])} | {pct(b['dom_rate'])} "
              f"| {pct(b['full_exact_rate'])} | {fmt(b['median_total_abs'])} |")
        A("")

    A("## Аудит кандидата (независимо от эталона)")
    names = {
        "neg_or_nan_amounts": "Отрицательные/нечисловые суммы",
        "missed_invalid": "Портрет дефектный, но статус не invalid",
        "false_invalid": "Портрет валидный, но статус invalid",
        "ok_sum_gt_fcf": "ok: res+debt+goal+inv > FCF",
        "ok_but_fcf_neg": "ok при FCF < 0",
        "deficit_but_fcf_nonneg": "deficit при FCF ≥ 0",
        "deficit_positive_monthly": "deficit с положительными месячными суммами",
        "lump_gt_bliq": "lump > bliq",
    }
    A("| проверка | нарушений | примеры id |")
    A("|---|---|---|")
    for k, label in names.items():
        exs = ", ".join(audit_ex.get(k, [])) or "—"
        A(f"| {label} | {fmt(audit[k])} | {exs} |")
    A("")
    A(f"Худшие расхождения (топ-{TOP_WORST}): `{os.path.basename(worst_path)}`.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def write_worst(path, row_detail, ref, cand_by_pos, portraits):
    rows = sorted(row_detail, key=lambda d: (-(d[2]), -(d[3]), -d[5]))[:TOP_WORST]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row_index", "id", "ref_status", "cand_status", "ref_dom",
                    "cand_dom"] + [f"d_{c}" for c in AMT_COLS] +
                   ["total_abs_diff", "fcf", "risk", "pdn"])
        for i, rid, st_m, dom_m, dmap, ta in rows:
            if not (st_m or dom_m or ta > EPS):
                continue
            r, c = ref[i], cand_by_pos[i]
            p = portraits[i] if i < len(portraits) else None
            feat = p["feat"] if p and p["valid"] else {}
            w.writerow([i, rid, r["st"], c["st"], r["dom"], c["dom"]] +
                       [("" if col not in dmap or dmap[col] != dmap[col]
                         else round(dmap[col], 2)) for col in AMT_COLS] +
                       [round(ta, 2), feat.get("fcf", ""), feat.get("rt", ""),
                        ("" if feat.get("pdn") is None else round(feat["pdn"], 4))])


# ---------------------------------------------------------------- self-test

def selftest(portraits, ref, outdir):
    print("[selftest] identity: эталон против самого себя …")
    pairs, mode, miss, extra = align(ref, ref)
    m, det = compute(pairs, portraits)
    assert mode == "positional" and miss == extra == 0
    assert m["status"]["rate"] == 1.0, m["status"]
    assert m["dom"]["rate"] == 1.0, m["dom"]
    assert m["rows"]["full_exact"] == m["rows"]["amount_compared"]
    assert all(m["amounts"][c]["mismatch"] == 0 for c in AMT_COLS)
    print("          OK — 100% совпадение, расхождений 0.")

    print("[selftest] возмущённый кандидат с посаженными правками …")
    rng = random.Random(20260717)
    cand = [{"id": r["id"], "st": r["st"], "dom": r["dom"], "a": dict(r["a"])}
            for r in ref]
    ok_idx = [i for i, r in enumerate(ref) if r["st"] == "ok"]
    noninv = [i for i, r in enumerate(ref) if r["st"] != "invalid"]
    lump_idx = [i for i in noninv if ref[i]["a"]["lump"] > 0]
    pool = set(noninv)

    def take(cands, k):
        avail = [i for i in cands if i in pool]
        chosen = rng.sample(avail, k)
        pool.difference_update(chosen)
        return chosen

    st_flip = take(ok_idx, 37)
    for i in st_flip:
        cand[i]["st"] = "deficit"
    dom_flip = take([i for i in ok_idx], 61)
    for i in dom_flip:
        cand[i]["dom"] = next(d for d in DOMS if d != cand[i]["dom"])
    res_idx = take(noninv, 200)
    for i in res_idx:
        cand[i]["a"]["res"] += 123
    inv_idx = take(noninv, 150)
    for i in inv_idx:
        cand[i]["a"]["inv"] += 777
    lump_zero = take(lump_idx, 80)
    for i in lump_zero:
        cand[i]["a"]["lump"] = 0

    pairs, mode, miss, extra = align(ref, cand)
    m, det = compute(pairs, portraits)
    st_mism = m["n_pairs"] - m["status"]["match"]
    dom_mism = m["dom"]["pairs_both_non_invalid"] - m["dom"]["match"]
    assert st_mism == 37, st_mism
    assert dom_mism == 61, dom_mism
    assert m["amounts"]["res"]["mismatch"] == 200, m["amounts"]["res"]
    assert abs(m["amounts"]["res"]["sum_diff"] - 200 * 123) < 1e-6
    assert m["amounts"]["inv"]["mismatch"] == 150
    assert abs(m["amounts"]["inv"]["sum_diff"] - 150 * 777) < 1e-6
    assert m["amounts"]["lump"]["mismatch"] == 80
    exp_lump_drop = -sum(ref[i]["a"]["lump"] for i in lump_zero)
    assert abs(m["amounts"]["lump"]["sum_diff"] - exp_lump_drop) < 1e-6
    assert m["amounts"]["debt"]["mismatch"] == 0
    assert m["amounts"]["goal"]["mismatch"] == 0
    print("          OK — все посаженные правки найдены точно "
          "(37 status, 61 dom, 200 res, 150 inv, 80 lump).")

    buckets = bucketize(pairs, portraits, det)
    audit, audit_ex = audit_candidate(pairs, portraits)
    meta = {"reference": "expert_answers_v3.csv",
            "candidate": "DEMO: эталон + посаженные возмущения (не реальное решение)",
            "align_mode": mode, "missing": miss, "extra": extra}
    worst = os.path.join(outdir, "worst_mismatches_DEMO.csv")
    write_worst(worst, det, ref, [c for c in cand], portraits)
    write_report(os.path.join(outdir, "comparison_report_DEMO.md"),
                 meta, m, buckets, audit, audit_ex, [], worst)
    print(f"[selftest] демо-отчёт: {outdir}/comparison_report_DEMO.md")
    print("[selftest] PASS")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--portraits", nargs="+", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--candidate")
    ap.add_argument("--out", required=True)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    t0 = time.time()
    portraits = load_portraits(args.portraits)
    ref, ref_problems = load_answers(args.reference, "reference")
    if len(ref) != len(portraits):
        print(f"ВНИМАНИЕ: строк в эталоне {len(ref)}, портретов {len(portraits)}")
    idm = sum(1 for p, r in zip(portraits, ref) if p["id"] != r["id"])
    if idm:
        print(f"ВНИМАНИЕ: id эталона и портретов расходятся в {idm} позициях")

    if args.selftest:
        selftest(portraits, ref, args.out)
        return

    if not args.candidate:
        ap.error("нужен --candidate (или --selftest)")
    cand, cand_problems = load_answers(args.candidate, "candidate")
    pairs, mode, miss, extra = align(ref, cand)
    m, det = compute(pairs, portraits)
    buckets = bucketize(pairs, portraits, det)
    audit, audit_ex = audit_candidate(pairs, portraits)

    cand_by_pos = {}
    for r, c, i in pairs:
        cand_by_pos[i] = c
    meta = {"reference": os.path.basename(args.reference),
            "candidate": os.path.basename(args.candidate),
            "align_mode": mode, "missing": miss, "extra": extra}
    worst = os.path.join(args.out, "worst_mismatches.csv")
    write_worst(worst, det, ref, cand_by_pos, portraits)
    write_report(os.path.join(args.out, "comparison_report.md"),
                 meta, m, buckets, audit, audit_ex,
                 ref_problems + cand_problems, worst)
    with open(os.path.join(args.out, "comparison_metrics.json"), "w",
              encoding="utf-8") as f:
        json.dump({"meta": meta, "metrics": m, "buckets": buckets,
                   "audit": audit, "problems": ref_problems + cand_problems},
                  f, ensure_ascii=False, indent=1)
    print(f"Готово за {time.time() - t0:.2f} с → {args.out}/comparison_report.md")


if __name__ == "__main__":
    main()
