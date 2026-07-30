"""Согласия и юридические документы (юрблок L1, L3, L4, L5).

Три эндпоинта состояния/выдачи/отзыва плюс публичный реестр документов: фронту
нужно знать не только что показать, но и КАКУЮ РЕДАКЦИЮ он показывает, чтобы
записать именно её.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.legal import DISCLAIMER_39FZ, LEGAL_DOCUMENTS, is_known
from app.database.db import get_db
from app.database.models import User
from app.dependencies import require_user
from app.services.consent import (
    ConsentWithdrawalNotAllowed,
    consent_state,
    grant_consent,
    withdraw_consent,
)

router = APIRouter(tags=["Согласия и право"])


@router.get("/consents", summary="Состояние согласий пользователя")
def get_consents(user: User = Depends(require_user),
                 db: Session = Depends(get_db)) -> dict:
    """Все известные типы, включая невыданные: фронт должен знать, что спросить."""
    return {"consents": consent_state(db, user.id)}


@router.post("/consents/{consent_type}", summary="Выдать согласие")
def grant(consent_type: str, request: Request,
          user: User = Depends(require_user),
          db: Session = Depends(get_db)) -> dict:
    if not is_known(consent_type):
        raise HTTPException(status_code=404, detail="Неизвестный тип согласия")
    record = grant_consent(
        db, user.id, consent_type,
        source_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"granted": True, "type": consent_type,
            "version": record.doc_version,
            "granted_at": record.granted_at.isoformat()}


@router.delete("/consents/{consent_type}", summary="Отозвать согласие")
def withdraw(consent_type: str, user: User = Depends(require_user),
             db: Session = Depends(get_db)) -> Response:
    if not is_known(consent_type):
        raise HTTPException(status_code=404, detail="Неизвестный тип согласия")
    try:
        withdraw_consent(db, user.id, consent_type)
    except ConsentWithdrawalNotAllowed:
        raise HTTPException(
            status_code=409,
            detail="Это согласие — основание обработки ваших данных. "
                   "Отозвать его можно только вместе с удалением аккаунта: "
                   "DELETE /api/auth/account",
        )
    # 204 отдаётся явным Response без status_code в декораторе: иначе FastAPI
    # ставит application/json на пустое тело и WebKit ломается (engineering_practices).
    return Response(status_code=204)


@router.get("/legal/documents", summary="Реестр юридических документов")
def legal_documents() -> dict:
    """Публичный: версии нужны и до входа — на странице регистрации."""
    return {
        "documents": {
            key: {"title": doc["title"], "version": doc["version"],
                  "effective_from": doc["effective_from"], "url": doc["url"]}
            for key, doc in LEGAL_DOCUMENTS.items()
        },
        "disclaimer_39fz": DISCLAIMER_39FZ,
    }
