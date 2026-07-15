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

    def test_init_sentry_with_dsn_passes_release_and_env(self, monkeypatch) -> None:
        import sentry_sdk

        captured: dict = {}
        monkeypatch.setattr(sentry_sdk, "init", lambda **kw: captured.update(kw))

        ok = init_sentry(
            "https://examplePublicKey@o0.ingest.sentry.io/0",
            environment="staging",
            release="9.9.9",
        )
        assert ok is True
        assert captured["dsn"].startswith("https://")
        assert captured["environment"] == "staging"
        assert captured["release"] == "9.9.9"

    def test_lifespan_initialises_sentry_with_app_version(self, monkeypatch) -> None:
        # Sentry должен подключаться на старте приложения, а DSN/release — браться из
        # настроек (release = версия, чтобы ошибки группировались по релизу).
        import app.main as main_mod
        from app.config import settings

        captured: dict = {}

        def _fake_init(dsn, **kw):
            captured["dsn"] = dsn
            captured.update(kw)
            return False

        monkeypatch.setattr(main_mod, "init_sentry", _fake_init)
        with TestClient(main_mod.app):
            pass

        assert "dsn" in captured, "init_sentry не вызван при старте приложения (lifespan)"
        assert captured["dsn"] == settings.SENTRY_DSN
        assert captured.get("release") == settings.APP_VERSION
        assert captured.get("environment") == settings.ENVIRONMENT
