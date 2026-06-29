"""Telegram-бот: каркас привязки аккаунта и команд (P3.6).

Бот связывает Telegram-чат с аккаунтом FINPILOT, чтобы слать туда те же уведомления,
что email/in-app. Привязка — через одноразовый link-токен (deep link `?start=<token>`):

1. В вебе пользователь запрашивает привязку → получает deep link с токеном.
2. Открывает бота по ссылке → бот получает `/start <token>` → связывает chat_id с user_id.
3. Команды бота: /start [token], /link <token>, /unlink, /status.

Реальная отправка в Telegram и приём webhook работают только на проде (публичный HTTPS +
доступ к api.telegram.org, который из песочницы отдаёт 403 — как cbr.ru). Поэтому здесь
тестируется логика: выпуск/проверка токена, разбор команд и привязка в БД (TelegramService
без токена — no-op, реальный HTTP не вызывается), secret-валидация webhook, веб-эндпоинты.
"""
from __future__ import annotations

from app.database import crud
from app.database.db import SessionLocal
from app.database.models import User
from app.services.security import token_service
from app.services.telegram import process_update, telegram_service
from app.utils.time import utcnow


# ─────────────────────────── helpers ───────────────────────────

def _register(client, email: str) -> str:
    r = client.post("/api/auth/register",
                    json={"email": email, "password": "password123", "consent": True})
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _uid(email: str) -> str:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first().id
    finally:
        db.close()


def _chat_update(chat_id: int, text: str) -> dict:
    """Минимальный Telegram update с текстовым сообщением."""
    return {"message": {"chat": {"id": chat_id}, "text": text}}


# ─────────────────────── link-токен (TokenService) ───────────────────────

class TestLinkToken:
    def test_issue_decode_roundtrip(self) -> None:
        tok = token_service.issue_telegram_link("user-123", "t@test.io")
        assert token_service.decode_telegram_link(tok) == "user-123"

    def test_wrong_purpose_rejected(self) -> None:
        # Токен сброса пароля не должен годиться как link-токен.
        reset = token_service.issue_password_reset("user-123", "t@test.io")
        assert token_service.decode_telegram_link(reset) is None

    def test_garbage_rejected(self) -> None:
        assert token_service.decode_telegram_link("not-a-jwt") is None


# ─────────────────────── CRUD привязки ───────────────────────

