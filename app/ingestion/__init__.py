"""Ingestion-слой v3.0.0 (международный/B2B).

Provider-agnostic загрузка данных и адаптация ядра под контракт FinanceEngine
(KEEP-07). Источник (ManualProvider/PlaidProvider/B2B) отдаёт FinancialSnapshot,
движок (CoreFinanceEngine) возвращает Recommendation — связь только через Protocol.
"""
