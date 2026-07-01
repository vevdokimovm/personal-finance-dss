"""
Статистические утилиты: размеры эффекта, обёртки над тестами различий и связи,
поправка на множественные сравнения, доверительные интервалы для долей.

Каждый результат снабжается размером эффекта и словесной интерпретацией —
p-value без размера эффекта не репортится (принцип академической методички).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TestResult:
    name: str
    statistic: float
    p_value: float
    n: int
    effect_name: str
    effect_value: float
    effect_label: str
    detail: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def significant(self) -> bool:
        return self.p_value < 0.05

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "statistic": round(self.statistic, 4),
            "p_value": round(self.p_value, 4),
            "n": self.n,
            "significant": self.significant,
            "effect_name": self.effect_name,
            "effect_value": round(self.effect_value, 4),
            "effect_label": self.effect_label,
            "detail": self.detail,
            **({"extra": self.extra} if self.extra else {}),
        }


# ── Интерпретаторы размеров эффекта ─────────────────────────────────────
def interpret_r(r: float) -> str:
    a = abs(r)
    if a < 0.1:
        return "связи нет"
    if a < 0.3:
        return "слабая"
    if a < 0.5:
        return "умеренная"
    return "сильная"


def interpret_d(d: float) -> str:
    a = abs(d)
    if a < 0.2:
        return "пренебрежимый"
    if a < 0.5:
        return "малый"
    if a < 0.8:
        return "средний"
    return "крупный"


def interpret_cramers_v(v: float, dof: int) -> str:
    # пороги Cohen с поправкой на размер таблицы (min размерность)
    k = max(1, dof)
    small, medium, large = 0.1 / math.sqrt(k), 0.3 / math.sqrt(k), 0.5 / math.sqrt(k)
    if v < small:
        return "связи нет"
    if v < medium:
        return "слабая"
    if v < large:
        return "умеренная"
    return "сильная"


# ── Связь категория × категория ─────────────────────────────────────────
def chi_square(a: pd.Series, b: pd.Series) -> Optional[TestResult]:
    df = pd.DataFrame({"a": a, "b": b}).dropna()
    if df["a"].nunique() < 2 or df["b"].nunique() < 2:
        return None
    table = pd.crosstab(df["a"], df["b"])
    if table.values.min() == 0 and table.size > 4:
        pass  # χ² ещё валиден, но отметим осторожность ниже
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = int(table.values.sum())
    min_dim = min(table.shape) - 1
    v = math.sqrt(chi2 / (n * min_dim)) if n and min_dim else 0.0
    low_expected = (expected < 5).mean()
    detail = f"таблица {table.shape[0]}×{table.shape[1]}"
    if low_expected > 0.2:
        detail += f"; внимание: {low_expected*100:.0f}% ячеек с ожид.<5"
    return TestResult(
        name="χ² (хи-квадрат)", statistic=chi2, p_value=p, n=n,
        effect_name="Cramér's V", effect_value=v,
        effect_label=interpret_cramers_v(v, min_dim), detail=detail,
        extra={"table": table.to_dict()},
    )


# ── Различие двух групп по порядковой/числовой метрике ──────────────────
def mann_whitney(values: pd.Series, group: pd.Series) -> Optional[TestResult]:
    df = pd.DataFrame({"v": values, "g": group}).dropna()
    groups = df["g"].unique()
    if len(groups) != 2:
        return None
    g1 = df[df["g"] == groups[0]]["v"]
    g2 = df[df["g"] == groups[1]]["v"]
    if len(g1) < 3 or len(g2) < 3:
        return None
    u, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")
    n1, n2 = len(g1), len(g2)
    rank_biserial = 1 - (2 * u) / (n1 * n2)  # размер эффекта для MWU
    return TestResult(
        name="Манна–Уитни U", statistic=u, p_value=p, n=n1 + n2,
        effect_name="rank-biserial r", effect_value=abs(rank_biserial),
        effect_label=interpret_r(rank_biserial),
        detail=f"{groups[0]} (n={n1}, med={g1.median():.1f}) vs "
               f"{groups[1]} (n={n2}, med={g2.median():.1f})",
    )


def kruskal(values: pd.Series, group: pd.Series) -> Optional[TestResult]:
    df = pd.DataFrame({"v": values, "g": group}).dropna()
    samples = [grp["v"].values for _, grp in df.groupby("g") if len(grp) >= 3]
    if len(samples) < 3:
        return None
    h, p = stats.kruskal(*samples)
    n = sum(len(s) for s in samples)
    k = len(samples)
    eta2 = (h - k + 1) / (n - k) if n > k else 0.0  # ε²-подобный размер эффекта
    return TestResult(
        name="Краскела–Уоллиса H", statistic=h, p_value=p, n=n,
        effect_name="ε² (eta-squared)", effect_value=max(0.0, eta2),
        effect_label=interpret_r(math.sqrt(max(0.0, eta2))),
        detail=f"{k} групп",
    )


# ── Корреляция ──────────────────────────────────────────────────────────
def spearman(x: pd.Series, y: pd.Series) -> Optional[TestResult]:
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(df) < 5:
        return None
    rho, p = stats.spearmanr(df["x"], df["y"])
    return TestResult(
        name="Спирмен ρ", statistic=rho, p_value=p, n=len(df),
        effect_name="ρ", effect_value=rho, effect_label=interpret_r(rho),
    )


# ── Доверительный интервал для доли (Wilson) ────────────────────────────
def wilson_ci(count: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = count / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


# ── Поправка на множественные сравнения (Холм) ──────────────────────────
def holm_correction(results: list[TestResult]) -> list[dict]:
    indexed = sorted(enumerate(results), key=lambda t: t[1].p_value)
    m = len(results)
    out: dict[int, dict] = {}
    prev = 0.0
    for rank, (orig_i, res) in enumerate(indexed):
        adj = min(1.0, (m - rank) * res.p_value)
        adj = max(adj, prev)
        prev = adj
        d = res.as_dict()
        d["p_holm"] = round(adj, 4)
        d["significant_holm"] = adj < 0.05
        out[orig_i] = d
    return [out[i] for i in range(m)]


def cronbach_alpha(items: pd.DataFrame) -> tuple[float, int]:
    """Cronbach's α для батареи Лайкерта (строки с полным набором ответов)."""
    data = items.dropna()
    k = data.shape[1]
    if k < 2 or len(data) < 3:
        return float("nan"), len(data)
    item_var = data.var(axis=0, ddof=1).sum()
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan"), len(data)
    alpha = (k / (k - 1)) * (1 - item_var / total_var)
    return float(alpha), len(data)