class TestLinkCrud:
    def test_link_and_lookup(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_link@test.io", password_hash="x")
        crud.link_telegram(db, u.id, "chat-555")
        found = crud.get_user_by_telegram_chat(db, "chat-555")
        assert found is not None and found.id == u.id

    def test_unlink(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_unlink@test.io", password_hash="x")
        crud.link_telegram(db, u.id, "chat-777")
        crud.unlink_telegram(db, u.id)
        assert crud.get_user_by_telegram_chat(db, "chat-777") is None

    def test_chat_reassigned_to_new_user(self, db_session) -> None:
        """Один Telegram-чат может быть привязан только к одному аккаунту:
        повторная привязка к другому пользователю снимает её с прежнего."""
        db = db_session
        a = crud.create_user(db, email="tg_a@test.io", password_hash="x")
        b = crud.create_user(db, email="tg_b@test.io", password_hash="x")
        crud.link_telegram(db, a.id, "chat-dup")
        crud.link_telegram(db, b.id, "chat-dup")

        found = crud.get_user_by_telegram_chat(db, "chat-dup")
        assert found.id == b.id
        db.refresh(a)
        assert a.telegram_chat_id is None


# ─────────────────────── команды бота (process_update) ───────────────────────

class TestProcessUpdate:
    def test_start_without_token_greets_no_link(self, db_session) -> None:
        db = db_session
        reply = process_update(db, _chat_update(1001, "/start"))
        assert reply is not None
        assert str(reply["chat_id"]) == "1001"
        assert reply["text"]  # приветствие непустое
        # Никто не привязан.
        assert crud.get_user_by_telegram_chat(db, "1001") is None

    def test_start_with_token_links(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_start@test.io", password_hash="x")
        tok = token_service.issue_telegram_link(u.id, u.email)

        reply = process_update(db, _chat_update(2002, f"/start {tok}"))
        assert reply is not None
        linked = crud.get_user_by_telegram_chat(db, "2002")
        assert linked is not None and linked.id == u.id

    def test_link_command_links(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_linkcmd@test.io", password_hash="x")
        tok = token_service.issue_telegram_link(u.id, u.email)

        process_update(db, _chat_update(3003, f"/link {tok}"))
        assert crud.get_user_by_telegram_chat(db, "3003").id == u.id

    def test_link_invalid_token_no_link(self, db_session) -> None:
        db = db_session
        reply = process_update(db, _chat_update(4004, "/link garbage"))
        assert reply is not None  # бот отвечает сообщением об ошибке
        assert crud.get_user_by_telegram_chat(db, "4004") is None

    def test_unlink_command(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_unlinkcmd@test.io", password_hash="x")
        crud.link_telegram(db, u.id, "5005")

        process_update(db, _chat_update(5005, "/unlink"))
        assert crud.get_user_by_telegram_chat(db, "5005") is None

    def test_status_linked_vs_unlinked(self, db_session) -> None:
        db = db_session
        u = crud.create_user(db, email="tg_status@test.io", password_hash="x")

        # Не привязан.
        r1 = process_update(db, _chat_update(6006, "/status"))
        assert r1 is not None

        crud.link_telegram(db, u.id, "6006")
        r2 = process_update(db, _chat_update(6006, "/status"))
        assert r2 is not None
        # Тексты для разных состояний различаются.
        assert r1["text"] != r2["text"]

    def test_no_message_returns_none(self, db_session) -> None:
        # Update без message (например, edited_message/прочее) — игнор.
        assert process_update(db_session, {"update_id": 1}) is None


# ─────────────────────── webhook + веб-эндпоинты ───────────────────────

class TestWebhookEndpoint:
    def test_webhook_processes_update(self, client, monkeypatch) -> None:
        # Перехватываем отправку (реальный HTTP в песочнице недоступен).
        sent: list = []
        monkeypatch.setattr(telegram_service, "send_message",
                            lambda chat_id, text: sent.append((chat_id, text)) or True)

        r = client.post("/api/telegram/webhook", json=_chat_update(7007, "/start"))
        assert r.status_code == 200, r.text
        assert r.json()["ok"] is True
        assert len(sent) == 1  # бот ответил приветствием

    def test_webhook_rejects_wrong_secret(self, client, monkeypatch) -> None:
        # Если secret задан в конфиге, неправильный заголовок отклоняется.
        from app.config import settings
        monkeypatch.setattr(settings, "TELEGRAM_WEBHOOK_SECRET", "expected-secret")
        r = client.post("/api/telegram/webhook", json=_chat_update(8008, "/start"),
                        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"})
        assert r.status_code == 403


class TestWebLinkEndpoints:
    def test_link_endpoint_returns_deep_link(self, client) -> None:
        token = _register(client, "tg_web_link@test.io")
        r = client.post("/api/telegram/link", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "link_token" in data
        assert "deep_link" in data
        assert "start=" in data["deep_link"]

    def test_status_endpoint(self, client) -> None:
        token = _register(client, "tg_web_status@test.io")
        uid = _uid("tg_web_status@test.io")
        # Не привязан.
        r1 = client.get("/api/telegram/status", headers={"Authorization": f"Bearer {token}"})
        assert r1.status_code == 200
        assert r1.json()["linked"] is False

        # Привязываем напрямую и проверяем.
        db = SessionLocal()
        try:
            crud.link_telegram(db, uid, "9009")
        finally:
            db.close()
        r2 = client.get("/api/telegram/status", headers={"Authorization": f"Bearer {token}"})
        assert r2.json()["linked"] is True

    def test_unlink_endpoint(self, client) -> None:
        token = _register(client, "tg_web_unlink@test.io")
        uid = _uid("tg_web_unlink@test.io")
        db = SessionLocal()
        try:
            crud.link_telegram(db, uid, "1010")
        finally:
            db.close()

        r = client.post("/api/telegram/unlink", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        db = SessionLocal()
        try:
            assert crud.get_user_by_telegram_chat(db, "1010") is None
        finally:
            db.close()

    def test_link_requires_auth(self, client) -> None:
        assert client.post("/api/telegram/link").status_code == 401
        assert client.get("/api/telegram/status").status_code == 401


# ─────────────────── хук: уведомления уходят и в Telegram ───────────────────

class TestTelegramNotificationHook:
    """При рассылке (run_user_notifications) пользователь с привязанным Telegram
    получает уведомление и туда — рядом с email и in-app."""

    def test_goal_deadline_sent_to_telegram(self, db_session, monkeypatch) -> None:
        from datetime import timedelta

        from app.services import notifications as notif

        db = db_session
        u = crud.create_user(db, email="tg_hook@test.io", password_hash="x")
        crud.link_telegram(db, u.id, "hookchat-1")
        crud.create_goal(db, name="Отпуск", target_amount=100000, current_amount=10000,
                         deadline=utcnow() + timedelta(days=4), user_id=u.id)

        sent: list = []
        monkeypatch.setattr(notif.telegram_service, "send_message",
                            lambda chat_id, text: sent.append((chat_id, text)) or True)

        notif.run_user_notifications(db, u)
        assert any(chat == "hookchat-1" for chat, _ in sent)

    def test_no_telegram_when_not_linked(self, db_session, monkeypatch) -> None:
        from datetime import timedelta

        from app.services import notifications as notif

        db = db_session
        u = crud.create_user(db, email="tg_nohook@test.io", password_hash="x")  # без привязки
        crud.create_goal(db, name="Цель", target_amount=100000, current_amount=10000,
                         deadline=utcnow() + timedelta(days=4), user_id=u.id)

        sent: list = []
        monkeypatch.setattr(notif.telegram_service, "send_message",
                            lambda chat_id, text: sent.append((chat_id, text)) or True)

        notif.run_user_notifications(db, u)
        assert sent == []  # некуда слать — Telegram не привязан
