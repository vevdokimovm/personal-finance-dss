"""Plaid open-banking маршруты (FR-18, INFRA-16, INFRA-17).

Только для рынков с агрегатором (US/CA). Активны лишь при заданных PLAID_* в .env;
иначе любой вызов отвечает 404 «не активировано» (РФ-сборка, KEEP-06).

Поток: фронт получает public_token через Plaid Link → шлёт его сюда →
сервер обменивает на access_token и сохраняет ШИФРОВАННО (TokenStore, INFRA-17).
Сырой токен наружу не возвращается (NFR-06).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db import get_db
from app.database.models import User
from app.dependencies import require_user
from app.ingestion.engine import CoreFinanceEngine
from app.ingestion.providers.plaid import (
    EncryptedTokenStore,
    PlaidProvider,
    RealPlaidClient,
)
from app.services.currency import CurrencyConverter
from app.services.event_logger import log_event
from app.services.security import TokenCipher

router = APIRouter(prefix="/plaid", tags=["Plaid (open banking)"])


class ExchangeRequest(BaseModel):
    public_token: str
    item_id: str = "plaid-item"


def _ensure_plaid_enabled() -> RealPlaidClient:
    if not settings.PLAID_CLIENT_ID or not settings.PLAID_SECRET:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plaid-интеграция не активирована (нет PLAID_* в окружении).",
        )
    return RealPlaidClient(
        client_id=settings.PLAID_CLIENT_ID,
        secret=settings.PLAID_SECRET,
        environment=settings.PLAID_ENV,
    )


@router.post("/exchange", summary="Обменять public_token на access_token и сохранить (шифрованно)")
def exchange_token(
    payload: ExchangeRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = _ensure_plaid_enabled()
    try:
        # SDK-метод обмена; обёрнут в RealPlaidClient на стороне реальной интеграции.
        access_token = client.exchange_public_token(
            payload.public_token)  # type: ignore[attr-defined]
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Метод обмена токена не реализован в текущем клиенте.",
        )
    store = EncryptedTokenStore(db, TokenCipher())
    store.save(user.id, payload.item_id, access_token)
    log_event("plaid_linked", {"item_id": payload.item_id}, user_id=user.id)
    return {"detail": "Банк подключён. Токен сохранён в зашифрованном виде."}


@router.post("/sync", summary="Синхронизировать снимок из Plaid и получить рекомендацию")
def sync(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> dict:
    client = _ensure_plaid_enabled()
    store = EncryptedTokenStore(db, TokenCipher())
    provider = PlaidProvider(client, store, base_currency=settings.DEFAULT_BASE_CURRENCY)

    snapshot = provider.fetch_snapshot(user.id)
    converter = CurrencyConverter.from_db(db)
    rec = CoreFinanceEngine(converter=converter).analyze(snapshot, snapshot.risk_profile)

    log_event("plaid_synced", {"accounts": len(snapshot.accounts)}, user_id=user.id)
    return {
        "indicators": {
            "Rt": float(rec.rt), "Lt": float(rec.lt),
            "Dt": float(rec.dt), "BLR": float(rec.blr),
        },
        "allocation": {
            "to_debt": float(rec.allocation.to_debt),
            "to_reserve": float(rec.allocation.to_reserve),
            "to_goals": float(rec.allocation.to_goals),
        },
        "accounts_synced": len(snapshot.accounts),
        "transactions_synced": len(snapshot.transactions),
    }
