"""Plaid-интеграция: шифрованный TokenStore + провайдер (FR-18, INFRA-16, INFRA-17).

Назначение — open-banking-рынки (US/CA): одна интеграция → тысячи банков.
Для РФ неприменимо (KEEP-06), поэтому путь опционален и активируется только при
заданных PLAID_* в .env.

Безопасность (NFR-06, CONSTR-04):
  - access_token хранится через TokenStore ТОЛЬКО в шифрованном виде (Fernet);
  - токен никогда не логируется и не возвращается в API/URL;
  - сырой PlaidClient развязан Protocol-ом — реальный SDK подключается отдельно,
    тесты используют фейковый клиент.

Реальный `plaid-python` намеренно НЕ импортируется на уровне модуля: пакет может
отсутствовать в РФ-сборке. `RealPlaidClient` импортирует SDK лениво, при создании.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.models import PlaidToken
from app.ingestion.models import (
    Account,
    Debt,
    FinancialSnapshot,
    Transaction,
    TransactionType,
)
from app.services.security import TokenCipher


class EncryptedTokenStore:
    """TokenStore с шифрованием access_token «в покое» (INFRA-17, NFR-06)."""

    def __init__(self, db: Session, cipher: TokenCipher | None = None) -> None:
        self._db = db
        self._cipher = cipher or TokenCipher()

    def save(self, user_ref: str, item_id: str, access_token: str) -> None:
        encrypted = self._cipher.encrypt(access_token)
        row = PlaidToken(
            user_id=user_ref,
            item_id=item_id,
            token_encrypted=encrypted,
            created_at=datetime.utcnow(),
        )
        self._db.add(row)
        self._db.commit()

    def load(self, user_ref: str) -> str | None:
        row = (
            self._db.query(PlaidToken)
            .filter(PlaidToken.user_id == user_ref)
            .order_by(PlaidToken.created_at.desc())
            .first()
        )
        if row is None:
            return None
        return self._cipher.decrypt(row.token_encrypted)


class PlaidProvider:
    """FinancialDataProvider поверх Plaid (INFRA-16). Нормализует в FinancialSnapshot."""

    name = "plaid"

    def __init__(self, client, token_store: EncryptedTokenStore, base_currency: str = "USD") -> None:
        self._client = client
        self._tokens = token_store
        self._base_currency = base_currency

    def fetch_snapshot(self, user_ref: str) -> FinancialSnapshot:
        access_token = self._tokens.load(user_ref)
        if not access_token:
            return FinancialSnapshot(base_currency=self._base_currency)

        accounts = [self._map_account(a) for a in self._client.accounts_get(access_token)]
        transactions = [self._map_txn(t) for t in self._client.transactions_get(access_token)]
        debts = [self._map_debt(d) for d in self._client.liabilities_get(access_token)]

        return FinancialSnapshot(
            base_currency=self._base_currency,
            accounts=accounts,
            transactions=transactions,
            debts=debts,
            goals=[],
        )

    # ── Нормализация Plaid → канон ───────────────────────────────────
    def _map_account(self, raw: dict) -> Account:
        subtype = str(raw.get("subtype", "")).lower()
        is_liquid = subtype in {"savings", "money market", "cd", "cash management"}
        return Account(
            account_id=str(raw.get("account_id", "")),
            name=str(raw.get("name", "Account")),
            balance=_dec(raw.get("balances", {}).get("available") or raw.get("balances", {}).get("current", 0)),
            currency=str(raw.get("balances", {}).get("iso_currency_code") or self._base_currency),
            is_liquid=is_liquid,
        )

    def _map_txn(self, raw: dict) -> Transaction:
        amount = _dec(raw.get("amount", 0))
        # Plaid: положительная сумма = расход (списание), отрицательная = поступление.
        txn_type = TransactionType.EXPENSE if amount >= 0 else TransactionType.INCOME
        return Transaction(
            transaction_id=str(raw.get("transaction_id", "")),
            amount=abs(amount),
            type=txn_type,
            date=_parse_date(raw.get("date")),
            currency=str(raw.get("iso_currency_code") or self._base_currency),
            description=raw.get("name"),
            mcc=str(raw["mcc"]) if raw.get("mcc") else None,
        )

    def _map_debt(self, raw: dict) -> Debt:
        return Debt(
            debt_id=str(raw.get("account_id", "")),
            name=str(raw.get("name", "Debt")),
            balance=_dec(raw.get("balance", 0)),
            monthly_payment=_dec(raw.get("minimum_payment_amount", 0)),
            interest_rate=_dec(raw.get("apr", 0)) / Decimal("100"),
            currency=str(raw.get("iso_currency_code") or self._base_currency),
        )


class RealPlaidClient:
    """PlaidClient поверх официального plaid-python SDK (INFRA-16).

    SDK импортируется лениво — модуль не требует пакета в РФ-сборке.
    """

    def __init__(self, client_id: str, secret: str, environment: str = "sandbox") -> None:
        try:
            import plaid  # type: ignore
            from plaid.api import plaid_api  # type: ignore
        except ImportError as exc:  # pragma: no cover - зависит от окружения
            raise RuntimeError(
                "plaid-python не установлен. Добавьте 'plaid-python' в requirements "
                "для активации open-banking-синхронизации."
            ) from exc

        host = {
            "sandbox": plaid.Environment.Sandbox,
            "production": plaid.Environment.Production,
        }.get(environment, plaid.Environment.Sandbox)
        configuration = plaid.Configuration(
            host=host,
            api_key={"clientId": client_id, "secret": secret},
        )
        self._api = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def accounts_get(self, access_token: str) -> list[dict]:  # pragma: no cover - сетевой вызов
        from plaid.model.accounts_get_request import AccountsGetRequest  # type: ignore

        response = self._api.accounts_get(AccountsGetRequest(access_token=access_token))
        return [a.to_dict() for a in response["accounts"]]

    def transactions_get(self, access_token: str) -> list[dict]:  # pragma: no cover - сетевой вызов
        from plaid.model.transactions_sync_request import TransactionsSyncRequest  # type: ignore

        response = self._api.transactions_sync(TransactionsSyncRequest(access_token=access_token))
        return [t.to_dict() for t in response["added"]]

    def liabilities_get(self, access_token: str) -> list[dict]:  # pragma: no cover - сетевой вызов
        from plaid.model.liabilities_get_request import LiabilitiesGetRequest  # type: ignore

        response = self._api.liabilities_get(LiabilitiesGetRequest(access_token=access_token))
        liabilities = response.get("liabilities", {})
        result: list[dict] = []
        for credit in liabilities.get("credit", []) or []:
            result.append(credit.to_dict() if hasattr(credit, "to_dict") else dict(credit))
        return result


def _dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _parse_date(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.utcnow()
    return datetime.utcnow()
