"""
Слой данных: загрузка анкеты, фильтрация валидной выборки по attention-check,
доступ к колонкам по алиасам, кодирование порядковых шкал и разбор
мультиселектов через матчинг канонических вариантов.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from finpilot_survey import config as cfg


class SurveyData:
    """Обёртка над выгрузкой Google Forms с доступом по алиасам колонок."""

    def __init__(self, path: str) -> None:
        self._raw = pd.read_excel(path, sheet_name=0)
        self._columns = list(self._raw.columns)
        self.df = self._filter_valid(self._raw)

    # ── выборка ─────────────────────────────────────────────────────────
    def _attention_col(self) -> str:
        for c in self._columns:
            if cfg.ATTENTION_MARKER in str(c):
                return c
        raise KeyError("Не найдена колонка attention-check")

    def _filter_valid(self, raw: pd.DataFrame) -> pd.DataFrame:
        att = raw[self._attention_col()]
        mask = att.isna() | (att == cfg.ATTENTION_PASS_VALUE)
        return raw[mask].reset_index(drop=True)

    @property
    def n_total(self) -> int:
        return len(self._raw)

    @property
    def n_valid(self) -> int:
        return len(self.df)

    @property
    def n_dropped(self) -> int:
        return self.n_total - self.n_valid

    # ── доступ к колонкам ───────────────────────────────────────────────
    def col(self, alias: str) -> pd.Series:
        idx = cfg.QCOL[alias]
        return self.df.iloc[:, idx - 1]

    def question_text(self, alias: str) -> str:
        idx = cfg.QCOL[alias]
        return str(self._columns[idx - 1])

    def n_answered(self, alias: str) -> int:
        return int(self.col(alias).notna().sum())

    # ── кодирование порядковых шкал ─────────────────────────────────────
    def ordinal(self, alias: str) -> pd.Series:
        """Числовой ряд из порядковой шкалы по правилам config.ORDINAL_RULES."""
        if alias in cfg.NUMERIC_15 or alias in cfg.LIKERT_CRITERIA:
            return self._numeric_lead(self.col(alias))
        rules = cfg.ORDINAL_RULES[alias]
        return self.col(alias).map(lambda v: _apply_rules(v, rules))

    @staticmethod
    def _numeric_lead(series: pd.Series) -> pd.Series:
        def parse(v: object) -> float:
            if pd.isna(v):
                return np.nan
            try:
                return float(v)
            except (TypeError, ValueError):
                s = str(v).strip()
                return float(s[0]) if s and s[0].isdigit() else np.nan
        return series.map(parse)

    def age_numeric(self) -> pd.Series:
        return self.ordinal("age").map(cfg.AGE_MIDPOINTS)

    # ── категориальная перекодировка ────────────────────────────────────
    def recode(self, alias: str, mapping: dict[str, tuple[str, str]]) -> pd.Series:
        def to_key(v: object) -> object:
            if pd.isna(v):
                return np.nan
            low = str(v).lower()
            for substr, (key, _label) in mapping.items():
                if substr in low:
                    return key
            return np.nan
        return self.col(alias).map(to_key)

    # ── мультиселекты ───────────────────────────────────────────────────
    def multiselect(self, alias: str) -> pd.DataFrame:
        """One-hot матрица вариантов мультиселекта (матчинг по подстроке)."""
        options = cfg.MULTISELECT[alias]
        series = self.col(alias)
        data: dict[str, list[int]] = {}
        for key, (_label, substr) in options.items():
            data[key] = [
                1 if (pd.notna(v) and substr in str(v).lower()) else 0
                for v in series
            ]
        out = pd.DataFrame(data, index=self.df.index)
        out["_answered"] = series.notna().astype(int).values
        return out

    def multiselect_freq(self, alias: str) -> pd.DataFrame:
        """Частоты вариантов: count и доля от ответивших на вопрос."""
        oh = self.multiselect(alias)
        n = int(oh["_answered"].sum())
        labels = {k: v[0] for k, v in cfg.MULTISELECT[alias].items()}
        rows = []
        for key in cfg.MULTISELECT[alias]:
            cnt = int(oh[key].sum())
            rows.append({
                "key": key,
                "label": labels[key],
                "count": cnt,
                "share": round(cnt / n, 4) if n else 0.0,
            })
        res = pd.DataFrame(rows).sort_values("count", ascending=False)
        res.attrs["n"] = n
        return res


@lru_cache(maxsize=1)
def load() -> SurveyData:
    return SurveyData(cfg_path())


def cfg_path() -> str:
    return DATA_PATH


def _apply_rules(value: object, rules: list[tuple[str, float]]) -> float:
    if pd.isna(value):
        return np.nan
    low = str(value).lower()
    for substr, code in rules:
        if substr in low:
            return float(code)
    return np.nan


# Путь к данным задаётся снаружи (run_analysis.py), значение по умолчанию ниже
DATA_PATH = (
    "/mnt/user-data/uploads/"
    "Исследование__Выбор_финансовых_стратегий__Ответы_385_респондентов_.xlsx"
)
