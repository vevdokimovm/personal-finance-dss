"""Telegram-бот (P3.6): отправка сообщений и разбор команд.

Без TELEGRAM_BOT_TOKEN сервис — тихий no-op (как email_service): команды разбираются
и привязка в БД происходит, но реальная отправка в Telegram пропускается. Реальная
доставка и приём webhook работают только на проде (публичный HTTPS + доступ к
api.telegram.org; из песочницы он отдаёт 403).

Привязка аккаунта — через одноразовый link-токен (TokenService.issue_telegram_link),
который кладётся в deep link `https://t.me/<bot>?start=<token>`. Бот, получив
`/start <token>` или `/link <token>`, связывает chat_id с user_id.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.database import crud
from app.services.security import token_service

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org"

_GREETING = (
    "Привет! Это бот FINPILOT — помощник по личным финансам.\n"
    "Чтобы получать сюда уведомления, привяжите аккаунт: откройте FINPILOT в браузере, "
    "раздел уведомлений, и нажмите «Привязать Telegram». Либо пришлите команду "
    "/link с кодом привязки."
)
_LINKED_OK = "Готово! Аккаунт привязан — уведомления будут приходить сюда."
_LINK_BAD = "Код привязки недействителен или истёк. Сгенерируйте новый в приложении."
_UNLINKED = "Telegram отвязан от аккаунта. Уведомления сюда больше не приходят."
_NOT_LINKED = "Этот чат не привязан ни к одному аккаунту. Используйте /link <код> для привязки."
_STATUS_LINKED = "Аккаунт привязан. Уведомления приходят в этот чат."
_STATUS_UNLINKED = "Аккаунт не привязан. Используйте /link <код>, чтобы привязать."
_UNKNOWN = "Не понял команду. Доступно: /start, /link <код>, /unlink, /status."


class TelegramService:
    """Тонкая обёртка над Telegram Bot API. Без токена — тихий no-op."""

    def __init__(self) -> None:
        self.enabled = settings.telegram_enabled
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.username = settings.TELEGRAM_BOT_USERNAME

    def deep_link(self, link_token: str) -> str:
        """Ссылка-приглашение в бота с токеном привязки."""
        user = self.username or "your_bot"
        return f"https://t.me/{user}?start={link_token}"

    def send_message(self, chat_id: str, text: str) -> bool:
        """Отправить сообщение в чат. Без токена — no-op (возвращает False)."""
        if not self.enabled:
            logger.info("telegram no-op (token not set): chat=%s", chat_id)
            return False
        url = f"{_API_BASE}/bot{self.token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError) as exc:  # сеть/таймаут — не валим вызывающий код
            logger.warning("telegram send failed: %s", exc)
            return False


telegram_service = TelegramService()


def _extract_command_arg(text: str) -> tuple[str, Optional[str]]:
    """Разбирает '/cmd arg' → ('/cmd', 'arg'). Без аргумента → ('/cmd', None)."""
    parts = text.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else None
    return cmd, arg


def process_update(db: Session, update: dict) -> Optional[dict]:
    """Обрабатывает Telegram update. Привязка/отвязка пишется в БД здесь же.

    Возвращает {'chat_id': str, 'text': str} с ответом бота, либо None, если в апдейте
    нет текстового сообщения (edited_message, callback и пр. — игнорируем в каркасе).
    Саму отправку делает вызывающий код (webhook) через telegram_service.send_message.
    """
    message = update.get("message")
    if not message or "text" not in message:
        return None

    chat_id = str(message["chat"]["id"])
    cmd, arg = _extract_command_arg(message["text"])

    if cmd == "/start":
        if arg:  # deep link с токеном привязки
            return {"chat_id": chat_id, "text": _try_link(db, chat_id, arg)}
        return {"chat_id": chat_id, "text": _GREETING}

    if cmd == "/link":
        if not arg:
            return {"chat_id": chat_id, "text": "Пришлите код: /link <код привязки>."}
        return {"chat_id": chat_id, "text": _try_link(db, chat_id, arg)}

    if cmd == "/unlink":
        user = crud.get_user_by_telegram_chat(db, chat_id)
        if user is None:
            return {"chat_id": chat_id, "text": _NOT_LINKED}
        crud.unlink_telegram(db, user.id)
        return {"chat_id": chat_id, "text": _UNLINKED}

    if cmd == "/status":
        linked = crud.get_user_by_telegram_chat(db, chat_id) is not None
        return {"chat_id": chat_id, "text": _STATUS_LINKED if linked else _STATUS_UNLINKED}

    return {"chat_id": chat_id, "text": _UNKNOWN}


def _try_link(db: Session, chat_id: str, link_token: str) -> str:
    """Проверить link-токен и привязать чат к аккаунту. Возвращает текст ответа."""
    user_id = token_service.decode_telegram_link(link_token)
    if user_id is None:
        return _LINK_BAD
    linked = crud.link_telegram(db, user_id, chat_id)
    return _LINKED_OK if linked is not None else _LINK_BAD
