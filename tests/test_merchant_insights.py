"""Layer 2 советов по расходам — анализ мерчантов (P2.2).

Информационный слой: где сосредоточены дискреционные траты по конкретным мерчантам.
Не влияет на U(a)/a* — это аналитика трат, отдельная от ядра оптимизации.
"""
from __future__ import annotations

from app.core.spending_advice import ExpenseRecord, MerchantStats, SpendingAdvisor


def _rec(category: str, amount: float, period: str, merchant: str | None) -> ExpenseRecord:
    return ExpenseRecord(category=category, amount=amount, period=period, merchant=merchant)


class TestMerchantAnalysis:
    def test_groups_and_ranks_by_total(self) -> None:
        advisor = SpendingAdvisor()
        records = [
            _rec("Кафе и рестораны", 1000, "2026-06", "Кофейня А"),
            _rec("Кафе и рестораны", 2000, "2026-06", "Кофейня А"),
            _rec("Развлечения", 500, "2026-06", "Кинотеатр Б"),
        ]
        merchants = advisor.analyze_merchants(records, current_period="2026-06")
        assert isinstance(merchants[0], MerchantStats)
        assert merchants[0].merchant == "Кофейня А"
        assert merchants[0].total == 3000
        assert merchants[0].count == 2

    def test_obligatory_merchants_excluded(self) -> None:
        advisor = SpendingAdvisor()
        records = [
            _rec("ЖКХ и связь", 5000, "2026-06", "Управляющая компания"),  # несжимаемое
            _rec("Развлечения", 1000, "2026-06", "Бар"),
        ]
        names = [m.merchant for m in advisor.analyze_merchants(records, current_period="2026-06")]
        assert "Управляющая компания" not in names
        assert "Бар" in names

    def test_avg_check(self) -> None:
        advisor = SpendingAdvisor()
        records = [
            _rec("Развлечения", 1000, "2026-06", "X"),
            _rec("Развлечения", 3000, "2026-06", "X"),
        ]
        m = advisor.analyze_merchants(records, current_period="2026-06")[0]
        assert m.avg_check == 2000

    def test_only_current_period(self) -> None:
        advisor = SpendingAdvisor()
        records = [
            _rec("Развлечения", 9999, "2026-05", "Старый мерчант"),
            _rec("Развлечения", 100, "2026-06", "Текущий мерчант"),
        ]
        names = [m.merchant for m in advisor.analyze_merchants(records, current_period="2026-06")]
        assert names == ["Текущий мерчант"]

    def test_merchant_names_normalized(self) -> None:
        advisor = SpendingAdvisor()
        records = [
            _rec("Развлечения", 1000, "2026-06", "  Бар   У Джо  "),
            _rec("Развлечения", 500, "2026-06", "Бар У Джо"),
        ]
        merchants = advisor.analyze_merchants(records, current_period="2026-06")
        assert len(merchants) == 1  # схлопнулись в один
        assert merchants[0].total == 1500

    def test_empty_when_no_merchant(self) -> None:
        advisor = SpendingAdvisor()
        records = [_rec("Развлечения", 1000, "2026-06", None)]
        assert advisor.analyze_merchants(records, current_period="2026-06") == []


class TestServiceMerchantInsights:
    def test_endpoint_returns_merchant_insights(self, client) -> None:
        r = client.get("/api/planning/spending-advice")
        assert r.status_code == 200
        assert "merchant_insights" in r.json()
