"""Security-регрессии (SEC-4.4) — защитная сетка для харденинга.

Фиксируют инварианты, которые легко сломать незаметным изменением: security-заголовки
обязаны стоять на ЛЮБОМ типе ответа (успех/ошибка/редирект/CSRF-отказ), CSRF-проверка
обязана срабатывать на ВСЕХ изменяющих методах, а старт-гард — валить production с
дефолтными/отсутствующими секретами (включая ключ шифрования «в покое»).
"""
from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from app.config import Settings, validate_production_security
from app.middleware import SecurityHeadersMiddleware

_HEADERS = [
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Content-Security-Policy",
]
_FERNET_KEY = "PpUqrWqj3kK0n0a9rO2mWqH3sT6vY8bX1cZ4dF7gH0k="  # валидный по форме


def _assert_security_headers(resp) -> None:
    for h in _HEADERS:
        assert h in resp.headers, f"нет заголовка {h} (статус {resp.status_code})"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"


# ── A. Заголовки безопасности на всех типах ответов ───────────────────────

class TestSecurityHeadersOnEveryResponse:
    def test_on_200(self, client: TestClient) -> None:
        _assert_security_headers(client.get("/health"))

    def test_on_404(self, client: TestClient) -> None:
        r = client.get("/api/this-route-does-not-exist")
        assert r.status_code == 404
        _assert_security_headers(r)

    def test_on_401(self, client: TestClient) -> None:
        r = client.get("/api/auth/me")  # без токена
        assert r.status_code == 401
        _assert_security_headers(r)

    def test_on_422(self, client: TestClient) -> None:
        r = client.post("/api/auth/register", json={"email": "not-an-email"})
        assert r.status_code == 422
        _assert_security_headers(r)

    def test_on_csrf_403(self, client: TestClient) -> None:
        # 403 от CSRFMiddleware обязан пройти обратно через SecurityHeadersMiddleware.
        r = client.post("/api/auth/login",
                        json={"email": "a@b.io", "password": "x"},
                        headers={"Origin": "https://evil.example"})
        assert r.status_code == 403
        _assert_security_headers(r)

    def test_csp_locks_framing_and_default_src(self, client: TestClient) -> None:
        csp = client.get("/health").headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp


# ── HSTS: только когда включён (production за TLS) ─────────────────────────

class TestHsts:
    @staticmethod
    def _dispatch(hsts: bool):
        mw = SecurityHeadersMiddleware(app=lambda *a: None, hsts=hsts)

        async def call_next(request):
            return PlainTextResponse("ok")

        req = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
        return asyncio.run(mw.dispatch(req, call_next))

    def test_hsts_present_when_enabled(self) -> None:
        resp = self._dispatch(hsts=True)
        assert resp.headers.get("Strict-Transport-Security", "").startswith("max-age=")

    def test_hsts_absent_when_disabled(self) -> None:
        resp = self._dispatch(hsts=False)
        assert "Strict-Transport-Security" not in resp.headers

    def test_hsts_absent_in_dev_app(self, client: TestClient) -> None:
        assert "Strict-Transport-Security" not in client.get("/health").headers


# ── B. CSRF-проверка на всех изменяющих методах ───────────────────────────
# CSRFMiddleware срабатывает по методу до роутинга, поэтому путь может быть любым.

class TestCsrfAcrossMethods:
    EVIL = {"Origin": "https://evil.example"}
    TRUSTED = {"Origin": "http://localhost:8000"}  # из CORS_ORIGINS по умолчанию

    def test_post_foreign_origin_blocked(self, client: TestClient) -> None:
        assert client.post("/api/x", headers=self.EVIL).status_code == 403

    def test_put_foreign_origin_blocked(self, client: TestClient) -> None:
        assert client.put("/api/x", headers=self.EVIL).status_code == 403

    def test_patch_foreign_origin_blocked(self, client: TestClient) -> None:
        assert client.patch("/api/x", headers=self.EVIL).status_code == 403

    def test_delete_foreign_origin_blocked(self, client: TestClient) -> None:
        assert client.delete("/api/x", headers=self.EVIL).status_code == 403

    def test_trusted_origin_not_csrf_blocked(self, client: TestClient) -> None:
        # Доверенный Origin не отвергается CSRF (статус любой, кроме 403).
        assert client.post("/api/x", headers=self.TRUSTED).status_code != 403

    def test_missing_origin_not_csrf_blocked(self, client: TestClient) -> None:
        # Не-браузерный клиент (нет Origin) CSRF-риска не несёт.
        assert client.post("/api/x").status_code != 403

    def test_bearer_bypasses_csrf(self, client: TestClient) -> None:
        # Запрос по Bearer не использует амбиентные cookies — CSRF не применяется.
        h = {**self.EVIL, "Authorization": "Bearer sometoken"}
        assert client.post("/api/x", headers=h).status_code != 403

    def test_safe_get_not_csrf_blocked(self, client: TestClient) -> None:
        assert client.get("/health", headers=self.EVIL).status_code != 403


# ── C. Старт-гард: production обязан иметь явные секреты ───────────────────

class TestProductionSecretsGuard:
    def test_missing_encryption_key_flagged(self) -> None:
        # Явный ключ шифрования «в покое» обязателен в production: иначе он
        # деривится из JWT_SECRET — нет разделения ключей, ротация невозможна.
        s = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 40,
                     COOKIE_SECURE=True, ADMIN_API_KEY="y" * 24)
        problems = validate_production_security(s)
        assert any("TOKEN_ENCRYPTION" in p for p in problems)

    def test_explicit_encryption_key_passes(self) -> None:
        s = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 40,
                     COOKIE_SECURE=True, ADMIN_API_KEY="y" * 24,
                     TOKEN_ENCRYPTION_KEY=_FERNET_KEY)
        assert validate_production_security(s) == []

    def test_encryption_keys_multi_passes(self) -> None:
        s = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 40,
                     COOKIE_SECURE=True, ADMIN_API_KEY="y" * 24,
                     TOKEN_ENCRYPTION_KEYS=_FERNET_KEY)
        assert validate_production_security(s) == []

    def test_development_still_clean(self) -> None:
        assert validate_production_security(Settings(ENVIRONMENT="development")) == []
