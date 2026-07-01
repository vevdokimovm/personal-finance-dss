"""
Количественные анализаторы. Каждый класс получает SurveyData и возвращает
структурированный результат через .run(). Логика опирается на методы
SurveyData (кодирование, мультиселекты) и stats_utils (тесты, эффекты).
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from finpilot_survey import config as cfg
from finpilot_survey import stats_utils as su
from finpilot_survey.data import SurveyData


class DescriptiveAnalyzer:
    """Частоты, меры центра и разброса по ключевым полям + профиль N."""

    SINGLE = [
        "look_freq", "choice_method", "stat_tool_useful", "has_goal", "income",
        "has_debt", "debt_dilemma", "money_left", "followed_advice", "material",
        "literacy", "situation_freq", "options_compared", "saving_principle",
        "envelopes", "behavior_after",
    ]
    ORDINAL = [
        "income", "material", "literacy", "money_left", "look_freq",
        "options_compared", "planning_horizon", "savings_runway",
        "forget_fear", "anxiety", "confidence", "hindsight",
    ]
    MULTI = [
        "accounting_tools", "advice_format", "ui_annoyance", "tool_helps",
        "tool_lacks", "must_have", "trust_factors", "saving_motives",
    ]

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "n_profile": self._n_profile(),
            "categorical": self._categorical(),
            "ordinal": self._ordinal(),
            "multiselect": self._multiselect(),
        }

    def _n_profile(self) -> list[dict]:
        rows = []
        for alias in cfg.QCOL:
            if alias in ("timestamp", "email", "attention"):
                continue
            n = self.d.n_answered(alias)
            rows.append({"alias": alias, "n": n,
                         "small": n < cfg.SMALL_N_THRESHOLD})
        return rows

    def _categorical(self) -> dict[str, dict]:
        out = {}
        for alias in self.SINGLE:
            s = self.d.col(alias)
            vc = s.value_counts()
            n = int(s.notna().sum())
            out[alias] = {
                "question": self.d.question_text(alias),
                "n": n,
                "distribution": {str(k): int(v) for k, v in vc.items()},
            }
        return out

    def _ordinal(self) -> dict[str, dict]:
        out = {}
        for alias in self.ORDINAL:
            s = self.d.ordinal(alias)
            clean = s.dropna()
            if clean.empty:
                continue
            out[alias] = {
                "n": int(clean.size),
                "mean": round(float(clean.mean()), 3),
                "median": float(clean.median()),
                "sd": round(float(clean.std(ddof=1)), 3) if clean.size > 1 else 0.0,
                "min": float(clean.min()),
                "max": float(clean.max()),
            }
        return out

    def _multiselect(self) -> dict[str, dict]:
        out = {}
        for alias in self.MULTI:
            f = self.d.multiselect_freq(alias)
            out[alias] = {
                "question": self.d.question_text(alias),
                "n": int(f.attrs["n"]),
                "items": f[["label", "count", "share"]].to_dict("records"),
            }
        return out


class AudienceProfiler:
    """Демографический портрет, диагностика смещений выборки,
    проверка репрезентативности поздней когорты (по отметке времени)."""

    DEMO = ["gender", "age", "region", "education", "marital", "material", "income"]

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "demographics": self._demographics(),
            "bias": self._bias_flags(),
            "late_cohort_check": self._late_cohort_check(),
        }

    def _demographics(self) -> dict[str, dict]:
        out = {}
        for alias in self.DEMO:
            s = self.d.col(alias)
            vc = s.value_counts()
            n = int(s.notna().sum())
            out[alias] = {
                "n": n,
                "top": {str(k): int(v) for k, v in vc.head(6).items()},
            }
        return out

    def _bias_flags(self) -> list[dict]:
        flags = []
        # концентрация в столицах
        reg = self.d.col("region")
        n_reg = reg.notna().sum()
        capital = reg.astype(str).str.contains("Москва", na=False).sum()
        flags.append(self._flag("Гео", "Москва/СПб", capital, n_reg))
        # молодёжь 18–27
        age = self.d.ordinal("age")
        young = age.isin([1, 2]).sum()
        flags.append(self._flag("Возраст", "18–27 лет", int(young), int(age.notna().sum())))
        # пол
        gen = self.d.col("gender")
        fem = gen.astype(str).str.contains("Женск", na=False).sum()
        flags.append(self._flag("Пол", "женщины", int(fem), int(gen.notna().sum())))
        # образование (студенты/высшее)
        edu = self.d.col("education")
        higher = edu.astype(str).str.contains("высшее", case=False, na=False).sum()
        flags.append(self._flag("Образование", "высшее/незаконч. высшее",
                                int(higher), int(edu.notna().sum())))
        return flags

    @staticmethod
    def _flag(dim: str, label: str, count: int, n: int) -> dict:
        share = count / n if n else 0.0
        lo, hi = su.wilson_ci(count, n)
        return {
            "dimension": dim, "label": label, "count": count, "n": n,
            "share": round(share, 3), "ci": [round(lo, 3), round(hi, 3)],
            "skewed": share > 0.6,
        }

    def _late_cohort_check(self) -> dict[str, Any]:
        """Сравнение «поздней когорты» (видели вопрос-ловушку, поз. 53)
        с полной выборкой по полу/возрасту/доходу. Закрывает риск смены
        источника набора во времени (не отвал — все доходили до конца)."""
        att = self.d.col("attention")
        late_mask = att.notna()  # видели поздний вопрос
        out = {"n_late": int(late_mask.sum()), "n_full": self.d.n_valid,
               "comparisons": []}
        for alias in ["gender", "age", "income"]:
            s = self.d.col(alias)
            full = s.dropna()
            late = s[late_mask].dropna()
            if full.empty or late.empty:
                continue
            full_share = (full.value_counts(normalize=True))
            late_share = (late.value_counts(normalize=True))
            cats = set(full_share.index) | set(late_share.index)
            max_gap = max(
                abs(full_share.get(c, 0) - late_share.get(c, 0)) for c in cats
            )
            out["comparisons"].append({
                "field": alias,
                "max_share_gap": round(float(max_gap), 3),
                "representative": bool(max_gap < 0.15),
            })
        return out


class SegmentAnalyzer:
    """Априорная сегментация: долг да/нет, доход-группы, тревожность —
    и поведение сегментов по ключевым осям."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "by_debt": self._by_debt(),
            "by_income": self._by_income(),
            "by_choice_method": self._choice_method_profile(),
        }

    def _debt_group(self) -> pd.Series:
        def f(v: object) -> object:
            if pd.isna(v):
                return np.nan
            s = str(v)
            if "Нет" == s.strip() or s.startswith("Нет"):
                return "Без долга"
            if s.startswith("Да"):
                return "С долгом"
            return np.nan
        return self.d.col("has_debt").map(f)

    def _by_debt(self) -> dict[str, Any]:
        grp = self._debt_group()
        out = {"sizes": {str(k): int(v) for k, v in grp.value_counts().items()}}
        # доля столкнувшихся с дилеммой среди групп
        dil = self.d.col("debt_dilemma").astype(str)
        had_dilemma = dil.str.startswith("Да")
        df = pd.DataFrame({"g": grp, "d": had_dilemma})
        out["dilemma_share"] = {
            str(k): round(float(v), 3)
            for k, v in df.dropna(subset=["g"]).groupby("g")["d"].mean().items()
        }
        # тревога забыть платёж по группам (mean forget_fear)
        ff = self.d.ordinal("forget_fear")
        df2 = pd.DataFrame({"g": grp, "ff": ff}).dropna()
        out["forget_fear_mean"] = {
            str(k): round(float(v), 2)
            for k, v in df2.groupby("g")["ff"].mean().items()
        }
        return out

    def _income_group(self) -> pd.Series:
        inc = self.d.ordinal("income")
        return inc.map(lambda x: ("Низкий ≤60k" if x <= 2
                                  else "Средний 60–200k" if x <= 4
                                  else "Высокий >200k") if pd.notna(x) else np.nan)

    def _by_income(self) -> dict[str, Any]:
        grp = self._income_group()
        out = {"sizes": {str(k): int(v) for k, v in grp.value_counts().items()}}
        ml = self.d.ordinal("money_left")
        df = pd.DataFrame({"g": grp, "ml": ml}).dropna()
        out["money_left_mean"] = {
            str(k): round(float(v), 2)
            for k, v in df.groupby("g")["ml"].mean().items()
        }
        return out

    def _choice_method_profile(self) -> dict[str, Any]:
        cm = self.d.recode("choice_method", cfg.CHOICE_METHOD_MAP)
        labels = {key: label for (key, label) in cfg.CHOICE_METHOD_MAP.values()}
        vc = cm.value_counts()
        n = int(cm.notna().sum())
        return {
            "n": n,
            "distribution": {labels.get(k, k): int(v) for k, v in vc.items()},
            "non_optimizing_share": round(
                float(cm.isin(["feeling", "defer"]).sum() / n), 3) if n else 0.0,
        }


