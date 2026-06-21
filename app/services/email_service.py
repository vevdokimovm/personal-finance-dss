"""Отправка email (приветственное письмо при регистрации).

Если SMTP не сконфигурирован (settings.email_enabled == False) — модуль работает
как no-op: пишет в лог и ничего не отправляет. Регистрация никогда не падает
из-за почты: отправка вызывается фоновой задачей и любые ошибки логируются.
"""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("finpilot.email")


class EmailService:
    """Тонкая обёртка над SMTP. Без конфигурации — тихий no-op."""

    def __init__(self) -> None:
        self.enabled = settings.email_enabled
        self.sender = settings.SMTP_FROM or settings.SMTP_USER

    def send_welcome(self, to_email: str, display_name: str | None = None) -> bool:
        """Отправляет приветственное письмо. Возвращает True при успехе."""
        name = display_name or to_email.split("@")[0]
        subject = "Добро пожаловать в FINPILOT"
        text = (
            f"Здравствуйте, {name}!\n\n"
            "Вы зарегистрировались в FINPILOT — системе поддержки принятия решений "
            "по личным финансам. Теперь вы можете загрузить операции, задать цели и "
            "обязательства, а алгоритм подскажет, как распределить свободные деньги "
            "между досрочным погашением кредитов, подушкой безопасности и целями.\n\n"
            "Хорошего планирования!\n"
            "— Команда FINPILOT"
        )
        html = f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:auto;color:#1a1a1a;">
  <h2 style="color:#2BBF6A;">Добро пожаловать в FINPILOT</h2>
  <p>Здравствуйте, <strong>{name}</strong>!</p>
  <p>Вы зарегистрировались в FINPILOT — системе поддержки принятия решений по личным
  финансам. Загрузите операции, задайте цели и обязательства — алгоритм подскажет,
  как распределить свободные деньги между досрочным погашением кредитов, подушкой
  безопасности и целями.</p>
  <p style="color:#777;font-size:13px;">Хорошего планирования!<br>— Команда FINPILOT</p>
</div>"""
        return self._send(to_email, subject, text, html)

    def send_verification(self, to_email: str, verify_url: str, display_name: str | None = None) -> bool:
        """Письмо со ссылкой подтверждения email."""
        name = display_name or to_email.split("@")[0]
        subject = "Подтвердите email — FINPILOT"
        text = (
            f"Здравствуйте, {name}!\n\n"
            "Чтобы завершить регистрацию в FINPILOT, подтвердите ваш email, перейдя "
            f"по ссылке:\n\n{verify_url}\n\n"
            "Ссылка действует 48 часов. Если вы не регистрировались — просто "
            "проигнорируйте это письмо.\n\n— Команда FINPILOT"
        )
        html = f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:auto;color:#1a1a1a;">
  <h2 style="color:#2BBF6A;">Подтвердите ваш email</h2>
  <p>Здравствуйте, <strong>{name}</strong>!</p>
  <p>Чтобы завершить регистрацию в FINPILOT, подтвердите email:</p>
  <p><a href="{verify_url}" style="display:inline-block;padding:12px 28px;background:#2BBF6A;
     color:#fff;text-decoration:none;border-radius:8px;font-weight:600;">Подтвердить email</a></p>
  <p style="color:#777;font-size:13px;">Ссылка действует 48 часов. Если вы не регистрировались — проигнорируйте письмо.</p>
</div>"""
        return self._send(to_email, subject, text, html)

    def send_password_reset(self, to_email: str, reset_url: str, display_name: str | None = None) -> bool:
        """Письмо со ссылкой для сброса пароля."""
        name = display_name or to_email.split("@")[0]
        subject = "Сброс пароля — FINPILOT"
        text = (
            f"Здравствуйте, {name}!\n\n"
            "Вы запросили сброс пароля в FINPILOT. Чтобы задать новый пароль, перейдите "
            f"по ссылке:\n\n{reset_url}\n\n"
            "Ссылка действует 1 час. Если вы не запрашивали сброс — просто проигнорируйте "
            "это письмо, ваш пароль останется прежним.\n\n— Команда FINPILOT"
        )
        html = f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:auto;color:#1a1a1a;">
  <h2 style="color:#2BBF6A;">Сброс пароля</h2>
  <p>Здравствуйте, <strong>{name}</strong>!</p>
  <p>Вы запросили сброс пароля в FINPILOT. Задайте новый пароль:</p>
  <p><a href="{reset_url}" style="display:inline-block;padding:12px 28px;background:#2BBF6A;
     color:#fff;text-decoration:none;border-radius:8px;font-weight:600;">Задать новый пароль</a></p>
  <p style="color:#777;font-size:13px;">Ссылка действует 1 час. Если вы не запрашивали сброс — проигнорируйте письмо.</p>
