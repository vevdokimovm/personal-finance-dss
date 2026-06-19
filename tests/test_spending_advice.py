"""Тесты ядра рекомендаций по тратам (мат-модель v3.0.0, §§3-7).

Проверяют математику (медиана-норма, MAD, robust z-score, pain-score),
генерацию советов и устойчивость к краевым случаям (MAD=0, мало истории,
пустой вход, нулевые счётчики).
"""
import pytest

from app.core.spending_advice import (
    DEFAULT_COMPRESSIBILITY,
    ExpenseRecord,
    SpendingAdvisor,
)


def _months(category, values_by_period, txns_per_month=1):
    """Хелпер: строит ExpenseRecord-ы. values_by_period: {period: month_total}.
    Каждый месяц бьётся на txns_per_month равных операций."""
    records = []
    for period, total in values_by_period.items():
        per = total / txns_per_month
        for _ in range(txns_per_month):
            records.append(ExpenseRecord(category=category, amount=per, period=period))
    return records


class TestRobustStatistics:
    def test_mad_basic(self):
        # отклонения от центра 10: [0,2,2,4,6] → медиана модулей = 2
        vals = [10, 12, 8, 14, 16]
        assert SpendingAdvisor.mad(vals, 10.0) == 2.0

    def test_mad_empty(self):
        assert SpendingAdvisor.mad([], 5.0) == 0.0

    def test_zscore_basic(self):
        # 0.6745 * (20 - 10) / 2 = 3.3725
        z = SpendingAdvisor.robust_zscore(20.0, 10.0, 2.0)
        assert z == pytest.approx(3.3725, abs=1e-4)

    def test_zscore_mad_zero_no_division(self):
        # MAD=0 не должно делить на ноль — возвращаем 0
        assert SpendingAdvisor.robust_zscore(100.0, 10.0, 0.0) == 0.0

    def test_zscore_negative_for_underspend(self):
        assert SpendingAdvisor.robust_zscore(5.0, 10.0, 2.0) < 0

    def test_compressibility_known_and_default(self):
        assert SpendingAdvisor.compressibility("Кафе и рестораны") == 1.0
        assert SpendingAdvisor.compressibility("ЖКХ и связь") == 0.1
        assert SpendingAdvisor.compressibility("Неизвестная") == DEFAULT_COMPRESSIBILITY


class TestAnalyze:
    def test_baseline_is_median_of_past_months(self):
        # прошлые месяцы 10,12,8 → медиана 10; текущий 30
        records = _months("Кафе и рестораны", {"2026-01": 10, "2026-02": 12, "2026-03": 8, "2026-04": 30})
        stats = SpendingAdvisor().analyze(records, current_period="2026-04")
        cafe = next(s for s in stats if s.category == "Кафе и рестораны")
        assert cafe.baseline == 10.0
        assert cafe.current == 30.0
        assert cafe.months_observed == 3

    def test_anomaly_flagged(self):
        # стабильно 100 три месяца (MAD=0!) → z=0, не аномалия (защита от ложного срабатывания)
        records = _months("Покупки", {"2026-01": 100, "2026-02": 100, "2026-03": 100, "2026-04": 999})
        stats = SpendingAdvisor().analyze(records, current_period="2026-04")
        buy = next(s for s in stats if s.category == "Покупки")
        assert buy.mad == 0.0
        assert buy.z_score == 0.0
        assert buy.is_anomaly is False

    def test_anomaly_with_spread(self):
        # есть разброс → крупный перерасход ловится
        records = _months("Развлечения", {"2026-01": 100, "2026-02": 120, "2026-03": 80, "2026-04": 500})
        stats = SpendingAdvisor().analyze(records, current_period="2026-04")
        ent = next(s for s in stats if s.category == "Развлечения")
        assert ent.z_score > 3.5
        assert ent.is_anomaly is True

    def test_fail_loud_insufficient_history(self):
        # только 2 прошлых месяца < MIN_MONTHS=3 → категория не анализируется
        records = _months("Кафе и рестораны", {"2026-01": 10, "2026-02": 12, "2026-03": 30})
        stats = SpendingAdvisor().analyze(records, current_period="2026-03")
        assert stats == []

    def test_empty_input(self):
        assert SpendingAdvisor().analyze([], current_period="2026-04") == []
        assert SpendingAdvisor().analyze([]) == []

    def test_low_txn_count_skipped(self):
        # 4 месяца, но всего 2 операции (< MIN_CATEGORY_TXNS=3) → пропуск
        records = [
            ExpenseRecord("Покупки", 100, "2026-01"),
            ExpenseRecord("Покупки", 100, "2026-02"),
        ]
        # добавим 2 пустых периода-заглушки в другой категории, чтобы был current
        records += _months("Прочее", {"2026-01": 5, "2026-02": 5, "2026-03": 5, "2026-04": 5}, txns_per_month=2)
        stats = SpendingAdvisor().analyze(records, current_period="2026-04")
        assert all(s.category != "Покупки" for s in stats)

    def test_pain_score_orders_results(self):
        records = (
            _months("Кафе и рестораны", {"2026-01": 200, "2026-02": 200, "2026-03": 200, "2026-04": 200}, txns_per_month=10)
            + _months("Продукты", {"2026-01": 1000, "2026-02": 1000, "2026-03": 1000, "2026-04": 1000}, txns_per_month=4)
        )
        stats = SpendingAdvisor().analyze(records, current_period="2026-04")
        # отсортировано по pain_score убыв.
        pains = [s.pain_score for s in stats]
        assert pains == sorted(pains, reverse=True)


class TestGenerateAdvice:
    def test_overspend_advice(self):
        records = _months("Развлечения", {"2026-01": 1000, "2026-02": 1200, "2026-03": 800, "2026-04": 5000}, txns_per_month=3)
        advice = SpendingAdvisor().generate_advice(records, current_period="2026-04")
        ent = next(a for a in advice if a.category == "Развлечения")
        assert ent.reason == "overspend"
        # экономия = current - baseline = 5000 - 1000 = 4000
        assert ent.potential_saving == pytest.approx(4000.0, abs=1.0)

    def test_obligatory_category_excluded(self):
        # ЖКХ (v_c=0.1) не должен попадать в советы даже при перерасходе
        records = _months("ЖКХ и связь", {"2026-01": 5000, "2026-02": 5200, "2026-03": 4800, "2026-04": 20000}, txns_per_month=2)
        advice = SpendingAdvisor().generate_advice(records, current_period="2026-04")
        assert all(a.category != "ЖКХ и связь" for a in advice)

    def test_min_saving_filter(self):
        # маленькие траты: дискреционное сокращение ниже порога 500 → нет совета
        records = _months("Подписки и сервисы", {"2026-01": 300, "2026-02": 300, "2026-03": 300, "2026-04": 300}, txns_per_month=3)
        advice = SpendingAdvisor().generate_advice(records, current_period="2026-04")
        # 0.15 * 0.7 * 300 = 31.5 < 500
        assert all(a.category != "Подписки и сервисы" for a in advice)

    def test_top_k_limit(self):
        records = []
        for cat in ["Кафе и рестораны", "Развлечения", "Покупки", "Транспорт"]:
            records += _months(cat, {"2026-01": 8000, "2026-02": 8000, "2026-03": 8000, "2026-04": 8000}, txns_per_month=10)
        advice = SpendingAdvisor(top_k=3).generate_advice(records, current_period="2026-04")
        assert len(advice) <= 3

    def test_empty_input_no_advice(self):
        assert SpendingAdvisor().generate_advice([]) == []
