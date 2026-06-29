"""Telegram-бот (P3.6): webhook + привязка аккаунта.

- POST /telegram/webhook — приём апдейтов от Telegram (на проде: setWebhook на этот URL).
  Если задан TELEGRAM_WEBHOOK_SECRET, апдейты без совпадающего заголовка отклоняются (403).
- POST /telegram/link — выдать пользователю одноразовый код привязки + deep link в бота.
- GET  /telegram/status — привязан ли Telegram к аккаунту.
- POST /telegram/unlink — отвязать.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import crud
from app.database.db import get_db
from app.database.models import User
from app.dependencies import require_user
from app.services.security import token_service
from app.services.telegram import process_update, telegram_service

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/webhook", summary="Приём апдейтов Telegram (для setWebhook на проде)")
def telegram_webhook(
    update: dict,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    # Если secret настроен — апдейт обязан принести совпадающий заголовок. Пустой
    # secret (dev) проверку пропускает, чтобы не мешать локальной разработке.
    expected = settings.TELEGRAM_WEBHOOK_SECRET
    if expected and x_telegram_bot_api_secret_token != expected:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    reply = process_update(db, update)
    if reply:
        telegram_service.send_message(reply["chat_id"], reply["text"])
    return {"ok": True}


@router.post("/link", summary="Получить код и ссылку для привязки Telegram")
def telegram_link(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    link_token = token_service.issue_telegram_link(user.id, user.email)
    return {
        "link_token": link_token,
        "deep_link": telegram_service.deep_link(link_token),
        "bot_username": settings.TELEGRAM_BOT_USERNAME or None,
    }


@router.get("/status", summary="Статус привязки Telegram")
def telegram_status(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    return {"linked": user.telegram_chat_id is not None}


@router.post("/unlink", summary="Отвязать Telegram от аккаунта")
def telegram_unlink(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    crud.unlink_telegram(db, user.id)
    return {"status": "ok"}
