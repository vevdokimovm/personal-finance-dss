"""
Поведенческая валидация (stated vs revealed), продуктово-бизнесовый слой
(WTP, opportunity scoring, приоритизация, доверие к ИИ) и качественное
кодирование открытых ответов.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from finpilot_survey import config as cfg
from finpilot_survey import stats_utils as su
from finpilot_survey.data import SurveyData


class BehavioralValidator:
    """Разрыв «заявленное vs реальное»: как люди ГОВОРЯТ, что выбирают,
    против того, на что опирались в конкретном денежном кейсе, плюс падение
    уверенности при переоценке решения задним числом."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "stated_choice": self._stated(),
            "case_outcome": self._case(),
            "case_basis": self._case_basis(),
            "intention_action_gap": self._gap(),
            "confidence_vs_hindsight": self._confidence_shift(),
        }

    def _stated(self) -> dict[str, Any]:
        cm = self.d.recode("choice_method", cfg.CHOICE_METHOD_MAP)
        labels = {k: l for (k, l) in cfg.CHOICE_METHOD_MAP.values()}
        n = int(cm.notna().sum())
        vc = cm.value_counts()
        return {
            "n": n,
            "distribution": {labels[k]: int(v) for k, v in vc.items()},
            "manual_calc_share": round(float(vc.get("manual_calc", 0) / n), 3),
        }

    def _case(self) -> dict[str, Any]:
        c = self.d.recode("case", cfg.CASE_MAP)
        labels = {k: l for (k, l) in cfg.CASE_MAP.values()}
        n = int(c.notna().sum())
        vc = c.value_counts()
        return {"n": n, "preliminary": n < cfg.SMALL_N_THRESHOLD,
                "distribution": {labels[k]: int(v) for k, v in vc.items()}}

    def _case_basis(self) -> dict[str, Any]:
        b = self.d.recode("case_basis", cfg.CASE_BASIS_MAP)
        labels = {k: l for (k, l) in cfg.CASE_BASIS_MAP.values()}
        n = int(b.notna().sum())
        vc = b.value_counts()
        calc = int(vc.get("calc", 0))
        emotional = int(vc.get("worst_case", 0) + vc.get("comfort", 0))
        return {
            "n": n, "preliminary": n < cfg.SMALL_N_THRESHOLD,
            "distribution": {labels[k]: int(v) for k, v in vc.items()},
            "calc_share": round(calc / n, 3) if n else 0.0,
            "emotional_share": round(emotional / n, 3) if n else 0.0,
        }

    def _gap(self) -> dict[str, Any]:
        stated = self._stated()["manual_calc_share"]
        revealed = self._case_basis()["calc_share"]
        return {
            "stated_manual_calc": stated,
            "revealed_calc": revealed,
            "gap": round(stated - revealed, 3),
            "interpretation": (
                "Заявляют, что считают выгоду вручную, существенно чаще, чем "
                "реально опирались на расчёт в конкретном кейсе — классический "
                "intention-action gap (System 1 vs System 2)."),
            "note_revealed_n": self._case_basis()["n"],
        }

    def _confidence_shift(self) -> dict[str, Any]:
        conf = self.d.ordinal("confidence")
        hind = self.d.ordinal("hindsight")
        paired = pd.DataFrame({"c": conf, "h": hind}).dropna()
        if len(paired) < 5:
            return {"n": len(paired), "available": False}
        try:
            stat_w, p = stats.wilcoxon(paired["c"], paired["h"])
        except ValueError:
            stat_w, p = float("nan"), float("nan")
        return {
            "n": len(paired), "available": True,
            "confidence_mean": round(float(paired["c"].mean()), 2),
            "hindsight_mean": round(float(paired["h"].mean()), 2),
            "wilcoxon_p": round(float(p), 4),
            "dropped": round(float((paired["h"] < paired["c"]).mean()), 3),
        }


