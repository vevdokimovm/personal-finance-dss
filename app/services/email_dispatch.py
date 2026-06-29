"""Наблюдаемая обёртка над фоновой отправкой писем.

Транспорт (`EmailService`) ничего не знает о пользователе и о продуктовой
аналитике — он просто формирует и шлёт письмо. При отправке через
`BackgroundTasks` его результат (ушло / no-op / сбой) терялся: на проде сбой
SMTP был виден только в текстовом логе, в таблице `events` — ничего. Из-за этого
проблема «письма не приходят» маскировалась — не было наблюдаемого следа.

Эта обёртка вызывается из фоновой задачи вместо прямого вызова сервиса и
фиксирует РЕЗУЛЬТАТ отправки продуктовым событием:
  - `email_sent`    — почта сконфигурирована и письмо ушло;
  - `email_skipped` — SMTP не настроен (намеренный no-op, self-hosted без почты);
  - `email_failed`  — почта сконфигурирована, но отправка не удалась (или упала).

В payload кладётся только домен адреса (`email_domain`), не сам адрес — PII не
утекает в аналитику (тот же приём, что в событии `login_failed`).
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

from app.services.email_service import email_service
from app.services.event_logger import log_event

logger = logging.getLogger("finpilot.email")


def dispatch_email(
    send: Callable[[], bool],
    *,
    event_kind: str,
    to_email: str,
    user_id: Optional[int] = None,
) -> bool:
    """Выполняет фоновую отправку и фиксирует её результат событием.

    Возвращает результат отправки (True — письмо ушло). Никогда не пробрасывает
    исключение: фоновая задача не должна падать молча, без следа в аналитике.
    """
    domain = to_email.rsplit("@", 1)[-1] if "@" in to_email else ""

    try:
        ok = send()
    except Exception as exc:  # noqa: BLE001 — фон не должен падать без события
        logger.warning("Отправка письма (%s) упала исключением: %s", event_kind, exc)
        log_event(
            "email_failed",
            {"kind": event_kind, "email_domain": domain, "error": type(exc).__name__},
            user_id=user_id,
        )
        return False

    if not email_service.enabled:
        status = "email_skipped"
    elif ok:
        status = "email_sent"
    else:
        status = "email_failed"

    log_event(status, {"kind": event_kind, "email_domain": domain}, user_id=user_id)
    return ok
