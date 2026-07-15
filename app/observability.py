"""Трекинг ошибок через Sentry (P1.5) — опционально.

Если SENTRY_DSN не задан, init_sentry — тихий no-op (локальная разработка и тесты
работают без Sentry). DSN, проект и алерты настраиваются на стороне деплоя.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def init_sentry(
    dsn: str | None,
    environment: str = "production",
    release: str | None = None,
    traces_sample_rate: float = 0.1,
) -> bool:
    """Инициализирует Sentry, если задан DSN. Возвращает True при успешной инициализации."""
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            integrations=[StarletteIntegration(), FastApiIntegration()],
            traces_sample_rate=traces_sample_rate,
        )
        logger.info("Sentry initialised (environment=%s)", environment)
        return True
    except Exception:
        logger.warning("Sentry init failed — продолжаем без него.", exc_info=True)
        return False