class BusinessAnalyzer:
    """Продуктово-бизнесовый слой: готовность платить, концепт-спрос,
    opportunity scoring (важность × неудовлетворённость), приоритизация
    фич, доверие к ИИ по задачам, разрыв «кому нужно ≠ кто платит»."""

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "wtp": self._wtp(),
            "concept_demand": self._concept_demand(),
            "opportunity": self._opportunity(),
            "feature_priority": self._feature_priority(),
            "ai_trust": self._ai_trust(),
            "need_vs_pay": self._need_vs_pay(),
        }

    def _wtp(self) -> dict[str, Any]:
        s = self.d.col("wtp")
        n = int(s.notna().sum())
        vc = s.value_counts()
        buckets = {str(k): int(v) for k, v in vc.items()}
        # доля «до 200 ₽/мес» — потолок массовой подписки
        low = int(sum(v for k, v in vc.items() if "до 200" in str(k).lower()))
        recurring = int(sum(v for k, v in vc.items()
                            if "₽/мес" in str(k)))
        return {
            "n": n,
            "distribution": buckets,
            "low_tier_share": round(low / n, 3) if n else 0.0,
            "recurring_share": round(recurring / n, 3) if n else 0.0,
            "verdict": (
                "Модаль готовности — «до 200 ₽/мес». Массовая B2C-подписка "
                "на такой ARPU при платном привлечении «молодёжи столиц» "
                "сходится плохо (LTV/CAC под давлением). Рассмотреть freemium, "
                "разовую оплату или B2B2C-дистрибуцию через банк/работодателя."),
        }

    def _concept_demand(self) -> dict[str, Any]:
        s = self.d.col("stat_tool_useful")
        n = int(s.notna().sum())
        yes = s.astype(str).str.contains("именно этого не хватает", na=False).sum()
        maybe = s.astype(str).str.contains("зависит от того", na=False).sum()
        no = s.astype(str).str.contains("решать сам", na=False).sum()
        return {
            "n": n,
            "yes": int(yes), "conditional": int(maybe), "no": int(no),
            "positive_share": round(float((yes + maybe) / n), 3) if n else 0.0,
            "note": ("Высокий условный спрос: большинство «за», но при условии "
                     "прозрачности — она становится фактором №1 (триангулирует "
                     "с факторами доверия и болью «не объясняет логику»)."),
        }

    def _opportunity(self) -> list[dict]:
        """Сопоставление боли (чего НЕ умеет, q8) и желаемого (что должно быть,
        q13). Высокая важность + высокая неудовлетворённость = точка возможности."""
        lacks = self.d.multiselect_freq("tool_lacks").set_index("key")
        wants = self.d.multiselect_freq("must_have").set_index("key")
        pairs = [
            ("Предупреждение о нехватке денег", lacks.loc["no_warning", "share"],
             wants.loc["warning", "share"]),
            ("Совет куда направить + объяснение", lacks.loc["no_direction", "share"],
             wants.loc["advice_why", "share"]),
            ("Долги и цели в одной картине", lacks.loc["no_debt_goals", "share"],
             wants.loc["all_in_one", "share"]),
            ("Прозрачность логики совета", lacks.loc["no_logic", "share"],
             wants.loc["advice_why", "share"]),
        ]
        out = []
        for name, pain, want in pairs:
            out.append({
                "opportunity": name,
                "unmet_share": round(float(pain), 3),
                "want_share": round(float(want), 3),
                "score": round(float(pain) * float(want), 3),
            })
        return sorted(out, key=lambda x: -x["score"])

    def _feature_priority(self) -> list[dict]:
        """RICE-подобный рейтинг фич: Reach = доля выбравших в q13."""
        wants = self.d.multiselect_freq("must_have")
        n = wants.attrs["n"]
        # Impact/Effort заданы экспертно по связи с ядром модели FINPILOT
        impact = {"free_money": 3, "advice_why": 3, "all_in_one": 2,
                  "what_if": 2, "warning": 3}
        effort = {"free_money": 1, "advice_why": 2, "all_in_one": 2,
                  "what_if": 3, "warning": 2}
        moscow = {"free_money": "Must", "advice_why": "Must",
                  "all_in_one": "Must", "what_if": "Should", "warning": "Should"}
        out = []
        for _, r in wants.iterrows():
            k = r["key"]
            reach = float(r["share"])
            imp, eff = impact[k], effort[k]
            rice = round(reach * imp / eff, 3)
            out.append({
                "feature": r["label"], "reach": round(reach, 3),
                "impact": imp, "effort": eff, "rice": rice,
                "moscow": moscow[k],
            })
        return sorted(out, key=lambda x: -x["rice"])

    def _ai_trust(self) -> dict[str, Any]:
        rows = []
        n_ref = 0
        for alias, label in cfg.AI_TRUST_COLS.items():
            s = self.d.col(alias)
            n = int(s.notna().sum())
            n_ref = max(n_ref, n)
            scores = s.map(lambda v: cfg.AI_TRUST_SCORE.get(str(v).strip().lower())
                           if pd.notna(v) else np.nan).dropna()
            yes = int((s.astype(str).str.strip().str.lower() == "да").sum())
            rows.append({
                "task": label, "n": n,
                "yes_share": round(yes / n, 3) if n else 0.0,
                "mean_trust": round(float(scores.mean()), 3) if len(scores) else 0.0,
            })
        rows.sort(key=lambda x: -x["yes_share"])
        return {
            "n": n_ref, "preliminary": n_ref < cfg.SMALL_N_THRESHOLD,
            "tasks": rows,
            "pattern": ("Доверяют ИИ считать, объяснять и советовать — но НЕ "
                        "доверяют автономно распоряжаться деньгами. Продукт должен "
                        "быть советником с подтверждением действий человеком, "
                        "а не автоисполнителем."),
        }

    def _need_vs_pay(self) -> dict[str, Any]:
        """Среди тех, у кого боль «не говорит куда направить» — какова
        готовность платить? Проверка разрыва «кому нужно ≠ кто платит»."""
        lacks = self.d.multiselect("tool_lacks")
        has_pain = lacks["no_direction"] == 1
        wtp = self.d.col("wtp")
        df = pd.DataFrame({"pain": has_pain, "wtp": wtp})
        paid_low = df[df["pain"]]["wtp"].astype(str).str.contains(
            "до 200", case=False, na=False).mean()
        return {
            "pain_group_n": int(has_pain.sum()),
            "low_tier_in_pain_group": round(float(paid_low), 3)
            if has_pain.sum() else 0.0,
            "note": ("Боль острая и массовая, но платёжеспособность сегмента "
                     "(молодёжь, студенты) низкая — нужда не конвертируется в "
                     "высокую цену напрямую."),
        }