class HypothesisTester:
    """Содержательные гипотезы H0/H1 на надёжных N с размером эффекта
    и поправкой Холма на множественность."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def _debt_binary(self) -> pd.Series:
        def f(v: object) -> object:
            if pd.isna(v):
                return np.nan
            s = str(v)
            if s.startswith("Да"):
                return "С долгом"
            if s.startswith("Нет") or s.strip() == "Нет":
                return "Без долга"
            return np.nan
        return self.d.col("has_debt").map(f)

    def _gender_binary(self) -> pd.Series:
        return self.d.col("gender").map(
            lambda v: ("Ж" if "Женск" in str(v) else "М" if "Мужск" in str(v)
                       else np.nan) if pd.notna(v) else np.nan)

    def run(self) -> dict[str, Any]:
        tests: list[tuple[str, str, su.TestResult | None]] = []

        # H1: наличие долга ↔ дилемма «гасить/копить»
        tests.append((
            "H1", "Наличие долга связано с переживанием дилеммы «гасить или копить»",
            su.chi_square(self._debt_binary(), self.d.col("debt_dilemma"))))

        # H2: доход ↔ готовность платить (WTP)
        tests.append((
            "H2", "Чем выше доход, тем выше готовность платить за инструмент",
            su.spearman(self.d.ordinal("income"), self._wtp_ordinal())))

        # H3: финграмотность ↔ уверенность в решении
        tests.append((
            "H3", "Чем выше финграмотность, тем выше уверенность в своём решении",
            su.spearman(self.d.ordinal("literacy"), self.d.ordinal("confidence"))))

        # H4: долг ↔ страх забыть платёж
        tests.append((
            "H4", "Должники сильнее боятся забыть обязательный платёж",
            su.mann_whitney(self.d.ordinal("forget_fear"), self._debt_binary())))

        # H5: материальное положение ↔ остаток денег в конце месяца
        tests.append((
            "H5", "Лучше материальное положение — чаще остаются свободные деньги",
            su.spearman(self.d.ordinal("material"), self.d.ordinal("money_left"))))

        # H6: горизонт планирования ↔ запас прочности при потере дохода
        tests.append((
            "H6", "Длиннее горизонт планирования — больше финансовый запас прочности",
            su.spearman(self.d.ordinal("planning_horizon"),
                        self.d.ordinal("savings_runway"))))

        # H7: способ выбора ↔ финграмотность
        cm = self.d.recode("choice_method", cfg.CHOICE_METHOD_MAP)
        tests.append((
            "H7", "Способ выбора связан с уровнем финграмотности",
            su.kruskal(self.d.ordinal("literacy"), cm)))

        # H8: пол ↔ финансовая тревожность
        tests.append((
            "H8", "Финансовая тревожность различается по полу",
            su.mann_whitney(self.d.ordinal("anxiety"), self._gender_binary())))

        # H9: наличие цели ↔ как часто остаются деньги
        has_goal = self.d.col("has_goal").map(
            lambda v: ("Есть цель" if "Да" in str(v) or "размыто" in str(v)
                       else "Нет цели") if pd.notna(v) else np.nan)
        tests.append((
            "H9", "Наличие финансовой цели связано с частотой остатка денег",
            su.mann_whitney(self.d.ordinal("money_left"), has_goal)))

        # H10: тревога забыть платёж ↔ как часто заглядывает в финансы
        tests.append((
            "H10", "Чем выше тревога по платежам, тем чаще человек проверяет финансы",
            su.spearman(self.d.ordinal("forget_fear"), self.d.ordinal("look_freq"))))

        valid = [(code, hyp, r) for code, hyp, r in tests if r is not None]
        corrected = su.holm_correction([r for _, _, r in valid])
        results = []
        for (code, hyp, _r), corr in zip(valid, corrected):
            results.append({"code": code, "hypothesis": hyp, **corr})
        skipped = [{"code": c, "hypothesis": h} for c, h, r in tests if r is None]
        return {"results": results, "skipped": skipped, "n_tests": len(valid)}

    def _wtp_ordinal(self) -> pd.Series:
        order = {"до 200": 1, "200–500": 2, "500–1000": 3}
        def f(v: object) -> float:
            if pd.isna(v):
                return np.nan
            low = str(v).lower()
            for k, val in order.items():
                if k in low:
                    return float(val)
            return np.nan  # «разово» и «процент» — не на шкале мес. платежа
        return self.d.col("wtp").map(f)


class PreferenceAnalyzer:
    """Структура критериев распределения (Доходность/Ликвидность/Долг/
    Безопасность). На N≈19 — только предварительно: Cronbach + корреляции;
    полноценный факторный анализ невозможен и помечается как таковой."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def _matrix(self) -> pd.DataFrame:
        cols = {cfg.CRITERION_LABELS[a]: self.d.ordinal(a)
                for a in cfg.LIKERT_CRITERIA}
        return pd.DataFrame(cols)

    def run(self) -> dict[str, Any]:
        m = self._matrix()
        n_complete = int(m.dropna().shape[0])
        means = {c: round(float(m[c].mean()), 2) for c in m.columns}
        medians = {c: float(m[c].median()) for c in m.columns}
        corr = m.corr(method="spearman").round(3)
        alpha, n_alpha = su.cronbach_alpha(m)
        efa = self._try_efa(m)
        return {
            "n_complete": n_complete,
            "means": means,
            "medians": medians,
            "spearman_corr": corr.to_dict(),
            "cronbach_alpha": None if math.isnan(alpha) else round(alpha, 3),
            "cronbach_n": n_alpha,
            "efa": efa,
            "preliminary": n_complete < 100,
        }

    def _try_efa(self, m: pd.DataFrame) -> dict[str, Any]:
        data = m.dropna()
        verdict = {"feasible": False,
                   "reason": f"N={len(data)} < 100 и 4 переменные: "
                             f"для EFA нужно ≥100 наблюдений и ≥5 на переменную "
                             f"(правило адекватности KMO). Результат был бы "
                             f"статистически невалиден."}
        try:
            from factor_analyzer.factor_analyzer import (
                calculate_bartlett_sphericity, calculate_kmo)
            chi2, p = calculate_bartlett_sphericity(data)
            _, kmo_model = calculate_kmo(data)
            verdict["bartlett_p"] = round(float(p), 4)
            verdict["kmo"] = round(float(kmo_model), 3)
        except Exception as e:  # noqa: BLE001 — диагностический путь
            verdict["error"] = str(e)
        return verdict


