"""Анализ расходов и генерация рекомендаций по тратам (мат-модель v3.0.0, §§3-7).

Изолированное ядро без зависимостей от ORM/БД: на вход — простые записи о
расходах, на выход — статистика по категориям и советы. Сервисный слой
конвертирует ORM-транзакции в ExpenseRecord и вызывает SpendingAdvisor.

Метод устойчив к выбросам: норма категории — медиана (а не среднее),
разброс — MAD (median absolute deviation), аномалии — robust z-score.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import median

# --- Параметры модели (мат-модель v3.0.0, §11) ---
MIN_MONTHS: int = 3          # минимум завершённых прошлых месяцев для нормы (fail-loud)
MIN_CATEGORY_TXNS: int = 3   # минимум операций в категории, иначе норма не определена
Z_THRESHOLD: float = 3.5     # порог аномалии (Hampel)
MAD_SCALE: float = 0.6745    # приведение MAD к шкале сигмы: Φ⁻¹(0.75)
SUGGESTED_CUT: float = 0.15  # предлагаемое умеренное сокращение дискреционного
TOP_K: int = 3               # сколько советов отдавать
MIN_SAVING: float = 500.0    # порог значимости экономии, ₽/мес

# Коэффициент сжимаемости v_c по категориям движка (мат-модель v3.0.0, §6.1).
COMPRESSIBILITY: dict[str, float] = {
    "Кафе и рестораны": 1.0,
    "Развлечения": 1.0,
    "Подписки и сервисы": 0.7,
    "Покупки": 0.6,
    "Транспорт": 0.3,
    "Продукты": 0.3,
    "Здоровье": 0.2,
    "ЖКХ и связь": 0.1,
    "Прочее": 0.5,
}
DEFAULT_COMPRESSIBILITY: float = 0.5
OBLIGATORY_CEILING: float = 0.1  # v_c ≤ этого — категория несжимаемая, советов не даём


@dataclass(frozen=True)
class ExpenseRecord:
    """Одна расходная операция в форме, независимой от ORM."""
    category: str
    amount: float
    period: str  # "YYYY-MM"


@dataclass
class CategoryStats:
    category: str
    baseline: float       # медианная норма по прошлым месяцам
    mad: float
    current: float        # расход текущего периода
    z_score: float
    freq_month: float
    avg_check: float
    share: float
    compressibility: float
    pain_score: float
    is_anomaly: bool
    months_observed: int


@dataclass
class SpendingAdvice:
    category: str
    potential_saving: float
    reason: str           # "overspend" | "discretionary"
    current: float
    baseline: float
    message: str


class SpendingAdvisor:
    def __init__(
        self,
        *,
        min_months: int = MIN_MONTHS,
        min_category_txns: int = MIN_CATEGORY_TXNS,
        z_threshold: float = Z_THRESHOLD,
        suggested_cut: float = SUGGESTED_CUT,
        top_k: int = TOP_K,
        min_saving: float = MIN_SAVING,
    ) -> None:
        self.min_months = min_months
        self.min_category_txns = min_category_txns
        self.z_threshold = z_threshold
        self.suggested_cut = suggested_cut
        self.top_k = top_k
        self.min_saving = min_saving

    @staticmethod
    def compressibility(category: str) -> float:
        return COMPRESSIBILITY.get(category, DEFAULT_COMPRESSIBILITY)

    @staticmethod
    def mad(values: list[float], center: float) -> float:
        if not values:
            return 0.0
        return float(median([abs(v - center) for v in values]))

    @staticmethod
    def robust_zscore(value: float, center: float, mad: float) -> float:
        if mad <= 0:
            return 0.0
        return MAD_SCALE * (value - center) / mad

    def _resolve_current_period(self, records: list[ExpenseRecord], current_period: str | None) -> str | None:
        if current_period is not None:
            return current_period
        periods = {r.period for r in records}
        return max(periods) if periods else None

    def analyze(self, records: list[ExpenseRecord], current_period: str | None = None) -> list[CategoryStats]:
        """Статистика по каждой категории: норма, разброс, аномальность, pain-score."""
        current_period = self._resolve_current_period(records, current_period)
        if current_period is None:
            return []

        # {category: {period: sum}} и {category: {period: count}}
        sums: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for rec in records:
            sums[rec.category][rec.period] += rec.amount
            counts[rec.category][rec.period] += 1

        total_all = sum(rec.amount for rec in records) or 0.0
        stats: list[CategoryStats] = []

        for category, by_period in sums.items():
            past_periods = [p for p in by_period if p != current_period]
            months_observed = len(past_periods)
            if months_observed < self.min_months:
                continue

            cat_count = sum(counts[category].values())
            if cat_count < self.min_category_txns:
                continue

            past_values = [by_period[p] for p in past_periods]
            baseline = float(median(past_values))
            mad_value = self.mad(past_values, baseline)
            current = by_period.get(current_period, 0.0)
            z = self.robust_zscore(current, baseline, mad_value)

            months_total = len(by_period)
            cat_sum = sum(by_period.values())
            freq_month = cat_count / months_total if months_total else 0.0
            avg_check = cat_sum / cat_count if cat_count else 0.0
            share = cat_sum / total_all if total_all else 0.0
            comp = self.compressibility(category)
            pain = freq_month * avg_check * comp

            stats.append(CategoryStats(
                category=category,
                baseline=round(baseline, 2),
                mad=round(mad_value, 2),
                current=round(current, 2),
                z_score=round(z, 3),
                freq_month=round(freq_month, 2),
                avg_check=round(avg_check, 2),
                share=round(share, 4),
                compressibility=comp,
                pain_score=round(pain, 2),
                is_anomaly=abs(z) > self.z_threshold,
                months_observed=months_observed,
            ))

        stats.sort(key=lambda s: s.pain_score, reverse=True)
        return stats

    def generate_advice(self, records: list[ExpenseRecord], current_period: str | None = None) -> list[SpendingAdvice]:
        """Топ-K советов без шейминга: возврат к норме при перерасходе либо
        умеренное сокращение дискреционного."""
        stats = self.analyze(records, current_period)
        advice: list[SpendingAdvice] = []

        for s in stats:
            if s.compressibility <= OBLIGATORY_CEILING:
                continue  # несжимаемые (ЖКХ и т.п.) не трогаем

            if s.z_score > self.z_threshold:
                saving = max(0.0, s.current - s.baseline)
                reason = "overspend"
            else:
                saving = self.suggested_cut * s.compressibility * s.baseline
                reason = "discretionary"

            saving = round(saving, 2)
            if saving < self.min_saving:
                continue

            advice.append(SpendingAdvice(
                category=s.category,
                potential_saving=saving,
                reason=reason,
                current=s.current,
                baseline=s.baseline,
                message=self._format_message(s.category, saving, reason, s.current, s.baseline),
            ))
            if len(advice) >= self.top_k:
                break

        return advice

    @staticmethod
    def _format_message(category: str, saving: float, reason: str, current: float, baseline: float) -> str:
        if reason == "overspend":
            return (
                f"На категории «{category}» в этом месяце ушло {current:,.0f} ₽ — "
                f"это на {saving:,.0f} ₽ выше вашей обычной нормы (~{baseline:,.0f} ₽). "
                f"Возврат к норме освободит ~{saving:,.0f} ₽/мес."
            ).replace(",", " ")
        return (
            f"«{category}» — обычно ~{baseline:,.0f} ₽/мес. "
            f"Сокращение примерно на {saving:,.0f} ₽/мес освободит эти деньги "
            f"на досрочку, подушку или цели."
        ).replace(",", " ")
