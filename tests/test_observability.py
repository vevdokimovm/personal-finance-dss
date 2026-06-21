"""Наблюдаемость и прод-готовность (P1.5).

Покрывает: эндпоинт /health (liveness + проверка БД), структурное JSON-логирование,
сквозной request_id в ответе, опциональную инициализацию Sentry (без DSN — no-op).
"""
from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient

from app.logging_config import JsonFormatter
from app.observability import init_sentry


class TestHealthCheck:
    def test_health_ok(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["database"] == "ok"
        assert "version" in data

    def test_health_no_auth_required(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200


class TestStructuredLogging:
    def test_json_formatter_outputs_valid_json(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x", lineno=1,
            msg="hello %s", args=("world",), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["message"] == "hello world"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
        assert parsed["logger"] == "test"

    def test_json_formatter_includes_exception(self) -> None:
        formatter = JsonFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="t", level=logging.ERROR, pathname="x", lineno=1,
                msg="failed", args=(), exc_info=sys.exc_info(),
            )
        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]

    def test_request_id_in_response_header(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.headers.get("X-Request-ID")

    def test_request_logged_with_context(self, client: TestClient, monkeypatch) -> None:
        from app import middleware

        captured: list[dict] = []
        monkeypatch.setattr(
            middleware._request_logger,
            "info",
            lambda msg, *a, **kw: captured.append(kw.get("extra", {})),
        )
        client.get("/health")
        match = [c for c in captured if c.get("path") == "/health"]
        assert match, "request не залогирован структурно"
        assert match[-1]["status_code"] == 200
        assert "request_id" in match[-1]
        assert "latency_ms" in match[-1]


class TestSentry:
    def test_init_sentry_without_dsn_is_noop(self) -> None:
        assert init_sentry("") is False
        assert init_sentry(None) is False