class RankingAnalyzer:
    """Анализ ранжирования 5 приоритетов: средний ранг, Borda, Kendall's W.
    Респонденты с невалидной перестановкой (дубли рангов) исключаются."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def _rank_matrix(self) -> pd.DataFrame:
        cols = {}
        for alias in cfg.RANK_COLS:
            s = self.d.col(alias)
            cols[alias] = pd.to_numeric(s, errors="coerce")
        m = pd.DataFrame(cols)
        valid = m.dropna()
        # валидная перестановка: ровно {1,2,3,4,5}
        is_perm = valid.apply(
            lambda row: sorted(row.tolist()) == [1, 2, 3, 4, 5], axis=1)
        return valid[is_perm]

    def run(self) -> dict[str, Any]:
        m = self._rank_matrix()
        n = len(m)
        labels = cfg.RANK_LABELS
        mean_rank = {labels[a]: round(float(m[a].mean()), 2) for a in cfg.RANK_COLS}
        first_share = {labels[a]: round(float((m[a] == 1).mean()), 3)
                       for a in cfg.RANK_COLS}
        # Borda: 5 объектов, 1-е место = 5 баллов
        borda = {labels[a]: int((6 - m[a]).sum()) for a in cfg.RANK_COLS}
        w, chi2, p = self._kendall_w(m)
        return {
            "n_valid_rankings": n,
            "mean_rank": mean_rank,
            "first_place_share": first_share,
            "borda": dict(sorted(borda.items(), key=lambda x: -x[1])),
            "kendall_w": round(w, 3),
            "kendall_chi2": round(chi2, 3),
            "kendall_p": round(p, 4),
            "agreement": self._w_label(w),
            "preliminary": n < 100,
        }

    @staticmethod
    def _kendall_w(m: pd.DataFrame) -> tuple[float, float, float]:
        arr = m.values
        n_judges, n_items = arr.shape
        if n_judges < 2:
            return float("nan"), float("nan"), float("nan")
        rank_sums = arr.sum(axis=0)
        mean_rs = rank_sums.mean()
        s = ((rank_sums - mean_rs) ** 2).sum()
        w = 12 * s / (n_judges**2 * (n_items**3 - n_items))
        chi2 = n_judges * (n_items - 1) * w
        p = 1 - stats.chi2.cdf(chi2, n_items - 1)
        return float(w), float(chi2), float(p)

    @staticmethod
    def _w_label(w: float) -> str:
        if math.isnan(w):
            return "не определено"
        if w < 0.1:
            return "согласия практически нет"
        if w < 0.3:
            return "слабое согласие"
        if w < 0.5:
            return "умеренное согласие"
        return "сильное согласие"
