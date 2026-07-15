"""Protocol-контракты ingestion-слоя (KEEP-07, INFRA-15..18).

Движок зависит ТОЛЬКО от этих интерфейсов, не от конкретных реализаций.
Новая страна = новый FinancialDataProvider; смена движка = новый FinanceEngine.
Это и есть развязка «источник ↔ движок», ради которой строится слой.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ingestion.models import FinancialSnapshot, Recommendation, RiskProfile


@runtime_checkable
class FinanceEngine(Protocol):
    """Контракт движка СППР (INFRA-15). Реальное ядро SAW+Avalanche+MC под него адаптировано."""

    def analyze(
        self, snapshot: FinancialSnapshot, profile: RiskProfile
    ) -> Recommendation: ...


@runtime_checkable
class FinancialDataProvider(Protocol):
    """Контракт источника данных (KEEP-06, KEEP-07). Manual/Plaid/CSV/B2B реализуют его."""

    name: str

    def fetch_snapshot(self, user_ref: str) -> FinancialSnapshot: ...


@runtime_checkable
class TokenStore(Protocol):
    """Хранилище провайдер-токенов (INFRA-17). Реализация обязана шифровать «в покое»."""

    def save(self, user_ref: str, item_id: str, access_token: str) -> None: ...

    def load(self, user_ref: str) -> str | None: ...


@runtime_checkable
class PlaidClient(Protocol):
    """Тонкая обёртка над plaid-python SDK (INFRA-16). Развязана ради тестируемости."""

    def accounts_get(self, access_token: str) -> list[dict]: ...

    def transactions_get(self, access_token: str) -> list[dict]: ...

    def liabilities_get(self, access_token: str) -> list[dict]: ...
