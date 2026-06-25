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
from itertools import combinations
from statistics import median

# --- Параметры модели (мат-модель v3.0.0, §11) ---
MIN_MONTHS: int = 3          # минимум завершённых прошлых месяцев для нормы (fail-loud)
MIN_CATEGORY_TXNS: int = 3   # минимум операций в категории, иначе норма не определена
Z_THRESHOLD: float = 3.5     # порог аномалии (Hampel)
MAD_SCALE: float = 0.6745    # приведение MAD к шкале сигмы: Φ⁻¹(0.75)
SUGGESTED_CUT: float = 0.15  # предлагаемое умеренное сокращение дискреционного
TOP_K: int = 3               # сколько советов отдавать
MIN_SAVING: float = 500.0    # порог значимости экономии, ₽/мес
TREND_PCT_THRESHOLD: float = 5.0  # %/мес: ниже по модулю — тренд незначим (flat), не показываем

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
    merchant: str | None = None


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


@dataclass
class MerchantStats:
    """Layer 2: агрегат по мерчанту за текущий период (информационно)."""
    merchant: str
    total: float          # суммарные траты у мерчанта за период
    count: int            # число операций
    avg_check: float      # средний чек
    category: str
    compressibility: float


@dataclass
class TemporalPattern:
    """Layer 3-A: тренд категории по завершённым месяцам (информационно).

    Наклон робастный (Theil-Sen), считается по прошлым месяцам без текущего
    (неполного) периода. slope_pct — относительно медианной нормы категории.
    """
    category: str
    direction: str        # "rising" | "falling"
    slope_abs: float      # ₽/мес, знаковый (Theil-Sen)
    slope_pct: float      # %/мес относительно нормы, знаковый
    baseline: float       # медианная норма по прошлым месяцам
    months_observed: int
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
    def _normalize_merchant(name: str) -> str:
        """Схлопывает пробелы и обрезает края — «  Бар   У Джо » → «Бар У Джо»."""
        return " ".join(name.split())

    def analyze_merchants(
        self,
        records: list[ExpenseRecord],
        current_period: str | None = None,
        top_k: int = 5,
    ) -> list["MerchantStats"]:
        """Layer 2: топ дискреционных мерчантов текущего периода.

        Чисто информационный слой (где сосредоточены сжимаемые траты). Несжимаемые
        категории исключаются. Не входит в U(a) и не влияет на выбор a*.
        """
        period = self._resolve_current_period(records, current_period)
        if period is None:
            return []

        agg: dict[str, dict] = {}
        for rec in records:
            if rec.period != period or not rec.merchant:
                continue
            name = self._normalize_merchant(rec.merchant)
            if not name:
                continue
            slot = agg.setdefault(name, {"total": 0.0, "count": 0, "category": rec.category})
            slot["total"] += rec.amount
            slot["count"] += 1
            slot["category"] = rec.category

        result: list[MerchantStats] = []
        for name, data in agg.items():
            comp = self.compressibility(data["category"])
            if comp <= OBLIGATORY_CEILING:
                continue  # несжимаемые мерчанты (ЖКХ и т.п.) не советуем
            count = data["count"]
            total = round(data["total"], 2)
            result.append(MerchantStats(
                merchant=name,
                total=total,
                count=count,
                avg_check=round(total / count, 2) if count else 0.0,
                category=data["category"],
                compressibility=comp,
            ))

        result.sort(key=lambda m: m.total, reverse=True)
        return result[:top_k]

    @staticmethod
    def theil_sen(points: list[tuple[float, float]]) -> float:
        """Робастный наклон: медиана попарных наклонов (x по календарным месяцам)."""
        slopes = [
            (yj - yi) / (xj - xi)
            for (xi, yi), (xj, yj) in combinations(points, 2)
            if xj != xi
        ]
        return float(median(slopes)) if slopes else 0.0

    @staticmethod
    def _month_ordinal(period: str) -> int:
        """«YYYY-MM» → порядковый номер месяца, чтобы наклон был на реальный месяц."""
        year, month = period.split("-")
        return int(year) * 12 + (int(month) - 1)

    def analyze_trends(
        self,
        records: list[ExpenseRecord],
        current_period: str | None = None,
        top_k: int | None = None,
    ) -> list["TemporalPattern"]:
        """Layer 3-A: тренды категорий по завершённым месяцам.

        Текущий (последний) период исключается из тренда — он обычно неполный.
        Наклон робастный (Theil-Sen), пропуски месяцев учитываются по календарю.
        Возвращаются только значимые тренды (|slope_pct| ≥ порога), отсортированные
        по абсолютному ₽-влиянию, не более top_k. Информационный слой: не входит
        в U(a) и не влияет на выбор a*.
        """
        top_k = self.top_k if top_k is None else top_k
        current_period = self._resolve_current_period(records, current_period)
        if current_period is None:
            return []

        sums: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for rec in records:
            sums[rec.category][rec.period] += rec.amount

        patterns: list[TemporalPattern] = []
        for category, by_period in sums.items():
            past_periods = sorted(p for p in by_period if p != current_period)
            if len(past_periods) < self.min_months:
                continue

            points = [(self._month_ordinal(p), by_period[p]) for p in past_periods]
            slope = self.theil_sen(points)
            baseline = float(median([by_period[p] for p in past_periods]))
            slope_pct = (slope / baseline * 100.0) if baseline else 0.0
            if abs(slope_pct) < TREND_PCT_THRESHOLD:
                continue

            direction = "rising" if slope_pct > 0 else "falling"
            slope = round(slope, 2)
            slope_pct = round(slope_pct, 1)
            baseline = round(baseline, 2)
            patterns.append(TemporalPattern(
                category=category,
                direction=direction,
                slope_abs=slope,
                slope_pct=slope_pct,
                baseline=baseline,
                months_observed=len(past_periods),
                message=self._format_trend(category, direction, slope, slope_pct, baseline),
            ))

        patterns.sort(key=lambda p: abs(p.slope_abs), reverse=True)
        return patterns[:top_k]

    @staticmethod
    def _format_trend(category: str, direction: str, slope_abs: float, slope_pct: float, baseline: float) -> str:
        if direction == "rising":
            return (
                f"Траты на «{category}» растут примерно на {abs(slope_pct):.0f}% в месяц "
                f"(+{slope_abs:,.0f} ₽/мес к норме ~{baseline:,.0f} ₽). "
                f"Если динамика сохранится, стоит присмотреться к этой категории."
            ).replace(",", " ")
        return (
            f"Траты на «{category}» снижаются примерно на {abs(slope_pct):.0f}% в месяц "
            f"(норма ~{baseline:,.0f} ₽/мес). Хорошая динамика."
        ).replace(",", " ")

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