</div>"""
        return self._send(to_email, subject, text, html)

    def send_goal_deadline_reminder(
        self, to_email: str, goal_name: str, days_left: int,
        current: float, target: float, display_name: str | None = None,
    ) -> bool:
        """Напоминание о приближении дедлайна цели."""
        name = display_name or to_email.split("@")[0]
        when = "сегодня" if days_left <= 0 else f"через {days_left} дн."
        subject = f"Цель «{goal_name}» — дедлайн близко"
        text = (
            f"Здравствуйте, {name}!\n\n"
            f"Дедлайн вашей цели «{goal_name}» наступает {when}. "
            f"Накоплено {current:,.0f} из {target:,.0f} руб.\n\n"
            "Загляните в FINPILOT, чтобы при необходимости скорректировать план.\n\n"
            "— Команда FINPILOT"
        ).replace(",", " ")
        html = f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:auto;color:#1a1a1a;">
  <h2 style="color:#2BBF6A;">Дедлайн цели близко</h2>
  <p>Здравствуйте, <strong>{name}</strong>!</p>
  <p>Дедлайн цели «<strong>{goal_name}</strong>» наступает <strong>{when}</strong>.
  Накоплено {current:,.0f} из {target:,.0f} руб.</p>
  <p style="color:#777;font-size:13px;">Загляните в FINPILOT, чтобы скорректировать план.<br>— Команда FINPILOT</p>
</div>""".replace(",", " ")
        return self._send(to_email, subject, text, html)

    def send_budget_overrun_alert(
        self, to_email: str, category: str, spent: float, limit: float,
        display_name: str | None = None,
    ) -> bool:
        """Уведомление о превышении бюджета по категории (информационное)."""
        name = display_name or to_email.split("@")[0]
        over = max(0.0, spent - limit)
        subject = f"Превышен бюджет: «{category}»"
        text = (
            f"Здравствуйте, {name}!\n\n"
            f"Расходы по категории «{category}» превысили бюджет: "
            f"{spent:,.0f} из {limit:,.0f} руб (на {over:,.0f} больше).\n\n"
            "Это информационное уведомление, а не списание.\n\n"
            "— Команда FINPILOT"
        ).replace(",", " ")
        html = f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:560px;margin:auto;color:#1a1a1a;">
  <h2 style="color:#E0533D;">Превышен бюджет</h2>
  <p>Здравствуйте, <strong>{name}</strong>!</p>
  <p>Расходы по категории «<strong>{category}</strong>» превысили бюджет:
  {spent:,.0f} из {limit:,.0f} руб (на {over:,.0f} больше).</p>
  <p style="color:#777;font-size:13px;">Это информационное уведомление, а не списание.<br>— Команда FINPILOT</p>
</div>""".replace(",", " ")
        return self._send(to_email, subject, text, html)

    def _send(self, to_email: str, subject: str, text: str, html: str) -> bool:
        if not self.enabled:
            logger.info("Email отключён (нет SMTP-конфига) — письмо для %s не отправлено.", to_email)
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = to_email
        message.set_content(text)
        message.add_alternative(html, subtype="html")

        try:
            if settings.SMTP_USE_TLS:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(
                    settings.SMTP_HOST, settings.SMTP_PORT,
                    context=ssl.create_default_context(), timeout=10,
                ) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(message)
            logger.info("Приветственное письмо отправлено на %s.", to_email)
            return True
        except Exception as exc:  # noqa: BLE001 — почта не должна ронять регистрацию
            logger.warning("Не удалось отправить письмо на %s: %s", to_email, exc)
            return False


email_service = EmailService()