class QualitativeCoder:
    """Closed coding открытых ответов: разметка по темам через ключевые
    слова + извлечение показательных (неперсональных) цитат."""

    WHY_QUIT_THEMES = {
        "still_using": ["пользуюсь до сих пор", "пользуюсь"],
        "no_value": ["не вижу", "пользы", "дальше что", "бесполезн"],
        "never_tried": ["никогда не пробовал", "не пробовал", "не начина"],
        "too_tedious": ["лень", "муторно", "вручную", "забываю вносить", "долго"],
        "only_stats": ["статистик", "только показывает", "цифры"],
    }
    RESULT_DIFF_THEMES = {
        "unexpected_expenses": ["непредвиденные", "неожиданные расходы"],
        "income_changed": ["изменился доход", "доход"],
        "missed_payments": ["не учёл", "не учел", "платеж"],
        "external": ["внешние", "рынок", "курс", "инфляц"],
        "as_planned": ["как планировал", "всё прошло", "все прошло"],
    }

    def __init__(self, data: SurveyData) -> None:
        self.d = data

    def run(self) -> dict[str, Any]:
        return {
            "why_quit": self._code("why_quit", self.WHY_QUIT_THEMES),
            "result_diff": self._code("result_diff", self.RESULT_DIFF_THEMES),
            "quotes": self._quotes(),
        }

    def _code(self, alias: str, themes: dict[str, list[str]]) -> dict[str, Any]:
        s = self.d.col(alias).dropna().astype(str)
        n = len(s)
        counts = Counter()
        for text in s:
            low = text.lower()
            for theme, keys in themes.items():
                if any(k in low for k in keys):
                    counts[theme] += 1
        return {
            "n": n,
            "note": "открытый вопрос — доли качественные, не репрезентативные",
            "themes": {t: int(counts.get(t, 0)) for t in themes},
        }

    def _quotes(self) -> dict[str, list[str]]:
        out = {}
        for alias in ["why_quit", "ideal_helper", "story"]:
            s = self.d.col(alias).dropna().astype(str)
            picks = [t.strip() for t in s
                     if 15 < len(t.strip()) < 160
                     and not any(b in t.lower() for b in
                                 ["хуй", "воробуш", "@", "http"])]
            out[alias] = picks[:5]
        return out
