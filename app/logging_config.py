"""Структурное логирование (P1.5).

JSON-логи в stdout — машиночитаемо и готово под агрегацию (Loki/ELK/Datadog).
Контекстные поля (request_id, путь, статус, латентность) добавляются через extra
в RequestLoggingMiddleware и попадают в каждую запись запроса.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

_CONTEXT_FIELDS = ("request_id", "method", "path", "status_code", "latency_ms", "user_id")

# Маскирование ПДн в логах (юрблок L10). Финансовый портрет — чувствительнее
# паспорта, а отладочный вывод с суммами и адресами уезжает в систему
# агрегации и живёт там годами. Маскируем на форматтере, а не на вызовах:
# полагаться на дисциплину каждого `logger.info` бесполезно.
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Денежная сумма: четыре и более значащих цифр, с копейками или без.
# Короткие числа (коды ответов, счётчики, идентификаторы шагов) не трогаем.
_MONEY_RE = re.compile(r"\b\d{4,}(?:[.,]\d{1,2})?\b")


def scrub(text: str) -> str:
    """Убирает из строки e-mail и денежные суммы."""
    text = _EMAIL_RE.sub("<email>", text)
    return _MONEY_RE.sub("<amount>", text)


class JsonFormatter(logging.Formatter):
    """Форматирует запись лога в одну строку JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": scrub(record.getMessage()),
        }
        for field in _CONTEXT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Настраивает корневой логгер: JSON в проде, человекочитаемый текст в dev."""
    handler = logging.StreamHandler()
    if json_format:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Шумные access-логи uvicorn глушим — свой RequestLoggingMiddleware информативнее.
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False
