"""Тесты наблюдаемой обёртки фоновой отправки писем (dispatch_email).

Проверяют, что результат фоновой отправки фиксируется продуктовым событием
(email_sent / email_failed / email_skipped), что PII (полный адрес) не утекает
в аналитику, и что обёртка никогда не падает исключением (фон не должен рушиться
без следа). Сеть не используется — отправка и log_event замоканы.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.database.models import Event
from app.services import email_dispatch
from app.services.email_dispatch import dispatch_email
from app.services.email_service import email_service


class TestDispatchEventLogging:
    def test_sent_logs_email_sent_event(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(email_service, "enabled", True)
        with patch.object(email_dispatch, "log_event") as mock_log:
            ok = dispatch_email(
                lambda: True, event_kind="verification",
                to_email="user@example.com", user_id=42,
            )
        assert ok is True
        mock_log.assert_called_once_with(
            "email_sent", {"kind": "verification", "email_domain": "example.com"}, user_id=42
        )

    def test_failed_logs_email_failed_event(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(email_service, "enabled", True)
        with patch.object(email_dispatch, "log_event") as mock_log:
            ok = dispatch_email(
                lambda: False, event_kind="password_reset",
                to_email="user@example.com", user_id=7,
            )
        assert ok is False
        mock_log.assert_called_once_with(
            "email_failed", {"kind": "password_reset", "email_domain": "example.com"}, user_id=7
        )

    def test_skipped_when_email_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Без SMTP-конфига send() — no-op (возвращает False), но это НЕ сбой:
        # классифицируем как skipped, а не failed.
        monkeypatch.setattr(email_service, "enabled", False)
        with patch.object(email_dispatch, "log_event") as mock_log:
            ok = dispatch_email(
                lambda: False, event_kind="welcome",
                to_email="user@example.com", user_id=1,
            )
        assert ok is False
        mock_log.assert_called_once_with(
            "email_skipped", {"kind": "welcome", "email_domain": "example.com"}, user_id=1
        )


class TestDispatchResilience:
    def test_exception_in_send_logs_failed_and_does_not_raise(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(email_service, "enabled", True)

        def boom() -> bool:
            raise RuntimeError("smtp blew up")

        with patch.object(email_dispatch, "log_event") as mock_log:
            ok = dispatch_email(
                boom, event_kind="verification",
                to_email="user@example.com", user_id=5,
            )
        assert ok is False
        event_type, payload = mock_log.call_args[0]
        assert event_type == "email_failed"
        assert payload["kind"] == "verification"
        assert payload["email_domain"] == "example.com"
        assert payload["error"] == "RuntimeError"
        assert mock_log.call_args.kwargs["user_id"] == 5


class TestDispatchPrivacy:
    def test_payload_uses_domain_not_full_address(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(email_service, "enabled", True)
        with patch.object(email_dispatch, "log_event") as mock_log:
            dispatch_email(
                lambda: True, event_kind="verification",
                to_email="alice.secret@bank.ru", user_id=9,
            )
        payload = mock_log.call_args[0][1]
        assert payload["email_domain"] == "bank.ru"
        assert "alice.secret@bank.ru" not in str(payload)
        assert "alice.secret" not in str(payload)

    def test_address_without_at_yields_empty_domain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(email_service, "enabled", True)
        with patch.object(email_dispatch, "log_event") as mock_log:
            dispatch_email(
                lambda: True, event_kind="welcome",
                to_email="malformed", user_id=None,
            )
        assert mock_log.call_args[0][1]["email_domain"] == ""


class TestDispatchWiredIntoRegistration:
    """Проводка end-to-end: реальная регистрация оставляет наблюдаемое событие об
    отправке. В тест-среде SMTP не настроен → событие email_skipped. Это и есть
    устранение «молчаливой маскировки»: даже no-op фиксируется в events."""

    def test_register_emits_email_event(self, client) -> None:
        from app.database.db import SessionLocal

        r = client.post(
            "/api/auth/register",
            json={"email": "wire@fp.io", "password": "strongpass1"},
        )
        assert r.status_code == 201

        session = SessionLocal()
        try:
            events = (
                session.query(Event)
                .filter(Event.event_type.in_(["email_sent", "email_failed", "email_skipped"]))
                .all()
            )
        finally:
            session.close()

        assert len(events) >= 1
        ev = events[-1]
        assert ev.event_payload["kind"] == "verification"
        assert ev.event_payload["email_domain"] == "fp.io"
