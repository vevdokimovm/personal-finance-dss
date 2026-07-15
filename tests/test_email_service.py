"""Тесты транспорта EmailService: STARTTLS/SSL-пути, аутентификация, устойчивость к
ошибкам и no-op без конфига. Сеть не используется — smtplib замокан."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.config import settings
from app.services.email_service import EmailService


@pytest.fixture
def smtp_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USER", "bot@example.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(settings, "SMTP_FROM", "noreply@example.com")
    monkeypatch.setattr(settings, "SMTP_USE_TLS", True)


class TestSendTransport:
    def test_starttls_path_sends(self, smtp_config: None) -> None:
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            server = mock_smtp.return_value.__enter__.return_value
            ok = EmailService().send_welcome("user@example.com", "User")
        assert ok is True
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("bot@example.com", "secret")
        server.send_message.assert_called_once()

    def test_ssl_path_sends(self, monkeypatch: pytest.MonkeyPatch, smtp_config: None) -> None:
        monkeypatch.setattr(settings, "SMTP_USE_TLS", False)
        monkeypatch.setattr(settings, "SMTP_PORT", 465)
        with patch("app.services.email_service.smtplib.SMTP_SSL") as mock_ssl:
            server = mock_ssl.return_value.__enter__.return_value
            ok = EmailService().send_welcome("user@example.com")
        assert ok is True
        server.login.assert_called_once()
        server.send_message.assert_called_once()

    def test_sender_falls_back_to_user_when_from_empty(
        self, monkeypatch: pytest.MonkeyPatch, smtp_config: None
    ) -> None:
        monkeypatch.setattr(settings, "SMTP_FROM", "")
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            server = mock_smtp.return_value.__enter__.return_value
            EmailService().send_welcome("user@example.com")
        msg = server.send_message.call_args[0][0]
        assert msg["From"] == "bot@example.com"


class TestSendResilience:
    def test_smtp_error_returns_false(self, smtp_config: None) -> None:
        with patch("app.services.email_service.smtplib.SMTP", side_effect=OSError("refused")):
            ok = EmailService().send_welcome("user@example.com")
        assert ok is False

    def test_noop_when_not_configured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(settings, "SMTP_HOST", "")
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            ok = EmailService().send_welcome("user@example.com")
        assert ok is False
        mock_smtp.assert_not_called()


class TestMessageContent:
    def test_message_has_text_and_html_parts(self, smtp_config: None) -> None:
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            server = mock_smtp.return_value.__enter__.return_value
            EmailService().send_welcome("user@example.com", "User")
        msg = server.send_message.call_args[0][0]
        assert msg.is_multipart()
        subtypes = {part.get_content_subtype() for part in msg.iter_parts()}
        assert {"plain", "html"} <= subtypes

    def test_verification_embeds_url(self, smtp_config: None) -> None:
        url = "https://finpilot.ru/verify?token=abc123"
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            server = mock_smtp.return_value.__enter__.return_value
            EmailService().send_verification("user@example.com", url)
        msg = server.send_message.call_args[0][0]
        bodies = " ".join(part.get_content() for part in msg.iter_parts())
        assert "finpilot.ru/verify" in bodies

    def test_password_reset_embeds_url(self, smtp_config: None) -> None:
        url = "https://finpilot.ru/reset?token=xyz789"
        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp:
            server = mock_smtp.return_value.__enter__.return_value
            EmailService().send_password_reset("user@example.com", url)
        msg = server.send_message.call_args[0][0]
        bodies = " ".join(part.get_content() for part in msg.iter_parts())
        assert "finpilot.ru/reset" in bodies
